"""Isi panel pejabat: tanggal, centang, jabatan, nama — via aset PNG."""

from __future__ import annotations

from typing import Any

from otobpn.actions.field import AksiField
from otobpn.domain.models import HasilLangkah, elemen_dari


def aksi_pejabat(field: AksiField, cfg: dict[str, Any], kunci: str) -> HasilLangkah:
    blok = cfg.get(kunci, {}) or {}
    if not blok.get("enabled", False):
        return HasilLangkah(True, kunci, dilewati=True)
    _isi_tanggal(field, blok, kunci)
    _klik_centang(field, blok, kunci)
    _isi_dropdown(field, blok, kunci, "jabatan", str(blok.get("jabatan_teks", "")))
    _isi_dropdown(field, blok, kunci, "nama", str(blok.get("nama_teks", "")))
    return HasilLangkah(True, kunci, pesan="ok")


def _isi_tanggal(field: AksiField, blok: dict, kunci: str) -> None:
    if not blok.get("tanggal_enabled"):
        field.log("    tanggal dilewati")
        return
    nilai = str(blok.get("tanggal_nilai", "")).strip()
    if not nilai:
        field.log("    tanggal dilewati (kosong)")
        return
    field.isi_elemen(elemen_dari(f"{kunci}.tanggal", blok.get("tanggal")), nilai, "tanggal")


def _klik_centang(field: AksiField, blok: dict, kunci: str) -> None:
    if not blok.get("centang_enabled"):
        field.log("    centang dilewati")
        return
    data = blok.get("centang") or {}
    if not data.get("image"):
        field.log("    centang dilewati (tidak ada aset)")
        return
    field.klik_elemen(elemen_dari(f"{kunci}.centang", data))
    field.log(f"    centang {data.get('image')}")


def _isi_dropdown(field: AksiField, blok: dict, kunci: str, prefix: str, teks: str) -> None:
    data = blok.get(prefix) or {}
    if data.get("image") and teks.strip():
        field.isi_elemen(elemen_dari(f"{kunci}.{prefix}", data), teks, prefix)
    data2 = blok.get(f"{prefix}_klik2") or {}
    if data2.get("image"):
        field.klik_elemen(elemen_dari(f"{kunci}.{prefix}_klik2", data2))
        field.log(f"    {prefix} klik2 {data2.get('image')}")
