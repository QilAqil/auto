"""Detail Lain-Lain SU dan Petunjuk BT — klik via aset PNG."""

from __future__ import annotations

from typing import Any

from otobpn.actions.field import AksiField
from otobpn.domain.models import HasilLangkah, elemen_dari
from otobpn.domain.text_rules import ekstrak_nama_pemohon, gabung_sisip, susun_template

_URUTAN = (
    ("keadaan_tanah", "Keadaan Tanah"),
    ("tanda_tanda_batas", "Tanda-Tanda Batas"),
    ("pengukuran_dan_pemetaan", "Penunjukan dan Penetapan Batas"),
    ("hal_lain_lain", "Hal Lain-Lain"),
)


def aksi_detail_lain(field: AksiField, detail_cfg: dict[str, Any]) -> HasilLangkah:
    for kunci, label in _URUTAN:
        sub = detail_cfg.get(kunci, {}) or {}
        if not sub.get("enabled"):
            field.log(f"  [{label}] dilewati")
            continue
        if not sub.get("image"):
            field.log(f"  [{label}] tidak ada aset PNG")
            continue
        el = elemen_dari(kunci, sub)
        mode = str(sub.get("mode", "default"))
        if mode == "template_nama":
            _mode_template(field, el, sub, label)
        elif mode == "sisip_sebelum_kurung":
            _mode_sisip_kurung(field, el, sub, label)
        else:
            nilai = str(sub.get("nilai", "")).strip()
            if nilai:
                field.isi_elemen(el, nilai, label)
    return HasilLangkah(True, "detail_lain")


def aksi_petunjuk_bt(field: AksiField, cfg: dict[str, Any]) -> HasilLangkah:
    pet = (cfg.get("bt") or {}).get("petunjuk") or {}
    if not pet.get("enabled", True):
        return HasilLangkah(True, "petunjuk_bt", dilewati=True)
    if not pet.get("image"):
        return HasilLangkah(False, "petunjuk_bt", pesan="tidak ada aset PNG")
    el = elemen_dari("petunjuk_bt", pet)
    teks_baru = str(pet.get("nilai", "")).strip() or field.screen.clipboard_get().strip()
    if not teks_baru:
        return HasilLangkah(True, "petunjuk_bt", dilewati=True)
    mode = str(pet.get("mode", "sisip_atas")).strip().lower()
    isi_lama = "" if mode == "timpa" else field.baca_elemen(el).strip()
    gabung = gabung_sisip(isi_lama, teks_baru, mode)
    field.isi_elemen(el, gabung, "Petunjuk BT")
    return HasilLangkah(True, "petunjuk_bt")


def _mode_template(field: AksiField, el, sub: dict, label: str) -> None:
    isi_lama = field.baca_elemen(el)
    nama = ekstrak_nama_pemohon(isi_lama)
    teks = susun_template(str(sub.get("template", "{nama}")), nama)
    field.log(f"  [{label}] nama={nama!r}")
    field.screen.clipboard_set(teks)
    field.screen.hotkey("ctrl", "a")
    field.screen.hotkey("ctrl", "v")
    field.log(f"  [{label}] template ok")


def _mode_sisip_kurung(field: AksiField, el, sub: dict, label: str) -> None:
    isi = field.baca_elemen(el)
    tambah = str(sub.get("teks_tambah", ""))
    idx = isi.find("(")
    if idx == -1:
        nl = isi.find("\n")
        pos = nl + 1 if nl != -1 else len(isi)
        baru = isi[:pos] + tambah + "\n" + isi[pos:]
    else:
        awal = isi.rfind("\n", 0, idx)
        awal = awal + 1 if awal != -1 else 0
        baru = isi[:awal] + tambah + "\n" + isi[awal:]
    field.screen.clipboard_set(baru)
    field.screen.hotkey("ctrl", "a")
    field.screen.hotkey("ctrl", "v")
    field.log(f"  [{label}] sisip ok")
