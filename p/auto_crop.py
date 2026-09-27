"""Regenerate small label templates from the latest full screenshots."""

import csv
import glob
import json
import os
import re
import sys

from PIL import Image, ImageOps
import pytesseract
from pytesseract import Output

from validate import configure_tesseract

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OCR_SCALE = 2
OCR_CONFIG = "--oem 3 --psm 6"

LABEL_PATTERNS = {
    "label_di_301": (("di", "301"), ("di301",), ("d1301",)),
    "label_di_303": (("di", "303"), ("di303",), ("d1303",)),
    "label_tab_detil": (("detil",),),
    "label_tgl_penomoran": (("tgl", "penomoran"), ("penomoran",)),
    "label_pembukuan_tanggal": (("tanggal",),),
    "label_penerbitan_tanggal": (("tanggal",),),
    "label_pembukuan_bt_tanggal": (("tanggal",),),
    "label_penerbitan_bt_tanggal": (("tanggal",),),
    "label_pembukuan_jabatan": (("jabatan",),),
    "label_penerbitan_jabatan": (("jabatan",),),
    "label_pembukuan_bt_jabatan": (("jabatan",),),
    "label_penerbitan_bt_jabatan": (("jabatan",),),
    "label_pembukuan_nama": (("nama",),),
    "label_penerbitan_nama": (("nama",),),
    "label_pembukuan_bt_nama": (("nama",),),
    "label_penerbitan_bt_nama": (("nama",),),
    "label_keadaan_tanah": (("keadaan", "tanah"),),
    "label_tanda_batas": (("tanda", "tanda", "batas"), ("tanda", "batas")),
    "label_pengukuran": (("penunjukan",),),
    "label_hal_lain": (("hal", "lain", "lain"), ("hal", "lain")),
    "label_petunjuk_bt": (("penunjuk",), ("petunjuk",)),
}


def normalize_word(text):
    return re.sub(r"[^a-z0-9]", "", text.casefold())


def latest_screenshot(tag):
    paths = glob.glob(os.path.join(BASE_DIR, "screenshots", f"{tag}_full_*.png"))
    return max(paths, key=os.path.basename) if paths else None


def read_ocr_lines(image_path):
    with Image.open(image_path) as image:
        original_width, original_height = image.size
        processed = ImageOps.autocontrast(image.convert("L"))
        processed = processed.resize(
            (original_width * OCR_SCALE, original_height * OCR_SCALE),
            Image.Resampling.LANCZOS,
        )
        data = pytesseract.image_to_data(
            processed,
            lang="ind+eng",
            config=OCR_CONFIG,
            output_type=Output.DICT,
        )

    lines = {}
    for index, text in enumerate(data["text"]):
        normalized = normalize_word(text)
        if not normalized:
            continue
        key = (
            data["block_num"][index],
            data["par_num"][index],
            data["line_num"][index],
        )
        lines.setdefault(key, []).append(
            {
                "text": normalized,
                "left": data["left"][index] / OCR_SCALE,
                "top": data["top"][index] / OCR_SCALE,
                "width": data["width"][index] / OCR_SCALE,
                "height": data["height"][index] / OCR_SCALE,
                "confidence": float(data["conf"][index]),
            }
        )
    return original_width, original_height, list(lines.values())


def page_matches_tab(lines, tab_key):
    words = [word["text"] for line in lines for word in line]
    if tab_key == "su":
        return any(words[index:index + 2] == ["surat", "ukur"] for index in range(len(words) - 1))
    return any(words[index:index + 2] == ["buku", "tanah"] for index in range(len(words) - 1))


def find_matches(label_name, lines):
    patterns = LABEL_PATTERNS.get(label_name)
    if not patterns:
        return []

    matches = []
    for line in lines:
        line.sort(key=lambda word: word["left"])
        for pattern in patterns:
            for start in range(len(line) - len(pattern) + 1):
                words = line[start:start + len(pattern)]
                if tuple(word["text"] for word in words) != pattern:
                    continue
                if min(word["confidence"] for word in words) < 20:
                    continue
                left = min(word["left"] for word in words)
                top = min(word["top"] for word in words)
                right = max(word["left"] + word["width"] for word in words)
                bottom = max(word["top"] + word["height"] for word in words)
                if label_name.endswith(("_tanggal", "_jabatan", "_nama")):
                    if left < 1000 or top < 600:
                        continue
                matches.append(
                    {
                        "x": (left + right) / 2,
                        "y": (top + bottom) / 2,
                        "phrase": " ".join(word["text"] for word in words),
                    }
                )

    matches.sort(key=lambda match: (match["y"], match["x"]))
    unique = []
    for match in matches:
        if not any(abs(match["x"] - item["x"]) < 10 and abs(match["y"] - item["y"]) < 10 for item in unique):
            unique.append(match)
    return unique


def save_crop(image_path, output_path, center, width, height):
    with Image.open(image_path) as image:
        left = round(center[0] - width / 2)
        top = round(center[1] - height / 2)
        box = (
            max(0, left),
            max(0, top),
            min(image.width, left + width),
            min(image.height, top + height),
        )
        image.crop(box).save(output_path)


def run():
    configure_tesseract()
    with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as file:
        config = json.load(file)

    output_dir = os.path.join(BASE_DIR, config["output_dir"])
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "auto_crop_report.csv")
    rows = []
    created = set()

    for tab_key, tab in config["tabs"].items():
        screenshot = latest_screenshot(tab_key)
        if not screenshot:
            print(f"[X] Screenshot {tab_key.upper()} tidak ditemukan.")
            rows.append({"tab": tab_key, "screenshot": "", "label": "*", "status": "SCREENSHOT TIDAK ADA"})
            continue

        width, height, lines = read_ocr_lines(screenshot)
        if not page_matches_tab(lines, tab_key):
            print(f"[X] {os.path.basename(screenshot)} bukan halaman {tab_key.upper()} yang dikenali; dilewati.")
            rows.append(
                {
                    "tab": tab_key,
                    "screenshot": os.path.basename(screenshot),
                    "label": "*",
                    "status": "HALAMAN TIDAK COCOK",
                }
            )
            continue

        print(f"[OK] Screenshot {tab_key.upper()}: {os.path.basename(screenshot)} ({width}x{height})")
        labels = tab["labels"]
        grouped_matches = {}
        for label in labels:
            if label["name"] in LABEL_PATTERNS:
                grouped_matches[label["name"]] = find_matches(label["name"], lines)
        section_anchors = sorted(
            {
            match["y"]
            for label in labels
            if label["name"].endswith("_jabatan")
            for match in grouped_matches.get(label["name"], [])
            }
        )

        for label in labels:
            name = label["name"]
            if name.endswith("_item"):
                status = "PERLU SCREENSHOT DROPDOWN TERBUKA"
                match = None
            elif name.endswith("_centang"):
                status = "PERLU LOCATOR CHECKBOX"
                match = None
            elif name not in LABEL_PATTERNS:
                status = "TIDAK ADA ATURAN OCR"
                match = None
            else:
                matches = grouped_matches[name]
                patterns = LABEL_PATTERNS[name]
                occurrence = sum(
                    LABEL_PATTERNS.get(item["name"]) == patterns
                    for item in labels[:labels.index(label)]
                )
                if name.endswith(("_tanggal", "_nama")) and section_anchors:
                    section_matches = [
                        candidate
                        for candidate in matches
                        if min(
                            range(len(section_anchors)),
                            key=lambda index: abs(candidate["y"] - section_anchors[index]),
                        ) == occurrence
                        and min(abs(candidate["y"] - anchor) for anchor in section_anchors) <= 80
                    ]
                    match = min(
                        section_matches,
                        key=lambda candidate: abs(candidate["y"] - section_anchors[occurrence]),
                        default=None,
                    ) if occurrence < len(section_anchors) else None
                else:
                    match = matches[occurrence] if occurrence < len(matches) else None
                status = "DIBUAT" if match else "TEKS TIDAK DITEMUKAN"

            if match and name in created:
                status = "SUDAH DIBUAT DARI SCREENSHOT LAIN"
            elif match:
                output_path = os.path.join(output_dir, f"{name}.png")
                save_crop(screenshot, output_path, (match["x"], match["y"]), label["w"], label["h"])
                created.add(name)
                print(f"  [OK] {name}.png ({label['w']}x{label['h']}) dari '{match['phrase']}'")
            else:
                print(f"  [--] {name}: {status}")

            rows.append(
                {
                    "tab": tab_key,
                    "screenshot": os.path.basename(screenshot),
                    "label": name,
                    "status": status,
                    "x": round(match["x"]) if match else "",
                    "y": round(match["y"]) if match else "",
                    "width": label["w"],
                    "height": label["h"],
                }
            )

    with open(report_path, "w", newline="", encoding="utf-8-sig") as report:
        fields = ("tab", "screenshot", "label", "status", "x", "y", "width", "height")
        writer = csv.DictWriter(report, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[OK] {len(created)} template dibuat; laporan: {report_path}")
    return 0 if created else 1


if __name__ == "__main__":
    try:
        sys.exit(run())
    except RuntimeError as error:
        print(f"[X] {error}")
        sys.exit(1)