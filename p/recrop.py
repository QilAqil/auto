"""
Re-crop 1 label saja. Usage: python recrop.py <nama_label>
Contoh: python recrop.py label_di_303
"""

import json, os, sys
import cv2
from PIL import Image
import pyautogui

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    CFG = json.load(f)

OUT_DIR = os.path.join(BASE_DIR, CFG["output_dir"])
SHOT_DIR = os.path.join(BASE_DIR, CFG["screenshot_dir"])


def cari_label(name):
    for tab_key, tab in CFG["tabs"].items():
        for lbl in tab["labels"]:
            if lbl["name"] == name:
                return tab_key, lbl
    return None, None


def shot_terakhir(tag):
    files = sorted([f for f in os.listdir(SHOT_DIR)
                    if f.startswith(f"{tag}_") and f.endswith(".png")],
                   reverse=True)
    return os.path.join(SHOT_DIR, files[0]) if files else None


def main():
    if len(sys.argv) < 2:
        print("Usage: python recrop.py <nama_label>"); sys.exit(1)
    name = sys.argv[1]
    tab_key, label = cari_label(name)
    if not label:
        print(f"[X] Label '{name}' tidak ada di config.json"); sys.exit(1)

    shot = shot_terakhir(tab_key)
    if not shot:
        print(f"[X] Screenshot {tab_key} tidak ada. Jalankan capture.py dulu.")
        sys.exit(1)

    print(f"[OK] Tab: {tab_key} | Label: {name} | W={label['w']} H={label['h']}")
    print(f"[OK] Gambar: {shot}")
    print("Klik tengah label, ENTER = OK, ESC = batal.")

    img = cv2.imread(shot)
    h, w = img.shape[:2]
    scale = min(1.0, 1600 / w)
    disp = cv2.resize(img, (int(w*scale), int(h*scale)))
    clicked = {"xy": None}

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            clicked["xy"] = (int(x/scale), int(y/scale))
            d = disp.copy()
            cx, cy = clicked["xy"]
            lw, lh = label["w"], label["h"]
            l = int((cx-lw/2)*scale); t = int((cy-lh/2)*scale)
            r = int((cx+lw/2)*scale); b = int((cy+lh/2)*scale)
            cv2.rectangle(d, (l, t), (r, b), (0, 255, 0), 2)
            # titik klik aktual
            kx = int((cx + label.get("offset_x", 0)) * scale)
            ky = int((cy + label.get("offset_y", 0)) * scale)
            cv2.drawMarker(d, (kx, ky), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
            cv2.imshow(win, d)

    win = f"Re-crop: {name}"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, on_mouse)
    cv2.imshow(win, disp)

    while True:
        k = cv2.waitKey(20) & 0xFF
        if k == 13 and clicked["xy"]: break
        if k == 27:
            print("[!] Dibatalkan."); cv2.destroyWindow(win); return
    cv2.destroyWindow(win)

    pil = Image.open(shot)
    cx, cy = clicked["xy"]
    lw, lh = label["w"], label["h"]
    crop = pil.crop((int(cx-lw/2), int(cy-lh/2),
                     int(cx-lw/2)+lw, int(cy-lh/2)+lh))
    out = os.path.join(OUT_DIR, f"{name}.png")
    crop.save(out)
    print(f"[OK] Tersimpan: {out} ({crop.width}×{crop.height})")


if __name__ == "__main__":
    main()