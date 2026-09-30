import struct
import pefile
import subprocess
import json
import os

exe_path = "/home/daun/aplikasi-prak/digitalworks/DigitalWorks.exe"
out_dir = "/home/daun/aplikasi-prak/digitalworks/re_extracted"
os.makedirs(f"{out_dir}/forms", exist_ok=True)

pe = pefile.PE(exe_path)
image_base = pe.OPTIONAL_HEADER.ImageBase

with open(exe_path, "rb") as f:
    raw_data = f.read()

def rva_to_off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.Misc_VirtualSize:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None

def va_to_off(va):
    return rva_to_off(va - image_base)

def read_ptr(off):
    if off + 4 <= len(raw_data):
        return struct.unpack("<I", raw_data[off:off+4])[0]
    return 0

def read_shortstring(va):
    off = va_to_off(va)
    if off is None or off >= len(raw_data):
        return ""
    length = raw_data[off]
    if length > 100 or off + 1 + length > len(raw_data):
        return ""
    try:
        return raw_data[off+1:off+1+length].decode("latin1")
    except Exception:
        return ""

# 1. Extract and save raw DFM resources
print("[-] Extracting DFM form resources...")
for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    if entry.name is None and entry.struct.Id == 10:  # RCDATA
        for sub in entry.directory.entries:
            sub_name = str(sub.name or sub.struct.Id)
            data_rva = sub.directory.entries[0].data.struct.OffsetToData
            data_size = sub.directory.entries[0].data.struct.Size
            raw_off = rva_to_off(data_rva)
            if raw_off:
                form_bytes = raw_data[raw_off:raw_off + data_size]
                with open(f"{out_dir}/forms/{sub_name}.raw", "wb") as f_out:
                    f_out.write(form_bytes)

# 2. Extract Delphi Classes, VMTs, and Published Methods
print("[-] Scanning Delphi VMTs and Methods...")
code_sec = next(s for s in pe.sections if s.Name.startswith(b"CODE"))
data_sec = next(s for s in pe.sections if s.Name.startswith(b"DATA"))

classes_dict = {}
for sec in [code_sec, data_sec]:
    start = sec.PointerToRawData
    end = start + sec.SizeOfRawData
    for off in range(start + 76, end - 4, 4):
        self_ptr = read_ptr(off - 76)
        expected_va = image_base + sec.VirtualAddress + (off - start)
        if self_ptr == expected_va:
            cname_ptr = read_ptr(off - 44)
            name = read_shortstring(cname_ptr)
            if name and name.startswith("T") and len(name) > 1 and name[1].isupper():
                parent_vmt = read_ptr(off - 36)
                method_tbl_va = read_ptr(off - 52)
                
                methods = []
                if method_tbl_va != 0:
                    mtbl_off = va_to_off(method_tbl_va)
                    if mtbl_off:
                        count = struct.unpack("<H", raw_data[mtbl_off:mtbl_off + 2])[0]
                        p = mtbl_off + 2
                        for _ in range(count):
                            if p + 6 >= len(raw_data):
                                break
                            size = struct.unpack("<H", raw_data[p:p + 2])[0]
                            addr = struct.unpack("<I", raw_data[p + 2:p + 6])[0]
                            nlen = raw_data[p + 6]
                            mname = raw_data[p + 7:p + 7 + nlen].decode("latin1", errors="ignore")
                            methods.append({"name": mname, "address": hex(addr)})
                            p += size

                classes_dict[name] = {
                    "className": name,
                    "vmt_address": hex(expected_va),
                    "parent_vmt": hex(parent_vmt),
                    "methods_count": len(methods),
                    "published_methods": methods
                }

with open(f"{out_dir}/classes_and_methods.json", "w") as f_out:
    json.dump(classes_dict, f_out, indent=2)

with open(f"{out_dir}/symbols_map.txt", "w") as f_out:
    f_out.write("=================================================================\n")
    f_out.write("DIGITAL WORKS (DELPHI 5) - RECOVERED SYMBOLS & EVENT HANDLERS MAP\n")
    f_out.write("=================================================================\n\n")
    for cname in sorted(classes_dict.keys()):
        info = classes_dict[cname]
        vmt_addr = info["vmt_address"]
        f_out.write(f"Class: {cname} (VMT: {vmt_addr})\n")
        for m in info["published_methods"]:
            f_out.write(f"  {m['address']} : {m['name']}\n")
        f_out.write("\n")

print(f"[+] Successfully extracted {len(classes_dict)} Delphi classes to {out_dir}/symbols_map.txt")
