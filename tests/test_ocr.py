from otobpn.errors import OCRFailed
from otobpn.vision.ocr import ModulOCR
import pytest


def test_ocr_mati_naikkan_error():
    m = ModulOCR({"ocr": {"enabled": False}})
    with pytest.raises(OCRFailed):
        m.baca(None)
