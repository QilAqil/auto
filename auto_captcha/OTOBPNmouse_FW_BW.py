import cv2
import numpy as np
import pyautogui
import easyocr
import keyboard
import time
import threading
from pynput import mouse

# Optimasi Kecepatan PyAutoGUI
pyautogui.PAUSE = 0.01

print_lock = threading.Lock()

def log(message="", end="\n"):
    with print_lock:
        print(message, end=end, flush=True)

log("Memuat AI EasyOCR ke dalam memori... (Mohon tunggu sebentar)")
reader = easyocr.Reader(['en'], gpu=False)

# Cache lokasi terakhir anchor form
last_anchor_loc = None
last_anchor_type = None

def process_captcha():
    global last_anchor_loc, last_anchor_type
    log("\n[Forward Ditekan (Mouse/F2)] Memulai proses...")
    
    box_location = None
    anchor_type = None
    
    # ==================================================
    # 1. MENCARI ANCHOR (DENGAN CACHE & 2 ALTERNATIF GAMBAR)
    # ==================================================
    
    # Coba cari di sekitar lokasi terakhir terlebih dahulu untuk kecepatan maksimal
    if last_anchor_loc is not None:
        anchor_x, anchor_y, anchor_w, anchor_h = last_anchor_loc
        region = (max(0, int(anchor_x - 100)), max(0, int(anchor_y - 100)), int(anchor_w + 200), int(anchor_h + 200))
        
        try:
            if last_anchor_type == 'kosong':
                box_location = pyautogui.locateOnScreen('input_box.png', confidence=0.8, region=region)
                if box_location is not None:
                    anchor_type = 'kosong'
            elif last_anchor_type == 'terisi':
                box_location = pyautogui.locateOnScreen('teks_enter_captcha.png', confidence=0.7, grayscale=True, region=region)
                if box_location is not None:
                    anchor_type = 'terisi'
        except Exception:
            box_location = None

    # Jika tidak ketemu di area cache atau cache kosong, cari di seluruh layar
    if box_location is None:
        # Alternatif 1: Cari form dalam keadaan KOSONG ('input_box.png')
        try:
            box_location = pyautogui.locateOnScreen('input_box.png', confidence=0.8)
            if box_location is not None:
                anchor_type = 'kosong'
        except pyautogui.ImageNotFoundException:
            pass

        # Alternatif 2: Cari form TERISI ('teks_enter_captcha.png')
        if box_location is None:
            try:
                box_location = pyautogui.locateOnScreen('teks_enter_captcha.png', confidence=0.7, grayscale=True)
                if box_location is not None:
                    anchor_type = 'terisi'
            except pyautogui.ImageNotFoundException:
                pass
    
    # ==================================================
    # 2. EKSEKUSI PEMOTONGAN & PEMBACAAN JIKA ANCHOR DITEMUKAN
    # ==================================================
    if box_location is not None:
        # Simpan lokasi dan tipe anchor ke cache
        last_anchor_loc = box_location
        last_anchor_type = anchor_type
        
        input_left, input_top, input_width, input_height = box_location
        
        # --- PENYESUAIAN KOORDINAT BERDASARKAN JENIS ANCHOR ---
        if anchor_type == 'kosong':
            log("[Deteksi] Menggunakan patokan 1: Kotak Kosong")
            captcha_x = int(input_left) + 5
            captcha_y = int(input_top) - 100 
            
            # Titik klik pas di tengah form besar
            click_x = input_left + (input_width / 2)
            click_y = input_top + (input_height / 2)
            
        elif anchor_type == 'terisi':
            log("[Deteksi] Menggunakan patokan 2: Teks 'Enter captcha' Kecil")
            captcha_x = int(input_left) - 10 
            captcha_y = int(input_top) - 95 
            
            # Titik klik diturunkan sedikit dari teks kecil agar masuk area ketik
            click_x = input_left + 20
            click_y = input_top + 30 
        
        # Area potong CAPTCHA
        captcha_w = 200 
        captcha_h = 80  
        captcha_region = (captcha_x, captcha_y, captcha_w, captcha_h)
        
        # --- BACA GAMBAR ---
        screenshot = pyautogui.screenshot(region=captcha_region)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Filter HSV
        img_resized = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        
        # Konfigurasi pre-processing yang dicoba (Urutan dioptimalkan berdasarkan hasil benchmark offline)
        # Mendahulukan metode biner yang terbukti memiliki akurasi spasial tertinggi
        configs = [
            {"type": "binary", "sat_thresh": 25, "dilate": False},
            {"type": "binary", "sat_thresh": 20, "dilate": True},
            {"type": "binary", "sat_thresh": 15, "dilate": True},
            {"type": "binary", "sat_thresh": 30, "dilate": False},
            {"type": "gray_inv_enhanced"},
        ]
        
        captcha_text = ""
        best_fallback_text = ""
        
        for idx, config in enumerate(configs):
            if config["type"] == "gray_inv_enhanced":
                # 1. CLAHE untuk meratakan kontras saturasi warna
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                sat_clahe = clahe.apply(saturation)
                
                # 2. Normalisasi
                sat_norm = cv2.normalize(sat_clahe, None, 0, 255, cv2.NORM_MINMAX)
                
                # 3. Inversi (Karakter gelap di atas background putih)
                gray_inv = 255 - sat_norm
                
                # 4. Bilateral filter untuk denoising tanpa merusak tepi
                filtered = cv2.bilateralFilter(gray_inv, 5, 50, 50)
                
                # 5. Sharpening menggunakan kernel 2D untuk mempertegas siku/sudut karakter
                kernel_sharpening = np.array([[-1,-1,-1], 
                                              [-1, 9,-1], 
                                              [-1,-1,-1]])
                proc = cv2.filter2D(filtered, -1, kernel_sharpening)
                
            elif config["type"] == "gray_inv":
                sat_norm = cv2.normalize(saturation, None, 0, 255, cv2.NORM_MINMAX)
                proc = 255 - sat_norm
                
            else:
                sat_thresh = config["sat_thresh"]
                use_dilate = config["dilate"]
                
                _, thresh = cv2.threshold(saturation, sat_thresh, 255, cv2.THRESH_BINARY)
                
                if use_dilate:
                    kernel = np.ones((2, 2), np.uint8)
                    thresh = cv2.dilate(thresh, kernel, iterations=1)
                
                # Pembersihan noise kecil
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    if cv2.contourArea(cnt) < 40:
                        cv2.drawContours(thresh, [cnt], -1, 0, -1)
                proc = thresh
            
            # Ekstraksi Teks dengan EasyOCR
            result = reader.readtext(
                proc, 
                detail=0, 
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                adjust_contrast=True,
                text_threshold=0.7,
                mag_ratio=1.0
            )
            
            text = "".join(result).replace(" ", "").strip().upper()
            
            if len(text) == 6:
                captcha_text = text
                log(f"[OCR Sukses] Mencoba config-{idx+1} ({config['type']}) -> Hasil: '{captcha_text}' (Cocok 6 karakter)")
                break
            else:
                if len(text) > 0 and not best_fallback_text:
                    best_fallback_text = text
                    log(f"[OCR Simpan Sementara] Mencoba config-{idx+1} ({config['type']}) -> Hasil: '{text}' (Panjang {len(text)})")
                else:
                    log(f"[OCR Info] Mencoba config-{idx+1} ({config['type']}) -> Hasil: '{text}'")

        # Jika tidak ditemukan yang tepat 6 karakter, gunakan hasil pembacaan terbaik yang ada
        if not captcha_text:
            captcha_text = best_fallback_text
            
        log(f"---> Hasil bacaan akhir: '{captcha_text}'")
        
        # # ==================================================
        # # 2.5 SIMPAN GAMBAR UNTUK BENCHMARK & EVALUASI AKURASI (FOLDER BARU V2)
        # # ==================================================
        # try:
        #     import os
        #     os.makedirs('captcha_samples_v2', exist_ok=True)
        #     timestamp = int(time.time())
        #     filename = f"captcha_samples_v2/{timestamp}_{captcha_text or 'gagal'}.png"
        #     cv2.imwrite(filename, img)
        #     log(f"[Dataset] Gambar disimpan untuk evaluasi: {filename}")
        # except Exception as e:
        #     log(f"[Dataset Warning] Gagal menyimpan gambar: {e}")
            
        if captcha_text:
            # ==================================================
            # 3. KLIK, TRIPLE CLICK UNTUK SELEKSI & KETIK
            # ==================================================
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            
            # Triple-click untuk menyeleksi/menghapus karakter lama secara andal
            pyautogui.click(click_x, click_y, clicks=3, interval=0.08)
            time.sleep(0.05)
            
            pyautogui.write(captcha_text)
            log("[Sukses] Teks diketik.")
        else:
            log("GAGAL: Teks tidak terbaca. Silakan klik Refresh [2] dan tekan F4 lagi.")
            
    else:
        log("GAGAL: Kedua gambar patokan (Kosong/Terisi) tidak terlihat di layar.")
        log("Pastikan bagian input form tidak tertutup jendela lain.")

def click_checkbox_and_back():
    log("\n[Backward Ditekan (Mouse/F3)] Memulai aksi klik...")

    # ==================================================
    # 1. CARI DAN KLIK CHECKBOX
    # ==================================================
    log("-> Mencari gambar checkbox...")
    try:
        # Menggunakan grayscale=True karena checkbox didominasi warna abu-abu/putih
        checkbox_loc = pyautogui.locateCenterOnScreen('checkbox.png', confidence=0.8, grayscale=True)
        
        if checkbox_loc is not None:
            pyautogui.click(checkbox_loc)
            log("✅ [Sukses] Checkbox berhasil diklik!")
            time.sleep(0.2) # Jeda setengah detik sebelum lanjut
            
            # ==================================================
            # 2. CARI DAN KLIK TOMBOL KEMBALI (HANYA DIEKSEKUSI JIKA CHECKBOX KETEMU)
            # ==================================================
            log("-> Mencari tombol kembali hijau...")
            try:
                # Tombol hijau dicari tanpa grayscale
                btn_kembali_loc = pyautogui.locateCenterOnScreen('back_button.png', confidence=0.8)
                
                if btn_kembali_loc is not None:
                    pyautogui.click(btn_kembali_loc)
                    log("✅ [Sukses] Tombol Kembali berhasil diklik!")
                else:
                    log("❌ [Gagal] Gambar 'back_button.png' tidak terlihat di layar.")
                    
            except pyautogui.ImageNotFoundException:
                log("❌ [Error] File 'back_button.png' tidak ditemukan di dalam folder Anda.")
                
        else:
            # JIKA CHECKBOX TIDAK KETEMU, STOP SAMPAI DI SINI
            log("❌ [Gagal] Gambar 'checkbox.png' tidak terlihat. Eksekusi tombol kembali dibatalkan.")
            
    except pyautogui.ImageNotFoundException:
        log("❌ [Error] File 'checkbox.png' tidak ditemukan. Eksekusi tombol kembali dibatalkan.")
        
def main():
    log("\n=====================================================")
    log("SKRIP AUTO-FILL CAPTCHA & AUTO-KLIK CHECKBOX FINAL SIAP!")
    log("Tekan tombol mouse Forward (X2) atau tombol F2 untuk membaca & mengisi otomatis.")
    log("Tekan tombol mouse Backward (X1) atau tombol F3 untuk klik checkbox dan tombol kembali.")
    log("- Tombol Keluar: ESC (pada keyboard)")
    
    def on_click(x, y, button, pressed):
        if pressed:
            if button == mouse.Button.x2:
                threading.Thread(target=process_captcha, daemon=True).start()
            elif button == mouse.Button.x1:
                threading.Thread(target=click_checkbox_and_back, daemon=True).start()

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    # Daftarkan hotkey keyboard F2 dan F3
    keyboard.add_hotkey('f2', lambda: threading.Thread(target=process_captcha, daemon=True).start())
    keyboard.add_hotkey('f3', lambda: threading.Thread(target=click_checkbox_and_back, daemon=True).start())
    
    # Tunggu tombol ESC ditekan
    keyboard.wait('esc')
    
    # Bersihkan hotkey dan listener
    keyboard.unhook_all()
    listener.stop()
    log("Program dimatikan.")

if __name__ == "__main__":
    main()