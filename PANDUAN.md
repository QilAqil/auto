# OTOBPN Detil v7

Aplikasi desktop untuk mengisi **tab DETIL** Manajemen Dokumen ATR/BPN:
**Surat Ukur (SU)** dan **Buku Tanah (BT)**. Ini adalah bangun ulang dari
folder `run/` (auto-paste koordinat) dengan pemisahan logika bisnis vs akses
layar, locator + cache, OCR opsional, retry/verifikasi, dry-run, dan resume.

Gunakan hanya pada akun dan data yang **Anda berwenang** mengolah.

---

## 1. Struktur folder

```
d:\c\
├── run_app.py                 # entry GUI
├── config.yaml                # sumber kebenaran (semua modul lewat loader)
├── requirements.txt
├── build.spec                 # PyInstaller --onedir
├── RUN.bat / RUN_silent.vbs
├── assets/                    # template PNG label UI
├── ocr_models/                # model EasyOCR (opsional, ikut bundle)
├── laporan_proses.txt         # log (dibuat saat jalan)
├── state_resume.json          # putaran terakhir
├── tests/                     # unit tes tanpa layar
├── run/                       # aplikasi lama (arsip)
└── otobpn/
    ├── paths.py               # base path script vs frozen
    ├── config_loader.py       # load/save YAML + default
    ├── logger.py              # log thread-safe + rotasi 1 MB
    ├── errors.py              # ElementNotFound, OCRFailed, timeout, stop
    ├── domain/                # murni, tanpa pyautogui
    │   ├── models.py          # ElemenUI, KolomDI, Region, HasilLangkah
    │   ├── text_rules.py      # validasi OCR, nama pemohon, sisip teks
    │   ├── guards.py          # rantai langkah (berhenti jika gagal)
    │   └── resume.py          # state_resume.json
    ├── screen/                # satu-satunya jembatan OS
    │   ├── protocol.py        # ScreenPort + Box
    │   ├── pyautogui_adapter.py
    │   ├── dry_run_adapter.py
    │   └── fake.py            # untuk tes
    ├── vision/
    │   ├── locator.py         # template matching, cache region, retry
    │   ├── preprocessor.py    # HSV/CLAHE/invert/bilateral/sharpen
    │   └── ocr.py             # EasyOCR + allowlist + panjang
    ├── actions/               # klik/paste memakai ScreenPort
    │   ├── field.py
    │   ├── pejabat.py
    │   ├── daftar_isian.py
    │   └── detail.py
    ├── orchestrator/
    │   ├── control.py         # pause/stop/timeout
    │   ├── context.py
    │   ├── flow_su.py         # urutan DETIL Surat Ukur
    │   ├── flow_bt.py         # urutan DETIL Buku Tanah
    │   └── runner.py          # loop + error handling + resume
    └── gui/                   # Tkinter
```

Kegunaan sama dengan aplikasi lama: isi Pembukuan, Penerbitan Sertifikat,
Daftar Isian, Detail Lain-Lain (SU), Petunjuk (BT); F1 mulai, jeda per
record, ESC stop.

---

## 2. Config

Semua klik memakai **template PNG di `assets/`** plus `offset_x` / `offset_y`
dari tengah gambar (bukan x,y layar). Nama file, delay, hotkey, dan
enable langkah ada di `config.yaml`. Modul hanya lewat `load_config()`.

Simpan dari GUI menimpa komentar. Cadangkan salinan sebelum eksperimen.

---

## 3. Error handling

| Kondisi | Perilaku |
|---|---|
| Elemen tidak ketemu | `ElementNotFound` setelah `retry.max_attempts`; putaran GAGAL, auto-jeda |
| OCR gagal | `OCRFailed` jika `ocr.enabled`; field biasa tetap clipboard |
| Timeout | `StepTimeout` pada tunggu predikat |
| Verifikasi paste | banding teks clipboard vs kiriman; `stop_on_verify_fail` opsional |
| Resume | `state_resume.json` menyimpan nomor putaran; RESET menolkan |
| Safe-stop | ESC / STOP set event; worker selesai langkah pendek lalu keluar; FAILSAFE pyautogui (sudut kiri atas) |

---

## 4. PyInstaller + setup komputer target

```powershell
pip install -r requirements.txt
pyinstaller build.spec
```

Salin **seluruh** `dist\otobpn_detil\` (bukan exe saja). Letakkan
`config.yaml` dan `assets\` di samping exe jika ingin diubah tanpa rebuild.

### Checklist layar (wajib sama dengan saat crop template)

- Resolusi native sama (mis. 1920×1080).
- Windows Display scaling **100%**.
- Zoom browser **100%**.
- Jendela BPN maximized, sidebar kiri sama lebar.
- DPI awareness: jangan mix monitor scaling berbeda.
- Ambil ulang PNG jika tema/warna UI berubah.
- Pakai **Cek Asset** untuk melihat PNG yang ada.
- `search_region` membatasi area scan template, bukan titik klik.

OCR: unduh model EasyOCR sekali di mesin build, simpan di `ocr_models/`,
baru bundle. Pengguna akhir tidak perlu internet untuk model.

---

## 5. Yang harus divalidasi manual

1. Satu record SU: Pembukuan jabatan+nama, Penerbitan, DI 303, template nama.
2. Satu record BT: Pembukuan BT, Penerbitan BT, DI 301, Petunjuk.
3. Dry-run: centang di GUI, pastikan log `[DRY]` tanpa perubahan form.
4. Jeda: F1 lalu hotkey jeda; record kedua tidak jalan sebelum jeda.
5. ESC di tengah ketik: berhenti, mouse tidak “liar”.
6. Verifikasi: sengaja ubah delay sangat kecil, lihat log jika field lambat.
7. Ganti resolusi / scaling 125%: harus gagal locate atau meleset — itu
   expected; jangan pakai sampai koordinat/PNG disesuaikan.
8. Ganti placeholder 1×1 di `assets/` dengan crop label asli (zoom 100%).
9. Sesuaikan `offset_x`/`offset_y` jika klik mengenai label, bukan field.

---

## 6. Kepatuhan penggunaan

- Otomasi ini meniru operator di **sesi Anda sendiri**. Jangan dipakai
  untuk mengakses sistem orang lain, menembus captcha milik pihak ketiga,
  atau mengirim data fiktif ke register pertanahan.
- Tanggung jawab isi (nama pejabat, tanggal, DI) ada pada petugas.
- Log `laporan_proses.txt` dapat berisi nama dan nomor dokumen — jangan
  bagikan sembarangan.
- Folder `run/` adalah versi lama; v7 adalah yang didukung.

---

## 7. Menjalankan

```powershell
pip install -r requirements.txt
py run_app.py
```

Tes tanpa GUI:

```powershell
py -m pytest tests -q
```
