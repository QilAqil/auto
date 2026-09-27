"""Adapter dry-run: tidak menggerakkan mouse; hanya mencatat aksi."""

from __future__ import annotations

from collections.abc import Callable

from otobpn.screen.protocol import Box


class DryRunAdapter:
    """Untuk uji alur tanpa menyentuh UI BPN."""

    def __init__(self, log: Callable[[str], None], screen_size=(1920, 1080)) -> None:
        self._log = log
        self._size = screen_size
        self._clip = ""
        self.aksi: list[str] = []

    def size(self) -> tuple[int, int]:
        return self._size

    def position(self) -> tuple[int, int]:
        return (0, 0)

    def screenshot(self, region=None):
        self._catat(f"screenshot region={region}")
        return None

    def locate_on_screen(self, image_path, confidence, region, grayscale):
        self._catat(f"locate {image_path} conf={confidence} region={region}")
        # dry-run: anggap ketemu di tengah region atau layar
        if region:
            return Box(region[0], region[1], max(region[2], 10), max(region[3], 10))
        return Box(100, 100, 40, 20)

    def click(self, x, y, clicks=1, interval=0.0) -> None:
        self._catat(f"click ({x},{y}) n={clicks}")

    def hotkey(self, *keys: str) -> None:
        self._catat("hotkey " + "+".join(keys))

    def press(self, key: str) -> None:
        self._catat(f"press {key}")

    def clipboard_set(self, teks: str) -> None:
        self._clip = str(teks)
        self._catat(f"clipboard_set {teks[:80]!r}")

    def clipboard_get(self) -> str:
        return self._clip

    def _catat(self, pesan: str) -> None:
        self.aksi.append(pesan)
        self._log(f"  [DRY] {pesan}")
