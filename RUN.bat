@echo off
cd /d "%~dp0"
py run_app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Gagal menjalankan. Pasang Python 3.11+ dan: pip install -r requirements.txt
    echo.
    pause
)
