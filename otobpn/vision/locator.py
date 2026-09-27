"""Locator template matching: cache anchor + retry + region fallback."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

from otobpn.domain.models import ElemenUI, Region
from otobpn.errors import ElementNotFound, OCRFailed, StopRequested
from otobpn.screen.protocol import Box, ScreenPort
from otobpn.vision.ocr import ModulOCR


class ImageLocator:
    """Cari elemen. Pencarian berikutnya memakai region lokal di sekitar cache."""

    def __init__(
        self,
        screen: ScreenPort,
        assets_dir: str,
        retry: dict[str, Any] | None = None,
        grayscale: bool = True,
        cfg: dict[str, Any] | None = None,
    ) -> None:
        self.screen = screen
        self.assets_dir = assets_dir
        self.retry = retry or {"max_attempts": 3, "interval_sec": 0.4}
        self.grayscale = grayscale
        self.ocr_cfg = (cfg or {}).get("ocr", {}) or {}
        self.ocr = ModulOCR({"ocr": {"enabled": bool(self.ocr_cfg.get("enabled", True)), **self.ocr_cfg}})
        self._cache: dict[str, Box] = {}

    def reset_cache(self) -> None:
        self._cache.clear()

    def locate(
        self,
        elemen: ElemenUI,
        region_global: Region | None = None,
        harus_jalan: Callable[[], bool] | None = None,
    ) -> Box:
        """Cari sampai ketemu atau attempts habis. Naikkan ElementNotFound."""
        path = os.path.join(self.assets_dir, elemen.image) if elemen.image else ""
        attempts = int(self.retry.get("max_attempts", 3))
        jeda = float(self.retry.get("interval_sec", 0.4))
        if path and os.path.exists(path):
            for _ in range(attempts):
                if harus_jalan and not harus_jalan():
                    raise StopRequested("Stop saat locate " + elemen.nama)
                last = self._satu_percobaan(elemen, region_global)
                if last:
                    self._cache[elemen.nama] = last
                    return last
                time.sleep(jeda)
        if self.ocr.enabled:
            try:
                ocr_box = self._fallback_ocr(elemen, region_global)
                if ocr_box is not None:
                    self._cache[elemen.nama] = ocr_box
                    return ocr_box
            except OCRFailed:
                pass
        raise ElementNotFound(
            f"Elemen '{elemen.nama}' ({elemen.image}) tidak di layar ({attempts}x)."
        )

    def titik_klik(self, elemen: ElemenUI, box: Box) -> tuple[int, int]:
        cx, cy = box.center
        return (cx + elemen.offset_x, cy + elemen.offset_y)

    def _fallback_ocr(self, elemen: ElemenUI, region_global: Region | None):
        target = elemen.nama.split(".")[-1].replace("_", " ")
        target = target.replace("label ", "").strip() or elemen.nama
        region = region_global.as_tuple() if region_global else None
        try:
            citra = self.screen.screenshot(region=region)
            x, y = self.ocr.cari_teks(citra, target)
        except Exception:
            return None
        if region is not None:
            left, top, _, _ = region
            x += left
            y += top
        return Box(max(0, x - 8), max(0, y - 8), 16, 16)

    def _satu_percobaan(self, elemen: ElemenUI, region_global: Region | None):
        path = os.path.join(self.assets_dir, elemen.image) if elemen.image else ""
        if not path or not os.path.exists(path):
            return None
        # 1) region cache lokal  2) region elemen  3) region global  4) layar
        for conf in self._tangga_confidence(elemen.confidence):
            for region in self._kandidat_region(elemen, region_global):
                box = self.screen.locate_on_screen(
                    path, conf, region, self.grayscale
                )
                if box:
                    return box
        return None

    def _kandidat_region(self, elemen: ElemenUI, glob: Region | None):
        hasil: list[tuple[int, int, int, int] | None] = []
        cached = self._cache.get(elemen.nama)
        if cached:
            hasil.append(self._pad(cached, elemen.cache_pad))
        if elemen.region:
            hasil.append(elemen.region.as_tuple())
        if glob:
            hasil.append(glob.as_tuple())
        hasil.append(None)
        return hasil

    def _pad(self, box: Box, pad: int) -> tuple[int, int, int, int]:
        sw, sh = self.screen.size()
        left = max(0, box.left - pad)
        top = max(0, box.top - pad)
        right = min(sw, box.left + box.width + pad)
        bottom = min(sh, box.top + box.height + pad)
        return (left, top, max(1, right - left), max(1, bottom - top))

    @staticmethod
    def _tangga_confidence(awal: float) -> list[float]:
        nilai = [awal, awal - 0.1, awal - 0.2]
        return [max(0.5, round(v, 2)) for v in nilai]
