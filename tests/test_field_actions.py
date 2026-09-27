from otobpn.actions.field import AksiField
from otobpn.domain.models import ElemenUI, Region
from otobpn.screen.fake import FakeScreen
from otobpn.vision.locator import ImageLocator


def test_isi_elemen_triple_click_dan_paste(tmp_path):
    png = tmp_path / "tahun.png"
    png.write_bytes(_png())
    screen = FakeScreen()
    loc = ImageLocator(screen, str(tmp_path), retry={"max_attempts": 1, "interval_sec": 0})
    cfg = {"delay": {}, "mode": {"verify_after_fill": True, "dry_run": False}}
    aksi = AksiField(screen, loc, cfg, lambda _: None, lambda: True, Region(0, 0, 800, 600))
    el = ElemenUI(nama="tahun", image="tahun.png", offset_x=10, offset_y=5)
    aksi.isi_elemen(el, "1900", "tahun")
    assert screen.clicks
    assert any(c[2] == 3 for c in screen.clicks)
    assert ("ctrl", "v") in screen.hotkeys
    assert screen.clip == "1900"


def test_temukan_fallback_ocr_ketika_template_gagal(monkeypatch):
    screen = FakeScreen()
    screen.auto_match = False
    loc = ImageLocator(screen, ".", retry={"max_attempts": 1, "interval_sec": 0})
    cfg = {
        "delay": {},
        "mode": {"verify_after_fill": False, "dry_run": False},
        "ocr": {"enabled": True},
    }

    def fake_cari(self, citra, target, allowlist=None, **kwargs):
        assert target.lower() == "jabatan"
        return (240, 135)

    monkeypatch.setattr("otobpn.vision.ocr.ModulOCR.cari_teks", fake_cari)

    aksi = AksiField(screen, loc, cfg, lambda _: None, lambda: True, Region(0, 0, 800, 600))
    el = ElemenUI(nama="pembukuan.jabatan", image="label_pembukuan_jabatan.png", offset_x=10, offset_y=5)

    assert aksi.temukan(el) == (250, 140)


def _png() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
