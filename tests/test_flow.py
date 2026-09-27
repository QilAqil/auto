from otobpn.actions.pejabat import aksi_pejabat
from otobpn.config_loader import load_config
from otobpn.orchestrator.context import buat_field
from otobpn.orchestrator.flow_bt import satu_putaran_bt
from otobpn.orchestrator.flow_su import satu_putaran_su
from otobpn.screen.fake import FakeScreen


def _cfg_cepat():
    cfg = load_config()
    cfg["delay"] = {k: 0 for k in (cfg.get("delay") or {})}
    cfg.setdefault("delay", {})
    cfg["delay"]["antar_field"] = 0
    cfg["delay"]["setelah_klik"] = 0
    cfg["delay"]["setelah_ketik"] = 0
    cfg["mode"]["verify_after_fill"] = False
    return cfg


def test_putaran_su_palsu():
    screen = FakeScreen()
    cfg = _cfg_cepat()
    field = buat_field(screen, cfg, lambda _: None, lambda: True)
    assert satu_putaran_su(field, cfg, lambda _: None, lambda: True)
    assert screen.clicks


def test_putaran_bt_palsu():
    screen = FakeScreen()
    cfg = _cfg_cepat()
    field = buat_field(screen, cfg, lambda _: None, lambda: True)
    assert satu_putaran_bt(field, cfg, lambda _: None, lambda: True)


def test_pejabat_skip_jika_disabled():
    screen = FakeScreen()
    cfg = _cfg_cepat()
    cfg["pembukuan"] = {"enabled": False}
    field = buat_field(screen, cfg, lambda _: None, lambda: True)
    hasil = aksi_pejabat(field, cfg, "pembukuan")
    assert hasil.dilewati
    assert not screen.clicks
