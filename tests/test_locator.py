from otobpn.domain.models import ElemenUI
from otobpn.screen.fake import FakeScreen
from otobpn.screen.protocol import Box
from otobpn.vision.locator import ImageLocator
from otobpn.errors import ElementNotFound
import pytest


def _png() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_cache_lalu_region_lokal(tmp_path):
    png = tmp_path / "x.png"
    png.write_bytes(_png())
    screen = FakeScreen()
    screen.auto_match = False
    path = str(png)
    screen.matches[path] = Box(100, 200, 20, 10)
    loc = ImageLocator(screen, str(tmp_path), retry={"max_attempts": 1, "interval_sec": 0})
    el = ElemenUI(nama="di", mode="image", image="x.png", confidence=0.8)
    box = loc.locate(el)
    assert box.left == 100
    box2 = loc.locate(el)
    assert box2.left == 100


def test_aset_hilang():
    screen = FakeScreen()
    loc = ImageLocator(screen, ".", retry={"max_attempts": 1, "interval_sec": 0})
    el = ElemenUI(nama="z", mode="image", image="tidak.png")
    with pytest.raises(ElementNotFound):
        loc.locate(el)


def test_ada_file_tapi_tidak_di_layar(tmp_path):
    (tmp_path / "z.png").write_bytes(_png())
    screen = FakeScreen()
    screen.auto_match = False
    loc = ImageLocator(screen, str(tmp_path), retry={"max_attempts": 1, "interval_sec": 0})
    el = ElemenUI(nama="z", image="z.png")
    with pytest.raises(ElementNotFound):
        loc.locate(el)
