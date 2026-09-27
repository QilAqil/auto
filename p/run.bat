@echo off
setlocal
title BPN Cropper - Running

cd /d "%~dp0"

:: Cek Python
python --version >nul 2>&1
if not %errorlevel%==0 (
    echo [X] Python tidak ditemukan. Jalankan install_python.bat dulu.
    pause
    exit /b 1
)

:: Cek venv
if not exist "venv\Scripts\activate.bat" (
    echo [!] Setup belum dijalankan. Menjalankan setup.bat dulu...
    call setup.bat
    if not exist "venv\Scripts\activate.bat" (
        echo [X] Setup gagal.
        pause
        exit /b 1
    )
)

:: Aktifkan venv
call venv\Scripts\activate.bat

echo.
echo Pilih proses:
echo   1. Capture / crop screenshot
echo   2. OCR hasil crop yang sudah ada
echo   3. Buat ulang crop otomatis dari screenshot terbaru
set /p PILIH=Pilihan [1]:
if "%PILIH%"=="2" goto OCR
if "%PILIH%"=="3" goto AUTO_CROP
if not "%PILIH%"=="" if not "%PILIH%"=="1" (
    echo [X] Pilihan tidak dikenal.
    pause
    exit /b 1
)

:: Jalankan capture
cls
python capture.py
goto SELESAI

:OCR
cls
python validate.py
goto SELESAI

:AUTO_CROP
cls
python auto_crop.py

:SELESAI

:: Tahan window agar tidak langsung close
echo.
echo ============================================
echo   Proses selesai.
echo ============================================
pause