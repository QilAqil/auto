from otobpn.domain.text_rules import (
    bersihkan_ocr,
    ekstrak_nama_pemohon,
    gabung_sisip,
    susun_template,
    teks_cocok,
    validasi_teks,
)


def test_validasi_panjang_tepat():
    assert validasi_teks("ABC123", allowlist="ABC123", panjang_tepat=6)
    assert not validasi_teks("ABC12", panjang_tepat=6)


def test_bersihkan_ocr_allowlist():
    assert bersihkan_ocr("AB#C", allowlist="ABC") == "ABC"


def test_teks_cocok_abaikan_spasi():
    assert teks_cocok("kepala seksi", "kepala  seksi")


def test_ekstrak_nama_dari_template():
    mentah = "Batas-batas ditunjukan oleh : SUYANTI (pemohon)"
    assert ekstrak_nama_pemohon(mentah) == "SUYANTI"


def test_template_nama():
    assert "SUYANTI" in susun_template("{nama} (pemohon)", "SUYANTI")


def test_sisip_tidak_duplikat():
    lama = "AAA\nBBB"
    assert gabung_sisip(lama, "AAA", "sisip_atas") == lama
    assert gabung_sisip(lama, "CCC", "sisip_atas").startswith("CCC")
