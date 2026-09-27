# PyInstaller --onedir untuk OTOBPN Detil v7
#   pyinstaller build.spec
# Output: dist/otobpn_detil/otobpn_detil.exe  (+ folder _internal)

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

HERE = os.path.dirname(os.path.abspath(SPEC))  # noqa: F821

datas = [
    (os.path.join(HERE, "assets"), "assets"),
    (os.path.join(HERE, "config.yaml"), "."),
]
ocr_dir = os.path.join(HERE, "ocr_models")
if os.path.isdir(ocr_dir):
    datas.append((ocr_dir, "ocr_models"))

hiddenimports = [
    "otobpn",
    "otobpn.gui.app",
    "otobpn.orchestrator.runner",
    "otobpn.screen.pyautogui_adapter",
    "otobpn.vision.locator",
    "otobpn.vision.ocr",
    "otobpn.vision.preprocessor",
    "pyautogui",
    "pyperclip",
    "pyscreeze",
    "PIL",
    "PIL._tkinter_finder",
    "yaml",
    "keyboard",
    "cv2",
    "numpy",
]

a = Analysis(
    scripts=[os.path.join(HERE, "run_app.py")],
    pathex=[HERE],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["torch", "torchvision", "pandas", "scipy", "sklearn", "matplotlib"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="otobpn_detil",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="otobpn_detil",
)
