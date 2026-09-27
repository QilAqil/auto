"""Pengecualian domain otomasi — tanpa ketergantungan layar."""


class OtobpnError(Exception):
    """Kesalahan dasar aplikasi."""


class ConfigError(OtobpnError):
    """Config.yaml tidak valid atau tidak terbaca."""


class ElementNotFound(OtobpnError):
    """Template atau elemen UI tidak ditemukan di layar."""


class OCRFailed(OtobpnError):
    """OCR gagal atau teks tidak lolos validasi."""


class StepTimeout(OtobpnError):
    """Langkah melebihi batas waktu."""


class VerificationFailed(OtobpnError):
    """Isi field setelah paste tidak cocok dengan nilai yang dikirim."""


class StopRequested(OtobpnError):
    """Pengguna menekan stop / exit; alur harus berhenti aman."""
