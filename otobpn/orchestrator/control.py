"""Kontrol pause / stop / timeout yang thread-safe."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from otobpn.errors import StepTimeout, StopRequested


class KontrolAlur:
    """Event stop + run (set = boleh jalan). Dipakai GUI dan worker."""

    def __init__(self) -> None:
        self.stop_ev = threading.Event()
        self.run_ev = threading.Event()

    def reset_siap(self) -> None:
        """Mulai worker dalam keadaan paused sampai hotkey jeda."""
        self.stop_ev.clear()
        self.run_ev.clear()

    def minta_stop(self) -> None:
        self.stop_ev.set()
        self.run_ev.set()

    def toggle_jeda(self) -> bool:
        """Return True jika sekarang running."""
        if self.stop_ev.is_set():
            return False
        if self.run_ev.is_set():
            self.run_ev.clear()
            return False
        self.run_ev.set()
        return True

    def set_jeda(self, jeda: bool) -> None:
        if jeda:
            self.run_ev.clear()
        else:
            self.run_ev.set()

    def boleh_jalan(self) -> bool:
        return not self.stop_ev.is_set()

    def sedang_jeda(self) -> bool:
        return not self.run_ev.is_set()

    def tunggu_lanjut(self, interval: float = 0.1) -> None:
        while self.sedang_jeda() and self.boleh_jalan():
            time.sleep(interval)
        if not self.boleh_jalan():
            raise StopRequested("Stop saat jeda")


def tunggu_dengan_timeout(
    predikat: Callable[[], bool],
    timeout: float,
    interval: float = 0.2,
    boleh_jalan: Callable[[], bool] | None = None,
    label: str = "langkah",
) -> None:
    """Tunggu predikat True atau naikkan StepTimeout / StopRequested."""
    mulai = time.time()
    while True:
        if boleh_jalan and not boleh_jalan():
            raise StopRequested("Stop saat menunggu " + label)
        if predikat():
            return
        if time.time() - mulai >= timeout:
            raise StepTimeout(f"Timeout {timeout}s: {label}")
        time.sleep(interval)
