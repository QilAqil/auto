"""Aturan teks: validasi OCR, ekstraksi nama pemohon, normalisasi."""

from __future__ import annotations

import re


def validasi_teks(
    teks: str,
    allowlist: str | None = None,
    panjang_tepat: int | None = None,
    min_len: int | None = None,
    max_len: int | None = None,
) -> bool:
    """True jika teks lolos allowlist karakter dan aturan panjang."""
    t = (teks or "").strip()
    if not t:
        return False
    if allowlist:
        if any(ch not in allowlist for ch in t):
            return False
    if panjang_tepat is not None and len(t) != panjang_tepat:
        return False
    if min_len is not None and len(t) < min_len:
        return False
    if max_len is not None and len(t) > max_len:
        return False
    return True


def bersihkan_ocr(teks: str, allowlist: str | None = None) -> str:
    """Buang karakter di luar allowlist dan spasi berlebih."""
    t = (teks or "").replace("\n", " ").strip()
    if allowlist:
        t = "".join(ch for ch in t if ch in allowlist)
    return re.sub(r"\s+", " ", t).strip()


def normalisasi_untuk_verifikasi(teks: str) -> str:
    """Bandingkan hasil paste vs nilai kiriman tanpa peka spasi/case."""
    return re.sub(r"\s+", " ", (teks or "").strip()).casefold()


def teks_cocok(kirim: str, terbaca: str) -> bool:
    a = normalisasi_untuk_verifikasi(kirim)
    b = normalisasi_untuk_verifikasi(terbaca)
    if not a:
        return True
    return a == b or a in b


def ekstrak_nama_pemohon(teks_mentah: str) -> str:
    """Ambil nama murni dari field, buang boilerplate peraturan/template."""
    t = (teks_mentah or "").strip()
    if not t:
        return ""
    t = _buang_sampah_peraturan(t)
    t = _potong_pola_pemohon(t)
    return re.sub(r"^[:\-\.\s]+|[:\-\.\s]+$", "", t).strip()


def susun_template(template: str, nama: str) -> str:
    return (template or "{nama}").replace("{nama}", nama)


def gabung_sisip(isi_lama: str, teks_baru: str, mode: str) -> str:
    """Sisip teks ke field Petunjuk tanpa duplikasi."""
    baru = (teks_baru or "").strip()
    lama = (isi_lama or "").strip()
    if not baru:
        return lama
    if lama and baru in lama:
        return lama
    if mode == "timpa" or not lama:
        return baru
    if mode == "sisip_bawah":
        return f"{lama}\n{baru}"
    return f"{baru}\n{lama}"


_SAMPAH = (
    "Telah terpasang sesuai dengan Peraturan Pemerintah Nomor 24 Tahun 1997 "
    "jo Peraturan Menteri Negara Agraria/ Kepala Badan Pertanahan Nasional "
    "Nomor 3 Tahun 1997 Pasal 22 Ayat 1.",
    "Telah terpasang sesuai dengan Peraturan Pemerintah",
    "Telah terpasang sesuai dengan PP No. 24 Tahun 1997",
    "Batas-batas ditunjukan oleh :",
    "Batas-batas ditunjukkan oleh :",
    "Batas-batas ditunjukan oleh:",
    "Batas-batas ditunjukkan oleh:",
    "Ditetapkan dan diukur oleh",
)


def _buang_sampah_peraturan(teks: str) -> str:
    t = teks
    for s in _SAMPAH:
        t = re.compile(re.escape(s), re.IGNORECASE).sub("", t)
    return t.strip()


def _potong_pola_pemohon(teks: str) -> str:
    m = re.search(
        r"(?:oleh\s*:\s*)?([A-Za-z0-9\s\.,\'\/-]+?)(?:\s*\(\s*pemohon|\s*$)",
        teks,
        re.IGNORECASE,
    )
    if m and m.group(1).strip():
        return m.group(1).strip()
    if "(" in teks:
        return teks.split("(")[0].strip()
    baris = [ln.strip() for ln in teks.splitlines() if ln.strip()]
    return baris[0] if baris else teks
