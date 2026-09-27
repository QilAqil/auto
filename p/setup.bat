@echo off
setlocal enabledelayedexpansion
title Setup BPN Cropper

echo ============================================
echo   SETUP BPN CROPPER
echo ============================================
echo.

:: Pastikan di folder yang benar
cd /d "%~dp0"

:: 1. Cek Python
echo [1/4] Cek Python...
python --version >nul 2>&1
if not %errorlevel%==0 (
    echo [X] Python tidak ditemukan!
    echo.
    echo Jalankan dulu: install_python.bat
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo     %%i

:: 2. Buat virtual environment
echo.
echo [2/4] Membuat virtual environment...
if not exist "venv" (
    python -m venv venv
    if not %errorlevel%==0 (
        echo [X] Gagal buat venv.
        pause
        exit /b 1
    )
    echo     [OK] venv dibuat
) else (
    echo     [OK] venv sudah ada
)

:: 3. Aktifkan venv
echo.
echo [3/4] Aktivasi venv...
call venv\Scripts\activate.bat

:: 4. Install dependencies
echo.
echo [4/4] Install dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if not %errorlevel%==0 (
    echo [X] Gagal install dependencies.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   [OK] SETUP SELESAI!
echo ============================================
echo.
echo Selanjutnya jalankan: run.bat
echo.
pause