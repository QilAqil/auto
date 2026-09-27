# Panduan crop aset (template matching)

Klik = **tengah PNG + offset_x/offset_y**. Crop hanya teks label, jangan ikut kotak input.

Syarat layar: zoom browser **100%**, scaling Windows **100%**, crop dari form BPN asli.

## Aturan ukuran

| Jenis | Lebar × tinggi | Isi crop |
|---|---|---|
| Kode DI (`DI 301`) | **50–80 × 16–24** | Hanya teks `DI 301` |
| Label pendek (`Nama`, `Tanggal`) | **60–120 × 16–24** | Hanya kata label |
| Label 2–3 baris (`Penunjukan dan…`) | **140–200 × 28–40** | Hanya teks label, tanpa textarea |
| Tab (`DETIL`) | **50–80 × 20–28** | Hanya kata **DETIL** (garis bawah boleh) |
| Checkbox | **14–22 × 14–22** | Kotak centang saja |
| Item dropdown | **140–240 × 18–26** | Satu baris hasil pencarian |

Jangan: lebar ≥ 400, tinggi ≥ 80, atau rasio sangat melebar (seluruh baris form).

---

## Hasil cek folder saat ini

### Crop kebesaran (ikut field / baris sebelah) — crop ulang

| File | Sekarang | Target | Crop yang benar |
|---|---|---|---|
| `label_di_301.png` | 500×50 | **56×20** | Hanya `DI 301`. Jangan kotak nomor, jangan `Tahun`. |
| `label_di_303.png` | 500×50 | **56×20** | Hanya `DI 303`. Jangan `Nomor...` / `Tahun...`. |
| `label_tab_detil.png` | 200×60 | **56×24** | Hanya `DETIL`. Jangan `PENCARIAN` / `CATATAN`. |
| `label_tgl_penomoran.png` | **80×20 (sudah diperbarui)** | **80×20** | Hanya teks `Tgl. Penomoran`; tanpa placeholder field. Offset config: **X=110, Y=0**. Confidence: **0.9**. |
| `label_pembukuan_tanggal.png` | 450×50 | **70×20** | Hanya kata `Tanggal` di blok Pembukuan. |
| `label_penerbitan_tanggal.png` | 450×50 | **70×20** | Hanya `Tanggal` di blok Penerbitan. |
| `label_pembukuan_bt_tanggal.png` | 450×50 | **70×20** | Sama, blok Pembukuan BT. |
| `label_penerbitan_bt_tanggal.png` | 450×50 | **70×20** | Sama, blok Penerbitan BT. |
| `label_pembukuan_jabatan.png` | 500×50 | **70×20** | Hanya `Jabatan`. Jangan checkbox `An.` / dropdown. |
| `label_penerbitan_jabatan.png` | 500×50 | **70×20** | Hanya `Jabatan` Penerbitan SU. |
| `label_pembukuan_bt_jabatan.png` | 500×50 | **70×20** | Hanya `Jabatan` Pembukuan BT. |
| `label_penerbitan_bt_jabatan.png` | 500×50 | **70×20** | Hanya `Jabatan` Penerbitan BT. |
| `label_pembukuan_nama.png` | 500×50 | **52×20** | Hanya `Nama`. Jangan kotak panjang. |
| `label_penerbitan_nama.png` | 500×50 | **52×20** | Hanya `Nama` Penerbitan SU. |
| `label_pembukuan_bt_nama.png` | 500×50 | **52×20** | Hanya `Nama` Pembukuan BT. |
| `label_penerbitan_bt_nama.png` | 500×50 | **52×20** | Hanya `Nama` Penerbitan BT. |
| `label_keadaan_tanah.png` | 650×100 | **120×20** | Hanya `Keadaan Tanah`. Jangan textarea & baris tetangga. |
| `label_tanda_batas.png` | 650×100 | **130×20** | Hanya `Tanda-Tanda Batas`. |
| `label_pengukuran.png` | 650×100 | **180×36** | Hanya `Penunjukan dan Penetapan Batas` (2 baris label OK). |
| `label_hal_lain.png` | 650×100 | **100×20** | Hanya `Hal Lain-lain`. |
| `label_petunjuk_bt.png` | 650×100 | **80×20** | Hanya `Penunjuk`. Jangan `No SK` / textarea. |
| `label_pembukuan_item.png` | 500×50 | **100×22** | Hanya judul `Pembukuan` (opsional, tidak dipakai config). |
| `label_penerbitan_item.png` | 500×50 | **160×22** | Hanya `Penerbitan Sertifikat`. |
| `label_pembukuan_bt_item.png` | 500×50 | **100×22** | Judul Pembukuan BT. |
| `label_penerbitan_bt_item.png` | 500×50 | **160×22** | Judul Penerbitan BT. |

Offset setelah crop kecil (dari tengah **label** ke input di kanan):  
`Nama`/`Tanggal`/`Jabatan` ≈ ox **90–140**; detail textarea ≈ ox **160–200**; DI nomor ≈ **70–110**, tahun ≈ **220–280**, tgl ≈ **340–420**.

### Ukuran sudah wajar — cek isinya

| File | Sekarang | Catatan |
|---|---|---|
| `label_pembukuan_centang.png` | 60×60 | Agak besar; ideal **18×18** kotak saja. Boleh dipakai jika hanya checkbox. |
| `label_pembukuan_bt_centang.png` | 60×60 | Sama; crop saat ini ikut teks `An.` — perkecil ke kotak. |

### Masih placeholder 1×1 — wajib diganti

Dipakai config sebagai hasil dropdown (klik2). Crop **satu baris** di list setelah ketik jabatan/nama.

| File | Target | Isi |
|---|---|---|
| `label_pembukuan_jabatan_item.png` | **180×22** | Baris list jabatan SU |
| `label_pembukuan_nama_item.png` | **180×22** | Baris list nama SU |
| `label_penerbitan_jabatan_item.png` | **180×22** | Baris list jabatan penerbitan SU |
| `label_penerbitan_nama_item.png` | **180×22** | Baris list nama penerbitan SU |
| `label_pembukuan_bt_jabatan_item.png` | **180×22** | Baris list jabatan BT |
| `label_pembukuan_bt_nama_item.png` | **180×22** | Baris list nama BT |
| `label_penerbitan_bt_jabatan_item.png` | **180×22** | Baris list jabatan penerbitan BT |
| `label_penerbitan_bt_nama_item.png` | **180×22** | Baris list nama penerbitan BT |
| `label_penerbitan_centang.png` | **18×18** | Checkbox Penerbitan SU |
| `label_penerbitan_bt_centang.png` | **18×18** | Checkbox Penerbitan BT |

---

## Kenapa crop besar gagal

Tengah gambar baris 500 px ada di **dalam kotak input** atau di label `Tahun`.  
Program lalu menambah `offset_x` lagi → klik ke kanan, di luar field.

`Tanggal` / `Jabatan` / `Nama` muncul **dua kali** (Pembukuan dan Penerbitan). Crop harus dari blok yang benar, atau locator bisa mengklik yang atas.

File `*_item.png` (judul seksi) **tidak** sama dengan `*_jabatan_item.png` (baris dropdown).
