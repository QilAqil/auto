"""
BPN Cropper — Template Matching (sesuai panduan crop aset)
- Crop KECIL: hanya teks label
- Offset_x/y: geser dari tengah label ke field
- Preview kotak hijau = area yang akan dicrop
"""

import json
import os
import sys
import time
from datetime import datetime

import cv2
import numpy as np
import pyautogui
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    CFG = json.load(f)

OUT_DIR = os.path.join(BASE_DIR, CFG["output_dir"])
SHOT_DIR = os.path.join(BASE_DIR, CFG["screenshot_dir"])
CAL_PATH = os.path.join(BASE_DIR, "kalibrasi.json")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(SHOT_DIR, exist_ok=True)

# Batas ukuran wajar (panduan)
MAX_W = 240
MAX_H = 40


def countdown(sec=3):
    for i in range(sec, 0, -1):
        print(f"   >> {i}...", end="\r", flush=True)
        time.sleep(1)
    print(" " * 30, end="\r")


def full_screenshot(tag):
    countdown(CFG.get("countdown", 3))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SHOT_DIR, f"{tag}_full_{ts}.png")
    pyautogui.screenshot().save(path)
    print(f"[OK] Screenshot {tag.upper()}: {path}")
    return path


def crop_and_save(image_path, label, cx, cy):
    """Crop dari tengah (cx,cy) dengan w/h label, simpan ke output/."""
    img = Image.open(image_path)
    w, h = label["w"], label["h"]
    left = max(0, int(cx - w / 2))
    top = max(0, int(cy - h / 2))
    right = min(img.width, left + w)
    bottom = min(img.height, top + h)
    crop = img.crop((left, top, right, bottom))
    out = os.path.join(OUT_DIR, f"{label['name']}.png")
    crop.save(out)

    warn = ""
    if w > MAX_W or h > MAX_H:
        warn = " ⚠️ KELEBIHAN (lihat panduan)"
    print(f"   -> {label['name']}.png ({crop.width}×{crop.height}){warn}")
    return out


def pick_center_gui(image_path, label, tab_key):
    """
    GUI klik. Fitur:
      - Klik kiri : set tengah label
      - ENTER     : OK, crop
      - S         : Skip
      - ESC       : Batal semua
      - T         : Auto-detect posisi teks (threshold)
      - +/-       : Perbesar/perkecil w
      - [ / ]     : Perkecil/perbesar h
      - Panah     : Geser offset_x/y
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"[!] Gagal buka {image_path}")
        return None

    h_img, w_img = img.shape[:2]
    scale = min(1.0, 1600 / w_img)
    disp_base = cv2.resize(img, (int(w_img * scale), int(h_img * scale)))

    st = {
        "cx": None, "cy": None,       # tengah label (di koordinat asli)
        "w": label["w"],
        "h": label["h"],
        "ox": label.get("offset_x", 0),
        "oy": label.get("offset_y", 0),
        "result": None,
    }

    win = f"[{tab_key.upper()}] {label['name']} | w={st['w']} h={st['h']} ox={st['ox']} oy={st['oy']}"

    def redraw():
        disp = disp_base.copy()
        if st["cx"] is not None:
            cx, cy = st["cx"], st["cy"]
            # kotak crop (hijau)
            l = int((cx - st["w"] / 2) * scale)
            t = int((cy - st["h"] / 2) * scale)
            r = int((cx + st["w"] / 2) * scale)
            b = int((cy + st["h"] / 2) * scale)
            cv2.rectangle(disp, (l, t), (r, b), (0, 255, 0), 2)

            # titik klik aktual (merah) = tengah label + offset
            kx = int((cx + st["ox"]) * scale)
            ky = int((cy + st["oy"]) * scale)
            cv2.drawMarker(disp, (kx, ky), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)

            # tengah label (biru)
            cv2.circle(disp, (int(cx * scale), int(cy * scale)), 4, (255, 0, 0), -1)

        cv2.putText(disp, f"w={st['w']} h={st['h']} ox={st['ox']} oy={st['oy']}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(disp, "ENTER=OK  S=Skip  ESC=Batal  +/-=w  [/]=h  Arrows=offset",
                    (10, h_img * scale - 10 if h_img * scale < 900 else 880),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.imshow(win, disp)

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            st["cx"] = int(x / scale)
            st["cy"] = int(y / scale)
            redraw()

    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, on_mouse)
    redraw()

    while True:
        k = cv2.waitKey(20) & 0xFF
        if k == 13:  # ENTER
            st["result"] = (st["cx"], st["cy"]) if st["cx"] is not None else None
            break
        elif k in (ord("s"), ord("S")):
            st["result"] = None; break
        elif k == 27:  # ESC
            st["result"] = "ABORT"; break
        elif k in (ord("+"), ord("=")):
            st["w"] += 4; redraw()
        elif k == ord("-"):
            st["w"] = max(8, st["w"] - 4); redraw()
        elif k == ord("]"):
            st["h"] += 2; redraw()
        elif k == ord("["):
            st["h"] = max(8, st["h"] - 2); redraw()
        elif k == 82:  # Up
            st["oy"] -= 4; redraw()
        elif k == 84:  # Down
            st["oy"] += 4; redraw()
        elif k == 81:  # Left
            st["ox"] -= 4; redraw()
        elif k == 83:  # Right
            st["ox"] += 4; redraw()
        elif k == ord("t"):
            # auto-tebak: cari blok teks gelap di sekitar klik terakhir
            if st["cx"] is not None:
                print("   [T] Auto-detect belum diimplementasi penuh.")
        # update title
        cv2.setWindowTitle(win,
            f"[{tab_key.upper()}] {label['name']} | w={st['w']} h={st['h']} "
            f"ox={st['ox']} oy={st['oy']}")

    cv2.destroyWindow(win)

    if st["result"] in (None, "ABORT"):
        return st["result"]

    # Update config in-memory supaya label ini pakai nilai terbaru
    label["w"] = st["w"]
    label["h"] = st["h"]
    label["offset_x"] = st["ox"]
    label["offset_y"] = st["oy"]
    return st["result"]


def load_kalibrasi():
    if os.path.exists(CAL_PATH):
        with open(CAL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_kalibrasi(cal):
    with open(CAL_PATH, "w", encoding="utf-8") as f:
        json.dump(cal, f, indent=2, ensure_ascii=False)


def save_config():
    """Simpan perubahan w/h/offset ke config.json."""
    with open(os.path.join(BASE_DIR, "config.json"), "w", encoding="utf-8") as f:
        json.dump(CFG, f, indent=2, ensure_ascii=False)


def process_tab(tab_key, image_path, mode, cal):
    tab_cfg = CFG["tabs"][tab_key]
    print(f"\n===== {tab_cfg['nama'].upper()} =====")
    total = len(tab_cfg["labels"])

    for idx, label in enumerate(tab_cfg["labels"], 1):
        key = f"{tab_key}.{label['name']}"
        print(f"[{idx}/{total}] {label['name']}  (w={label['w']} h={label['h']})")

        if mode == "full":
            xy = cal.get(key)
            if not xy:
                print("   [skip] belum ada kalibrasi")
                continue
            crop_and_save(image_path, label, xy[0], xy[1])
        else:
            res = pick_center_gui(image_path, label, tab_key)
            if res == "ABORT":
                print("   >> Dibatalkan.\n")
                return False
            if res is None:
                print("   >> Skip.\n")
                continue
            crop_and_save(image_path, label, res[0], res[1])
            cal[key] = list(res)
            save_kalibrasi(cal)  # langsung simpan setiap klik
            print()

    return True


def mode_manual():
    print("\n=== MODE MANUAL ===")
    print("Alur: buka halaman SU → klik tiap label → pindah BT → klik tiap label.\n")
    print("Hotkey di jendela:")
    print("  Klik       : titik tengah label")
    print("  ENTER      : OK, crop & simpan")
    print("  S          : Skip")
    print("  ESC        : Batal")
    print("  + / -      : perbesar / perkecil lebar (w)")
    print("  ] / [      : perbesar / perkecil tinggi (h)")
    print("  ← ↑ ↓ →    : geser offset_x/y")
    print()

    cal = load_kalibrasi()
    nav_cfg = CFG.get("navigasi", {})

    for tab_key in CFG["tabs"].keys():
        nav = nav_cfg.get(tab_key, {})
        print(f"\n{'='*55}")
        print(f"  TAB {tab_key.upper()} — {nav.get('nama', tab_key.upper())}")
        print(f"  Buka: {nav.get('breadcrumb', '-')}")
        print(f"{'='*55}")
        input("► Siap? ENTER untuk screenshot...")
        shot = full_screenshot(tab_key)
        ok = process_tab(tab_key, shot, "manual", cal)
        if not ok:
            break

    # Simpan perubahan config
    save_config()
    print(f"\n=== SELESAI ===")
    print(f"  Hasil       : {OUT_DIR}")
    print(f"  Kalibrasi   : {CAL_PATH}")
    print(f"  Config      : {os.path.join(BASE_DIR, 'config.json')}")


def mode_full():
    cal = load_kalibrasi()
    if not cal:
        print("[!] kalibrasi.json kosong. Jalankan mode MANUAL dulu.")
        return

    print("\n=== MODE FULL (pakai kalibrasi.json) ===")
    nav_cfg = CFG.get("navigasi", {})
    for tab_key in CFG["tabs"].keys():
        nav = nav_cfg.get(tab_key, {})
        print(f"\n► Buka: {nav.get('breadcrumb', '-')}, lalu ENTER...")
        input()
        shot = full_screenshot(tab_key)
        process_tab(tab_key, shot, "full", cal)

    print(f"\n=== SELESAI === Hasil di: {OUT_DIR}")


def main():
    print("=" * 55)
    print("  BPN CROPPER — Template Matching")
    print("=" * 55)
    pilih = input("Mode [1=MANUAL, 2=FULL]: ").strip()
    (mode_manual if pilih in ("1", "") else mode_full)()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Dibatalkan.")
        sys.exit(1)