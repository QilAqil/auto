"""Logger thread-safe ke berkas laporan + callback UI."""

from __future__ import annotations

import os
import threading
from collections.abc import Callable
from datetime import datetime

from otobpn.paths import log_path

_LOCK = threading.Lock()
_MAX_BYTES = 1024 * 1024


class ProsesLogger:
    """Tulis `[timestamp] pesan` ke file. Aman dipanggil dari worker thread."""

    def __init__(
        self,
        path: str | None = None,
        ui_callback: Callable[[str], None] | None = None,
    ) -> None:
        self.path = path or log_path()
        self._ui = ui_callback

    def set_ui(self, callback: Callable[[str], None] | None) -> None:
        self._ui = callback

    def tulis(self, pesan: str, item: str = "", status: str = "") -> str:
        """Format laporan: timestamp, item opsional, status, pesan."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bagian = [f"[{ts}]"]
        if item:
            bagian.append(item)
        if status:
            bagian.append(status)
        bagian.append(pesan)
        baris = " ".join(bagian) + "\n"
        with _LOCK:
            self._rotasi_jika_perlu()
            try:
                with open(self.path, "a", encoding="utf-8", errors="replace") as f:
                    f.write(baris)
            except OSError:
                pass
        if self._ui:
            self._ui(baris)
        return baris

    def item_selesai(self, item: str, status: str) -> None:
        """Satu baris ringkas per record (sukses/gagal/dilewati)."""
        self.tulis("selesai", item=item, status=status)

    def _rotasi_jika_perlu(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            if os.path.getsize(self.path) <= _MAX_BYTES:
                return
            bak = self.path + ".bak"
            if os.path.exists(bak):
                os.remove(bak)
            os.rename(self.path, bak)
        except OSError:
            pass
