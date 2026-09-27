"""Klik dan paste berdasarkan aset PNG (bukan koordinat absolut)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from otobpn.config_loader import get_delay
from otobpn.domain.models import ElemenUI, Region, elemen_dari
from otobpn.domain.text_rules import teks_cocok
from otobpn.errors import StopRequested, VerificationFailed
from otobpn.screen.protocol import ScreenPort
from otobpn.vision.locator import ImageLocator


class AksiField:
    """Semua input teks lewat clipboard paste (aman untuk Unicode)."""

    def __init__(
        self,
        screen: ScreenPort,
        locator: ImageLocator,
        cfg: dict[str, Any],
        log: Callable[[str], None],
        harus_jalan: Callable[[], bool],
        region_global: Region | None = None,
    ) -> None:
        self.screen = screen
        self.locator = locator
        self.cfg = cfg
        self.log = log
        self.harus_jalan = harus_jalan
        self.region_global = region_global

    def temukan(self, elemen: ElemenUI) -> tuple[int, int]:
        """Cari template, kembalikan titik klik (tengah + offset)."""
        self._jaga()
        box = self.locator.locate(elemen, self.region_global, self.harus_jalan)
        return self.locator.titik_klik(elemen, box)

    def klik_elemen(self, elemen: ElemenUI, jeda_key: str = "setelah_klik"):
        x, y = self.temukan(elemen)
        self.screen.click(x, y)
        time.sleep(get_delay(self.cfg, jeda_key, 0.25))
        return (x, y)

    def isi_elemen(self, elemen: ElemenUI, nilai: str, label: str = "") -> None:
        if not str(nilai).strip():
            self.log(f"    {label or elemen.nama}: (biarkan)")
            return
        x, y = self.temukan(elemen)
        self._paste_di(x, y, nilai, label or elemen.nama)

    def baca_elemen(self, elemen: ElemenUI) -> str:
        x, y = self.klik_elemen(elemen, "setelah_klik")
        self.screen.clipboard_set("")
        time.sleep(0.04)
        self.screen.hotkey("ctrl", "a")
        time.sleep(0.06)
        self.screen.hotkey("ctrl", "c")
        time.sleep(0.12)
        return self.screen.clipboard_get()

    def fokus_form(self) -> None:
        data = (self.cfg.get("elemen") or {}).get("fokus_form") or {}
        if not data.get("image"):
            data = (self.cfg.get("elemen") or {}).get("tab_detil") or {}
        if not data.get("image"):
            self.log("  [FOKUS] dilewati (tidak ada aset)")
            return
        self.klik_elemen(elemen_dari("fokus_form", data))
        self.log(f"  [FOKUS] {data.get('image')}")

    def _paste_di(self, x: int, y: int, nilai: str, label: str) -> None:
        self._jaga()
        self.screen.click(x, y)
        time.sleep(get_delay(self.cfg, "setelah_klik", 0.08))
        # triple-click lalu Ctrl+A: aman untuk input dan textarea
        self.screen.click(x, y, clicks=3, interval=0.05)
        self.screen.hotkey("ctrl", "a")
        time.sleep(0.04)
        self.screen.clipboard_set(str(nilai))
        self.screen.hotkey("ctrl", "v")
        time.sleep(get_delay(self.cfg, "setelah_ketik", 0.15))
        self.log(f"    → {label} '{nilai}'")
        if self.cfg.get("mode", {}).get("verify_after_fill", True):
            self._verifikasi(nilai, label)

    def _verifikasi(self, kirim: str, label: str) -> None:
        if self.cfg.get("mode", {}).get("dry_run"):
            return
        self.screen.hotkey("ctrl", "a")
        time.sleep(0.05)
        self.screen.hotkey("ctrl", "c")
        time.sleep(0.08)
        terbaca = self.screen.clipboard_get()
        if not teks_cocok(kirim, terbaca):
            raise VerificationFailed(f"{label}: kirim={kirim!r} terbaca={terbaca!r}")

    def _jaga(self) -> None:
        if not self.harus_jalan():
            raise StopRequested("Stop saat aksi field")
