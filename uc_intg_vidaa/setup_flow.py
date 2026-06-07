"""
VIDAA TV setup flow for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ucapi import IntegrationSetupError, RequestUserInput, SetupError, UserDataResponse
from ucapi_framework import BaseSetupFlow
from vidaa import AsyncVidaaTV

from uc_intg_vidaa.config import VidaaConfig, get_token_storage
from uc_intg_vidaa.const import DEFAULT_PORT
from uc_intg_vidaa.device import extract_mac_from_device_info

_LOG = logging.getLogger(__name__)

MAX_PIN_ATTEMPTS = 3


class VidaaSetupFlow(BaseSetupFlow[VidaaConfig]):
    """Setup flow for VIDAA TV integration with PIN pairing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._pairing_tv: AsyncVidaaTV | None = None
        self._pin_attempts: int = 0

    def get_manual_entry_form(self) -> RequestUserInput:
        return RequestUserInput(
            {"en": "VIDAA TV Setup"},
            [
                {
                    "id": "info",
                    "label": {"en": "Information"},
                    "field": {
                        "label": {
                            "value": {
                                "en": "Make sure the TV is powered ON before continuing. "
                                "A pairing PIN will be displayed on the TV screen."
                            }
                        }
                    },
                },
                {
                    "id": "name",
                    "label": {"en": "TV Name"},
                    "field": {"text": {"value": "VIDAA TV"}},
                },
                {
                    "id": "host",
                    "label": {"en": "IP Address"},
                    "field": {"text": {"value": ""}},
                },
                {
                    "id": "mac",
                    "label": {"en": "MAC Address (optional, for Wake-on-LAN)"},
                    "field": {"text": {"value": ""}},
                },
            ],
        )

    async def _cleanup_pairing_client(self) -> None:
        if self._pairing_tv:
            try:
                await self._pairing_tv.async_disconnect()
            except Exception:
                pass
            self._pairing_tv = None

    def _build_pin_screen(self, error: str | None = None) -> RequestUserInput:
        fields: list[dict[str, Any]] = []
        if error:
            fields.append({
                "id": "error",
                "label": {"en": "Error"},
                "field": {"label": {"value": {"en": f"⚠️ {error}"}}},
            })
        fields.append({
            "id": "info",
            "label": {"en": "Pairing"},
            "field": {
                "label": {
                    "value": {
                        "en": "A 4-digit PIN is now displayed on your TV screen. "
                        "Enter it below to complete pairing."
                    }
                }
            },
        })
        fields.append({
            "id": "pin",
            "label": {"en": "PIN Code"},
            "field": {"text": {"value": ""}},
        })
        return RequestUserInput({"en": "Enter PIN from TV"}, fields)

    async def query_device(
        self, input_values: dict[str, Any]
    ) -> VidaaConfig | SetupError | RequestUserInput:
        host = input_values.get("host", "").strip()
        if not host:
            raise ValueError("IP address is required")

        name = input_values.get("name", "").strip() or f"VIDAA TV ({host})"
        mac = input_values.get("mac", "").strip().upper().replace("-", ":")

        _LOG.info("Setting up VIDAA TV at %s", host)

        await self._cleanup_pairing_client()
        self._pin_attempts = 0

        tv = AsyncVidaaTV(
            host=host,
            port=DEFAULT_PORT,
            use_dynamic_auth=True,
            mac_address=mac or None,
            enable_persistence=True,
            storage=get_token_storage(),
        )

        try:
            connected = await tv.async_connect(timeout=10)
        except Exception as err:
            _LOG.error("Connection to %s failed: %s", host, err)
            connected = False

        if not connected:
            try:
                await tv.async_disconnect()
            except Exception:
                pass
            raise ValueError(
                f"Cannot reach TV at {host}. "
                "Verify the TV is powered on and on the same network."
            )

        model = ""
        sw_version = ""
        try:
            device_info = await tv.async_get_device_info(timeout=5)
            if device_info:
                name = device_info.get("tv_name") or name
                model = device_info.get("model_name") or ""
                sw_version = device_info.get("tv_version") or ""
                info_mac = extract_mac_from_device_info(device_info)
                if info_mac:
                    mac = info_mac
        except Exception as err:
            _LOG.debug("Device info query failed during setup: %s", err)

        if mac:
            identifier = f"vidaa_{mac.replace(':', '').lower()}"
        else:
            identifier = f"vidaa_{host.replace('.', '_').replace(':', '_')}"

        config = VidaaConfig(
            identifier=identifier,
            name=name,
            host=host,
            port=DEFAULT_PORT,
            mac=mac,
            model=model,
            sw_version=sw_version,
        )

        if tv.is_authenticated:
            _LOG.info("TV already authenticated with saved token, skipping pairing")
            await tv.async_disconnect()
            return config

        try:
            await tv.async_start_pairing()
            await asyncio.sleep(1)
        except Exception as err:
            _LOG.error("Failed to start pairing: %s", err)
            await tv.async_disconnect()
            raise ValueError(f"Failed to start pairing with TV: {err}") from err

        self._pairing_tv = tv
        self._pending_device_config = config
        return self._build_pin_screen()

    async def handle_additional_configuration_response(
        self, msg: UserDataResponse
    ) -> RequestUserInput | SetupError | VidaaConfig | None:
        pin = msg.input_values.get("pin", "").strip()

        if not self._pairing_tv:
            _LOG.error("No active pairing session")
            return SetupError(error_type=IntegrationSetupError.OTHER)

        if not pin:
            return self._build_pin_screen("Please enter the PIN shown on the TV.")

        self._pin_attempts += 1
        if self._pin_attempts > MAX_PIN_ATTEMPTS:
            _LOG.error("Too many PIN attempts")
            await self._cleanup_pairing_client()
            return SetupError(error_type=IntegrationSetupError.AUTHORIZATION_ERROR)

        try:
            success = await self._pairing_tv.async_authenticate(pin, timeout=10)
        except Exception as err:
            _LOG.error("Authentication error: %s", err)
            success = False

        if not success:
            _LOG.warning("PIN authentication failed (attempt %d)", self._pin_attempts)
            try:
                await self._pairing_tv.async_start_pairing()
                await asyncio.sleep(1)
            except Exception:
                _LOG.debug("Could not re-trigger PIN display")
            return self._build_pin_screen(
                "Invalid PIN. A new PIN is displayed on the TV - please try again."
            )

        _LOG.info("PIN authentication successful")

        try:
            device_info = await self._pairing_tv.async_get_device_info(timeout=5)
            if device_info and self._pending_device_config:
                self._pending_device_config.name = (
                    device_info.get("tv_name") or self._pending_device_config.name
                )
                self._pending_device_config.model = (
                    device_info.get("model_name") or self._pending_device_config.model
                )
                self._pending_device_config.sw_version = (
                    device_info.get("tv_version") or self._pending_device_config.sw_version
                )
                info_mac = extract_mac_from_device_info(device_info)
                if info_mac:
                    self._pending_device_config.mac = info_mac
                    self._pending_device_config.identifier = (
                        f"vidaa_{info_mac.replace(':', '').lower()}"
                    )
        except Exception as err:
            _LOG.debug("Device info query after pairing failed: %s", err)

        await self._cleanup_pairing_client()
        return None
