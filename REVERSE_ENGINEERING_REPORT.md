# Laporan Reverse Engineering & Peta Modding Digital Works
> **Target Binary:** `/home/daun/aplikasi-prak/digitalworks/DigitalWorks.exe`  
> **Platform Target:** Windows x86 (PE32) via Wine di Linux  
> **Hasil Ekstraksi:** 229 Class Delphi, 106 Event Handler `TMainForm`, 19 Form DFM

---

## 1. Spesifikasi Teknis Binary

| Atribut | Keterangan |
|---|---|
| **Format File** | PE32 executable for MS Windows 4.00 (GUI), Intel i386 (32-bit) |
| **Compiler / Framework** | **Borland Delphi 5 (Rilis 1999)**, VCL (*Visual Component Library*) |
| **Proteksi / Packing** | **TIDAK ADA (Unpacked / Raw)**. Tidak ada VMProtect, Themida, maupun UPX. |
| **Section Layout** | `CODE` (0x401000), `DATA` (0x4a2000), `BSS` (0x4a4000), `.idata` (0x4a5000), `.rsrc` (0x4b5000) |
| **UI Resources** | 19 Form DFM biner (`TPF0`) tersimpan rapi di dalam `RT_RCDATA` |

---

## 2. Peta Class Delphi & Simbol Internal (229 Class)

Semua class Delphi internal telah dipetakan lengkap dengan alamat **VMT (Virtual Method Table)** di:
📄 [`re_extracted/symbols_map.txt`](file:///home/daun/aplikasi-prak/digitalworks/re_extracted/symbols_map.txt)  
📄 [`re_extracted/classes_and_methods.json`](file:///home/daun/aplikasi-prak/digitalworks/re_extracted/classes_and_methods.json)

### Class Komponen Logika Utama:
- **Gerbang Logika:** `TGate`, `TGateDevice`, `TAndGate`, `TNandGate`, `TOrGate`, `TNorGate`, `TXorGate`, `TXnorGate`, `TNotGate`, `TTriState`
- **Kabel & Sambungan:** `TWire` (VMT `0x00455814`), `TPin` (VMT `0x004556a4`), `TSolder` (VMT `0x004558c8`)
- **Komponen I/O:** `TInteractiveInput` / `TInteractiveSwitch`, `TClockDevice`, `TLEDDevice`, `TSegment` (7-Segment), `TNumericDevice`
- **Flip-Flop & Memory:** `TRSFlipFlop` (VMT `0x00460a34`), `TDFlipFlop`, `TJKFlipFlop`, `TClockedFlipFlop`, `TMemoryDevice`
- **Serialization & File:** `TSerialize`, `TSerializeList`, `TSerializeReader`, `TSerializeWriter`
- **Form Utama:** `TMainForm` (VMT `0x00498178`), `TPartsForm` (VMT `0x0049548c`), `TAnalyserForm` (VMT `0x004733ec`)

---

## 3. Peta Titik Kunci Event Handler (Untuk Target Hook / Modding)

Seluruh 106 published methods dari `TMainForm` telah diidentifikasi dan dibongkar disassembly-nya:
📄 [`re_extracted/core_handlers_disasm.asm`](file:///home/daun/aplikasi-prak/digitalworks/re_extracted/core_handlers_disasm.asm)

Berikut titik-titik krusial yang bisa kita jadikan target modifikasi:

| Fungsi / Event Handler | Alamat Virtual (VA) | Kegunaan & Potensi Modding |
|---|---|---|
| **`RunCircuit`** | `0x0049dabc` | Jantung evaluasi logika. Tempat rangkaian disimulasikan setiap tick. |
| **`SpeedRunClick`** | `0x0049db78` | Handler tombol "Run" simulasi. |
| **`SpeedStopClick`** | `0x0049dbfc` | Handler tombol "Stop" simulasi. |
| **`SpeedStepClick`** | `0x0049da40` | Handler tombol "Step" pulsa clock manual. |
| **`FormKeyDown`** | `0x0049f394` | Handler input keyboard form utama. **Tempat ideal untuk injeksi shortcut kustom (seperti `Ctrl+Z`)**. |
| **`FormShortCut`** | `0x0049f2a4` | Filter akselerator keyboard Windows. |
| **`DeleteClick`** | `0x0049d5c4` | Dipanggil saat user menghapus komponen/kabel. Pintu masuk untuk menyimpan state ke history stack sebelum objek dimusnahkan. |
| **`DrawingMouseDown`** | `0x0049a590` | Handler klik mouse pada kanvas rangkaian (memilih gerbang, menyambung kabel). |
| **`SpeedWireToolClick`**| `0x0049d490` | Handler pemilihan tool kawat/kabel. |
| **`MenuGridSetupClick`** | `0x0049d2f0` | Handler pengaturan grid & snap. |
| **`MenuSaveAsClick`** | `0x0049a16c` | Handler simpan file `.dwm`. |

---

## 4. Resource Form DFM yang Berhasil Diekstrak

Semua 19 layout dialog dan form VCL telah diekstrak ke folder:
📂 [`re_extracted/forms/`](file:///home/daun/aplikasi-prak/digitalworks/re_extracted/forms)

- **`TMAINFORM.raw`** (198 KB) — Seluruh menu bar, toolbar, palette tombol, dan canvas event bindings.
- **`TPARTSFORM.raw`** (56 KB) — Jendela pemilihan IC Parts Centre.
- **`TANALYSERFORM.raw`** — Logic timing analyzer window.
- **`TEDITSWITCHDIALOG.raw`**, **`TCHANGEMEMORYDIALOG.raw`**, **`TGRIDSETUPDIALOG.raw`**, dll.

---

## 5. Pilihan Metode Modding

Kini setelah struktur internal dan alamat fungsi terbongkar, Anda dapat menentukan teknik modding apa yang ingin kita gunakan:

### 🎯 Pilihan 1: Wine Proxy DLL Sideloading (Teknik Paling Fleksibel & Canggih)
- `DigitalWorks.exe` mengimpor `version.dll`. Kita buat file `version.dll` 32-bit kustom di folder aplikasi ini.
- Begitu Digital Works dibuka dengan Wine, DLL kita otomatis terinjeksi ke dalam memori proses.
- **Kemampuan:**
  - Menambah menu baru di Menu Bar Digital Works (misal: menu *"Sisdig Mods"*).
  - Meng-hook `FormKeyDown` / `WndProc` untuk mengaktifkan **Shortcut Undo (`Ctrl+Z`)** via internal snapshot buffer.
  - Meng-hook fungsi GDI (`FillRect`, `SetBkColor`) untuk menyuntikkan **Dark Mode** langsung pada kanvas Digital Works.
  - Membaca memori state gerbang logika saat simulasi untuk auto-export ke tabel kebenaran.

### 🎯 Pilihan 2: Binary Byte Patching (Modifikasi File Langsung)
- Memodifikasi langsung *opcode* mesin di dalam section `CODE` atau resource string di `TMAINFORM`.
- **Kemampuan:**
  - Mengubah shortcut bawaan.
  - Mengubah batas maksimum frekuensi clock, ukuran default kanvas, atau default setting grid.

### 🎯 Pilihan 3: Python Companion Engine (Aman & Tanpa Ganggu Stabilitas Binary)
- Menjalankan helper script yang berjalan berdampingan dengan Digital Works:
  - Auto-Backup daemon tiap detik (jika salah hapus di Digital Works, ada tombol revert instan).
  - Truth Table Solver otomatis dari file `.dwm` yang sedang aktif.

---

**Semua hasil bedah reverse engineering sudah siap di dalam folder.**  
Silakan tentukan modding apa yang ingin kita buat!
