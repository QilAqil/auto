"""Pemuat dan penyimpan config.yaml — satu sumber kebenaran untuk semua modul."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import yaml

from otobpn.errors import ConfigError
from otobpn.paths import config_path


def load_config(path: str | None = None) -> dict[str, Any]:
    """Baca YAML. Semua modul wajib memakai hasil fungsi ini, bukan path sendiri."""
    berkas = path or config_path()
    try:
        with open(berkas, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError as exc:
        raise ConfigError(f"Config tidak ditemukan: {berkas}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"YAML rusak: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Akar config.yaml harus mapping.")
    return _with_defaults(data)


def save_config(cfg: dict[str, Any], path: str | None = None) -> None:
    """Tulis ulang config. Komentar YAML tidak dipertahankan."""
    berkas = path or config_path()
    with open(berkas, "w", encoding="utf-8") as f:
        yaml.dump(
            cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def get_delay(cfg: dict[str, Any], key: str, default: float) -> float:
    """Ambil jeda dari cfg['delay'] dengan fallback aman."""
    try:
        return float(cfg.get("delay", {}).get(key, default))
    except (TypeError, ValueError):
        return default


def langkah_aktif(cfg: dict[str, Any], nama: str, default: bool = True) -> bool:
    """Cek enable/disable langkah di cfg['langkah']."""
    blok = cfg.get("langkah", {})
    if not isinstance(blok, dict):
        return default
    return bool(blok.get(nama, default))


def _with_defaults(data: dict[str, Any]) -> dict[str, Any]:
    """Isi kunci wajib agar modul lain tidak perlu hardcode."""
    cfg = deepcopy(data)
    cfg.setdefault("hotkey", {})
    cfg["hotkey"].setdefault("mulai_su", "\\")
    cfg["hotkey"].setdefault("mulai_bt", "`")
    cfg["hotkey"].setdefault("mulai", "f1")
    cfg["hotkey"].setdefault("jeda_su", "\\")
    cfg["hotkey"].setdefault("jeda_bt", "`")
    cfg["hotkey"].setdefault("reset", "f3")
    cfg["hotkey"].setdefault("exit", "esc")
    cfg.setdefault("delay", {})
    cfg.setdefault("retry", {"max_attempts": 3, "interval_sec": 0.4})
    cfg.setdefault("locator", {})
    cfg.setdefault("ocr", {"enabled": True})
    cfg.setdefault("mode", {})
    cfg["mode"].setdefault("dry_run", False)
    cfg["mode"].setdefault("verify_after_fill", True)
    cfg["mode"].setdefault("resume", True)
    cfg.setdefault("langkah", {})
    return cfg
