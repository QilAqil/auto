"""Panel Daftar Isian dan panel pejabat (aset PNG + offset, tanpa x/y layar)."""

from __future__ import annotations

import tkinter as tk

from otobpn.gui import BG2, BG3, TEXT_DIM
from otobpn.gui.widgets import chk, ent, frm, lbl, txt_widget

_ASET_PEJABAT = (
    ("tanggal", "Tanggal"),
    ("centang", "Centang"),
    ("jabatan", "Jabatan"),
    ("jabatan_klik2", "Jabatan item"),
    ("nama", "Nama field"),
    ("nama_klik2", "Nama item"),
)


class PanelDaftarIsian(tk.Frame):
    def __init__(self, parent, kolom_data: list, **kw):
        kw.setdefault("bg", BG2)
        super().__init__(parent, **kw)
        self._kolom: list[dict] = []
        self._header()
        for k in kolom_data:
            self._add(k)

    def _header(self) -> None:
        h = frm(self, bg=BG3)
        h.pack(fill="x", padx=4, pady=(2, 0))
        for t, w in [
            ("✓", 3), ("ID", 8), ("Aset PNG", 22),
            ("Nomor", 8), ("Tahun", 6), ("Tanggal", 10),
        ]:
            lbl(h, t, bold=True, bg=BG3, width=w).pack(side="left", padx=2, pady=3)

    def _add(self, data: dict) -> None:
        row = frm(self, bg=BG2)
        row.pack(fill="x", padx=4, pady=1)
        v: dict = {}
        v["enabled"] = tk.BooleanVar(value=data.get("enabled", True))
        chk(row, "", v["enabled"], bg=BG2).pack(side="left", padx=(4, 2))
        for key, w in [
            ("id", 8), ("image", 22), ("nomor", 8), ("tahun", 6), ("tanggal", 10),
        ]:
            sv = tk.StringVar(value=str(data.get(key, "")))
            v[key] = sv
            ent(row, var=sv, w=w).pack(side="left", padx=2)
        self._kolom.append(v)

    def get_data(self) -> list:
        hasil = []
        for k in self._kolom:
            hasil.append({
                "id": k["id"].get(),
                "enabled": k["enabled"].get(),
                "image": k["image"].get().strip(),
                "nomor": k["nomor"].get(),
                "tahun": k["tahun"].get(),
                "tanggal": k["tanggal"].get(),
            })
        return hasil


def build_panel_pejabat(parent, cfg_data: dict) -> dict:
    pf = frm(parent, bg=BG2)
    pf.pack(fill="x", padx=4, pady=2)
    v: dict = {}
    r1 = frm(pf, bg=BG2)
    r1.pack(fill="x", padx=8, pady=(4, 1))
    v["enabled"] = tk.BooleanVar(value=cfg_data.get("enabled", False))
    chk(r1, "Aktif", v["enabled"], bg=BG2).pack(side="left")
    lbl(r1, "  Jabatan:", color=TEXT_DIM, bg=BG2).pack(side="left", padx=(8, 2))
    v["jabatan_teks"] = tk.StringVar(value=str(cfg_data.get("jabatan_teks", "")))
    ent(r1, var=v["jabatan_teks"], w=28).pack(side="left")
    lbl(r1, "  Nama:", color=TEXT_DIM, bg=BG2).pack(side="left", padx=(6, 2))
    v["nama_teks"] = tk.StringVar(
        value=str(cfg_data.get("nama_teks") or "")
    )
    ent(r1, var=v["nama_teks"], w=18).pack(side="left")
    _baris_tanggal(pf, v, cfg_data)
    r_c = frm(pf, bg=BG2)
    r_c.pack(fill="x", padx=8, pady=(0, 2))
    v["centang_enabled"] = tk.BooleanVar(value=cfg_data.get("centang_enabled", False))
    chk(r_c, "Klik centang", v["centang_enabled"], bg=BG2).pack(side="left")
    for key, judul in _ASET_PEJABAT:
        _baris_aset(pf, v, cfg_data.get(key) or {}, judul, key)
    return v


def pejabat_ke_dict(v: dict) -> dict:
    d = {
        "enabled": v["enabled"].get(),
        "centang_enabled": bool(v.get("centang_enabled") and v["centang_enabled"].get()),
        "tanggal_enabled": bool(v.get("tanggal_enabled") and v["tanggal_enabled"].get()),
        "tanggal_nilai": v["tanggal_nilai"].get() if "tanggal_nilai" in v else "",
        "jabatan_teks": v["jabatan_teks"].get(),
        "nama_teks": v["nama_teks"].get(),
    }
    for key, _judul in _ASET_PEJABAT:
        d[key] = {
            "image": v[f"{key}_image"].get().strip(),
            "offset_x": _int(v[f"{key}_ox"].get(), 0),
            "offset_y": _int(v[f"{key}_oy"].get(), 0),
        }
    return d


def _baris_tanggal(pf, v, cfg_data) -> None:
    r = frm(pf, bg=BG2)
    r.pack(fill="x", padx=8, pady=(2, 1))
    v["tanggal_enabled"] = tk.BooleanVar(value=cfg_data.get("tanggal_enabled", False))
    chk(r, "Tanggal", v["tanggal_enabled"], bg=BG2).pack(side="left")
    lbl(r, "  Nilai:", color=TEXT_DIM, bg=BG2).pack(side="left", padx=(4, 2))
    v["tanggal_nilai"] = tk.StringVar(value=str(cfg_data.get("tanggal_nilai", "")))
    ent(r, var=v["tanggal_nilai"], w=18).pack(side="left")


def _baris_aset(pf, v, blok: dict, judul: str, key: str) -> None:
    r = frm(pf, bg=BG2)
    r.pack(fill="x", padx=8, pady=1)
    lbl(r, judul, color=TEXT_DIM, bg=BG2, width=14).pack(side="left")
    v[f"{key}_image"] = tk.StringVar(value=str(blok.get("image", "")))
    ent(r, var=v[f"{key}_image"], w=28).pack(side="left", padx=2)
    lbl(r, "ox:", color=TEXT_DIM, bg=BG2, size=8).pack(side="left")
    v[f"{key}_ox"] = tk.StringVar(value=str(blok.get("offset_x", 0)))
    ent(r, var=v[f"{key}_ox"], w=5).pack(side="left")
    lbl(r, "oy:", color=TEXT_DIM, bg=BG2, size=8).pack(side="left")
    v[f"{key}_oy"] = tk.StringVar(value=str(blok.get("offset_y", 0)))
    ent(r, var=v[f"{key}_oy"], w=5).pack(side="left")


def build_dl_field(parent, key, label_text, sub, multiline, store: dict) -> None:
    f = frm(parent, bg=BG2)
    f.pack(fill="x", padx=8, pady=1)
    en = tk.BooleanVar(value=sub.get("enabled", True))
    top = frm(f, bg=BG2)
    top.pack(fill="x")
    chk(top, label_text, en, bg=BG2).pack(side="left")
    img = tk.StringVar(value=str(sub.get("image", "")))
    ox = tk.StringVar(value=str(sub.get("offset_x", 180)))
    oy = tk.StringVar(value=str(sub.get("offset_y", 0)))
    lbl(top, " aset:", color=TEXT_DIM, bg=BG2, size=8).pack(side="left", padx=(8, 1))
    ent(top, var=img, w=22).pack(side="left")
    lbl(top, " ox:", color=TEXT_DIM, bg=BG2, size=8).pack(side="left")
    ent(top, var=ox, w=5).pack(side="left")
    lbl(top, " oy:", color=TEXT_DIM, bg=BG2, size=8).pack(side="left")
    ent(top, var=oy, w=5).pack(side="left")
    w = _nilai_widget(f, sub, multiline)
    store[key] = {"en": en, "w": w, "img": img, "ox": ox, "oy": oy}


def dl_ke_dict(store: dict) -> dict:
    out = {}
    for key, d in store.items():
        w = d["w"]
        m = getattr(w, "_mode", "single")
        if m in ("template_nama", "sisip_sebelum_kurung"):
            val_key = getattr(w, "_val_key", "template")
            entry = {"enabled": d["en"].get(), val_key: w.get("1.0", "end-1c"), "mode": m}
        elif m == "multiline":
            entry = {"enabled": d["en"].get(), "nilai": w.get("1.0", "end-1c")}
        else:
            entry = {"enabled": d["en"].get(), "nilai": w._sv.get()}
        entry["image"] = d["img"].get().strip()
        entry["offset_x"] = _int(d["ox"].get(), 180)
        entry["offset_y"] = _int(d["oy"].get(), 0)
        out[key] = entry
    return out


def _nilai_widget(parent, sub, multiline):
    bot = frm(parent, bg=BG2)
    bot.pack(fill="x", pady=(1, 2))
    mode = sub.get("mode", "default")
    if mode in ("template_nama", "sisip_sebelum_kurung"):
        val_key = "template" if mode == "template_nama" else "teks_tambah"
        w = txt_widget(bot, h=4, w=52)
        w.insert("1.0", str(sub.get(val_key, "")))
        w.pack(fill="x", expand=True)
        w._mode = mode
        w._val_key = val_key
        return w
    if multiline:
        w = txt_widget(bot, h=2, w=50)
        w.insert("1.0", sub.get("nilai", ""))
        w.pack(fill="x", expand=True)
        w._mode = "multiline"
        return w
    sv = tk.StringVar(value=str(sub.get("nilai", "")))
    w = ent(bot, var=sv, w=52)
    w.pack(side="left", fill="x", expand=True)
    w._sv = sv
    w._mode = "single"
    return w


def _int(s: str, default: int) -> int:
    try:
        return int(str(s).strip())
    except ValueError:
        return default
