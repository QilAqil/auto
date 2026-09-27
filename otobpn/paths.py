"""Lokasi berkas runtime (script, PyInstaller onedir, atau frozen)."""

from __future__ import annotations

import os
import sys


def base_path() -> str:
    """Folder kerja: di samping .exe (frozen) atau folder proyek."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # paket otobpn/ ada di dalam repo; config berada di root proyek
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    return parent if os.path.isdir(parent) else here


def config_path(nama: str = "config.yaml") -> str:
    return os.path.join(base_path(), nama)


def assets_dir() -> str:
    return os.path.join(base_path(), "assets")


def log_path(nama: str = "laporan_proses.txt") -> str:
    return os.path.join(base_path(), nama)


def state_path(nama: str = "state_resume.json") -> str:
    return os.path.join(base_path(), nama)


def bundled_ocr_dir() -> str:
    """Folder model EasyOCR yang ikut di-bundle PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "ocr_models")  # type: ignore[attr-defined]
    return os.path.join(base_path(), "ocr_models")
