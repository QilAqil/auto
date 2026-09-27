@echo off
setlocal
title Install Python untuk BPN Cropper

echo ============================================
echo   INSTALL PYTHON OTOMATIS
echo ============================================
echo.

:: Cek apakah sudah ada Python
python --version >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Python sudah terinstal:
    python --version
    echo.
    pause
    exit /b 0
)

echo [!] Python belum terinstal. Mulai download...
echo.

:: Set versi Python
set PYVER=3.12.7
set PYFILE=python-%PYVER%-amd64.exe
set PYURL=https://www.python.org/ftp/python/%PYVER%/%PYFILE%
set PYPATH=%TEMP%\%PYFILE%

:: Download pakai PowerShell
echo [1/3] Mendownload Python %PYVER%...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYPATH%'}"

if not exist "%PYPATH%" (
    echo [X] Gagal download. Cek koneksi internet.
    pause
    exit /b 1
)

echo [2/3] Menginstall Python (silent)...
"%PYPATH%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1

echo [3/3] Menunggu instalasi selesai...
timeout /t 10 /nobreak >nul

:: Refresh PATH untuk sesi ini
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"

echo.
echo [OK] Python terinstal!
python --version
echo.
echo Silakan jalankan setup.bat selanjutnya.
pause