"""Isi satu kolom Daftar Isian: temukan label DI, lalu offset nomor/tahun/tanggal."""

from __future__ import annotations

from typing import Any

from otobpn.actions.field import AksiField
from otobpn.domain.models import ElemenUI, HasilLangkah, KolomDI


def aksi_satu_kolom(
    field: AksiField, cfg: dict[str, Any], kolom: KolomDI
) -> HasilLangkah:
    if not kolom.enabled:
        return HasilLangkah(True, kolom.id, dilewati=True)
    if not kolom.image:
        field.log(f"  [{kolom.id}] tidak ada aset PNG")
        return HasilLangkah(True, kolom.id, dilewati=True)
    off = cfg.get("di_offset", {}) or {}
    el = ElemenUI(
        nama=kolom.id,
        mode="image",
        image=kolom.image,
        confidence=float(cfg.get("locator", {}).get("confidence", 0.75)),
        offset_y=int(off.get("offset_y", 0)),
    )
    try:
        x, y = field.temukan(el)
    except Exception as exc:  # noqa: BLE001
        return HasilLangkah(False, kolom.id, pesan=str(exc))
    field.log(f"  [{kolom.id}] aset {kolom.image}")
    field._paste_di(x + int(off.get("nomor", 110)), y, kolom.nomor, "Nomor")
    field._paste_di(x + int(off.get("tahun", 250)), y, kolom.tahun, "Tahun")
    field._paste_di(x + int(off.get("tanggal", 370)), y, kolom.tanggal, "Tanggal")
    return HasilLangkah(True, kolom.id)
