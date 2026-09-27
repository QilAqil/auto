"""Loop putaran SU/BT: jeda antar record, resume, error handling."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, Literal

from otobpn.domain.resume import muat_state, simpan_state
from otobpn.errors import (
    ElementNotFound,
    OCRFailed,
    StopRequested,
    StepTimeout,
    VerificationFailed,
)
from otobpn.logger import ProsesLogger
from otobpn.orchestrator.context import buat_field
from otobpn.orchestrator.control import KontrolAlur
from otobpn.orchestrator.flow_bt import satu_putaran_bt
from otobpn.orchestrator.flow_su import satu_putaran_su
from otobpn.paths import state_path
from otobpn.screen.dry_run_adapter import DryRunAdapter
from otobpn.screen.protocol import ScreenPort
from otobpn.screen.pyautogui_adapter import PyAutoGuiAdapter

Mode = Literal["su", "bt"]


def buat_screen(cfg: dict[str, Any], log: Callable[[str], None]) -> ScreenPort:
    if cfg.get("mode", {}).get("dry_run"):
        log("mode dry-run: mouse tidak digerakkan")
        return DryRunAdapter(log)
    return PyAutoGuiAdapter()


def jalankan_loop(
    mode: Mode,
    cfg: dict[str, Any],
    kontrol: KontrolAlur,
    logger: ProsesLogger,
    progress: Callable[[str], None],
    after_putaran: Callable[[], None] | None = None,
) -> None:
    """Loop sampai stop. Setelah tiap record: auto-jeda (lanjut via hotkey)."""
    log = logger.tulis
    screen = buat_screen(cfg, log)
    field = buat_field(screen, cfg, log, kontrol.boleh_jalan)
    putaran = _putaran_awal(mode, cfg)
    alur = satu_putaran_su if mode == "su" else satu_putaran_bt
    log(f"mulai loop {mode.upper()} putaran={putaran}")
    try:
        while kontrol.boleh_jalan():
            kontrol.tunggu_lanjut()
            putaran += 1
            progress(f"Putaran ke-{putaran}")
            log(f"-- {mode.upper()} putaran {putaran} --")
            ok = _jalankan_satu(alur, field, cfg, log, kontrol)
            _catat_hasil(logger, mode, putaran, ok, cfg)
            if not kontrol.boleh_jalan():
                break
            if after_putaran:
                after_putaran()
            else:
                kontrol.set_jeda(True)
                log("selesai isi — tekan jeda untuk record berikutnya")
            time.sleep(float((cfg.get("delay") or {}).get("antar_putaran", 0.3)))
    except StopRequested:
        log("safe-stop: alur dihentikan")
    log(f"berhenti {mode.upper()} total={putaran}")


def _jalankan_satu(alur, field, cfg, log, kontrol) -> bool:
    try:
        return alur(field, cfg, log, kontrol.boleh_jalan)
    except StopRequested:
        raise
    except ElementNotFound as exc:
        log(f"elemen tidak ditemukan: {exc}")
    except OCRFailed as exc:
        log(f"OCR gagal: {exc}")
    except StepTimeout as exc:
        log(f"timeout: {exc}")
    except VerificationFailed as exc:
        log(f"verifikasi gagal: {exc}")
        if cfg.get("mode", {}).get("stop_on_verify_fail", False):
            return False
    except Exception as exc:  # noqa: BLE001
        log(f"kesalahan: {exc}")
    return False


def _putaran_awal(mode: Mode, cfg: dict[str, Any]) -> int:
    if not cfg.get("mode", {}).get("resume", True):
        return 0
    st = muat_state(state_path())
    kunci = "su_putaran" if mode == "su" else "bt_putaran"
    try:
        return int(st.get(kunci, 0) or 0)
    except (TypeError, ValueError):
        return 0


def _catat_hasil(logger: ProsesLogger, mode: Mode, putaran: int, ok: bool, cfg) -> None:
    status = "SUKSES" if ok else "GAGAL"
    logger.item_selesai(f"{mode.upper()}-{putaran}", status)
    if cfg.get("mode", {}).get("resume", True):
        st = muat_state(state_path())
        st["mode"] = mode
        st["su_putaran" if mode == "su" else "bt_putaran"] = putaran
        simpan_state(state_path(), st)
