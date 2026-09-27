from otobpn.config_loader import _with_defaults, load_config
from otobpn.errors import ConfigError
import pytest
from types import SimpleNamespace


def test_defaults_mengisi_hotkey_dan_mode():
    cfg = _with_defaults({})
    assert cfg["hotkey"]["mulai_su"] == "\\"
    assert cfg["hotkey"]["mulai_bt"] == "`"
    assert cfg["hotkey"]["mulai"] == "f1"
    assert cfg["mode"]["verify_after_fill"] is True
    assert cfg["retry"]["max_attempts"] == 3


def test_load_config_nyata():
    cfg = load_config()
    assert "pembukuan" in cfg
    assert "daftar_isian" in cfg
    assert cfg["hotkey"]["exit"] == "esc"


def test_load_hilang(tmp_path):
    with pytest.raises(ConfigError):
        load_config(str(tmp_path / "tidak_ada.yaml"))


def test_simpan_su_mempertahankan_confidence_penomoran(monkeypatch):
    from otobpn.gui import app as app_module

    tersimpan = {}
    monkeypatch.setattr(app_module, "save_config", lambda cfg: tersimpan.update(cfg))
    monkeypatch.setattr(app_module, "load_config", lambda: tersimpan)
    monkeypatch.setattr(app_module, "pejabat_ke_dict", lambda _: {})
    monkeypatch.setattr(app_module, "dl_ke_dict", lambda _: {})

    def var(nilai):
        return SimpleNamespace(get=lambda: nilai)

    app = SimpleNamespace(
        _cfg={"penomoran": {"confidence": 0.9}},
        _dry=var(False),
        _pen_en=var(True),
        _pen_val=var("04/04/2013"),
        _pen_img=var("label_tgl_penomoran.png"),
        _pen_ox=var("110"),
        _pen_oy=var("0"),
        _di_en=var(True),
        _panel_di=SimpleNamespace(get_data=lambda: []),
        _pb={},
        _ps={},
        _dl={},
        _logger=SimpleNamespace(tulis=lambda _: None),
    )

    app_module.AppDetil._simpan_su(app)

    assert tersimpan["penomoran"]["confidence"] == 0.9
