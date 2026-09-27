"""Alur satu putaran Buku Tanah (tab DETIL)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from otobpn.actions.daftar_isian import aksi_satu_kolom
from otobpn.actions.detail import aksi_petunjuk_bt
from otobpn.actions.field import AksiField
from otobpn.actions.pejabat import aksi_pejabat
from otobpn.config_loader import get_delay
from otobpn.domain.guards import RantaiLangkah
from otobpn.domain.models import HasilLangkah, KolomDI


def satu_putaran_bt(
    field: AksiField,
    cfg: dict[str, Any],
    log: Callable[[str], None],
    harus_jalan: Callable[[], bool],
) -> bool:
    rantai = RantaiLangkah(harus_jalan, log, wajib_sukses=True)
    if not rantai.jalankan("fokus", lambda: _fokus(field)):
        return False
    if not rantai.jalankan(
        "pembukuan_bt", lambda: aksi_pejabat(field, cfg, "pembukuan_bt")
    ):
        return False
    if not rantai.jalankan(
        "penerbitan_bt",
        lambda: aksi_pejabat(field, cfg, "penerbitan_sertifikat_bt"),
    ):
        return False
    if not rantai.jalankan("daftar_isian_bt", lambda: _daftar_isian_bt(field, cfg)):
        return False
    if not rantai.jalankan("petunjuk_bt", lambda: aksi_petunjuk_bt(field, cfg)):
        return False
    return rantai.semua_sukses()


def _fokus(field: AksiField) -> HasilLangkah:
    field.fokus_form()
    return HasilLangkah(True, "fokus")


def _daftar_isian_bt(field: AksiField, cfg: dict[str, Any]) -> HasilLangkah:
    blok = (cfg.get("bt") or {}).get("daftar_isian") or {}
    if not blok.get("enabled", True):
        return HasilLangkah(True, "daftar_isian_bt", dilewati=True)
    for raw in blok.get("kolom") or []:
        hasil = aksi_satu_kolom(field, cfg, KolomDI.from_dict(raw))
        if not hasil.sukses:
            return hasil
        time.sleep(get_delay(cfg, "antar_field", 0.2))
    return HasilLangkah(True, "daftar_isian_bt")
