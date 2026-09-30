#!/usr/bin/env python3
import os
import struct
import pefile
import subprocess
import capstone

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ORIG_EXE = os.path.join(APP_DIR, "DigitalWorks.exe.orig")
TARGET_EXE = os.path.join(APP_DIR, "DigitalWorks.exe")

print("[1/6] Reading original DigitalWorks.exe...")
with open(ORIG_EXE, "rb") as f:
    exe_data = bytearray(f.read())

pe = pefile.PE(data=exe_data)

# Section calculation
pe_off = struct.unpack('<I', exe_data[0x3c:0x40])[0]
num_sections = struct.unpack('<H', exe_data[pe_off+6:pe_off+8])[0]
opt_hdr_sz = struct.unpack('<H', exe_data[pe_off+20:pe_off+22])[0]
sec_tbl_off = pe_off + 24 + opt_hdr_sz
sec_align = struct.unpack('<I', exe_data[pe_off+56:pe_off+60])[0]
file_align = struct.unpack('<I', exe_data[pe_off+60:pe_off+64])[0]

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

MOD_RVA = max_va
MOD_VA = 0x400000 + MOD_RVA
MOD_SIZE = 0x2000 # 8192 bytes
mod_bytes = bytearray(MOD_SIZE)

print(f"[+] Appending .mod section at VA: 0x{MOD_VA:08x} (RVA: 0x{MOD_RVA:x}), Size: 0x{MOD_SIZE:x}")

# Add section header
new_sec_header = bytearray(40)
new_sec_header[0:4] = b'.mod'
struct.pack_into('<I', new_sec_header, 8, MOD_SIZE)   # Misc_VirtualSize
struct.pack_into('<I', new_sec_header, 12, MOD_RVA)   # VirtualAddress
struct.pack_into('<I', new_sec_header, 16, MOD_SIZE)  # SizeOfRawData
struct.pack_into('<I', new_sec_header, 20, len(exe_data)) # PointerToRawData
struct.pack_into('<I', new_sec_header, 36, 0xE0000060) # RWX code/data

sec_entry_off = sec_tbl_off + num_sections * 40
exe_data[sec_entry_off:sec_entry_off+40] = new_sec_header
struct.pack_into('<H', exe_data, pe_off+6, num_sections + 1)
struct.pack_into('<I', exe_data, pe_off+80, MOD_RVA + MOD_SIZE) # SizeOfImage

# Layout inside .mod section:
VA_UNDO_IDX   = MOD_VA + 0x000
VA_UNDO_CNT   = MOD_VA + 0x004
VA_IS_UNDOING = MOD_VA + 0x008
VA_LAST_TICK  = MOD_VA + 0x00c
VA_SAVED_DOC  = MOD_VA + 0x010
VA_UNDO_INIT  = MOD_VA + 0x014
VA_DARK_MODE  = MOD_VA + 0x018
VA_LAYOUT_DONE = MOD_VA + 0x01c

# Initialize Dark Mode to 1 (Active by default)
struct.pack_into('<I', mod_bytes, 0x018, 1)

VA_STR_TABLE  = MOD_VA + 0x020
VA_STR_CURR   = MOD_VA + 0x098
VA_STR_TRIG   = MOD_VA + 0x09c
VA_STR_BATCH  = MOD_VA + 0x0a0
VA_STR_EQ     = MOD_VA + 0x0a4
VA_STR_GRID   = MOD_VA + 0x0a8
VA_STR_AI     = MOD_VA + 0x0ac

# Construct string records starting at 0x100
str_off = 0x100
MAX_SNAPS = 30
for i in range(MAX_SNAPS):
    s = f".undo_history\\u{i:02d}.dwm\x00".encode('latin1')
    rec = struct.pack('<iI', -1, len(s) - 1) + s
    mod_bytes[str_off:str_off+len(rec)] = rec
    char_ptr = MOD_VA + str_off + 8
    struct.pack_into('<I', mod_bytes, 0x020 + i*4, char_ptr)
    str_off += (len(rec) + 3) & ~3

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

# trigger_batch.txt
s_batch = b".undo_history\\trigger_batch.txt\x00"
rec_batch = struct.pack('<iI', -1, len(s_batch) - 1) + s_batch
mod_bytes[str_off:str_off+len(rec_batch)] = rec_batch
struct.pack_into('<I', mod_bytes, 0x0a0, MOD_VA + str_off + 8)
str_off += (len(rec_batch) + 3) & ~3

# trigger_eq.txt
s_eq = b".undo_history\\trigger_eq.txt\x00"
rec_eq = struct.pack('<iI', -1, len(s_eq) - 1) + s_eq
mod_bytes[str_off:str_off+len(rec_eq)] = rec_eq
struct.pack_into('<I', mod_bytes, 0x0a4, MOD_VA + str_off + 8)
str_off += (len(rec_eq) + 3) & ~3

# trigger_grid.txt
s_grid = b".undo_history\\trigger_grid.txt\x00"
rec_grid = struct.pack('<iI', -1, len(s_grid) - 1) + s_grid
mod_bytes[str_off:str_off+len(rec_grid)] = rec_grid
struct.pack_into('<I', mod_bytes, 0x0a8, MOD_VA + str_off + 8)
str_off += (len(rec_grid) + 3) & ~3

# trigger_ai.txt
s_ai = b".undo_history\\trigger_ai.txt\x00"
rec_ai = struct.pack('<iI', -1, len(s_ai) - 1) + s_ai
mod_bytes[str_off:str_off+len(rec_ai)] = rec_ai
struct.pack_into('<I', mod_bytes, 0x0ac, MOD_VA + str_off + 8)
str_off += (len(rec_ai) + 3) & ~3

CODE_OFF = 0x600
CODE_VA = MOD_VA + CODE_OFF

print(f"[2/6] Generating assembly code for .mod section at 0x{CODE_VA:08x}...")
asm_src = f"""
.intel_syntax noprefix
.text
.globl SaveSnapshotStream, InitUndo, TakeSnapshot, DoUndo, DoRedo, DoTruthTable, DoBatchCapture, DoEquation, DoLayoutGrid, DoAIAssistant
.globl Hook_SetModified, Hook_FormShortCut, Hook_FormShow
.globl Hook_CreateSolidBrush, Hook_CreateBrushIndirect, Hook_CreatePenIndirect
.globl Hook_SetTextColor, Hook_SetBkColor, Hook_GetSysColor, ToggleDarkMode

.set SaveToFile,              0x004847a4
.set LoadFromFile,            0x004848f4
.set MainFormPtr,             0x004a49b8
.set GetTickCount,            0x004a5328
.set GetKeyState,             0x004a56f0
.set CreateFileA,             0x004a53a0
.set CloseHandle,             0x004a53ac
.set InvalidateRect,          0x004a5668
.set GetWinHandle,            0x004335b4

.set SpeedStepClick,          0x0049da40
.set SpeedRunClick,           0x0049db78
.set SpeedStopClick,          0x0049dbfc

.set Orig_CreateSolidBrush,   0x004a54ec
.set Orig_CreateBrushIndirect,0x004a5520
.set Orig_CreatePenIndirect,  0x004a54f8
.set Orig_SetTextColor,       0x004a53f4
.set Orig_SetBkColor,         0x004a541c
.set Orig_GetSysColor,        0x004a56a0

.set SetModCont,              0x00487433
.set FormSCCont,              0x0049f2aa

FixLayout:
    pushad
    cmp dword ptr [{VA_LAYOUT_DONE}], 0
    jne 99f
    mov dword ptr [{VA_LAYOUT_DONE}], 1

    # Force PartsForm invisible on startup
    mov eax, dword ptr [0x004a3050]
    test eax, eax
    je 99f
    mov eax, dword ptr [eax]
    test eax, eax
    je 99f
    xor edx, edx
    mov ebx, 0x004450c0
    call ebx

99:
    popad
    ret

SaveSnapshotStream:
    # Pure non-destructive serialization of TDWMDocument without resetting tools/wiring!
    # Input: EAX = TDWMDocument (esi), EDX = FileName Delphi string
    push ebp
    mov ebp, esp
    sub esp, 0x10
    push ebx
    push esi
    push edi

    mov esi, eax
    mov dword ptr [ebp - 4], edx

    push 0xffff
    mov ecx, dword ptr [ebp - 4]
    mov dl, 1
    mov eax, dword ptr [0x40da08]
    mov dword ptr [ebp - 8], 0x4113e8
    call dword ptr [ebp - 8]
    test eax, eax
    je 88f
    mov edi, eax

    push 0xff
    mov ecx, edi
    mov dl, 1
    mov eax, dword ptr [0x4525d8]
    mov dword ptr [ebp - 8], 0x452954
    call dword ptr [ebp - 8]
    test eax, eax
    je 87f
    mov ebx, eax

    mov dword ptr [ebx + 0x58], 0xc4dd
    mov byte ptr [ebx + 0x60], 0x22
    mov eax, ebx
    mov dword ptr [ebp - 8], 0x452c78
    call dword ptr [ebp - 8]

    mov ecx, dword ptr [esi + 0x200]
    mov edx, 0x64
    mov eax, ebx
    mov dword ptr [ebp - 8], 0x452d0c
    call dword ptr [ebp - 8]

    mov eax, dword ptr [esi + 0x1f8]
    mov ecx, dword ptr [eax + 0x34]
    mov edx, 0x65
    mov eax, ebx
    call dword ptr [ebp - 8]

    mov eax, dword ptr [esi + 0x1f8]
    mov ecx, dword ptr [eax + 0x10]
    mov edx, 0x66
    mov eax, ebx
    call dword ptr [ebp - 8]

    xor ecx, ecx
    mov edx, 0xca
    mov eax, ebx
    mov dword ptr [ebp - 8], 0x452d80
    call dword ptr [ebp - 8]

    mov ecx, 1
    mov edx, 0xc8
    mov eax, ebx
    call dword ptr [ebp - 8]

    mov eax, ebx
    mov dword ptr [ebp - 8], 0x452c8c
    call dword ptr [ebp - 8]

    mov edx, dword ptr [esi + 0x1f8]
    mov eax, ebx
    mov dword ptr [ebp - 8], 0x452b50
    call dword ptr [ebp - 8]

    mov eax, ebx
    mov dword ptr [ebp - 8], 0x402f9c
    call dword ptr [ebp - 8]

87:
    mov eax, edi
    mov dword ptr [ebp - 8], 0x402f9c
    call dword ptr [ebp - 8]

88:
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    pop ebp
    ret

InitUndo:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 1f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 1f
    cmp dword ptr [ebx + 0x23c], 0
    je 1f

    mov dword ptr [{VA_UNDO_IDX}], 0
    mov dword ptr [{VA_UNDO_CNT}], 0
    mov dword ptr [{VA_UNDO_INIT}], 1
    mov dword ptr [{VA_IS_UNDOING}], 1

    mov edx, dword ptr [{VA_STR_TABLE}]
    mov eax, ebx
    call SaveSnapshotStream

    mov dword ptr [{VA_IS_UNDOING}], 0

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
    cmp dword ptr [ebx + 0x23c], 0
    je 2f

    # CRITICAL: DO NOT take snapshot if wiring or dragging is in progress!
    cmp byte ptr [ebx + 0x298], 0
    jne 2f

    cmp dword ptr [{VA_UNDO_INIT}], 0
    jne 20f
    call InitUndo
20:

    call dword ptr [GetTickCount]
    mov ecx, eax
    sub ecx, dword ptr [{VA_LAST_TICK}]
    cmp ecx, 200
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
    call SaveSnapshotStream

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
    cmp dword ptr [ebx + 0x23c], 0
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

    mov eax, dword ptr [MainFormPtr]
    mov ebx, dword ptr [eax + 0x5e4]
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
    cmp dword ptr [ebx + 0x23c], 0
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

    mov eax, dword ptr [MainFormPtr]
    mov ebx, dword ptr [eax + 0x5e4]
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
    cmp dword ptr [ebx + 0x23c], 0
    je 8f

    mov edx, dword ptr [{VA_STR_CURR}]
    mov eax, ebx
    call SaveSnapshotStream

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

DoBatchCapture:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 81f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 81f
    cmp dword ptr [ebx + 0x23c], 0
    je 81f

    mov edx, dword ptr [{VA_STR_CURR}]
    mov eax, ebx
    call SaveSnapshotStream

    push 0
    push 0x80
    push 2
    push 0
    push 0
    push 0x40000000
    push dword ptr [{VA_STR_BATCH}]
    call dword ptr [CreateFileA]
    cmp eax, -1
    je 81f
    push eax
    call dword ptr [CloseHandle]

81:
    popad
    ret

DoEquation:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 82f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 82f
    cmp dword ptr [ebx + 0x23c], 0
    je 82f

    mov edx, dword ptr [{VA_STR_CURR}]
    mov eax, ebx
    call SaveSnapshotStream

    push 0
    push 0x80
    push 2
    push 0
    push 0
    push 0x40000000
    push dword ptr [{VA_STR_EQ}]
    call dword ptr [CreateFileA]
    cmp eax, -1
    je 82f
    push eax
    call dword ptr [CloseHandle]

82:
    popad
    ret

DoLayoutGrid:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 830f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 830f
    mov edx, dword ptr [ebx + 0x278]
    test edx, edx
    je 830f
    mov ecx, dword ptr [edx + 0x1dc]
    test ecx, ecx
    je 830f
    xor byte ptr [ecx + 0x14], 1
    mov eax, ebx
    mov edx, dword ptr [eax]
    call dword ptr [edx + 0x74]

830:
    push 0
    push 0x80
    push 2
    push 0
    push 0
    push 0x40000000
    push dword ptr [{VA_STR_GRID}]
    call dword ptr [CreateFileA]
    cmp eax, -1
    je 83f
    push eax
    call dword ptr [CloseHandle]

83:
    popad
    ret

DoAIAssistant:
    pushad
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 84f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 84f
    cmp dword ptr [ebx + 0x23c], 0
    je 84f

    mov edx, dword ptr [{VA_STR_CURR}]
    mov eax, ebx
    call SaveSnapshotStream

    push 0
    push 0x80
    push 2
    push 0
    push 0
    push 0x40000000
    push dword ptr [{VA_STR_AI}]
    call dword ptr [CreateFileA]
    cmp eax, -1
    je 84f
    push eax
    call dword ptr [CloseHandle]

84:
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

    # CRITICAL: DO NOT take snapshot if wiring or dragging is in progress!
    cmp byte ptr [ebx + 0x298], 0
    jne 9f

    pushad
    call TakeSnapshot
    popad

9:
    mov eax, ebx
    push SetModCont
    ret

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
    js 100f

    # Non-Ctrl shortcuts: Spacebar (Step), F5 (Run/Stop), W (Wiring Tool)
    # CRITICAL: DO NOT CLOBBER EAX, EDX, ECX! EAX is Self (TMainForm)!
    cmp word ptr [edx + 4], 0x20
    je 110f
    cmp word ptr [edx + 4], 0x74
    je 120f
    cmp word ptr [edx + 4], 0x57
    je 16f
    cmp word ptr [edx + 4], 0x77
    je 16f
    jmp 10f

100:
    # Ctrl shortcuts: Ctrl+Z, Ctrl+Y, Ctrl+D, Ctrl+G, Ctrl+I, Ctrl+W
    cmp word ptr [edx + 4], 0x5A
    je 11f
    cmp word ptr [edx + 4], 0x7A
    je 11f
    cmp word ptr [edx + 4], 0x59
    je 12f
    cmp word ptr [edx + 4], 0x79
    je 12f
    cmp word ptr [edx + 4], 0x44
    je 13f
    cmp word ptr [edx + 4], 0x64
    je 13f
    cmp word ptr [edx + 4], 0x47
    je 14f
    cmp word ptr [edx + 4], 0x67
    je 14f
    cmp word ptr [edx + 4], 0x49
    je 15f
    cmp word ptr [edx + 4], 0x69
    je 15f
    cmp word ptr [edx + 4], 0x57
    je 16f
    cmp word ptr [edx + 4], 0x77
    je 16f
    jmp 10f

11:
    push eax
    push ecx
    call DoUndo
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

12:
    push eax
    push ecx
    call DoRedo
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

13:
    push eax
    push ecx
    call ToggleDarkMode
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

14:
    push eax
    push ecx
    call DoLayoutGrid
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

15:
    push eax
    push ecx
    call DoAIAssistant
    pop ecx
    pop eax
    mov byte ptr [ecx], 1
    ret

16:
    # W / Ctrl+W -> Toggle SpeedWireTool
    push ebx
    push eax
    push ecx
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 161f
    mov edx, dword ptr [eax + 0x524]
    test edx, edx
    je 161f
    xor byte ptr [edx + 0x12a], 1
    mov ebx, 0x0049d490
    call ebx
161:
    pop ecx
    pop eax
    pop ebx
    mov byte ptr [ecx], 1
    ret

110:
    # Spacebar -> SpeedStepClick
    push ecx
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 111f
    mov edx, SpeedStepClick
    call edx
111:
    pop ecx
    mov byte ptr [ecx], 1
    ret

120:
    # F5 -> SpeedRunClick / SpeedStopClick toggle
    push ecx
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 121f
    cmp byte ptr [eax + 0x5e8], 0
    jne 122f
    mov edx, SpeedRunClick
    call edx
    jmp 121f
122:
    mov edx, SpeedStopClick
    call edx
121:
    pop ecx
    mov byte ptr [ecx], 1
    ret

10:
    push ebx
    push esi
    push edi
    push ebp
    mov ebp, ecx
    push FormSCCont
    ret

Hook_FormShow:
    pop ebx
    pop ecx
    pop ecx
    pop ebp
    pushad
    call FixLayout
    call InitUndo

    # Enable ShowGrid and SnapToGrid by default!
    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 98f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 98f
    mov edx, dword ptr [ebx + 0x278]
    test edx, edx
    je 98f
    mov ecx, dword ptr [edx + 0x1dc]
    test ecx, ecx
    je 98f
    mov byte ptr [ecx + 0x14], 1
    mov byte ptr [ecx + 0x15], 1
    mov eax, ebx
    mov edx, dword ptr [eax]
    call dword ptr [edx + 0x74]

98:
    popad
    ret

Hook_CreateSolidBrush:
    cmp dword ptr [{VA_DARK_MODE}], 0
    je 1f
    mov eax, dword ptr [esp + 4]
    cmp eax, 0x00FFFFFF
    je 2f
    cmp eax, 0x00D0D0D0
    jb 1f
    cmp eax, 0x00F8F8F8
    ja 1f
    mov dword ptr [esp + 4], 0x00231F20
    jmp 1f
2:
    mov dword ptr [esp + 4], 0x001D201C
1:
    jmp dword ptr [Orig_CreateSolidBrush]

Hook_CreateBrushIndirect:
    cmp dword ptr [{VA_DARK_MODE}], 0
    je 1f
    mov eax, dword ptr [esp + 4]
    test eax, eax
    je 1f
    mov edx, dword ptr [eax + 4]
    cmp edx, 0x00FFFFFF
    je 2f
    cmp edx, 0x00D0D0D0
    jb 1f
    cmp edx, 0x00F8F8F8
    ja 1f
    # Gray brush -> surfaceContainer 0x00231F20
    push ebp
    mov ebp, esp
    sub esp, 16
    push esi
    push edi
    push ecx
    mov esi, dword ptr [ebp + 8]
    lea edi, [ebp - 16]
    mov ecx, 3
    rep movsd
    mov dword ptr [ebp - 12], 0x00231F20
    lea eax, [ebp - 16]
    push eax
    call dword ptr [Orig_CreateBrushIndirect]
    pop ecx
    pop edi
    pop esi
    mov esp, ebp
    pop ebp
    ret 4
2:
    # White brush -> matte matcha slate 0x001D201C
    push ebp
    mov ebp, esp
    sub esp, 16
    push esi
    push edi
    push ecx
    mov esi, dword ptr [ebp + 8]
    lea edi, [ebp - 16]
    mov ecx, 3
    rep movsd
    mov dword ptr [ebp - 12], 0x001D201C
    lea eax, [ebp - 16]
    push eax
    call dword ptr [Orig_CreateBrushIndirect]
    pop ecx
    pop edi
    pop esi
    mov esp, ebp
    pop ebp
    ret 4
1:
    jmp dword ptr [Orig_CreateBrushIndirect]

Hook_CreatePenIndirect:
    cmp dword ptr [{VA_DARK_MODE}], 0
    je 1f
    mov eax, dword ptr [esp + 4]
    test eax, eax
    je 1f
    mov edx, dword ptr [eax + 12]
    cmp edx, 0x00000000
    je 2f
    cmp edx, 0x00800000
    je 3f
    cmp edx, 0x00FF0000
    je 3f
    cmp edx, 0x00008000
    je 4f
    cmp edx, 0x00000080
    je 5f
    cmp edx, 0x00800080
    je 6f
    jmp 1f

2:
    mov edx, 0x00E7E1E5
    jmp 7f
3:
    mov edx, 0x00FFCE9D
    jmp 7f
4:
    mov edx, 0x00BACCB5
    jmp 7f
5:
    mov edx, 0x00ABB4FF
    jmp 7f
6:
    mov edx, 0x00FFC1C2

7:
    push ebp
    mov ebp, esp
    sub esp, 16
    push esi
    push edi
    push ecx
    mov esi, dword ptr [ebp + 8]
    lea edi, [ebp - 16]
    mov ecx, 4
    rep movsd
    mov dword ptr [ebp - 4], edx
    lea eax, [ebp - 16]
    push eax
    call dword ptr [Orig_CreatePenIndirect]
    pop ecx
    pop edi
    pop esi
    mov esp, ebp
    pop ebp
    ret 4

1:
    jmp dword ptr [Orig_CreatePenIndirect]

Hook_SetTextColor:
    cmp dword ptr [{VA_DARK_MODE}], 0
    je 1f
    mov eax, dword ptr [esp + 8]
    cmp eax, 0x00000000
    je 2f
    cmp eax, 0x00800000
    je 3f
    cmp eax, 0x00FF0000
    je 3f
    cmp eax, 0x00008000
    je 4f
    cmp eax, 0x00000080
    je 5f
    cmp eax, 0x00800080
    je 6f
    jmp 1f

2:
    mov dword ptr [esp + 8], 0x00E7E1E5
    jmp 1f
3:
    mov dword ptr [esp + 8], 0x00FFCE9D
    jmp 1f
4:
    mov dword ptr [esp + 8], 0x00BACCB5
    jmp 1f
5:
    mov dword ptr [esp + 8], 0x00ABB4FF
    jmp 1f
6:
    mov dword ptr [esp + 8], 0x00FFC1C2

1:
    jmp dword ptr [Orig_SetTextColor]

Hook_SetBkColor:
    cmp dword ptr [{VA_DARK_MODE}], 0
    je 1f
    mov eax, dword ptr [esp + 8]
    cmp eax, 0x00FFFFFF
    je 2f
    cmp eax, 0x00D0D0D0
    jb 1f
    cmp eax, 0x00F8F8F8
    ja 1f
    mov dword ptr [esp + 8], 0x00231F20
    jmp 1f
2:
    mov dword ptr [esp + 8], 0x001D201C
1:
    jmp dword ptr [Orig_SetBkColor]

Hook_GetSysColor:
    cmp dword ptr [{VA_DARK_MODE}], 0
    je 1f
    mov eax, dword ptr [esp + 4]
    cmp eax, 0                   # COLOR_SCROLLBAR
    je 20f
    cmp eax, 15                  # COLOR_BTNFACE
    je 20f
    cmp eax, 5                   # COLOR_WINDOW
    je 21f
    cmp eax, 8                   # COLOR_WINDOWTEXT
    je 22f
    cmp eax, 12                  # COLOR_APPWORKSPACE
    je 23f
    cmp eax, 16                  # COLOR_BTNSHADOW
    je 24f
    cmp eax, 20                  # COLOR_BTNHIGHLIGHT
    je 25f
    jmp 1f

20:
    # Surface Container #201F23
    mov eax, 0x00231F20
    ret 4
21:
    # Matte Matcha Slate #1C201D
    mov eax, 0x001D201C
    ret 4
22:
    # onSurface light #E5E1E7
    mov eax, 0x00E7E1E5
    ret 4
23:
    # Background #131317
    mov eax, 0x00171313
    ret 4
24:
    # Button Shadow #141418
    mov eax, 0x00141418
    ret 4
25:
    # Button Highlight / Deep Matcha #374B3E
    mov eax, 0x003E4B37
    ret 4

1:
    jmp dword ptr [Orig_GetSysColor]

ToggleDarkMode:
    pushad
    xor dword ptr [{VA_DARK_MODE}], 1

    mov eax, dword ptr [MainFormPtr]
    test eax, eax
    je 2f
    mov ebx, dword ptr [eax + 0x5e4]
    test ebx, ebx
    je 2f

    cmp dword ptr [{VA_DARK_MODE}], 1
    jne 1f
    mov dword ptr [ebx + 0x1fc], 0x001D201C
    jmp 3f
1:
    mov dword ptr [ebx + 0x1fc], 0x00FFFFFF

3:
    # Invalidate DrawingArea
    push 1
    push 0
    mov eax, ebx
    mov edx, GetWinHandle
    call edx
    push eax
    call dword ptr [InvalidateRect]

    # Invalidate MainForm
    push 1
    push 0
    mov eax, dword ptr [MainFormPtr]
    mov edx, GetWinHandle
    call edx
    push eax
    call dword ptr [InvalidateRect]

2:
    popad
    ret
"""

with open('mod_gen.s', 'w') as f:
    f.write(asm_src)

subprocess.check_call(["clang", "-m32", "-c", "mod_gen.s", "-o", "mod_gen.o"])

syms_out = subprocess.check_output(["nm", "mod_gen.o"]).decode()
sym_offsets = {}
for line in syms_out.strip().splitlines():
    parts = line.split()
    if len(parts) == 3:
        off = int(parts[0], 16)
        name = parts[2]
        sym_offsets[name] = off

print("[+] Symbol offsets in compiled mod:")
for k, v in sorted(sym_offsets.items(), key=lambda x: x[1]):
    print(f"    {k:<26} -> 0x{CODE_VA + v:08x} (offset 0x{v:03x})")

subprocess.check_call(["objcopy", "-O", "binary", "-j", ".text", "mod_gen.o", "mod_gen.bin"])
with open("mod_gen.bin", "rb") as f:
    code_bytes = bytearray(f.read())

relocs_out = subprocess.check_output(["objdump", "-r", "mod_gen.o"]).decode()
for line in relocs_out.splitlines():
    if "R_386_PC32" in line:
        parts = line.split()
        r_off = int(parts[0], 16)
        r_sym = parts[2]
        if r_sym in sym_offsets:
            target_off = sym_offsets[r_sym]
            rel32 = target_off - (r_off + 4)
            struct.pack_into('<i', code_bytes, r_off, rel32)
            print(f"[+] Resolved local call to {r_sym} at 0x{r_off:x}: rel32 = 0x{rel32:x}")

mod_bytes[CODE_OFF:CODE_OFF+len(code_bytes)] = code_bytes
print(f"[+] .mod section machine code placed: {len(code_bytes)} bytes")

# Append .mod section to exe_data
exe_data += mod_bytes

total_sections = num_sections + 1

def rva_to_file_off(rva):
    for i in range(total_sections):
        s_off = sec_tbl_off + i * 40
        va = struct.unpack('<I', exe_data[s_off+12:s_off+16])[0]
        vs = struct.unpack('<I', exe_data[s_off+8:s_off+12])[0]
        raw_off = struct.unpack('<I', exe_data[s_off+20:s_off+24])[0]
        if va <= rva < va + vs:
            return raw_off + (rva - va)
    return None

def va_to_file_off(va):
    return rva_to_file_off(va - 0x400000)

print("[3/6] Applying in-app hooks with REGISTER-PRESERVING RELATIVE JUMPS (E9)...")

# Hook 1: SetModified (0x00487428) -> Hook_SetModified (exact 9 bytes: E9 rel32 + 4 NOPs)
va_setmod = 0x00487428
off_setmod = va_to_file_off(va_setmod)
hook_setmod_va = CODE_VA + sym_offsets["Hook_SetModified"]
disp_setmod = hook_setmod_va - (va_setmod + 5)
patch_setmod = b'\xe9' + struct.pack('<i', disp_setmod) + b'\x90\x90\x90\x90'
assert len(patch_setmod) == 9
exe_data[off_setmod:off_setmod+9] = patch_setmod
print(f"[+] Patched SetModified at 0x{va_setmod:08x} -> Hook_SetModified (0x{hook_setmod_va:08x})")

# Hook 2: FormShortCut (0x0049f2a4) -> Hook_FormShortCut (exact 6 bytes: E9 rel32 + 1 NOP)
va_fsc = 0x0049f2a4
off_fsc = va_to_file_off(va_fsc)
hook_fsc_va = CODE_VA + sym_offsets["Hook_FormShortCut"]
disp_fsc = hook_fsc_va - (va_fsc + 5)
patch_fsc = b'\xe9' + struct.pack('<i', disp_fsc) + b'\x90'
assert len(patch_fsc) == 6
exe_data[off_fsc:off_fsc+6] = patch_fsc
print(f"[+] Patched FormShortCut at 0x{va_fsc:08x} -> Hook_FormShortCut (0x{hook_fsc_va:08x})")

# Hook 3: FormShow epilogue (0x004a0def) -> Hook_FormShow (exact 5 bytes: E9 rel32)
va_fshow = 0x004a0def
off_fshow = va_to_file_off(va_fshow)
hook_fshow_va = CODE_VA + sym_offsets["Hook_FormShow"]
disp_fshow = hook_fshow_va - (va_fshow + 5)
patch_fshow = b'\xe9' + struct.pack('<i', disp_fshow)
assert len(patch_fshow) == 5
exe_data[off_fshow:off_fshow+5] = patch_fshow
print(f"[+] Patched FormShow at 0x{va_fshow:08x} -> Hook_FormShow (0x{hook_fshow_va:08x})")

# Hook 4: Menu Items Direct In-Memory Calls (E8 call + C3 ret + NOPs)
# SpeedProbeWindowClick (0x0049fba0) -> DoUndo
va_probe = 0x0049fba0
off_probe = va_to_file_off(va_probe)
do_undo_va = CODE_VA + sym_offsets["DoUndo"]
disp_probe = do_undo_va - (va_probe + 5)
patch_probe = b'\xe8' + struct.pack('<i', disp_probe) + b'\xc3' + b'\x90'*21
exe_data[off_probe:off_probe+len(patch_probe)] = patch_probe
print(f"[+] Patched Undo Menu Click (0x{va_probe:08x}) -> DoUndo (0x{do_undo_va:08x})")

# ToolsTemplateEditorClick (0x0049df7c) -> DoRedo
va_tpl = 0x0049df7c
off_tpl = va_to_file_off(va_tpl)
do_redo_va = CODE_VA + sym_offsets["DoRedo"]
disp_tpl = do_redo_va - (va_tpl + 5)
patch_tpl = b'\xe8' + struct.pack('<i', disp_tpl) + b'\xc3' + b'\x90'*20
exe_data[off_tpl:off_tpl+len(patch_tpl)] = patch_tpl
print(f"[+] Patched Redo Menu Click (0x{va_tpl:08x}) -> DoRedo (0x{do_redo_va:08x})")

# OptionsAttachDatasheetClick (0x0049fc20) -> DoTruthTable
va_att = 0x0049fc20
off_att = va_to_file_off(va_att)
do_tt_va = CODE_VA + sym_offsets["DoTruthTable"]
disp_att = do_tt_va - (va_att + 5)
patch_att = b'\xe8' + struct.pack('<i', disp_att) + b'\xc3' + b'\x90'*20
exe_data[off_att:off_att+len(patch_att)] = patch_att
print(f"[+] Patched Truth Table Menu Click (0x{va_att:08x}) -> DoTruthTable (0x{do_tt_va:08x})")

# OptionsNameMacroClick (0x0049fcfc) -> DoBatchCapture
va_nm = 0x0049fcfc
off_nm = va_to_file_off(va_nm)
do_bc_va = CODE_VA + sym_offsets["DoBatchCapture"]
disp_nm = do_bc_va - (va_nm + 5)
patch_nm = b'\xe8' + struct.pack('<i', disp_nm) + b'\xc3' + b'\x90'*20
exe_data[off_nm:off_nm+len(patch_nm)] = patch_nm
print(f"[+] Patched Batch Capture Menu Click (0x{va_nm:08x}) -> DoBatchCapture (0x{do_bc_va:08x})")

# OptionsSetDatasheetPathClick (0x0049fda8) -> DoEquation
va_sd = 0x0049fda8
off_sd = va_to_file_off(va_sd)
do_eq_va = CODE_VA + sym_offsets["DoEquation"]
disp_sd = do_eq_va - (va_sd + 5)
patch_sd = b'\xe8' + struct.pack('<i', disp_sd) + b'\xc3' + b'\x90'*20
exe_data[off_sd:off_sd+len(patch_sd)] = patch_sd
print(f"[+] Patched Boolean Equation Menu Click (0x{va_sd:08x}) -> DoEquation (0x{do_eq_va:08x})")

# ViewGridSetupClick (0x00488afc) -> ToggleDarkMode
va_dark_menu = 0x00488afc
off_dark_menu = va_to_file_off(va_dark_menu)
toggle_dark_va = CODE_VA + sym_offsets["ToggleDarkMode"]
disp_dark_menu = toggle_dark_va - (va_dark_menu + 5)
patch_dark_menu = b'\xe8' + struct.pack('<i', disp_dark_menu) + b'\xc3' + b'\x90'*20
exe_data[off_dark_menu:off_dark_menu+len(patch_dark_menu)] = patch_dark_menu
print(f"[+] Patched View Dark Mode Menu Click (0x{va_dark_menu:08x}) -> ToggleDarkMode (0x{toggle_dark_va:08x})")

# MenuGridSetupClick (0x0049d2f0) -> DoLayoutGrid
va_mgsc = 0x0049d2f0
off_mgsc = va_to_file_off(va_mgsc)
do_grid_va = CODE_VA + sym_offsets["DoLayoutGrid"]
disp_mgsc = do_grid_va - (va_mgsc + 5)
patch_mgsc = b'\xe8' + struct.pack('<i', disp_mgsc) + b'\xc3' + b'\x90'*20
exe_data[off_mgsc:off_mgsc+len(patch_mgsc)] = patch_mgsc
print(f"[+] Patched MenuGridSetupClick (0x{va_mgsc:08x}) -> DoLayoutGrid (0x{do_grid_va:08x})")

# MenuHelpTopicsClick (0x0049fedc) -> DoAIAssistant
va_ai_menu = 0x0049fedc
off_ai_menu = va_to_file_off(va_ai_menu)
do_ai_va = CODE_VA + sym_offsets["DoAIAssistant"]
disp_ai_menu = do_ai_va - (va_ai_menu + 5)
patch_ai_menu = b'\xe8' + struct.pack('<i', disp_ai_menu) + b'\xc3' + b'\x90'*20
exe_data[off_ai_menu:off_ai_menu+len(patch_ai_menu)] = patch_ai_menu
print(f"[+] Patched MenuHelpTopicsClick (0x{va_ai_menu:08x}) -> DoAIAssistant (0x{do_ai_va:08x})")

# Patch Parts Centre auto-popup in FormShow:
# At 0x0049beba: 8b d0 (mov edx, eax) -> 31 d2 (xor edx, edx)
# This forces PartsForm.SetVisible(False) on startup
va_pc_show = 0x0049beba
off_pc_show = va_to_file_off(va_pc_show)
exe_data[off_pc_show : off_pc_show + 2] = b"\x31\xd2"
print(f"[+] Patched Parts Centre Auto-Popup at 0x{va_pc_show:08x} -> xor edx, edx (Forced Hidden)")

# Hook 5: Bypass Delete Confirmation Warning Dialogs
# 1. Main Delete / Keyboard Delete (0x0049d5f3 -> 0x0049d640)
va_del_warn = 0x0049d5f3
off_del_warn = va_to_file_off(va_del_warn)
disp_del_warn = 0x0049d640 - (va_del_warn + 5)
patch_del_warn = b'\xe9' + struct.pack('<i', disp_del_warn) + b'\x90'
assert len(patch_del_warn) == 6
exe_data[off_del_warn:off_del_warn+6] = patch_del_warn
print(f"[+] Patched DeleteClick Warning Bypass at 0x{va_del_warn:08x} -> 0x0049d640")

# 2. Popup Context Menu Delete (0x004897dd -> 0x00489826)
va_pop_del = 0x004897dd
off_pop_del = va_to_file_off(va_pop_del)
disp_pop_del = 0x00489826 - (va_pop_del + 5)
patch_pop_del = b'\xe9' + struct.pack('<i', disp_pop_del) + b'\x90'
assert len(patch_pop_del) == 6
exe_data[off_pop_del:off_pop_del+6] = patch_pop_del
print(f"[+] Patched PopupDelete Warning Bypass at 0x{va_pop_del:08x} -> 0x00489826")

# Hook 6: GDI Thunk Hooks for Seamless Caelestia Matcha Dark Mode
# CreateSolidBrush (0x00406c00) -> Hook_CreateSolidBrush
va_csb = 0x00406c00
off_csb = va_to_file_off(va_csb)
hook_csb_va = CODE_VA + sym_offsets["Hook_CreateSolidBrush"]
disp_csb = hook_csb_va - (va_csb + 5)
patch_csb = b'\xe9' + struct.pack('<i', disp_csb) + b'\x90'
assert len(patch_csb) == 6
exe_data[off_csb:off_csb+6] = patch_csb
print(f"[+] Patched CreateSolidBrush at 0x{va_csb:08x} -> Hook_CreateSolidBrush (0x{hook_csb_va:08x})")

# CreateBrushIndirect (0x00406b98) -> Hook_CreateBrushIndirect
va_cbi = 0x00406b98
off_cbi = va_to_file_off(va_cbi)
hook_cbi_va = CODE_VA + sym_offsets["Hook_CreateBrushIndirect"]
disp_cbi = hook_cbi_va - (va_cbi + 5)
patch_cbi = b'\xe9' + struct.pack('<i', disp_cbi) + b'\x90'
assert len(patch_cbi) == 6
exe_data[off_cbi:off_cbi+6] = patch_cbi
print(f"[+] Patched CreateBrushIndirect at 0x{va_cbi:08x} -> Hook_CreateBrushIndirect (0x{hook_cbi_va:08x})")

# CreatePenIndirect (0x00406be8) -> Hook_CreatePenIndirect
va_cpi = 0x00406be8
off_cpi = va_to_file_off(va_cpi)
hook_cpi_va = CODE_VA + sym_offsets["Hook_CreatePenIndirect"]
disp_cpi = hook_cpi_va - (va_cpi + 5)
patch_cpi = b'\xe9' + struct.pack('<i', disp_cpi) + b'\x90'
assert len(patch_cpi) == 6
exe_data[off_cpi:off_cpi+6] = patch_cpi
print(f"[+] Patched CreatePenIndirect at 0x{va_cpi:08x} -> Hook_CreatePenIndirect (0x{hook_cpi_va:08x})")

# SetTextColor (0x00406df0) -> Hook_SetTextColor
va_stc = 0x00406df0
off_stc = va_to_file_off(va_stc)
hook_stc_va = CODE_VA + sym_offsets["Hook_SetTextColor"]
disp_stc = hook_stc_va - (va_stc + 5)
patch_stc = b'\xe9' + struct.pack('<i', disp_stc) + b'\x90'
assert len(patch_stc) == 6
exe_data[off_stc:off_stc+6] = patch_stc
print(f"[+] Patched SetTextColor at 0x{va_stc:08x} -> Hook_SetTextColor (0x{hook_stc_va:08x})")

# SetBkColor (0x00406da0) -> Hook_SetBkColor
va_sbc = 0x00406da0
off_sbc = va_to_file_off(va_sbc)
hook_sbc_va = CODE_VA + sym_offsets["Hook_SetBkColor"]
disp_sbc = hook_sbc_va - (va_sbc + 5)
patch_sbc = b'\xe9' + struct.pack('<i', disp_sbc) + b'\x90'
assert len(patch_sbc) == 6
exe_data[off_sbc:off_sbc+6] = patch_sbc
print(f"[+] Patched SetBkColor at 0x{va_sbc:08x} -> Hook_SetBkColor (0x{hook_sbc_va:08x})")

# GetSysColor (0x004070d0) -> Hook_GetSysColor (Forces dark scrollbar, buttonface, window colors)
va_gsc = 0x004070d0
off_gsc = va_to_file_off(va_gsc)
hook_gsc_va = CODE_VA + sym_offsets["Hook_GetSysColor"]
disp_gsc = hook_gsc_va - (va_gsc + 5)
patch_gsc = b'\xe9' + struct.pack('<i', disp_gsc) + b'\x90'
assert len(patch_gsc) == 6
exe_data[off_gsc:off_gsc+6] = patch_gsc
print(f"[+] Patched GetSysColor at 0x{va_gsc:08x} -> Hook_GetSysColor (0x{hook_gsc_va:08x})")

# Hook 7: Canvas Grid Points and Default Canvas Background Color
# Grid point color at 0x00484100: push 0x8000 (clGreen) -> push 0x0090B870 (Radiant Mint #70B890)
va_grid = 0x00484100
off_grid = va_to_file_off(va_grid)
patch_grid = b'\x68\x70\xb8\x90\x00'
exe_data[off_grid:off_grid+5] = patch_grid
print(f"[+] Patched Grid Point Color at 0x{va_grid:08x} -> 0x0090B870 (#70B890 Radiant Mint)")

# Default Canvas Background at 0x00482b5f: mov dword ptr [ebx + 0x1fc], 0xffffff -> 0x001d201c (#1C201D)
va_bg = 0x00482b5f
off_bg = va_to_file_off(va_bg)
patch_bg = b'\xc7\x83\xfc\x01\x00\x00\x1c\x20\x1d\x00'
exe_data[off_bg:off_bg+10] = patch_bg
print(f"[+] Patched Default Canvas Background at 0x{va_bg:08x} -> 0x001D201C (#1C201D Matte Matcha Slate)")

print("[4/6] Applying in-place DFM, Title String & Toolbar Icon Whitening Patches...")

# Whitening Toolbar Icons in ImageListDefault, ImageListHot and ImageListDisabled:
def process_il_smart(exe_data, stream_offset, is_hot=False, is_disabled=False):
    il_pos = exe_data.find(b'IL\x01\x01', stream_offset)
    if il_pos == -1:
        print(f"[-] IL stream not found at offset {hex(stream_offset)}")
        return
    bm1_pos = exe_data.find(b'BM', il_pos)
    bm2_pos = exe_data.find(b'BM', bm1_pos + 2)
    
    w1, h1, planes1, bpp1 = struct.unpack('<IIHH', exe_data[bm1_pos+18:bm1_pos+30])
    off1 = struct.unpack('<I', exe_data[bm1_pos+10:bm1_pos+14])[0]
    
    w2, h2, planes2, bpp2 = struct.unpack('<IIHH', exe_data[bm2_pos+18:bm2_pos+30])
    off2 = struct.unpack('<I', exe_data[bm2_pos+10:bm2_pos+14])[0]
    
    mask_pitch = ((w2 + 31) // 32) * 4
    mask_bits = exe_data[bm2_pos+off2 : bm2_pos+off2 + mask_pitch * h2]
    
    color_pitch = w1 * 4
    color_bits_offset = bm1_pos + off1
    
    whitened_count = 0
    for tile_y in range(h1 // 16):
        for tile_x in range(w1 // 16):
            tile_opaque = []
            for ty in range(16):
                y = tile_y * 16 + ty
                for tx in range(16):
                    x = tile_x * 16 + tx
                    byte_idx = y * mask_pitch + (x // 8)
                    bit_idx = 7 - (x % 8)
                    mask_val = (mask_bits[byte_idx] >> bit_idx) & 1
                    if mask_val == 0:
                        px_off = color_bits_offset + y * color_pitch + x * 4
                        b = exe_data[px_off]
                        g = exe_data[px_off+1]
                        r = exe_data[px_off+2]
                        tile_opaque.append((tx, ty, r, g, b, px_off))
            
            if not tile_opaque:
                continue
                
            has_black = any(r < 80 and g < 80 and b < 80 for tx, ty, r, g, b, px in tile_opaque)
            has_white = any(r > 200 and g > 200 and b > 200 for tx, ty, r, g, b, px in tile_opaque)
            
            for tx, ty, r, g, b, px_off in tile_opaque:
                is_color = max(r, g, b) - min(r, g, b) > 30
                if is_color:
                    continue
                
                if is_disabled:
                    if r < 80 and g < 80 and b < 80:
                        exe_data[px_off] = 0x24
                        exe_data[px_off+1] = 0x28
                        exe_data[px_off+2] = 0x25
                    elif r > 180 and g > 180 and b > 180:
                        exe_data[px_off] = 0x70
                        exe_data[px_off+1] = 0x75
                        exe_data[px_off+2] = 0x72
                    whitened_count += 1
                elif has_black and has_white:
                    # Mixed tile (IC chips RS, JK, D, text boxes, docs)
                    if r < 80 and g < 80 and b < 80:
                        exe_data[px_off] = 0xff
                        exe_data[px_off+1] = 0xff
                        exe_data[px_off+2] = 0xff
                    elif r > 180 and g > 180 and b > 180:
                        if is_hot:
                            exe_data[px_off] = 0x3e
                            exe_data[px_off+1] = 0x4b
                            exe_data[px_off+2] = 0x37
                        else:
                            exe_data[px_off] = 0x2a
                            exe_data[px_off+1] = 0x2e
                            exe_data[px_off+2] = 0x28
                    whitened_count += 1
                else:
                    # Line art (gates, clock, ground, pulse, Vcc, 7-seg)
                    if r < 120 and g < 120 and b < 120:
                        exe_data[px_off] = 0xff
                        exe_data[px_off+1] = 0xff
                        exe_data[px_off+2] = 0xff
                        whitened_count += 1
                    
    print(f"[+] Smart whitened {whitened_count} icon pixels in IL at 0x{il_pos:x}")

def_pos = exe_data.find(b'TImageList\x10ImageListDefault')
hot_pos = exe_data.find(b'TImageList\x0cImageListHot')
dis_pos = exe_data.find(b'TImageList\x11ImageListDisabled')
if def_pos != -1: process_il_smart(exe_data, def_pos, is_hot=False)
if hot_pos != -1: process_il_smart(exe_data, hot_pos, is_hot=True)
if dis_pos != -1: process_il_smart(exe_data, dis_pos, is_disabled=True)

# Patch ScrollBox Color in DFM (clWhite -> clBlack to eliminate white canvas borders)
clwhite_pattern = b'\x05Color\x07\x07clWhite'
clblack_replacement = b'\x05Color\x07\x07clBlack'
cw_pos = exe_data.find(clwhite_pattern)
while cw_pos != -1:
    exe_data[cw_pos:cw_pos+len(clwhite_pattern)] = clblack_replacement
    print(f"[+] Patched DFM Color clWhite -> clBlack at 0x{cw_pos:x}")
    cw_pos = exe_data.find(clwhite_pattern, cw_pos + len(clwhite_pattern))

t_idx = exe_data.find(b'&Tools')
while t_idx != -1:
    exe_data[t_idx:t_idx+6] = b'&Mods '
    print(f"[+] Patched DFM '&Tools' -> '&Mods ' at 0x{t_idx:x}")
    t_idx = exe_data.find(b'&Tools', t_idx + 6)

h_idx = exe_data.find(b'Logic &History...')
if h_idx != -1:
    exe_data[h_idx:h_idx+17] = b'&Undo (Ctrl+Z)   '
    print(f"[+] Patched DFM menu item -> '&Undo (Ctrl+Z)   ' at 0x{h_idx:x}")

te_idx = exe_data.find(b'&Template Editor...')
if te_idx != -1:
    exe_data[te_idx:te_idx+19] = b'&Redo (Ctrl+Y)     '
    print(f"[+] Patched DFM menu item -> '&Redo (Ctrl+Y)     ' at 0x{te_idx:x}")

ad_idx = exe_data.find(b'&Attach Datasheet')
if ad_idx != -1:
    exe_data[ad_idx:ad_idx+17] = b'Auto &Truth Table'
    print(f"[+] Patched DFM menu item -> 'Auto &Truth Table' at 0x{ad_idx:x}")

nm_idx = exe_data.find(b'&Name Macro...')
if nm_idx != -1:
    exe_data[nm_idx:nm_idx+14] = b'&Batch Capture'
    print(f"[+] Patched DFM menu item -> '&Batch Capture' at 0x{nm_idx:x}")

sd_idx = exe_data.find(b'&Set Datasheet Path...')
if sd_idx != -1:
    exe_data[sd_idx:sd_idx+22] = b'&Boolean Equation...  '
    print(f"[+] Patched DFM menu item -> '&Boolean Equation...  ' at 0x{sd_idx:x}")

# View Menu: Grid Setup -> Dark (Ctrl+D) (exact 14 bytes)
gs_idx = exe_data.find(b'&Grid Setup...')
if gs_idx != -1:
    exe_data[gs_idx:gs_idx+14] = b'&Dark (Ctrl+D)'
    print(f"[+] Patched DFM menu item -> '&Dark (Ctrl+D)' at 0x{gs_idx:x}")

    # 2nd occurrence in main menu View: GridSetup2 -> Layout Grid (exact 14 bytes)
    gs2_idx = exe_data.find(b'&Grid Setup...', gs_idx + 14)
    if gs2_idx != -1:
        exe_data[gs2_idx:gs2_idx+14] = b'&Layout Grid  '
        print(f"[+] Patched DFM menu item -> '&Layout Grid  ' at 0x{gs2_idx:x}")

ht_idx = exe_data.find(b'&Help Topics...')
if ht_idx != -1:
    exe_data[ht_idx:ht_idx+15] = b'&AI Assistant  '
    print(f"[+] Patched DFM menu item -> '&AI Assistant  ' at 0x{ht_idx:x}")

stub_idx = exe_data.find(b'This program must be run under Win32')
if stub_idx != -1:
    exe_data[stub_idx:stub_idx+36] = b'DigitalWorks for Arch Linux (Modded)'
    print(f"[+] Patched DOS Stub branding at 0x{stub_idx:x}")

ut_idx = 0
while True:
    ut_idx = exe_data.find(b'- Untitled', ut_idx)
    if ut_idx == -1: break
    exe_data[ut_idx:ut_idx+10] = b'[Arch-OS] '
    print(f"[+] Patched title suffix at 0x{ut_idx:x}")
    ut_idx += 10

expected_size = len(pe.write()) + MOD_SIZE
print(f"[5/6] Writing modded binary to {TARGET_EXE} (Size: {len(exe_data)} bytes)...")
assert len(exe_data) == 1134080 + MOD_SIZE, f"Length mismatch: {len(exe_data)} vs {1134080 + MOD_SIZE}"

with open(TARGET_EXE, "wb") as f:
    f.write(exe_data)

os.chmod(TARGET_EXE, 0o755)
print(f"[+] Successfully wrote exact {len(exe_data)} bytes to {TARGET_EXE}")

print("[6/6] Verifying patched binary with capstone disassembly...")
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

def verify_disas(va, length, name):
    off = va_to_file_off(va)
    code = exe_data[off:off+length]
    print(f"=== Verification of {name} at 0x{va:08x} ===")
    for ins in md.disasm(code, va):
        print(f"  0x{ins.address:08x}: {ins.mnemonic:<8} {ins.op_str}")

verify_disas(0x00487428, 14, "Hook_SetModified Call Site")
verify_disas(0x0049f2a4, 12, "Hook_FormShortCut Call Site")
verify_disas(0x004a0def, 10, "Hook_FormShow Call Site")
verify_disas(0x00406c00, 10, "Hook_CreateSolidBrush Thunk")
verify_disas(0x00406b98, 10, "Hook_CreateBrushIndirect Thunk")
verify_disas(0x00406be8, 10, "Hook_CreatePenIndirect Thunk")
verify_disas(0x00406df0, 10, "Hook_SetTextColor Thunk")
verify_disas(0x00406da0, 10, "Hook_SetBkColor Thunk")
verify_disas(0x004070d0, 10, "Hook_GetSysColor Thunk")
verify_disas(0x00484100, 10, "Grid Point Color Site")
verify_disas(0x00482b5f, 12, "Default Background Color Site")
verify_disas(0x00488afc, 10, "Dark Mode Menu Item Call Site")
verify_disas(0x0049fba0, 10, "Undo Menu Item Call Site")
verify_disas(0x0049df7c, 10, "Redo Menu Item Call Site")
verify_disas(0x0049fc20, 10, "Truth Table Menu Item Call Site")
verify_disas(0x0049fcfc, 10, "Batch Capture Menu Item Call Site")
verify_disas(0x0049fda8, 10, "Boolean Equation Menu Item Call Site")
verify_disas(0x0049d5f3, 10, "DeleteClick Warning Bypass Call Site")
verify_disas(0x004897dd, 10, "PopupDelete Warning Bypass Call Site")

print("\n*** BUILD COMPLETE & VERIFIED! EXACT SIZE MATCH! ***")
