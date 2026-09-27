from otobpn.domain.guards import RantaiLangkah
from otobpn.domain.models import HasilLangkah
from otobpn.errors import StopRequested
import pytest


def test_rantai_berhenti_jika_gagal():
    log = []
    r = RantaiLangkah(lambda: True, log.append)
    assert r.jalankan("a", lambda: HasilLangkah(True, "a"))
    assert not r.jalankan("b", lambda: HasilLangkah(False, "b", pesan="x"))


def test_skip_tidak_menggagalkan():
    r = RantaiLangkah(lambda: True, lambda _: None)
    assert r.jalankan("a", lambda: HasilLangkah(True, "a", dilewati=True))
    assert r.semua_sukses()


def test_stop_sebelum_aksi():
    r = RantaiLangkah(lambda: False, lambda _: None)
    with pytest.raises(StopRequested):
        r.jalankan("a", lambda: HasilLangkah(True, "a"))
