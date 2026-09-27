"""Guard rantai langkah: langkah berikutnya hanya jika sebelumnya sukses."""

from __future__ import annotations

from collections.abc import Callable

from otobpn.domain.models import HasilLangkah
from otobpn.errors import StopRequested


class RantaiLangkah:
    """Jalankan aksi berurutan; berhenti aman jika gagal atau stop."""

    def __init__(
        self,
        harus_jalan: Callable[[], bool],
        log: Callable[[str], None],
        wajib_sukses: bool = True,
    ) -> None:
        self._jalan = harus_jalan
        self._log = log
        self._wajib = wajib_sukses
        self.hasil: list[HasilLangkah] = []

    def jalankan(
        self,
        nama: str,
        aksi: Callable[[], HasilLangkah],
        wajib: bool | None = None,
    ) -> bool:
        """Return False jika rantai harus berhenti."""
        if not self._jalan():
            raise StopRequested("Stop diminta sebelum " + nama)
        try:
            hasil = aksi()
        except StopRequested:
            raise
        except Exception as exc:  # noqa: BLE001 — dibungkus hasil langkah
            hasil = HasilLangkah(False, nama, pesan=str(exc))
        self.hasil.append(hasil)
        if hasil.dilewati:
            self._log(f"  [{nama}] dilewati")
            return True
        if hasil.sukses:
            self._log(f"  [{nama}] ok {hasil.pesan}".rstrip())
            return True
        self._log(f"  [{nama}] gagal: {hasil.pesan}")
        if wajib if wajib is not None else self._wajib:
            return False
        return True

    def semua_sukses(self) -> bool:
        return all(h.sukses or h.dilewati for h in self.hasil)
