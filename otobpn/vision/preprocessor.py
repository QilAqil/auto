"""Pra-proses citra: beberapa konfigurasi fallback sebelum template/OCR."""

from __future__ import annotations

from typing import Any, Callable

try:
    import cv2
except ImportError:
    cv2 = None  # type: ignore[assignment]


def configs_default() -> list[str]:
    """Urutan fallback: hsv → clahe → invert → bilateral → sharpen."""
    return ["hsv_threshold", "clahe", "invert", "bilateral", "sharpen"]


def terapkan(citra: Any, nama: str) -> Any:
    """Terapkan satu pipeline. Jika OpenCV absen, kembalikan citra asli."""
    if cv2 is None or citra is None:
        return citra
    fn = _PIPELINE.get(nama)
    return fn(citra) if fn else citra


def _hsv_threshold(img):
    """Threshold saturasi HSV + dilate + buang noise kecil."""
    if len(img.shape) == 3:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _h, s, _v = cv2.split(hsv)
        _, mask = cv2.threshold(s, 40, 255, cv2.THRESH_BINARY)
    else:
        _, mask = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask = cv2.dilate(mask, kernel, iterations=1)
    return cv2.medianBlur(mask, 3)


def _clahe(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _invert(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return cv2.bitwise_not(gray)


def _bilateral(img):
    return cv2.bilateralFilter(img, 9, 75, 75)


def _sharpen(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    blur = cv2.GaussianBlur(gray, (0, 0), 3)
    return cv2.addWeighted(gray, 1.5, blur, -0.5, 0)


_PIPELINE: dict[str, Callable] = {
    "hsv_threshold": _hsv_threshold,
    "clahe": _clahe,
    "invert": _invert,
    "bilateral": _bilateral,
    "sharpen": _sharpen,
}
