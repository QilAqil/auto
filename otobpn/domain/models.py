"""Model data langkah dan elemen UI (semua nilai dari config)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

LocateMode = Literal["image", "ocr"]


@dataclass
class Region:
    left: int
    top: int
    width: int
    height: int

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.width, self.height)

    @classmethod
    def from_list(cls, nilai: list | None) -> Region | None:
        if not nilai or len(nilai) != 4:
            return None
        return cls(int(nilai[0]), int(nilai[1]), int(nilai[2]), int(nilai[3]))


@dataclass
class ElemenUI:
    """Deskripsi elemen: template PNG di assets/ + offset klik dari tengah gambar."""

    nama: str
    enabled: bool = True
    mode: LocateMode = "image"
    image: str = ""
    confidence: float = 0.75
    offset_x: int = 0
    offset_y: int = 0
    region: Region | None = None
    cache_pad: int = 80

    @classmethod
    def from_dict(cls, nama: str, data: dict[str, Any]) -> ElemenUI:
        mode = str(data.get("mode", "image"))
        if mode not in ("image", "ocr"):
            mode = "image"
        return cls(
            nama=nama,
            enabled=bool(data.get("enabled", True)),
            mode=mode,  # type: ignore[arg-type]
            image=str(data.get("image", "")),
            confidence=float(data.get("confidence", 0.75)),
            offset_x=int(data.get("offset_x", 0) or 0),
            offset_y=int(data.get("offset_y", 0) or 0),
            region=Region.from_list(data.get("region")),
            cache_pad=int(data.get("cache_pad", 80)),
        )


@dataclass
class KolomDI:
    id: str
    enabled: bool = True
    nomor: str = ""
    tahun: str = ""
    tanggal: str = ""
    image: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KolomDI:
        return cls(
            id=str(data.get("id", "?")),
            enabled=bool(data.get("enabled", True)),
            nomor=str(data.get("nomor", "")),
            tahun=str(data.get("tahun", "")),
            tanggal=str(data.get("tanggal", "")),
            image=_nama_aset_di(data),
        )


def elemen_dari(nama: str, data: dict[str, Any] | None) -> ElemenUI:
    """Bangun ElemenUI dari blok config (selalu mode image)."""
    d = dict(data or {})
    d.setdefault("mode", "image")
    return ElemenUI.from_dict(nama, d)


@dataclass
class HasilLangkah:
    sukses: bool
    nama: str
    pesan: str = ""
    dilewati: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


def _nama_aset_di(data: dict[str, Any]) -> str:
    img = str(data.get("image") or "").strip()
    if img:
        return img
    kode = str(data.get("id") or "").strip().lower().replace(" ", "_")
    return f"label_{kode}.png" if kode else ""
