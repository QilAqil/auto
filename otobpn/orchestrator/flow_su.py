"""Alur satu putaran Surat Ukur (tab DETIL)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from otobpn.actions.daftar_isian import aksi_satu_kolom
from otobpn.actions.detail import aksi_detail_lain
from otobpn.actions.field import AksiField
from otobpn.actions.pejabat import aksi_pejabat
from otobpn.config_loader import get_delay, langkah_aktif
from otobpn.domain.guards import RantaiLangkah
from otobpn.domain.models import HasilLangkah, KolomDI, elemen_dari


def satu_putaran_su(
    field: AksiField,
    cfg: dict[str, Any],
    log: Callable[[str], None],
    harus_jalan: Callable[[], bool],
) -> bool:
    """True jika putaran selesai (termasuk langkah yang dilewati)."""
    rantai = RantaiLangkah(harus_jalan, log, wajib_sukses=True)
    if not rantai.jalankan("tab_detil", lambda: _tab_detil(field, cfg)):
        return False
    if not rantai.jalankan("fokus", lambda: _fokus(field)):
        return False
    if langkah_aktif(cfg, "penomoran", True):
        if not rantai.jalankan("penomoran", lambda: _penomoran(field, cfg)):
            return False
    if not rantai.jalankan("pembukuan", lambda: aksi_pejabat(field, cfg, "pembukuan")):
        return False
    if not rantai.jalankan(
        "penerbitan", lambda: aksi_pejabat(field, cfg, "penerbitan_sertifikat")
    ):
        return False
    if not rantai.jalankan("daftar_isian", lambda: _daftar_isian(field, cfg)):
        return False
    if not rantai.jalankan(
        "detail_lain", lambda: aksi_detail_lain(field, cfg.get("detail_lain") or {})
    ):
        return False
    return rantai.semua_sukses()


def _fokus(field: AksiField) -> HasilLangkah:
    field.fokus_form()
    return HasilLangkah(True, "fokus")


def _tab_detil(field: AksiField, cfg) -> HasilLangkah:
    data = (cfg.get("elemen") or {}).get("tab_detil") or {
        "image": "label_tab_detil.png",
        "confidence": 0.75,
    }
    if not data.get("image"):
        return HasilLangkah(True, "tab_detil", dilewati=True)
    field.klik_elemen(elemen_dari("tab_detil", data))
    return HasilLangkah(True, "tab_detil")


def _penomoran(field: AksiField, cfg) -> HasilLangkah:
    pen = cfg.get("penomoran") or {}
    if not pen.get("tanggal_enabled"):
        return HasilLangkah(True, "penomoran", dilewati=True)
    nilai = str(pen.get("tanggal_nilai", "")).strip()
    if not nilai or not pen.get("image"):
        return HasilLangkah(True, "penomoran", dilewati=True)
    field.isi_elemen(elemen_dari("penomoran", pen), nilai, "Tgl Penomoran")
    return HasilLangkah(True, "penomoran")


def _daftar_isian(field: AksiField, cfg) -> HasilLangkah:
    blok = cfg.get("daftar_isian") or {}
    if not blok.get("enabled", True):
        return HasilLangkah(True, "daftar_isian", dilewati=True)
    for raw in blok.get("kolom") or []:
        hasil = aksi_satu_kolom(field, cfg, KolomDI.from_dict(raw))
        if not hasil.sukses:
            return hasil
        time.sleep(get_delay(cfg, "antar_field", 0.2))
    return HasilLangkah(True, "daftar_isian")
