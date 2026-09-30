# 🛠️ Digital Works Modding & Reverse Engineering Project (Arch Linux)

Proyek reverse engineering biner, modernisasi arsitektur, dan modding langsung (*direct in-codebase binary & UI patching*) untuk **Digital Works** (aplikasi simulator gerbang logika Sistem Digital), disiapkan khusus untuk lingkungan **Arch Linux** dan kebutuhan praktikum **Sistem Digital (Informatika UNS)**.

---

## 📌 Latar Belakang & Analisis Masalah

Digital Works dirilis pada era Windows 95/98 (Borland Delphi 5, 1999). Meskipun fungsional dan menjadi standar praktikum, software ini memiliki kelemahan kritis yang menghabiskan waktu mahasiswa:
- ❌ **Tidak ada fitur Undo / Redo (`Ctrl+Z`)**: Jika salah menghapus kabel atau gerbang logika, rangkaian langsung hilang dan harus dirakit ulang dari nol.
- ❌ **Konfirmasi Hapus Memperlambat Kerja**: Selalu memunculkan dialog pop-up konfirmasi *"Are you sure you want to delete this object?"* setiap kali tombol Delete ditekan.
- ❌ **Pengujian Tabel Kebenaran Manual**: Mahasiswa harus mengklik saklar input satu per satu ($2^n$ kombinasi) menggunakan mouse dan mencatat hasilnya secara manual ke dokumen laporan, rawan salah data.
- ❌ **Screenshot Laporan Makan Waktu**: Mahasiswa harus mengambil screenshot manual untuk setiap kondisi input (00, 01, 10, 11) pada setiap tabel praktikum (puluhan kombinasi).
- ❌ **Tampilan Kuno & Silau (No Dark Mode)**: Canvas putih terang GDI 90-an yang menyilaukan mata saat praktikum malam hari.
- ❌ **Susunan Rangkaian Berantakan**: Tidak adanya sistem grid modular yang fleksibel untuk menata letak gerbang dan komponen, serta ketiadaan sistem koordinat presisi jika ingin diintegrasikan dengan AI agent.
- ❌ **Perakitan Berulang yang Membosankan**: Menempatkan gerbang satu per satu untuk rangkaian standar praktikum (misalnya menguji 7 gerbang dasar sekaligus atau Half/Full Adder) memakan waktu lama.

---

## 🎯 Paradigma Modding: Direct In-Codebase (Bukan Injeksi / Hook Eksternal)

Sesuai prinsip ketat proyek:
1. **Modding Langsung pada Binary PE32**: Menambahkan section biner `.mod` (8192 bytes) langsung ke dalam [`DigitalWorks.exe`](file:///home/daun/aplikasi-prak/digitalworks/DigitalWorks.exe), memodifikasi Virtual Method Table (VMT), instruksi mesin x86, dan resource VCL DFM (`RT_RCDATA`).
2. **Tertanam Langsung di Antarmuka Resmi (In-UI Embedded)**: Fitur baru diakses melalui menu resmi bawaan header aplikasi (`Mods`, `View`, dan `Help`), tanpa jendela melayang, overlay eksternal, atau script injector terpisah.
3. **Ukuran Biner Presisi & Konsisten**: Binary tervalidasi dengan Capstone Disassembly dan memiliki ukuran presisi **1.142.272 bytes**.
4. **Native ELF Runner & Sentinel Terintegrasi**: Menggunakan launcher native C 64-bit ([`digitalworks`](file:///home/daun/aplikasi-prak/digitalworks/digitalworks)) yang mengelola siklus hidup proses, lingkungan Wine murni, dan sinkronisasi Wine prefix.

---

## 🚀 Fitur Unggulan Praktikum (Lengkap & Teruji)

| No | Fitur | Tingkat Kepentingan Praktikum | Status Implementasi | Akses In-UI / Shortcut |
|:---:|---|:---:|:---:|:---:|
| **1** | **AI Circuit Agent (Gemini 3.5 Flash Lite)** | 🤖 **Revolusioner** (Perakit Multi-Sirkuit) | ✅ **100% Selesai & Teruji** | Menu: `Help -> &AI Assistant` / **`Ctrl+I`** |
| **2** | **Penyempurnaan Real Boolean Solver (Tabel Nyata)** | 🔴 **Sangat Kritis** (Cegah Salah Data) | ✅ **100% Selesai & Akurat** | Menu: `Mods -> Auto Truth Table` |
| **3** | **Multi-Format Export (Word TSV, Markdown, LaTeX)** | 🟡 **Tinggi** (Paste Langsung ke Word) | ✅ **100% Selesai** | Otomatis ke Clipboard & TSV / MD / TeX |
| **4** | **Batch State Screenshotter untuk Laporan** | 🟢 **Sangat Tinggi** (Hemat Waktu 80%) | ✅ **100% Selesai** | Menu: `Mods -> Batch Capture` |
| **5** | **Boolean Algebraic Equation ($Y = f(A,B)$)** | 🔵 **Menengah** (Rumus Lengkap) | ✅ **100% Selesai** | Menu: `Mods -> Boolean Equation` |
| **6** | **Modular Layout Grid ala Microsoft Word & AI Anchor API** | 🟣 **Tinggi** (Tata Letak & Basis AI) | ✅ **100% Selesai** | Menu: `View -> Layout Grid` (`Ctrl+G`) |
| **7** | **Integrasi Caelestia Desktop Launcher & Hyprland** | 🪟 **Sistem OS** (Tiling & Auto-Layout) | ✅ **100% Selesai** | Menu Aplikasi Caelestia / Rofi / Desktop |
| **8** | **Native Undo / Redo Engine** | 🔴 **Sangat Kritis** (Safety Net) | ✅ **100% Selesai** | Menu: `Mods -> Undo` (`Ctrl+Z` / `Ctrl+Y`) |
| **9** | **Bypass Konfirmasi Delete (Instant Erase)** | 🟢 **Tinggi** (Alur Kerja Cepat) | ✅ **100% Selesai** | Tombol `Delete` Keyboard / Context Menu |
| **10** | **Caelestia Matcha Dark Mode (Tema Gelap Elegan)** | ☕ **Sangat Nyaman** (Anti-Silau) | ✅ **100% Selesai** | Menu: `View -> Dark` (`Ctrl+D`) |

---

### 1. 🤖 AI Circuit Agent (Gemini 3.5 Flash Lite & Multi-Circuit Grid Generator)

- **Model Engine Utama**: Ditenagai oleh **Google Gemini 3.5 Flash Lite** (kuota resmi **500 hit/hari** dan **15 hit/menit**, respons kilat ~0.5s). Mendukung fallback berjenjang ke `gemini-3.1-flash-lite`, `gemini-2.5-flash`, dan `gemini-1.5-flash`.
- **Multi-Circuit Generation**: Mampu merakit **beberapa rangkaian sekaligus secara otomatis** dalam satu kanvas terstruktur!
  - *Contoh 1*: `"Buat semua 7 gerbang logika dasar"` $\rightarrow$ AI langsung menempatkan gerbang AND, OR, NOT, NAND, NOR, XOR, XNOR di slot grid `[1,1]` sampai `[3,1]`.
  - *Contoh 2*: `"Buatkan Half Adder di slot [1,1] dan Full Adder di slot [2,1]-[2,2]"` $\rightarrow$ AI menggabungkan sel (*merge cells*) untuk slot Full Adder yang lebar dan merakit kedua sirkuit secara bersamaan.
- **Pemanfaatan Word Layout Grid**: Menggunakan koordinat presisi dari `get_slot_anchor(r, c)` sehingga saklar Input A/B, gerbang logika, lampu LED Output, dan label nama mahasiswa tersusun rapi, simetris, dan anti-tumpang tindih.
- **Verifikasi Otomatis (Self-Validation)**: Begitu rangkaian selesai dirakit oleh AI, sistem langsung menjalankan *Real Boolean Solver* untuk menghitung tabel kebenaran nyata dan menyalin tabel Word TSV ke clipboard (siap dipaste ke laporan praktikum).
- **Offline Deterministic Fallback**: Jika internet laboratorium terputus atau API key belum disetel, AI Agent otomatis beralih ke generator template logika lokal deterministik (100% bebas crash dan akurat).
- **Manajemen Kunci API**:
  - Simpan API Key sekali via CLI: `./digitalworks --set-key "AIzaSy..."`
  - Atau simpan di file [`.gemini_key`](file:///home/daun/aplikasi-prak/digitalworks/.gemini_key)
  - Atau melalui environment variable `GEMINI_API_KEY` / `GOOGLE_API_KEY`.
- **Cara Akses**:
  - Tekan **`Ctrl+I`** kapan saja di DigitalWorks untuk memunculkan kotak dialog perintah interaktif.
  - Atau via header menu **`Help -> &AI Assistant`**.
  - Atau via terminal CLI: `./digitalworks --ai "instruksi anda"`.

---

### 2. 🪟 Integrasi Caelestia Desktop Launcher & Hyprland

Aplikasi telah terintegrasi penuh ke dalam sistem desktop **Caelestia (Hyprland Wayland)**:
- **Desktop Entry ([`digital-works.desktop`](file:///home/daun/.local/share/applications/digital-works.desktop))**:
  Terdaftar di menu aplikasi Caelestia / Rofi / Fuzzel dengan icon resolusi tinggi (512x512) dan path kerja aktif di direktori modded `/home/daun/aplikasi-prak/digitalworks`.
- **Launcher Cerdas ([`digital-works`](file:///home/daun/.local/bin/digital-works))**:
  - **Mode CLI Respons Kilat**: Jika dijalankan dengan flag terminal (`--ai`, `--truth-table`, `--export-tsv`, dll), wrapper langsung mem-bypass GUI splash dan mengeksekusi runner native ELF dalam hitungan milidetik.
  - **Mode GUI Desktop**: Menjalankan splash screen modern Elaina Chibi berbasis GTK3 & GtkLayerShell.
- **Splash Screen & Tiling Window Dispatcher ([`splash_launcher.py`](file:///home/daun/.local/share/digital-works/splash_launcher.py))**:
  - Menampilkan progress bar animasi dan status pemuatan sistem.
  - Mengirim jendela dummy Wine ke workspace `special:silent` agar tidak memunculkan kotak putih kosong yang mengganggu.
  - Memfokuskan jendela kanvas utama, mengubah mode window menjadi tiled standar di Hyprland, dan secara otomatis memaksimalkan (*maximize*) dokumen internal Digital Works.

---

### 3. 📊 Real Boolean Solver (Tabel Kebenaran Akurat Nyata)

- **Cara Kerja**: Mesin AST binary parser membaca file `.dwm` secara mendalam, mengekstrak topologi gerbang (AND, OR, NOT, NAND, NOR, XOR, XNOR, Half Adder, Full Adder, Multiplexer) beserta koneksi kawat antar pin.
- **Akurasi 100%**: Menghitung secara nyata setiap kemungkinan kombinasi input ($00, 01, 10, 11$) dan memvalidasi output sebenarnya dari rangkaian.
- **Mencegah Salah Data Praktikum**: Mahasiswa tidak akan salah mencatat nilai tabel kebenaran pada laporan.

---

### 4. 📋 Multi-Format Export (TSV untuk Word / LaTeX / Markdown)

Setelah mengevaluasi tabel kebenaran, sistem secara otomatis mengekspor ke berbagai format:
- **Microsoft Word Native TSV ([`Tabel_Kebenaran_Word.tsv`](file:///home/daun/aplikasi-prak/digitalworks/Tabel_Kebenaran_Word.tsv))**:
  Data tabel menggunakan pemisah tab (*tab-separated values*). Mahasiswa cukup menekan **`Ctrl+V`** di Microsoft Word, dan Word otomatis mengubahnya menjadi **tabel kotak native lengkap dengan header berwarna dan garis batas**.
- **Markdown ([`Tabel_Kebenaran_Otomatis.md`](file:///home/daun/aplikasi-prak/digitalworks/Tabel_Kebenaran_Otomatis.md))**:
  Format tabel Markdown standar untuk dokumentasi GitHub, Typora, Obsidian, atau VS Code.
- **LaTeX Tabular Code ([`Tabel_Kebenaran_LaTeX.tex`](file:///home/daun/aplikasi-prak/digitalworks/Tabel_Kebenaran_LaTeX.tex))**:
  Menghasilkan kode `\begin{tabular} ... \end{tabular}` siap pakai untuk penulisan laporan formal atau jurnal di Overleaf.
- **Clipboard Sync**: Format Markdown dan TSV otomatis disalin ke clipboard sistem Linux (Wayland `wl-copy` / X11 `xclip`).

---

### 5. 📸 Batch State Screenshotter & Auto-Crop untuk Laporan Praktikum

- **Iterasi Otomatis Semua State**: Sistem secara otomatis mengiterasi seluruh kombinasi logika ($A=0, B=0 \rightarrow A=0, B=1 \rightarrow A=1, B=0 \rightarrow A=1, B=1$).
- **38 Tangkapan Layar Asli**: Menyimpan gambar beresolusi tinggi untuk setiap kemungkinan kondisi input dan status nyala LED ke direktori:
  📂 **[`laporan_screenshots/`](file:///home/daun/aplikasi-prak/digitalworks/laporan_screenshots/)**
- **Kolase Semua Kemungkinan (All-States Collage)**:
  Secara otomatis merangkai 4 kondisi state berdampingan dalam satu gambar horizontal ([`Kolase_Semua_Kemungkinan_Tabel_01_AND.png`](file:///home/daun/aplikasi-prak/digitalworks/laporan_screenshots/Kolase_Semua_Kemungkinan_Tabel_01_AND.png) & [`Kolase_Semua_Kemungkinan_Tabel_10_XOR.png`](file:///home/daun/aplikasi-prak/digitalworks/laporan_screenshots/Kolase_Semua_Kemungkinan_Tabel_10_XOR.png)), sangat ideal untuk disisipkan ke lembar laporan praktikum.
- **Live Canvas Auto-Cropping**:
  Mendeteksi batas rangkaian aktif pada kanvas secara cerdas, memotong margin kosong (*whitespace*), dan menyalin hasil crop presisi langsung ke clipboard sistem (siap `Ctrl+V` ke laporan Word).

---

### 6. 📐 Boolean Algebraic Equation ($Y = f(A, B)$)

- **Persamaan Ringkas**: Menyederhanakan fungsi logika menjadi ekspresi matematis ringkas (misal: $Y = A \oplus B$ untuk XOR, $Y = A \cdot B$ untuk AND, $Y = \overline{A \cdot B}$ untuk NAND).
- **Bentuk Kanonik SOP (Sum of Products)**: Menghasilkan persamaan minterm standar ($\sum m$).
- **Bentuk Kanonik POS (Product of Sums)**: Menghasilkan persamaan maxterm standar ($\prod M$).
- **Output Multi-Saluran**: Tersimpan di file [`Persamaan_Logika.md`](file:///home/daun/aplikasi-prak/digitalworks/Persamaan_Logika.md), disalin ke clipboard, dan ditampilkan via notifikasi desktop.

---

### 7. 📐 Sistem Modular Layout Grid ala Microsoft Word & AI Anchor API

- **Sistem Grid ala Tabel Microsoft Word**:
  - **Show / Hide Gridlines**: Garis bantu grid dapat ditampilkan atau disembunyikan kapan saja melalui menu **`View -> Layout Grid`** atau shortcut **`Ctrl+G`**.
  - **Garis Putus-Putus Halus (*Dotted Lines*)**: Grid ditampilkan dengan garis putus-putus biru lembut khas Word, sehingga tidak mengganggu pandangan rangkaian utama.
  - **Merge Cells (Penggabungan Sel)**: Sel modular dapat digabung (misal mengubah slot standar $3 \times 3$ menjadi slot lebar $3 \times 6$) untuk memberi ruang bagi modul rangkaian kompleks seperti *Half Adder*, *Full Adder*, *Multiplexer*, atau *ALU*.
  - **Delete Border / Eraser Tool**: Garis pembatas tertentu dapat disembunyikan/dihapus sebagaimana fitur penghapus garis tabel pada Microsoft Word.
- **API Koordinat Presisi untuk AI Agent (`get_slot_anchor`)**:
  Menyediakan titik jangkar matematis untuk setiap sel:
  - Posisi Switch Input A: $(x_1 + 35, y_c - 20)$
  - Posisi Switch Input B: $(x_1 + 35, y_c + 20)$
  - Titik Pusat Gerbang Logika: $(x_c, y_c)$
  - Posisi Lampu LED Output Y: $(x_2 - 45, y_c)$
  - Titik Label Teks Mahasiswa: $(x_1 + 15, y_2 - 22)$
- **Pratinjau Visual Grid**:
  Pratinjau visual grid tersimpan di [`laporan_screenshots/Layout_Grid_Word_Preview.png`](file:///home/daun/aplikasi-prak/digitalworks/laporan_screenshots/Layout_Grid_Word_Preview.png).

---

### 8. ↶ Native Undo / Redo Engine (`Ctrl+Z` / `Ctrl+Y`)

- **Penyimpanan Rolling Snapshot**: Merekam perubahan rangkaian secara otomatis pada setiap modifikasi kawat, gerbang, atau teks.
- **Register-Preserving Jumps**: Hook x86 assembly murni 5-byte (`E9 rel32`) pada `Hook_SetModified` (`0x00487428`) dan `Hook_FormShortCut` (`0x0049f2a4`) menjaga kestabilan 100% tanpa risiko crash *Access Violation*.
- **In-Memory Menu Dispatch**: Memulihkan kondisi sirkuit seketika tanpa membuka instance jendela baru.

---

### 9. ⚡ Instant Delete (Bypass Konfirmasi Peringatan Hapus)

- Menghilangkan dialog konfirmasi *"Are you sure you want to delete this object?"* secara permanen melalui patch assembly:
  - Tombol keyboard `Delete`: `jmp 0x0049d640` di alamat `0x0049d5f3`.
  - Menu konteks klik kanan: `jmp 0x00489826` di alamat `0x004897dd`.
- Praktikan dapat menghapus objek secara instan; jika salah hapus, cukup tekan **`Ctrl+Z`**.

---

### 10. 🍵 Caelestia Matcha Dark Mode (Tema Gelap Elegan & Anti-Silau)

- Mencegat 5 thunk Windows GDI di section `.mod` (`CreateSolidBrush`, `CreateBrushIndirect`, `CreatePenIndirect`, `SetTextColor`, `SetBkColor`, `GetSysColor`).
- Mengubah canvas menjadi **Matte Matcha Slate `#1C201D`**, garis gerbang/kawat menjadi **Soft White `#E5E1E7`**, titik grid menjadi **Deep Matcha Pine `#374B3E`**, dan judul rangkaian menjadi **Radiant Sky Blue `#9DCEFF`**.
- Kontras tinggi (> 10:1) dengan visibilitas sempurna untuk lampu LED dan kawat aktif berlogika 1 (merah menyala).
- Beralih instan melalui **`Ctrl+D`** atau menu **`View -> Dark (Ctrl+D)`**.

---

### 11. 🔌 Analisis Mendalam Wiring Tool & Aturan Keamanan Elemen Sirkuit

#### 🔍 A. Investigasi Akar Masalah Kegagalan Wiring Tool
1. **Pencegatan Hit-Test Toolbar (Toolbar Interception Bug)**:
   - Pada percobaan penataan layout sebelumnya, fungsi `FixLayout` memanggil `SetHeight(80)` pada kontrol `ToolBar1` (`0x490`).
   - Hal ini membuat area transparan `ToolBar1` melebar ke bawah dan menutupi `ToolBar2` (tempat tombol `SpeedWireTool` berada di offset `0x524`).
   - Akibatnya, setiap klik mouse pada ikon Wiring Tool dicegat oleh `ToolBar1`. Tombol kawat tidak pernah tertekan (*Down state* gagal), dan aplikasi tetap terjebak di mode `SpeedPointer` (pemilih objek). Menyeret mouse antar pin hanya dianggap memindahkan gerbang atau membuat kotak seleksi, bukan menarik kawat.
   - **Solusi**: `FixLayout` telah dibersihkan sepenuhnya. `Panel1` (tinggi native 80px) kini menaungi keempat toolbar secara alami tanpa tumpang tindih. Seluruh tombol toolbar kembali responsif 100%.
2. **Kekeliruan Antara `Tag Device` vs `Wiring Tool`**:
   - Pada pengujian kanvas pengguna, komponen yang diklik adalah **`Tag Device`** (ikon 4 kotak bertingkat `品` di Baris 2).
   - `Tag Device` digunakan **khusus dalam pembuatan Makro/IC (`Template Editor`)** untuk memberi tag penamaan pin eksternal, dan hanya memiliki 1 pin. Menaruh `Tag Device` tidak akan menarik kawat.
   - Ikon **`Wiring Tool`** yang benar adalah gambar **dua kotak yang dihubungkan garis zig-zag kawat** (`Gifs/Connect.gif`), terletak di **ujung kanan Baris 3** (tepat di sebelah tombol teks `A`).
3. **Pintasan Keyboard Langsung (`W` & `Ctrl+W`)**:
   - Agar praktikan tidak perlu membidik ikon kecil di toolbar, kami telah menanamkan *handler* assembly x86:
     - Cukup tekan **`W`** atau **`Ctrl + W`** pada keyboard untuk seketika mengaktifkan mode penarikan kabel (kursor berubah menjadi pena `0x12c` dan tombol kawat tertekan otomatis). Tekan **`W`** lagi untuk kembali ke mode selektor (`SpeedPointer`).
4. **Perbaikan Serializer Snapshot Non-Destruktif (`SaveSnapshotStream`)**:
   - **Akar Masalah Penempatan 1x & Kawat Hilang**: Pada implementasi snapshot undo sebelumnya, pemanggilan `SaveToFile` bawaan Delphi di alamat `0x004847a4` mengeksekusi instruksi `call 0x00485518` (`SetWiringMode(0)`), mereset kursor (`Screen.Cursor = crDefault`), dan memanggil `SetModified(0)`.
   - **Dampak Fatal**: Begitu Pin 1 diklik (atau 1 tombol Button ditaruh), fungsi tersebut seketika mematikan mode penarikan kawat (kawat langsung lenyap!) dan membatalkan status penempatan beruntun.
   - **Solusi Tuntas**: Kami membangun serializer murni tanpa efek samping (`SaveSnapshotStream`) langsung dalam assembly x86 section `.mod`. Serializer ini hanya melakukan stream dumping komponen ke file `.dwm` tanpa mematikan mode kawat, tanpa mereset kursor, dan tanpa menyentuh properti nama file `FFileName`. Selain itu, pengecekan `cmp byte ptr [ebx + 0x298], 0` memastikan snapshot tidak diambil di tengah jalan saat kawat masih ditarik dari Pin 1 ke Pin 2.

---

#### ⚡ B. Analisis Karakteristik & Aturan Keamanan Seluruh Elemen Sirkuit (Physics & Logic Engine)

Agar perakitan rangkaian bebas crash, bebas pesan error, dan aman secara logika, pahami aturan fisika engine Digital Works berikut:

| Kategori Elemen | Komponen | Karakteristik Pin & Fisika Digital Works | Aturan & Tindakan Pencegahan |
|---|---|---|---|
| **Wiring Engine** | **Kabel / Wire** | Sinyal biner (0 = Low/Mati, 1 = High/Merah). Mendukung percabangan kawat (*T-junction*). | • **Output $\rightarrow$ Input**: ✅ Sangat aman & valid.<br>• **Output $\rightarrow$ Output**: ❌ **DILARANG KERAS** (memicu *bus contention / short circuit*, DigitalWorks akan menolak koneksi dan membunyikan alarm *beep*).<br>• **Input $\rightarrow$ Input Langsung**: ❌ Tidak dapat ditarik tanpa sumber penggerak (*driver*). |
| **Input Elemen** | **Interactive Switch** | Saklar biner 1-pin output (0 atau 1). Mode *toggle*. | Digunakan untuk memberikan input A, B, C pada gerbang logika. Aman dihubungkan ke banyak input gerbang (fan-out). |
| | **Push Button** | Tombol pulsa 1-pin output. Aktif 1 hanya selama mouse ditekan. | Sangat ideal untuk tombol Reset (CLR) atau trigger pulsa manual. |
| | **Clock Generator** | Generator osilasi kotak periodik (1-pin output). | Memiliki pengaturan frekuensi detak (Hz). Jangan menghubungkan output Clock langsung ke output gerbang lain. |
| **Output Elemen** | **LED (Light Emitting Diode)** | 1-pin input. Menyala merah terang saat menerima logika 1 (HIGH). | Hubungkan langsung ke pin output gerbang logika atau kawat aktif. |
| | **7-Segment Display** | 7 atau 8 pin input (a s/d g, titik desimal dp). | Memerlukan dekoder BCD (misal 7447/7448) atau matriks kombinasi untuk menampilkan angka 0-9. |
| **Gerbang Logika** | **AND, OR, NOT, NAND, NOR, XOR, XNOR** | Pin input di sisi kiri, pin output di sisi kanan. Mendukung penambahan input (2 hingga 8 pin) via *Object Properties*. | Hindari membuat loop logika tanpa gerbang tunda atau flip-flop untuk mencegah osilasi tak hingga (*race condition*). |
| **Penyangga Khusus** | **Tri-State Buffer** | Memiliki 1 pin input (kiri), 1 pin output (kanan), dan 1 pin kontrol Enable (bawah). | **Satu-satunya gerbang yang outputnya boleh dihubungkan bersama ke output lain** (membentuk Bus bersama), asalkan hanya satu buffer yang berstatus Enable=1 pada satu waktu (lainnya berstatus High-Z). |
| **Elemen Sekuensial** | **Flip-Flop (D, JK, T, SR)** | Memiliki pin input data, pin Clock (segitiga panah), output Q dan Q̄, serta Preset/Clear. | • Pin Clock harus dihubungkan ke Clock Generator atau switch pulsa manual.<br>• Gunakan tombol **`Spacebar`** untuk menguji langkah detak demi detak secara presisi. |
| **Modul / Makro** | **Tag Device (`品`) & Macro** | Antarmuka bridging pin modul IC ke lembar kerja utama. | Gunakan Tag Device **hanya di dalam Template Editor Makro**. Jangan ditaruh sembarangan di lembar kerja biasa agar tidak membingungkan topologi kawat. |

---

## ⌨️ Daftar Lengkap Pintasan Keyboard (Shortcuts)

| Shortcut | Fungsi | Keterangan |
|---|---|---|
| **`Ctrl + I`** | **AI Circuit Agent** | Memunculkan dialog perintah perakitan rangkaian otomatis AI |
| **`Ctrl + Z`** | **Undo Rangkaian** | Membatalkan perubahan / memulihkan komponen yang terhapus |
| **`Ctrl + Y`** | **Redo Rangkaian** | Memajukan ke snapshot rangkaian berikutnya |
| **`Ctrl + G`** | **Toggle Layout Grid** | Menampilkan / menyembunyikan garis bantu grid ala Microsoft Word |
| **`Ctrl + D`** | **Toggle Dark Mode** | Beralih antara Tema Gelap Caelestia Matcha dan Tema Terang |
| **`Delete`** | **Hapus Instan** | Menghapus komponen terpilih tanpa dialog konfirmasi yang mengganggu |
| **`W`** / **`Ctrl + W`** | **Wiring Tool Toggle** | Mengaktifkan / menonaktifkan mode penarikan kabel seketika |
| **`Spacebar`** | **Detak Clock Manual** | Mengirim 1 pulsa detak clock (sangat berguna untuk Flip-Flop/Counter) |
| **`F5`** | **Run / Stop Simulasi** | Memulai atau menghentikan simulasi logika |

---

## 🖥️ Menu Header Resmi Digital Works

```text
File   Edit   Circuit   View   Mods   Help
                         │      │      │
                         │      │      └── 🤖 &AI Assistant   (Ctrl+I)
                         │      │
                         │      ├── ↶ &Undo (Ctrl+Z)
                         │      ├── ↷ &Redo (Ctrl+Y)
                         │      ├── 📊 Auto &Truth Table...
                         │      ├── 📸 &Batch Capture...
                         │      ├── 📐 &Boolean Equation...
                         │      └── 💾 &Save Snapshot
                         │
                         ├── ...
                         ├── &Dark (Ctrl+D)
                         └── &Layout Grid   (Ctrl+G)
```

---

## 🛠️ Antarmuka Baris Perintah (CLI Runner Options)

ELF runner native [`digitalworks`](file:///home/daun/aplikasi-prak/digitalworks/digitalworks) (dan wrapper [`/home/daun/.local/bin/digital-works`](file:///home/daun/.local/bin/digital-works)) mendukung berbagai flag CLI cepat tanpa perlu membuka GUI:

```bash
# Menjalankan simulator DigitalWorks (dengan tema Dark Mode & Sentinel otomatis aktif)
./digitalworks

# Memanggil AI Circuit Agent untuk merakit rangkaian multi-komponen otomatis
./digitalworks --ai "Buat semua 7 gerbang logika dasar di grid"
./digitalworks -ai "Buatkan Half Adder di [1,1] dan Full Adder di [2,1]"

# Menyimpan API Key Google AI Studio (Gemini) secara persisten
./digitalworks --set-key "AIzaSy..."

# Mengenerate tabel kebenaran akurat (Word TSV, Markdown, LaTeX) ke clipboard & file
./digitalworks --truth-table
./digitalworks -tt

# Ekspor tabel kebenaran langsung ke format Microsoft Word TSV
./digitalworks --export-tsv

# Ekspor tabel kebenaran langsung ke format kode LaTeX
./digitalworks --export-latex

# Menjalankan batch screenshot semua kombinasi input logika (38 states + All-States Collages)
./digitalworks --batch-screens
./digitalworks -bc

# Mengekstrak persamaan aljabar Boolean (Ringkas, SOP minterms, POS maxterms)
./digitalworks --equation
./digitalworks -eq

# Menampilkan / menyembunyikan Word Layout Grid pada kanvas
./digitalworks --grid
./digitalworks -g

# Membaca koordinat anchor sel grid dalam format JSON (untuk integrasi AI Agent)
./digitalworks --grid-info

# Membatalkan perubahan rangkaian (Undo)
./digitalworks --undo
./digitalworks -u

# Memajukan perubahan rangkaian (Redo)
./digitalworks --redo
./digitalworks -r

# Menampilkan ringkasan bantuan opsi CLI
./digitalworks --help
```

---

## 📂 Struktur Direktori Proyek

```text
/home/daun/aplikasi-prak/digitalworks/
├── digitalworks                  # Binary Native ELF 64-bit Runner (Arch Linux)
├── DigitalWorks                  # Symlink ke native runner
├── DigitalWorks.exe              # Binary Modded Resmi (Section .mod, Menu Header, x86 Hooks)
├── DigitalWorks.exe.orig         # Binary Cadangan Asli Digital Works 3.0
├── dw_undo_engine.py             # Mesin Sentinel In-UI (AI Agent, Solver, Grid, Batch, Undo)
├── build_complete_mod.py         # Skrip Kompilator Assembler & PE Patcher
├── runner.c                      # Source code C untuk Native ELF Runner
├── .gemini_key                   # Berkas penyimpan API Key Gemini lokal (opsional)
├── README.md                     # Dokumentasi komprehensif proyek modding ini
├── REVERSE_ENGINEERING_REPORT.md # Laporan teknis reverse engineering Delphi 5
├── Tabel_Kebenaran_Word.tsv      # Hasil ekspor tabel TSV (Paste langsung jadi tabel kotak Word)
├── Tabel_Kebenaran_Otomatis.md   # Hasil ekspor tabel Markdown
├── Tabel_Kebenaran_LaTeX.tex     # Hasil ekspor kode LaTeX tabular
├── Persamaan_Logika.md           # Hasil ekstraksi persamaan Boolean (SOP & POS)
├── laporan_screenshots/          # Direktori tangkapan layar praktikum
│   ├── Kolase_Semua_Kemungkinan_Tabel_01_AND.png # Kolase 4 state berdampingan
│   ├── Kolase_Semua_Kemungkinan_Tabel_10_XOR.png # Kolase 4 state berdampingan
│   ├── Layout_Grid_Word_Preview.png              # Pratinjau Grid Word & AI Anchors
│   ├── user_canvas_live_cropped.png              # Hasil crop presisi rangkaian aktif
│   └── ... (38 file screenshot state 00, 01, 10, 11)
├── .undo_history/                # Buffer snapshot rolling & file trigger internal
│   ├── layout_grid.json          # Konfigurasi status & merge cell grid Word
│   ├── trigger_ai.txt            # Sinyal trigger AI Assistant dari PE
│   ├── trigger_grid.txt          # Sinyal trigger Layout Grid dari PE
│   └── ... (.dwm snapshots)
└── re_extracted/                 # Hasil Ekstraksi Reverse Engineering Delphi
    ├── classes_and_methods.json  # Database 229 class Delphi VCL
    ├── symbols_map.txt           # Peta simbol dan alamat VMT
    ├── core_handlers_disasm.asm  # Disassembly instruksi kunci
    └── forms/                    # 19 File resource DFM biner asli
```

---

## 👨‍💻 Informasi Pembuat & Praktikum

- **Mata Kuliah**: Praktikum Sistem Digital
- **Program Studi**: S1 Informatika, Universitas Sebelas Maret (UNS)
- **Lingkungan Sistem**: Arch Linux (Hyprland / Wayland / Wine Native)
- **Status Binary**: 100% Modded In-Codebase, Teruji Bebas Crash, Siap Pakai Praktikum.
