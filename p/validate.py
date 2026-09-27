"""
OCR batch untuk hasil crop BPN Cropper.
"""
import csv
import glob
import json
import os
import re
import shutil
import sys
from PIL import Image
import pytesseract

OCR_LANG = "ind+eng"   # gabungan Indonesia + Inggris
OCR_PSM  = 7           # Treat image as a single text line (cocok untuk label)
OCR_OEM  = 3           # Default engine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mapping nama label → teks yang diharapkan (untuk validasi)
# Sesuai panduan crop: nama file harus cocok dengan isi teksnya.
EXPECTED_TEXT = {
    "label_di_301":                 ["DI 301", "DI301", "D1301"],
    "label_di_303":                 ["DI 303", "DI303", "D1303"],
    "label_tab_detil":              ["DETIL"],
    "label_tgl_penomoran":          ["Tgl. Penomoran", "Tgl Penomoran", "Penomoran"],
    "label_pembukuan_tanggal":      ["Tanggal"],
    "label_penerbitan_tanggal":     ["Tanggal"],
    "label_pembukuan_bt_tanggal":   ["Tanggal"],
    "label_penerbitan_bt_tanggal":  ["Tanggal"],
    "label_pembukuan_jabatan":      ["Jabatan"],
    "label_penerbitan_jabatan":     ["Jabatan"],
    "label_pembukuan_bt_jabatan":   ["Jabatan"],
    "label_penerbitan_bt_jabatan":  ["Jabatan"],
    "label_pembukuan_nama":         ["Nama"],
    "label_penerbitan_nama":        ["Nama"],
    "label_pembukuan_bt_nama":      ["Nama"],
    "label_penerbitan_bt_nama":     ["Nama"],
    "label_keadaan_tanah":          ["Keadaan Tanah", "KeadaanTanah"],
    "label_tanda_batas":            ["Tanda-Tanda Batas", "TandaTandaBatas", "Tanda Batas"],
    "label_pengukuran":             ["Penunjukan dan", "Penetapan Batas", "Penunjukan"],
    "label_hal_lain":               ["Hal Lain-lain", "Hal Lain"],
    "label_petunjuk_bt":            ["Penunjuk", "Petunjuk"],
}


def _clean(text: str) -> str:
    """Bersihkan teks hasil OCR: hapus newline, spasi ganda, karakter aneh."""
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Buang karakter yang sering jadi noise
    text = re.sub(r"[^\w\s\.\-/]", "", text)
    return text


def ocr_image(image_path: str, lang: str = OCR_LANG, psm: int = OCR_PSM) -> str:
    """OCR satu file gambar, kembalikan teks bersih."""
    if not os.path.exists(image_path):
        return ""
    with Image.open(image_path) as img:
        config = f"--oem {OCR_OEM} --psm {psm}"
        raw = pytesseract.image_to_string(img, lang=lang, config=config)
    return _clean(raw)


def ocr_and_save(image_path: str, label_name: str, out_dir: str) -> str:
    """OCR gambar, simpan hasil ke out_dir/<label_name>.txt, return teks."""
    text = ocr_image(image_path)
    txt_path = os.path.join(out_dir, f"{label_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def validate_against_label(label_name: str, ocr_text: str) -> bool:
    """
    Cek apakah hasil OCR cocok dengan yang diharapkan untuk label ini.
    Return True jika cocok (atau label tidak punya ekspektasi).
    """
    if label_name not in EXPECTED_TEXT:
        return True  # tidak ada ekspektasi → anggap OK
    ocr_norm = ocr_text.lower().replace(" ", "")
    for expected in EXPECTED_TEXT[label_name]:
        exp_norm = expected.lower().replace(" ", "")
        if exp_norm in ocr_norm or ocr_norm in exp_norm:
            return True
    return False


def configure_tesseract():
    """Cari instalasi Tesseract Windows dan pastikan model bahasa tersedia."""
    executable = shutil.which("tesseract")
    if not executable:
        candidates = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        )
        executable = next((path for path in candidates if os.path.isfile(path)), None)

    if not executable:
        raise RuntimeError(
            "Tesseract belum ditemukan. Instal dari https://github.com/UB-Mannheim/tesseract/wiki "
            "ke folder default, lalu jalankan OCR lagi."
        )

    pytesseract.pytesseract.tesseract_cmd = executable
    installed_languages = set(pytesseract.get_languages(config=""))
    missing_languages = set(OCR_LANG.split("+")) - installed_languages
    if missing_languages:
        missing = ", ".join(sorted(missing_languages))
        raise RuntimeError(
            f"Model bahasa Tesseract belum tersedia: {missing}. "
            "Jalankan installer Tesseract lagi dan tambahkan model bahasa tersebut."
        )


def run_batch():
    """Proses semua PNG di output dan simpan teks serta laporan validasi."""
    with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as file:
        config = json.load(file)

    output_dir = os.path.join(BASE_DIR, config["output_dir"])
    image_paths = sorted(glob.glob(os.path.join(output_dir, "*.png")))
    if not image_paths:
        print(f"[!] Tidak ada file PNG untuk OCR di: {output_dir}")
        return 1

    configure_tesseract()
    result_dir = os.path.join(output_dir, "ocr_results")
    os.makedirs(result_dir, exist_ok=True)
    report_path = os.path.join(result_dir, "hasil_ocr.csv")

    with open(report_path, "w", newline="", encoding="utf-8-sig") as report:
        writer = csv.DictWriter(report, fieldnames=("file", "teks_ocr", "validasi"))
        writer.writeheader()
        for image_path in image_paths:
            label_name = os.path.splitext(os.path.basename(image_path))[0]
            try:
                text = ocr_image(image_path)
            except Exception as error:
                print(f"[X] {label_name}: {error}")
                text = ""

            with open(os.path.join(result_dir, f"{label_name}.txt"), "w", encoding="utf-8") as text_file:
                text_file.write(text)

            if not text:
                status = "KOSONG / GAGAL"
            elif label_name not in EXPECTED_TEXT:
                status = "TIDAK DIATUR"
            elif validate_against_label(label_name, text):
                status = "COCOK"
            else:
                status = "TIDAK COCOK"

            writer.writerow({"file": os.path.basename(image_path), "teks_ocr": text, "validasi": status})
            print(f"[{status}] {label_name}: {text or '(tidak ada teks)'}")

    print(f"\n[OK] Laporan OCR: {report_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_batch())
    except RuntimeError as error:
        print(f"[X] {error}")
        sys.exit(1)