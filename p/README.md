# BPN Cropper dengan OCR

## Persiapan

1. Jalankan `setup.bat` untuk membuat virtual environment dan memasang dependensi Python.
2. Instal Tesseract untuk Windows dari [UB Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki). Gunakan direktori instalasi default atau direktori baru yang khusus untuk Tesseract; jangan memilih folder yang sudah berisi file lain.
3. Pastikan model bahasa `Indonesian` (`ind`) dan `English` (`eng`) ikut dipasang. OCR menggunakan keduanya.

Tesseract adalah program terpisah dari paket Python. OCR akan mencari `tesseract.exe` melalui `PATH` atau direktori instalasi Windows default.

## Menjalankan

Jalankan `run.bat`, lalu pilih:

- `1` untuk capture dan crop screenshot (pilihan default).
- `2` untuk menjalankan OCR pada file PNG yang sudah ada di `output`.
- `3` untuk memilih screenshot SU/BT terbaru otomatis dan membuat crop label yang ditemukan OCR.

Mode 3 memilih file terbaru berdasarkan nama `su_full_*.png` dan `bt_full_*.png`, lalu memeriksa apakah isi screenshot sesuai dengan tab-nya. Ukuran crop mengikuti `w` dan `h` di `config.json`; posisi klik yang tersimpan sebagai `offset_x` dan `offset_y` tidak diubah. Hasil dan status tiap label dicatat di `output/auto_crop_report.csv`. Label yang tak terbaca tidak dibuat agar crop lama tidak diganti dengan tebakan. Screenshot dropdown harus diambil saat daftar dropdown terbuka; checkbox memerlukan locator khusus.

Mode 2 menyimpan OCR ke `output/ocr_results`: satu file teks per gambar dan ringkasan validasi `hasil_ocr.csv`. Label dengan teks yang terdaftar di `validate.py` akan ditandai `COCOK` atau `TIDAK COCOK`; label lainnya ditandai `TIDAK DIATUR`.