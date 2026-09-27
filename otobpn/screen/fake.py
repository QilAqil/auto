"""Port palsu untuk unit tes — tidak menyentuh OS."""

from __future__ import annotations

from otobpn.screen.protocol import Box


class FakeScreen:
    def __init__(self) -> None:
        self.clicks: list[tuple] = []
        self.hotkeys: list[tuple] = []
        self.clip = ""
        self.matches: dict[str, Box] = {}
        self.auto_match = True

    def size(self) -> tuple[int, int]:
        return (1920, 1080)

    def position(self) -> tuple[int, int]:
        return (10, 10)

    def screenshot(self, region=None):
        return None

    def locate_on_screen(self, image_path, confidence, region, grayscale):
        if image_path in self.matches:
            return self.matches[image_path]
        if self.auto_match:
            return Box(200, 150, 40, 16)
        return None

    def click(self, x, y, clicks=1, interval=0.0) -> None:
        self.clicks.append((x, y, clicks))

    def hotkey(self, *keys: str) -> None:
        self.hotkeys.append(keys)

    def press(self, key: str) -> None:
        self.hotkeys.append((key,))

    def clipboard_set(self, teks: str) -> None:
        self.clip = str(teks)

    def clipboard_get(self) -> str:
        return self.clip
