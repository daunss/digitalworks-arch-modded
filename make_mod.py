import struct
import pefile
import capstone

pe_orig = pefile.PE('DigitalWorks.exe.orig')
with open('DigitalWorks.exe.orig', 'rb') as f:
    exe_data = bytearray(f.read())

# PE Header analysis
pe_off = struct.unpack('<I', exe_data[0x3c:0x40])[0]
num_sections = struct.unpack('<H', exe_data[pe_off+6:pe_off+8])[0]
opt_hdr_sz = struct.unpack('<H', exe_data[pe_off+20:pe_off+22])[0]
sec_tbl_off = pe_off + 24 + opt_hdr_sz
sec_align = struct.unpack('<I', exe_data[pe_off+56:pe_off+60])[0]
file_align = struct.unpack('<I', exe_data[pe_off+60:pe_off+64])[0]

# Calculate max VA and max RawOff
max_va = 0
max_raw = 0
for i in range(num_sections):
    s_off = sec_tbl_off + i * 40
    va = struct.unpack('<I', exe_data[s_off+12:s_off+16])[0]
    vs = struct.unpack('<I', exe_data[s_off+8:s_off+12])[0]
    raw_off = struct.unpack('<I', exe_data[s_off+20:s_off+24])[0]
    raw_sz = struct.unpack('<I', exe_data[s_off+16:s_off+20])[0]
    va_end = (va + vs + sec_align - 1) & ~(sec_align - 1)
    raw_end = (raw_off + raw_sz + file_align - 1) & ~(file_align - 1)
    if va_end > max_va: max_va = va_end
    if raw_end > max_raw: max_raw = raw_end

print(f"[+] Existing sections: {num_sections}")
print(f"[+] New section VA: 0x{max_va:x} (Base VA: 0x{0x400000 + max_va:08x}), RawOff: 0x{len(exe_data):x}")

# Mod Section Config
MOD_RVA = max_va
MOD_VA = 0x400000 + MOD_RVA
MOD_SIZE = 0x2000 # 8192 bytes
mod_bytes = bytearray(MOD_SIZE)

# Layout inside .mod section:
# 0x000: Variables
# 0x020: Pointers table (30 dwords for snapshots + current + trigger)
# 0x100: String records (Delphi AnsiString)
# 0x600: Code

VA_UNDO_IDX   = MOD_VA + 0x000
VA_UNDO_CNT   = MOD_VA + 0x004
VA_IS_UNDOING = MOD_VA + 0x008
VA_LAST_TICK  = MOD_VA + 0x00c
VA_SAVED_DOC  = MOD_VA + 0x010

VA_STR_TABLE  = MOD_VA + 0x020
VA_STR_CURR   = MOD_VA + 0x098
VA_STR_TRIG   = MOD_VA + 0x09c

# Construct String Records starting at offset 0x100
str_off = 0x100
MAX_SNAPS = 30

for i in range(MAX_SNAPS):
    s = f".undo_history\\u{i:02d}.dwm\x00".encode('latin1')
    str_rec = struct.pack('<iI', -1, len(s) - 1) + s
    mod_bytes[str_off:str_off+len(str_rec)] = str_rec
    char_ptr = MOD_VA + str_off + 8
    struct.pack_into('<I', mod_bytes, 0x020 + i*4, char_ptr)
    str_off += (len(str_rec) + 3) & ~3

# current.dwm
s_curr = b".undo_history\\current.dwm\x00"
rec_curr = struct.pack('<iI', -1, len(s_curr) - 1) + s_curr
mod_bytes[str_off:str_off+len(rec_curr)] = rec_curr
struct.pack_into('<I', mod_bytes, 0x098, MOD_VA + str_off + 8)
str_off += (len(rec_curr) + 3) & ~3

# trigger_tt.txt
s_trig = b".undo_history\\trigger_tt.txt\x00"
rec_trig = struct.pack('<iI', -1, len(s_trig) - 1) + s_trig
mod_bytes[str_off:str_off+len(rec_trig)] = rec_trig
struct.pack_into('<I', mod_bytes, 0x09c, MOD_VA + str_off + 8)
str_off += (len(rec_trig) + 3) & ~3

print(f"[+] String records end at offset 0x{str_off:x}")

# Code starts at offset 0x600 (VA: MOD_VA + 0x600)
CODE_OFF = 0x600
CODE_VA = MOD_VA + CODE_OFF

# Generate assembly for code segment
asm_src = f"""
.intel_syntax noprefix
.text
.globl InitUndo, TakeSnapshot, DoUndo, DoRedo, DoTruthTable, Hook_SetModified, Hook_FormShortCut, Hook_FormShowEnd

.set SaveToFile,    0x004847a4
.set LoadFromFile,  0x004848f4
.set MainFormPtr,   0x004a2ec4
.set GetTickCount,  0x004a5328
.set GetKeyState,   0x004a56f0
.set CreateFileA,   0x004a53a0
.set CloseHandle,   0x004a53ac
.set OrigCleanup,   0x00403c88
.set SetModCont,    0x00487431
.set FormSCCont,    0x0049f2aa

InitUndo:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 1f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 1f

    mov dword ptr [{VA_UNDO_IDX}], 0
    mov dword ptr [{VA_UNDO_CNT}], 0
    mov dword ptr [{VA_IS_UNDOING}], 0

    mov edx, dword ptr [{VA_STR_TABLE}]
    mov eax, ebx
    mov ebx, SaveToFile
    call ebx

1:
    popad
    ret

TakeSnapshot:
    pushad
    cmp dword ptr [{VA_IS_UNDOING}], 0
    jne 2f

    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 2f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 2f

    call dword ptr [GetTickCount]
    mov ecx, eax
    sub ecx, dword ptr [{VA_LAST_TICK}]
    cmp ecx, 120
    jb 3f

    mov edx, dword ptr [{VA_UNDO_IDX}]
    inc edx
    cmp edx, 29
    jbe 4f
    mov edx, 29
4:
    mov dword ptr [{VA_UNDO_IDX}], edx
    mov dword ptr [{VA_UNDO_CNT}], edx
    jmp 5f

3:
    mov edx, dword ptr [{VA_UNDO_IDX}]

5:
    mov dword ptr [{VA_LAST_TICK}], eax
    mov edx, dword ptr [{VA_STR_TABLE} + edx*4]
    mov eax, ebx
    mov ebx, SaveToFile
    call ebx

2:
    popad
    ret

DoUndo:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 6f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 6f

    mov edx, dword ptr [{VA_UNDO_IDX}]
    test edx, edx
    jle 6f

    mov dword ptr [{VA_IS_UNDOING}], 1
    dec edx
    mov dword ptr [{VA_UNDO_IDX}], edx

    mov ecx, dword ptr [ebx + 0x2a4]
    mov dword ptr [{VA_SAVED_DOC}], ecx

    mov edx, dword ptr [{VA_STR_TABLE} + edx*4]
    mov eax, ebx
    mov ebx, LoadFromFile
    call ebx

    mov ecx, dword ptr [{VA_SAVED_DOC}]
    mov dword ptr [ebx + 0x2a4], ecx

    mov dword ptr [{VA_IS_UNDOING}], 0

6:
    popad
    ret

DoRedo:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 7f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 7f

    mov edx, dword ptr [{VA_UNDO_IDX}]
    cmp edx, dword ptr [{VA_UNDO_CNT}]
    jge 7f

    mov dword ptr [{VA_IS_UNDOING}], 1
    inc edx
    mov dword ptr [{VA_UNDO_IDX}], edx

    mov ecx, dword ptr [ebx + 0x2a4]
    mov dword ptr [{VA_SAVED_DOC}], ecx

    mov edx, dword ptr [{VA_STR_TABLE} + edx*4]
    mov eax, ebx
    mov ebx, LoadFromFile
    call ebx

    mov ecx, dword ptr [{VA_SAVED_DOC}]
    mov dword ptr [ebx + 0x2a4], ecx

    mov dword ptr [{VA_IS_UNDOING}], 0

7:
    popad
    ret

DoTruthTable:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 8f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 8f

    mov edx, dword ptr [{VA_STR_CURR}]
    mov eax, ebx
    mov ebx, SaveToFile
    call ebx

    push 0
    push 0x80
    push 2
    push 0
    push 0
    push 0x40000000
    push dword ptr [{VA_STR_TRIG}]
    call dword ptr [CreateFileA]
    cmp eax, -1
    je 8f
    push eax
    call dword ptr [CloseHandle]

8:
    popad
    ret

Hook_SetModified:
    push ebx
    mov ebx, eax
    mov byte ptr [ebx + 0x2a1], dl

    cmp dl, 1
    jne 9f

    cmp dword ptr [{VA_IS_UNDOING}], 0
    jne 9f

    pushad
    call TakeSnapshot
    popad

9:
    mov eax, SetModCont
    jmp eax

Hook_FormShortCut:
    push eax
    push ecx
    push edx
    push 0x11
    call dword ptr [GetKeyState]
    test ax, ax
    pop edx
    pop ecx
    pop eax
    jns 10f

    push edx
    movzx edx, word ptr [edx + 4]
    cmp edx, 0x5A
    je 11f
    cmp edx, 0x7A
    je 11f
    cmp edx, 0x59
    je 12f
    cmp edx, 0x79
    je 12f
    pop edx
    jmp 10f

11:
    pop edx
    push eax
    push ecx
    call DoUndo
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

12:
    pop edx
    push eax
    push ecx
    call DoRedo
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

10:
    push ebx
    push esi
    push edi
    push ebp
    mov ebp, ecx
    mov eax, FormSCCont
    jmp eax

Hook_FormShowEnd:
    mov eax, OrigCleanup
    call eax
    pushad
    call InitUndo
    popad
    ret
"""

with open('mod_asm.s', 'w') as f:
    f.write(asm_src)

print("[+] mod_asm.s written. Assembling...")
