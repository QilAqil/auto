# Panduan Distribusi & Penerbitan OTOBPN WaitFind V6
Dokumen ini berisi rencana lengkap dan langkah-langkah teknis untuk membagikan program **OTOBPN WaitFind V6** ke komputer lain secara aman, cepat, tanpa membagikan file mentah (source code `.py`), serta penyesuaian aset layar dan OCR kustom.

---

## 📂 Struktur Folder Rilis yang Direkomendasikan (V6_Publish)
Untuk mendistribusikan aplikasi, Anda harus membuat folder bersih yang berisi semua file siap pakai. Di komputer tujuan, folder ini cukup diekstrak dan siap dijalankan.

Struktur folder rilis setelah kompilasi:
```text
V6_Publish/
├── run_su.exe               # Executable utama untuk versi SU (hasil kompilasi)
├── run_bt.exe               # Executable utama untuk versi BT (hasil kompilasi)
├── config.yaml              # Konfigurasi program (dapat diubah sesuai kebutuhan komputer tujuan)
└── assets/                  # Folder berisi gambar pencarian (template matching gabungan V5 & V6)
```

---

## 🛠️ Langkah 1: Proses Kompilasi di Komputer Developer (Anda)
Lakukan langkah ini di komputer Anda untuk menghasilkan file `.exe` yang aman dan menyembunyikan file OCR kustom Anda:

1. **Install PyInstaller:**
   Buka terminal/PowerShell di folder proyek Anda dan instal PyInstaller:
   ```powershell
   pip install pyinstaller
   ```

2. **Kompilasi dengan Menyisipkan (Bundling) Model OCR Kustom:**
   Agar OCR kustom yang Anda miliki tidak dapat diutak-atik atau disalin dari folder luar oleh orang lain, kita akan **membungkus folder `ocr_models` langsung ke dalam file executable** menggunakan parameter `--add-data`.
   
   Jalankan perintah kompilasi berikut di terminal proyek:
   ```powershell
   pyinstaller --onedir --add-data "ocr_models;ocr_models" run_su.py
   pyinstaller --onedir --add-data "ocr_models;ocr_models" run_bt.py
   ```
   *Catatan:* PyInstaller akan membuat folder `dist/run_su` dan `dist/run_bt`, lalu membungkus folder model OCR ke dalamnya secara rapi di dalam binary.

3. **Satukan Hasil Kompilasi ke Folder `V6_Publish`:**
   - Salin file `run_su.exe` dari `dist/run_su/` ke root folder `V6_Publish/`.
   - Salin file `run_bt.exe` dari `dist/run_bt/` ke root folder `V6_Publish/`.
   - **GABUNGKAN Aset Gambar (Penting!):**
     Karena kode V6 memiliki *fallback* pencarian ke folder V5 jika aset tidak ditemukan, maka untuk membuat folder `V6_Publish` ini mandiri 100%, Anda harus **menyalin semua file gambar dari folder `OTOBPN_WaitFind_V6/assets/` DAN folder `OTOBPN_WaitFind_V5/assets/`** ke dalam folder `V6_Publish/assets/`. (Pastikan file dari V6 menimpa file V5 jika ada nama file yang sama karena V6 memiliki aset yang lebih baru).
   - Salin file [config.yaml](file:///a:/Entry%20data%20BPN/Program/Captcha%20Auto/OTOBPN_WaitFind_V6/config.yaml) ke dalam `V6_Publish/`.

---

## 🧠 Langkah 2: Perlindungan & Kerahasiaan Model OCR Kustom
Dengan metode baru ini, model OCR kustom Anda aman dari modifikasi eksternal:
- **Kerahasiaan Terjamin:** Model kustom (`custom_easyocr.pth`, `custom_easyocr.yaml`, dan `custom_easyocr.py`) serta model deteksi standar (`craft_mlt_25k.pth`) dibungkus dalam folder internal PyInstaller yang hanya diekstrak ke memori / folder temp sementara saat program dijalankan dan langsung dihapus saat ditutup. Operator komputer tujuan tidak akan melihat file-file ini di direktori biasa.
- **Bebas Ribet:** Pengguna di komputer tujuan **TIDAK PERLU** menyalin file secara manual ke folder `C:\Users\<user>\.EasyOCR\`. Program akan langsung mendeteksi model di dalam folder internal bundelnya sendiri secara otomatis.
- **Offline Ready:** Karena model deteksi (`craft_mlt_25k.pth`) juga ikut dibungkus, komputer tujuan tidak membutuhkan koneksi internet sama sekali untuk mendownload model dasar EasyOCR saat pertama kali dijalankan.


---

## 🖥️ Langkah 3: Penyesuaian Resolusi Layar & Aset Gambar (Sangat Penting)
Program Anda menggunakan `pyautogui.locateCenterOnScreen` untuk mencari tombol/input secara visual. PyAutoGUI bekerja dengan mencocokkan pixel gambar secara presisi (Template Matching). Jika resolusi layar, scaling Windows, atau zoom browser di komputer tujuan berbeda, program **tidak akan bisa menemukan tombol (ImageNotFoundException)**.

### A. Aturan Wajib Setup Komputer Tujuan
1. **Windows Display Scale harus 100%:**
   Banyak laptop menggunakan scaling 125% atau 150%. Ini akan merusak ukuran pixel tangkapan layar.
   - Cara ubah: *Settings > System > Display > Scale and layout > Ubah ke 100%*.
2. **Browser/Web Page Zoom harus 100%:**
   Pastikan browser tempat membuka web BPN diatur ke zoom **100%** (tekan `Ctrl + 0`).
3. **Resolusi Layar Sama:**
   Jika memungkinkan, gunakan resolusi layar yang sama dengan komputer Anda (misalnya 1920x1080).

### B. Cara Mengatasi Jika Resolusi/Tampilan Berbeda (Rekam Aset Baru)
Jika setelah disamakan ke 100% program tetap tidak mendeteksi tombol, operator di komputer tujuan harus **mengganti aset gambar dengan screenshot dari layar mereka sendiri**:

1. Buka halaman BPN di browser komputer tujuan (layar penuh / maximized).
2. Gunakan Snipping Tool bawaan Windows untuk mengambil screenshot kecil pada tombol/label yang gagal dideteksi (potong pas pada bagian tombol saja).
3. Simpan gambar screenshot baru tersebut ke folder `V6_Publish/assets/` dengan **nama file yang persis sama** untuk menimpa file lama (contoh: `label_menu.png`).
4. Jalankan ulang program.

### C. Optimasi Toleransi via `config.yaml`
Di file `config.yaml`, Anda bisa menaikkan nilai toleransi pencarian gambar dengan menurunkan tingkat kepercayaan (`confidence`) pada elemen yang sulit dideteksi:
- Nilai `confidence: 0.8` berarti kecocokan harus 80%.
- Jika tombol sering terlewat, turunkan menjadi `confidence: 0.7` atau `0.75` pada elemen terkait di `config.yaml`. Namun jangan terlalu rendah agar tidak salah klik ke elemen lain.

---

## 📋 Checklist Implementasi Distribusi
- [ ] Lakukan kompilasi `run_su.py` dan `run_bt.py` ke `.exe` dengan menyertakan parameter `--add-data "ocr_models;ocr_models"`.
- [ ] Buat folder rilis `V6_Publish` dan isi dengan `.exe` (SU & BT), `config.yaml`, dan folder `assets/` (yang berisi gabungan aset V5 & V6).
- [ ] Pindahkan folder `V6_Publish` ke komputer tujuan.
- [ ] Atur display scale Windows & browser zoom ke 100% di komputer tujuan.
- [ ] Lakukan uji coba pertama, sesuaikan aset gambar jika ada tombol yang tidak terdeteksi.
