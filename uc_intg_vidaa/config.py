"""
VIDAA TV configuration for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from ucapi_framework import BaseConfigManager
from vidaa import TokenStorage

from uc_intg_vidaa.const import DEFAULT_PORT, TOKEN_FILE


@dataclass
class VidaaConfig:
    """VIDAA TV configuration."""

    identifier: str = ""
    name: str = ""
    host: str = ""
    port: int = DEFAULT_PORT
    mac: str = ""
    model: str = ""
    sw_version: str = ""


class VidaaConfigManager(BaseConfigManager[VidaaConfig]):
    pass


def get_token_storage() -> TokenStorage:
    """Return the token storage shared by setup flow and devices."""
    config_home = os.getenv("UC_CONFIG_HOME") or os.getenv("UC_DATA_HOME") or ""
    base = Path(config_home).absolute() if config_home else Path.cwd()
    return TokenStorage(base / TOKEN_FILE)
