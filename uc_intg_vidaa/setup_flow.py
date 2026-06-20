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
from vidaa import AsyncVidaaTV, async_discover_udp, async_probe_ip

from uc_intg_vidaa.config import VidaaConfig, get_token_storage
from uc_intg_vidaa.const import DEFAULT_PORT
from uc_intg_vidaa.device import _MAC_PATTERN

_LOG = logging.getLogger(__name__)

MAX_PIN_ATTEMPTS = 3


class VidaaSetupFlow(BaseSetupFlow[VidaaConfig]):
    """Setup flow for VIDAA TV integration with PIN pairing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._pairing_tv: AsyncVidaaTV | None = None
        self._pin_attempts: int = 0
        self._pairing_mac: str | None = None
        self._mac_prompted: bool = False

    def get_manual_entry_form(self) -> RequestUserInput:
        self._mac_prompted = False
        return self._build_entry_form()

    def _build_entry_form(
        self,
        *,
        error: str | None = None,
        name: str = "VIDAA TV",
        host: str = "",
        mac: str = "",
    ) -> RequestUserInput:
        fields: list[dict[str, Any]] = []
        if error:
            fields.append({
                "id": "error",
                "label": {"en": "Error"},
                "field": {"label": {"value": {"en": f"⚠️ {error}"}}},
            })
        fields.extend([
            {
                "id": "info",
                "label": {"en": "Information"},
                "field": {
                    "label": {
                        "value": {
                            "en": "Make sure the TV is powered ON before continuing. "
                            "A pairing PIN will be displayed on the TV screen. The MAC "
                            "address is detected automatically - only enter it if asked."
                        }
                    }
                },
            },
            {
                "id": "name",
                "label": {"en": "TV Name"},
                "field": {"text": {"value": name}},
            },
            {
                "id": "host",
                "label": {"en": "IP Address"},
                "field": {"text": {"value": host}},
            },
            {
                "id": "mac",
                "label": {"en": "MAC Address (auto-detected; for Wake-on-LAN)"},
                "field": {"text": {"value": mac}},
            },
        ])
        return RequestUserInput({"en": "VIDAA TV Setup"}, fields)

    async def _cleanup_pairing_client(self) -> None:
        if self._pairing_tv:
            try:
                await self._pairing_tv.async_disconnect()
            except Exception:
                pass
            self._pairing_tv = None

    @staticmethod
    def _normalize_mac(mac: str | None) -> str:
        mac = (mac or "").strip().upper().replace("-", ":")
        if ":" not in mac and len(mac) == 12:
            mac = ":".join(mac[i : i + 2] for i in range(0, 12, 2))
        return mac if _MAC_PATTERN.match(mac) else ""

    async def _discover_mac(self, host: str) -> str:
        """Resolve the TV MAC from the network without an authenticated session.

        The MAC is required up front to generate dynamic MQTT credentials, so it
        is read from the TV's own announcements - the UPnP descriptor first, then
        the Vidaa UDP discovery response.
        """
        try:
            device = await async_probe_ip(host, timeout=3)
            if device and getattr(device, "mac", None):
                mac = self._normalize_mac(device.mac)
                if mac:
                    return mac
        except Exception as err:
            _LOG.debug("UPnP MAC probe failed for %s: %s", host, err)

        try:
            found = await async_discover_udp(timeout=4)
            device = found.get(host) if found else None
            if device and getattr(device, "mac", None):
                mac = self._normalize_mac(device.mac)
                if mac:
                    return mac
        except Exception as err:
            _LOG.debug("UDP MAC discovery failed for %s: %s", host, err)

        return ""

    async def _wait_for_token_persisted(self, timeout: float = 15.0) -> bool:
        """Wait until the pairing access token is actually written to storage.

        async_authenticate() returns as soon as the PIN is accepted, but the
        access token is issued asynchronously on a separate topic. Completing
        setup before it persists leaves the runtime session unauthenticated and
        the TV silently ignores every command.
        """
        cfg = self._pending_device_config
        if not cfg:
            return False

        storage = get_token_storage()
        elapsed = 0.0
        interval = 0.5
        while elapsed < timeout:
            status = await asyncio.to_thread(
                storage.get_token_status, self._pairing_mac, cfg.host, DEFAULT_PORT
            )
            if status.get("has_token") and status.get("access_valid"):
                return True
            await asyncio.sleep(interval)
            elapsed += interval
        return False

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
        mac = self._normalize_mac(input_values.get("mac", ""))

        _LOG.info("Setting up VIDAA TV at %s", host)

        await self._cleanup_pairing_client()
        self._pin_attempts = 0

        if not mac:
            mac = await self._discover_mac(host)
            if mac:
                _LOG.info("Discovered MAC %s for TV at %s", mac, host)
            elif not self._mac_prompted:
                self._mac_prompted = True
                _LOG.warning(
                    "Could not auto-discover MAC for %s; prompting for manual entry",
                    host,
                )
                return self._build_entry_form(
                    error=(
                        "Could not auto-detect the TV's MAC address. Please enter it "
                        "manually - you can find it in the TV's network/about settings."
                    ),
                    name=name,
                    host=host,
                )
            else:
                _LOG.warning(
                    "Proceeding without a MAC for %s; pairing may fail on TVs that "
                    "require dynamic authentication.",
                    host,
                )

        self._pairing_mac = mac or None

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
        except Exception as err:
            _LOG.debug("Device info query after pairing failed: %s", err)

        if not await self._wait_for_token_persisted():
            _LOG.warning("PIN accepted but no access token was persisted; re-prompting")
            try:
                await self._pairing_tv.async_start_pairing()
                await asyncio.sleep(1)
            except Exception:
                _LOG.debug("Could not re-trigger PIN display")
            return self._build_pin_screen(
                "Pairing didn't complete - the TV did not issue an access token. "
                "A new PIN is shown on the TV; please enter it."
            )

        _LOG.info("Access token persisted - pairing complete")
        await self._cleanup_pairing_client()
        return None
