"""Simpan/muat titik lanjut putaran terakhir (tanpa akses layar)."""

from __future__ import annotations

import json
import os
from typing import Any


def muat_state(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {"su_putaran": 0, "bt_putaran": 0, "mode": ""}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {"su_putaran": 0, "bt_putaran": 0, "mode": ""}


def simpan_state(path: str, data: dict[str, Any]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def reset_state(path: str) -> None:
    simpan_state(path, {"su_putaran": 0, "bt_putaran": 0, "mode": ""})
