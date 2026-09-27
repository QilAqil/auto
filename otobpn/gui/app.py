"""GUI utama — kontrol SU/BT, simpan config, log, hotkey."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

from otobpn.config_loader import load_config, save_config
from otobpn.domain.resume import reset_state
from otobpn.gui import ACCENT, BG, BG2, BG3, BG4, DANGER, SUCCESS, TEXT, TEXT_DIM, WARNING
from otobpn.gui.panels import (
    PanelDaftarIsian,
    build_dl_field,
    build_panel_pejabat,
    dl_ke_dict,
    pejabat_ke_dict,
)
from otobpn.gui.widgets import btn, chk, ent, frm, lbl, section_bar
from otobpn.logger import ProsesLogger
from otobpn.orchestrator.control import KontrolAlur
from otobpn.orchestrator.runner import jalankan_loop
from otobpn.paths import assets_dir, state_path


class AppDetil(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("OTOBPN Detil v7 · Surat Ukur & Buku Tanah")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._cfg = load_config()
        self._su = KontrolAlur()
        self._bt = KontrolAlur()
        self._su_worker = None
        self._bt_worker = None
        self._logger = ProsesLogger()
        self._logger.set_ui(self._tampil_log)
        self._center(1020, 640)
        self._build()
        self._bind_hotkeys()

    def _center(self, w, h) -> None:
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build(self) -> None:
        bar = frm(self, bg=BG3)
        bar.pack(fill="x")
        lbl(bar, "  OTOBPN Detil v7", bold=True, color=ACCENT, size=11, bg=BG3).pack(
            side="left", pady=5
        )
        lbl(bar, "ATR/BPN  ", color=TEXT_DIM, size=9, bg=BG3).pack(side="right", pady=5)
        sb = frm(self, bg=BG3)
        sb.pack(fill="x", side="bottom")
        self._sb = tk.StringVar(value="Siap. Config dari config.yaml.")
        lbl(sb, "", textvariable=self._sb, color=TEXT_DIM, bg=BG3, size=9).pack(
            side="left", padx=8, pady=2
        )
        body = frm(self, bg=BG)
        body.pack(fill="both", expand=True, padx=4, pady=4)
        body.columnconfigure(0, weight=3, uniform="body")
        body.columnconfigure(1, weight=1, uniform="body")
        body.rowconfigure(0, weight=1)
        self._build_kiri(body)
        self._build_kanan(body)

    def _build_kiri(self, body) -> None:
        outer = frm(body, bg=BG)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        style = ttk.Style()
        style.configure("L.TNotebook", background=BG, borderwidth=0)
        style.configure(
            "L.TNotebook.Tab",
            background=BG3,
            foreground=TEXT_DIM,
            padding=[14, 4],
            font=("Segoe UI", 9),
        )
        self._lnb = ttk.Notebook(outer, style="L.TNotebook")
        self._lnb.pack(fill="both", expand=True)
        self._lnb.add(self._tab_su(), text="  Surat Ukur (SU)  ")
        self._lnb.add(self._tab_bt(), text="  Buku Tanah (BT)  ")

    def _scrollable(self, parent):
        outer = frm(parent, bg=BG)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = frm(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

        def _enter(_):
            canvas.bind_all(
                "<MouseWheel>",
                lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
            )

        def _leave(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _enter)
        canvas.bind("<Leave>", _leave)
        return outer, inner

    def _tab_su(self):
        outer, inner = self._scrollable(self._lnb)
        self._status_su = tk.StringVar(value="Menunggu…")
        self._prog_su = tk.StringVar(value="Putaran: -")
        self._debug = tk.BooleanVar(value=False)
        self._dry = tk.BooleanVar(value=bool(self._cfg.get("mode", {}).get("dry_run")))
        _kontrol(inner, self._status_su, self._prog_su, self._mulai_su, self._jeda_su,
                 self._reset_su, self._stop_su, self._debug, self._dry, self._simpan_su,
                 self._cek_asset)
        self._pen_en = tk.BooleanVar(value=self._cfg.get("penomoran", {}).get("tanggal_enabled"))
        self._pen_val = tk.StringVar(value=str(self._cfg.get("penomoran", {}).get("tanggal_nilai", "")))
        self._pen_img = tk.StringVar(value=str(self._cfg.get("penomoran", {}).get("image", "label_tgl_penomoran.png")))
        self._pen_ox = tk.StringVar(value=str(self._cfg.get("penomoran", {}).get("offset_x", 90)))
        self._pen_oy = tk.StringVar(value=str(self._cfg.get("penomoran", {}).get("offset_y", 0)))
        _blok_penomoran(inner, self._pen_en, self._pen_val, self._pen_img, self._pen_ox, self._pen_oy)
        section_bar(inner, "PEMBUKUAN")
        self._pb = build_panel_pejabat(inner, self._cfg.get("pembukuan") or {})
        section_bar(inner, "PENERBITAN SERTIFIKAT")
        self._ps = build_panel_pejabat(inner, self._cfg.get("penerbitan_sertifikat") or {})
        self._di_en, self._panel_di = _blok_di(inner, self._cfg.get("daftar_isian") or {}, "Proses Daftar Isian")
        section_bar(inner, "DETAIL LAIN-LAIN")
        self._dl = {}
        dl = frm(inner, bg=BG2)
        dl.pack(fill="x", padx=4, pady=2)
        sub = self._cfg.get("detail_lain") or {}
        for key, judul, ml in (
            ("keadaan_tanah", "Keadaan Tanah", False),
            ("tanda_tanda_batas", "Tanda-Tanda Batas", True),
            ("pengukuran_dan_pemetaan", "Penunjukan & Penetapan Batas", True),
            ("hal_lain_lain", "Hal Lain-Lain", False),
        ):
            build_dl_field(dl, key, judul, sub.get(key) or {}, ml, self._dl)
        return outer

    def _tab_bt(self):
        outer, inner = self._scrollable(self._lnb)
        self._status_bt = tk.StringVar(value="Menunggu…")
        self._prog_bt = tk.StringVar(value="Putaran: -")
        _kontrol(inner, self._status_bt, self._prog_bt, self._mulai_bt, self._jeda_bt,
                 self._reset_bt, self._stop_bt, None, None, self._simpan_bt, None, judul="KONTROL BT")
        section_bar(inner, "PEMBUKUAN BT")
        self._pb_bt = build_panel_pejabat(inner, self._cfg.get("pembukuan_bt") or {})
        section_bar(inner, "PENERBITAN SERTIFIKAT BT")
        self._ps_bt = build_panel_pejabat(inner, self._cfg.get("penerbitan_sertifikat_bt") or {})
        bt = self._cfg.get("bt") or {}
        self._bt_di_en, self._bt_panel_di = _blok_di(
            inner, bt.get("daftar_isian") or {}, "Proses Daftar Isian BT", judul="DAFTAR ISIAN BT"
        )
        self._bt_pet = _blok_petunjuk(inner, bt.get("petunjuk") or {})
        return outer

    def _build_kanan(self, body) -> None:
        rf = frm(body, bg=BG)
        rf.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        rf.rowconfigure(1, weight=1)
        rf.columnconfigure(0, weight=1)
        section_bar(rf, "LOG PROSES").grid(row=0, column=0, sticky="ew")
        self._logw = scrolledtext.ScrolledText(
            rf, bg=BG4, fg=TEXT, font=("Consolas", 8), state="disabled",
            relief="flat", wrap="word", width=25,
        )
        self._logw.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        br = frm(rf, bg=BG)
        br.grid(row=2, column=0, sticky="ew", padx=4, pady=4)
        btn(br, "Bersihkan", self._clear_log, color=BG3, w=14).pack(side="right")

    def _tampil_log(self, baris: str) -> None:
        def _ui():
            try:
                self._logw.config(state="normal")
                n = int(self._logw.index("end-1c").split(".")[0])
                if n > 400:
                    self._logw.delete("1.0", f"{n - 300}.0")
                self._logw.insert("end", baris)
                self._logw.see("end")
                self._logw.config(state="disabled")
            except Exception:
                pass
        self.after(0, _ui)

    def _clear_log(self) -> None:
        self._logw.config(state="normal")
        self._logw.delete("1.0", "end")
        self._logw.config(state="disabled")

    def _simpan_su(self) -> None:
        cfg = dict(self._cfg)
        cfg.setdefault("mode", {})["dry_run"] = bool(self._dry.get())
        cfg["penomoran"] = {
            **(cfg.get("penomoran") or {}),
            "tanggal_enabled": self._pen_en.get(),
            "tanggal_nilai": self._pen_val.get(),
            "image": self._pen_img.get().strip(),
            "offset_x": _int(self._pen_ox.get(), 90),
            "offset_y": _int(self._pen_oy.get(), 0),
        }
        cfg["daftar_isian"] = {"enabled": self._di_en.get(), "kolom": self._panel_di.get_data()}
        cfg["pembukuan"] = pejabat_ke_dict(self._pb)
        cfg["penerbitan_sertifikat"] = pejabat_ke_dict(self._ps)
        cfg["detail_lain"] = dl_ke_dict(self._dl)
        save_config(cfg)
        self._cfg = load_config()
        self._logger.tulis("config SU disimpan (semua modul baca ulang)")

    def _simpan_bt(self) -> None:
        cfg = dict(self._cfg)
        cfg.setdefault("bt", {})
        cfg["bt"]["daftar_isian"] = {
            "enabled": self._bt_di_en.get(),
            "kolom": self._bt_panel_di.get_data(),
        }
        p = self._bt_pet
        cfg["bt"]["petunjuk"] = {
            "enabled": p["en"].get(),
            "mode": p["mode"].get(),
            "nilai": p["val"].get(),
            "image": p["img"].get().strip(),
            "offset_x": _int(p["ox"].get(), 180),
            "offset_y": _int(p["oy"].get(), 0),
        }
        cfg["pembukuan_bt"] = pejabat_ke_dict(self._pb_bt)
        cfg["penerbitan_sertifikat_bt"] = pejabat_ke_dict(self._ps_bt)
        save_config(cfg)
        self._cfg = load_config()
        self._logger.tulis("config BT disimpan")

    def _mulai_su(self) -> None:
        if self._su_worker and self._su_worker.is_alive():
            return
        self._simpan_su()
        self._su.reset_siap()
        self._status_su.set("SU siap — tekan jeda untuk lanjut")
        self._su_worker = threading.Thread(target=self._run, args=("su",), daemon=True)
        self._su_worker.start()

    def _mulai_bt(self) -> None:
        if self._bt_worker and self._bt_worker.is_alive():
            return
        self._simpan_bt()
        self._bt.reset_siap()
        self._status_bt.set("BT siap — tekan jeda untuk lanjut")
        self._bt_worker = threading.Thread(target=self._run, args=("bt",), daemon=True)
        self._bt_worker.start()

    def _run(self, mode: str) -> None:
        kontrol = self._su if mode == "su" else self._bt
        prog = self._prog_su if mode == "su" else self._prog_bt
        status = self._status_su if mode == "su" else self._status_bt
        try:
            jalankan_loop(
                mode,  # type: ignore[arg-type]
                self._cfg,
                kontrol,
                self._logger,
                lambda m: self.after(0, lambda: prog.set(m)),
                after_putaran=lambda: self.after(0, lambda: self._auto_jeda(mode)),
            )
        except Exception as exc:
            self._logger.tulis(f"{mode} error: {exc}")
        finally:
            kontrol.minta_stop()
            self.after(0, lambda: status.set(f"{mode.upper()} selesai"))

    def _auto_jeda(self, mode: str) -> None:
        k = self._su if mode == "su" else self._bt
        k.set_jeda(True)
        st = self._status_su if mode == "su" else self._status_bt
        st.set(f"{mode.upper()} selesai isi — tekan jeda untuk lanjut")

    def _jeda_su(self) -> None:
        self._toggle(self._su, self._su_worker, self._status_su, "SU")

    def _jeda_bt(self) -> None:
        self._toggle(self._bt, self._bt_worker, self._status_bt, "BT")

    def _toggle(self, k: KontrolAlur, worker, status_var, nama: str) -> None:
        if worker is None or not worker.is_alive():
            self._logger.tulis(f"{nama} belum aktif — tekan MULAI dulu")
            return
        running = k.toggle_jeda()
        status_var.set(f"{nama} {'melanjutkan' if running else 'dijeda'}")

    def _reset_su(self) -> None:
        self._su.minta_stop()
        reset_state(state_path())
        self._status_su.set("SU reset (resume di-nolkan)")
        self._prog_su.set("Putaran: -")

    def _reset_bt(self) -> None:
        self._bt.minta_stop()
        reset_state(state_path())
        self._status_bt.set("BT reset")
        self._prog_bt.set("Putaran: -")

    def _stop_su(self) -> None:
        self._su.minta_stop()
        self._status_su.set("SU dihentikan (safe-stop)")

    def _stop_bt(self) -> None:
        self._bt.minta_stop()
        self._status_bt.set("BT dihentikan (safe-stop)")

    def _bind_hotkeys(self) -> None:
        import keyboard

        hk = self._cfg.get("hotkey") or {}
        to_remove = (
            hk.get("mulai_su", hk.get("mulai", "\\")),
            hk.get("mulai_bt", hk.get("mulai", "`")),
            hk.get("mulai"),
            hk.get("jeda_su"),
            hk.get("jeda_bt"),
            hk.get("reset"),
            hk.get("exit"),
        )
        for k in to_remove:
            if not k:
                continue
            try:
                keyboard.remove_hotkey(k)
            except Exception:
                pass
        keyboard.add_hotkey(hk.get("mulai_su", hk.get("mulai", "\\")), lambda: self.after(0, self._mulai_su))
        keyboard.add_hotkey(hk.get("mulai_bt", hk.get("mulai", "`")), lambda: self.after(0, self._mulai_bt))
        keyboard.add_hotkey(hk.get("mulai", "f1"), lambda: self.after(0, self._mulai_aktif))
        keyboard.add_hotkey(hk.get("jeda_su", "\\"), lambda: self.after(0, self._jeda_su))
        keyboard.add_hotkey(hk.get("jeda_bt", "`"), lambda: self.after(0, self._jeda_bt))
        keyboard.add_hotkey(hk.get("reset", "f3"), lambda: self.after(0, self._reset_aktif))
        keyboard.add_hotkey(hk.get("exit", "esc"), lambda: self.after(0, self._stop_semua))

    def _tab_aktif(self) -> str:
        try:
            return "bt" if self._lnb.index(self._lnb.select()) == 1 else "su"
        except Exception:
            return "su"

    def _mulai_aktif(self) -> None:
        (self._mulai_bt if self._tab_aktif() == "bt" else self._mulai_su)()

    def _reset_aktif(self) -> None:
        (self._reset_bt if self._tab_aktif() == "bt" else self._reset_su)()

    def _stop_semua(self) -> None:
        self._su.minta_stop()
        self._bt.minta_stop()
        self._status_su.set("Semua dihentikan")
        self._status_bt.set("Semua dihentikan")

    def _cek_asset(self) -> None:
        def _t():
            import os
            folder = assets_dir()
            if not os.path.isdir(folder):
                self._logger.tulis(f"folder assets tidak ada: {folder}")
                return
            n = 0
            for nama in os.listdir(folder):
                if nama.lower().endswith(".png"):
                    n += 1
                    self._logger.tulis(f"asset {nama}")
            self._logger.tulis(f"total png={n}")
        threading.Thread(target=_t, daemon=True).start()

    def destroy(self) -> None:
        try:
            import keyboard
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self._su.minta_stop()
        self._bt.minta_stop()
        super().destroy()


def _int(s: str, default: int) -> int:
    try:
        return int(str(s).strip())
    except ValueError:
        return default


def _kontrol(inner, status, prog, mulai, jeda, reset, stop, debug, dry, simpan, cek, judul="KONTROL"):
    section_bar(inner, judul)
    cf = frm(inner, bg=BG2)
    cf.pack(fill="x", padx=4, pady=2)
    st = frm(cf, bg=BG2)
    st.pack(fill="x", padx=6, pady=(4, 2))
    lbl(st, "", textvariable=status, bold=True, color=SUCCESS, bg=BG2, size=10).pack(side="left")
    lbl(st, "", textvariable=prog, color=WARNING, bg=BG2, size=9).pack(side="right", padx=6)
    br = frm(cf, bg=BG2)
    br.pack(fill="x", padx=6, pady=(2, 6))
    btn(br, "MULAI F1", mulai, color=SUCCESS, w=13).pack(side="left", padx=3)
    btn(br, "JEDA", jeda, color=WARNING, w=10).pack(side="left", padx=2)
    btn(br, "RESET F3", reset, color=ACCENT, w=12).pack(side="left", padx=2)
    btn(br, "STOP ESC", stop, color=DANGER, w=12).pack(side="left", padx=2)
    if simpan:
        btn(br, "Simpan", simpan, color="#2d6a4f", w=10).pack(side="left", padx=2)
    dr = frm(cf, bg=BG2)
    dr.pack(fill="x", padx=6, pady=(0, 4))
    if debug is not None:
        chk(dr, "Debug", debug, bg=BG2).pack(side="left")
    if dry is not None:
        chk(dr, "Dry-run", dry, bg=BG2).pack(side="left", padx=8)
    if cek:
        btn(dr, "Cek Asset", cek, color="#4a7a6f", w=12).pack(side="left", padx=2)


def _blok_penomoran(inner, en, val, img, ox, oy) -> None:
    section_bar(inner, "PENOMORAN")
    pf = frm(inner, bg=BG2)
    pf.pack(fill="x", padx=4, pady=2)
    pr = frm(pf, bg=BG2)
    pr.pack(fill="x", padx=8, pady=4)
    chk(pr, "Tgl. Penomoran", en).pack(side="left")
    lbl(pr, "  Nilai:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(pr, var=val, w=14).pack(side="left")
    lbl(pr, "  aset:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(pr, var=img, w=22).pack(side="left")
    lbl(pr, " ox:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(pr, var=ox, w=5).pack(side="left")
    lbl(pr, " oy:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(pr, var=oy, w=5).pack(side="left")


def _blok_di(inner, di_cfg, label, judul="DAFTAR ISIAN"):
    section_bar(inner, judul)
    df = frm(inner, bg=BG2)
    df.pack(fill="x", padx=4, pady=2)
    en = tk.BooleanVar(value=di_cfg.get("enabled", True))
    dr = frm(df, bg=BG2)
    dr.pack(fill="x", padx=8, pady=(4, 2))
    chk(dr, label, en).pack(side="left")
    panel = PanelDaftarIsian(df, kolom_data=di_cfg.get("kolom") or [])
    panel.pack(fill="x", padx=4, pady=(2, 4))
    return en, panel


def _blok_petunjuk(inner, pet) -> dict:
    from tkinter import ttk as _ttk

    section_bar(inner, "PETUNJUK BT")
    ptf = frm(inner, bg=BG2)
    ptf.pack(fill="x", padx=4, pady=2)
    v = {
        "en": tk.BooleanVar(value=pet.get("enabled", True)),
        "val": tk.StringVar(value=str(pet.get("nilai", ""))),
        "mode": tk.StringVar(value=str(pet.get("mode", "sisip_atas"))),
        "img": tk.StringVar(value=str(pet.get("image", "label_petunjuk_bt.png"))),
        "ox": tk.StringVar(value=str(pet.get("offset_x", 180))),
        "oy": tk.StringVar(value=str(pet.get("offset_y", 0))),
    }
    ptr = frm(ptf, bg=BG2)
    ptr.pack(fill="x", padx=8, pady=4)
    chk(ptr, "Petunjuk BT", v["en"]).pack(side="left")
    lbl(ptr, "  Mode:", color=TEXT_DIM, bg=BG2).pack(side="left")
    cb = _ttk.Combobox(
        ptr, textvariable=v["mode"],
        values=["sisip_atas", "timpa", "sisip_bawah"], state="readonly", width=11,
    )
    cb.pack(side="left")
    lbl(ptr, "  Nilai:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(ptr, var=v["val"], w=18).pack(side="left")
    lbl(ptr, "  aset:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(ptr, var=v["img"], w=20).pack(side="left")
    lbl(ptr, " ox:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(ptr, var=v["ox"], w=5).pack(side="left")
    lbl(ptr, " oy:", color=TEXT_DIM, bg=BG2).pack(side="left")
    ent(ptr, var=v["oy"], w=5).pack(side="left")
    return v
