"""Adapter pyautogui + pyperclip. Satu-satunya modul yang boleh impor pyautogui."""

from __future__ import annotations

from otobpn.screen.protocol import Box

try:
    import pyautogui
    import pyperclip
except ImportError:  # lingkungan tes tanpa GUI
    pyautogui = None  # type: ignore[assignment]
    pyperclip = None  # type: ignore[assignment]


class PyAutoGuiAdapter:
    """Akses layar nyata. FAILSAFE aktif: geser mouse ke sudut kiri-atas = stop."""

    def __init__(self) -> None:
        if pyautogui is None:
            raise RuntimeError("pyautogui tidak terpasang")
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01

    def size(self) -> tuple[int, int]:
        s = pyautogui.size()
        return (int(s[0]), int(s[1]))

    def position(self) -> tuple[int, int]:
        p = pyautogui.position()
        return (int(p[0]), int(p[1]))

    def screenshot(self, region=None):
        return pyautogui.screenshot(region=region)

    def locate_on_screen(self, image_path, confidence, region, grayscale):
        try:
            loc = pyautogui.locateOnScreen(
                image_path,
                confidence=confidence,
                region=region,
                grayscale=grayscale,
            )
        except Exception:  # ImageNotFoundException / OpenCV
            return None
        if loc is None:
            return None
        return Box(int(loc.left), int(loc.top), int(loc.width), int(loc.height))

    def click(self, x, y, clicks=1, interval=0.0) -> None:
        pyautogui.click(x, y, clicks=clicks, interval=interval)

    def hotkey(self, *keys: str) -> None:
        pyautogui.hotkey(*keys)

    def press(self, key: str) -> None:
        pyautogui.press(key)

    def clipboard_set(self, teks: str) -> None:
        pyperclip.copy(str(teks))

    def clipboard_get(self) -> str:
        return str(pyperclip.paste() or "")
