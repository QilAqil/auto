"""Bangun AksiField + locator dari config (dipakai SU dan BT)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from otobpn.actions.field import AksiField
from otobpn.domain.models import Region
from otobpn.paths import assets_dir
from otobpn.screen.protocol import ScreenPort
from otobpn.vision.locator import ImageLocator


def buat_field(
    screen: ScreenPort,
    cfg: dict[str, Any],
    log: Callable[[str], None],
    harus_jalan: Callable[[], bool],
) -> AksiField:
    locator = ImageLocator(
        screen,
        assets_dir(),
        retry=cfg.get("retry"),
        grayscale=bool(cfg.get("locator", {}).get("grayscale", True)),
        cfg=cfg,
    )
    region = Region.from_list(cfg.get("search_region"))
    return AksiField(screen, locator, cfg, log, harus_jalan, region)
