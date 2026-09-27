"""OCR multi-config: EasyOCR opsional + validasi allowlist/panjang."""

from __future__ import annotations

from typing import Any

from otobpn.domain.text_rules import bersihkan_ocr, validasi_teks
from otobpn.errors import OCRFailed
from otobpn.paths import bundled_ocr_dir
from otobpn.vision.preprocessor import configs_default, terapkan


class ModulOCR:
    """Baca teks dari crop layar. Nonaktif jika ocr.enabled=false atau EasyOCR absen."""

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg.get("ocr", {}) or {}
        self.enabled = bool(self.cfg.get("enabled", False))
        self._reader = None

    def baca(
        self,
        citra,
        allowlist: str | None = None,
        panjang_tepat: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
    ) -> str:
        """Coba tiap pre-process; kembalikan teks pertama yang lolos validasi."""
        if not self.enabled:
            raise OCRFailed("OCR dinonaktifkan di config.")
        allow = allowlist if allowlist is not None else self.cfg.get("allowlist")
        p_tepat = panjang_tepat
        if p_tepat is None:
            p_tepat = self.cfg.get("panjang_tepat")
        pipelines = self.cfg.get("pipelines") or configs_default()
        terakhir = ""
        for nama in pipelines:
            teks = bersihkan_ocr(self._ocr_satu(terapkan(citra, nama)), allow)
            terakhir = teks
            if validasi_teks(teks, allow, p_tepat, min_len, max_len):
                return teks
        raise OCRFailed(f"OCR gagal validasi. Terakhir={terakhir!r}")

    def cari_teks(
        self,
        citra,
        target: str,
        allowlist: str | None = None,
        **kwargs,
    ) -> tuple[int, int]:
        """Cari label di screenshot OCR dan kembalikan pusat teks yang cocok."""
        if not self.enabled:
            raise OCRFailed("OCR dinonaktifkan di config.")
        if citra is None:
            raise OCRFailed("Citra kosong untuk OCR.")
        target_norm = self._normalisasi_target(target)
        try:
            hasil = self._reader_ocr(citra, detail=True)
        except Exception as exc:  # pragma: no cover - bergantung EasyOCR
            raise OCRFailed(f"OCR gagal membaca citra: {exc}") from exc
        for box, teks, conf in hasil:
            teks_t = str(teks or "").strip()
            if not teks_t:
                continue
            teks_norm = self._normalisasi_target(teks_t)
            if not teks_norm:
                continue
            if target_norm and target_norm not in teks_norm:
                if not any(tok in teks_norm for tok in target_norm.split() if len(tok) > 2):
                    continue
            points = [pt for pts in box for pt in pts]
            x = sum(p[0] for p in points) / len(points)
            y = sum(p[1] for p in points) / len(points)
            if kwargs.get("return_box"):
                return box
            return int(x), int(y)
        raise OCRFailed(f"Target OCR tidak ditemukan: {target!r}")

    def _normalisasi_target(self, teks: str) -> str:
        t = str(teks or "").lower().replace("_", " ")
        t = t.replace("-", " ")
        t = "".join(ch for ch in t if ch.isalnum() or ch.isspace())
        return " ".join(t.split())

    def _ocr_satu(self, citra) -> str:
        hasil = self._reader_ocr(citra, detail=False)
        if isinstance(hasil, list):
            return " ".join(str(x) for x in hasil)
        return str(hasil or "")

    def _reader_ocr(self, citra, detail: bool):
        reader = self._pastikan_reader()
        if reader is None or citra is None:
            return ""
        hasil = reader.readtext(citra, detail=detail)
        if detail:
            return hasil
        return hasil

    def _pastikan_reader(self):
        if self._reader is not None:
            return self._reader
        try:
            import easyocr  # type: ignore
        except ImportError as exc:
            raise OCRFailed("easyocr tidak terpasang") from exc
        model_dir = self.cfg.get("model_dir") or bundled_ocr_dir()
        bahasa = self.cfg.get("bahasa") or ["id", "en"]
        # model ikut bundle agar pengguna tidak mengunduh sendiri
        self._reader = easyocr.Reader(
            bahasa, verbose=False, model_storage_directory=model_dir
        )
        return self._reader
