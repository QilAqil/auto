"""Protokol ScreenPort: satu-satunya jembatan ke mouse/keyboard/screenshot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class Box:
    left: int
    top: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.left + self.width // 2, self.top + self.height // 2)


class ScreenPort(Protocol):
    """Implementasi nyata: PyAutoGuiAdapter. Tes: FakeScreen."""

    def size(self) -> tuple[int, int]: ...

    def position(self) -> tuple[int, int]: ...

    def screenshot(self, region: tuple[int, int, int, int] | None = None) -> Any: ...

    def locate_on_screen(
        self,
        image_path: str,
        confidence: float,
        region: tuple[int, int, int, int] | None,
        grayscale: bool,
    ) -> Box | None: ...

    def click(self, x: int, y: int, clicks: int = 1, interval: float = 0.0) -> None: ...

    def hotkey(self, *keys: str) -> None: ...

    def press(self, key: str) -> None: ...

    def clipboard_set(self, teks: str) -> None: ...

    def clipboard_get(self) -> str: ...
