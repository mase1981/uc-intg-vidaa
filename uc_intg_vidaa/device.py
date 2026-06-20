"""
VIDAA TV device implementation for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from ucapi_framework import PollingDevice
from vidaa import AsyncVidaaTV
from vidaa.topics import TOPIC_SET_SOURCE, get_topic
from vidaa.wol import wake_tv

from uc_intg_vidaa.config import VidaaConfig, get_token_storage
from uc_intg_vidaa.const import (
    INPUT_SOURCES,
    KNOWN_APPS,
    POLL_INTERVAL,
    STATE_FAKE_SLEEP,
)

_LOG = logging.getLogger(__name__)

_MAC_PATTERN = re.compile(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}")


class VidaaDevice(PollingDevice):
    """VIDAA TV implementation using PollingDevice."""

    def __init__(self, device_config: VidaaConfig, **kwargs: Any) -> None:
        super().__init__(device_config, poll_interval=POLL_INTERVAL, **kwargs)
        self._device_config = device_config
        self._tv: AsyncVidaaTV | None = None
        self._connect_lock: asyncio.Lock = asyncio.Lock()

        self._state: str = "UNAVAILABLE"
        self._tv_on: bool = False
        self._volume: int = 0
        self._muted: bool = False
        self._source: str = ""
        self._app: str = ""
        self._sources: list[dict[str, Any]] = []
        self._apps: list[dict[str, Any]] = []
        self._device_info_fetched: bool = False

    @property
    def identifier(self) -> str:
        return self._device_config.identifier

    @property
    def name(self) -> str:
        return self._device_config.name

    @property
    def address(self) -> str:
        return self._device_config.host

    @property
    def log_id(self) -> str:
        return f"{self.name} ({self.address})"

    @property
    def state(self) -> str:
        return self._state

    @property
    def tv_on(self) -> bool:
        return self._tv_on

    @property
    def connected(self) -> bool:
        return bool(self._tv and self._tv.is_connected)

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def muted(self) -> bool:
        return self._muted

    @property
    def source(self) -> str:
        return self._source

    @property
    def app(self) -> str:
        return self._app

    @property
    def model(self) -> str:
        return self._device_config.model

    @property
    def sw_version(self) -> str:
        return self._device_config.sw_version

    @property
    def apps(self) -> list[dict[str, Any]]:
        return self._apps

    @property
    def sources(self) -> list[dict[str, Any]]:
        return self._sources

    @property
    def app_names(self) -> list[str]:
        names = []
        for app in self._apps:
            name = app.get("name")
            if name and name not in names:
                names.append(name)
        return names

    @property
    def input_source_names(self) -> list[str]:
        names = []
        for src in self._sources:
            name = src.get("displayname") or src.get("sourcename")
            if name and name not in names:
                names.append(name)
        if not names:
            names = list(INPUT_SOURCES.keys())
        return names

    @property
    def source_list(self) -> list[str]:
        return self.input_source_names + self.app_names

    async def establish_connection(self) -> AsyncVidaaTV:
        _LOG.info("[%s] Establishing connection", self.log_id)
        # A single MQTT client must be used for the device's lifetime. Creating
        # a second client (same MQTT client ID) makes the TV kick the first
        # session, and the two paho reconnect loops then fight forever.
        async with self._connect_lock:
            if self._tv is None:
                self._tv = AsyncVidaaTV(
                    host=self._device_config.host,
                    port=self._device_config.port,
                    use_dynamic_auth=True,
                    mac_address=self._device_config.mac or None,
                    enable_persistence=True,
                    storage=get_token_storage(),
                )

            connected = self._tv.is_connected
            if not connected:
                try:
                    connected = await self._tv.async_connect(timeout=10)
                except Exception as err:
                    _LOG.debug("[%s] Connect attempt failed: %s", self.log_id, err)

            if connected:
                try:
                    await self._refresh_device_info()
                    await self._refresh_lists()
                    await self._update_state()
                except Exception as err:
                    _LOG.warning("[%s] Initial state query failed: %s", self.log_id, err)
                self._state = "ON" if self._tv_on else "OFF"
                _LOG.info("[%s] Connection established (TV %s)", self.log_id, self._state)
            else:
                # TV is unreachable (likely powered off) - keep entities available
                # so the user can still power it on via Wake-on-LAN.
                self._tv_on = False
                self._state = "OFF"
                _LOG.info("[%s] TV unreachable, assuming powered off", self.log_id)

            return self._tv

    async def _reconnect(self, timeout: float = 5) -> bool:
        async with self._connect_lock:
            if not self._tv:
                return False
            if self._tv.is_connected:
                return True
            try:
                return await self._tv.async_connect(timeout=timeout)
            except Exception as err:
                _LOG.debug("[%s] Reconnect failed: %s", self.log_id, err)
                return False

    async def poll_device(self) -> None:
        if not self._tv:
            return
        try:
            if not self._tv.is_connected:
                if not await self._reconnect():
                    if self._state != "OFF":
                        _LOG.info("[%s] TV is now OFF or unreachable", self.log_id)
                    self._tv_on = False
                    self._state = "OFF"
                    self.push_update()
                    return
                _LOG.info("[%s] Reconnected to TV", self.log_id)
                await self._refresh_device_info()
                await self._refresh_lists()

            await self._update_state()
            self._state = "ON" if self._tv_on else "OFF"
            self.push_update()
        except Exception as err:
            _LOG.debug("[%s] Poll error: %s", self.log_id, err)
            self._tv_on = False
            self._state = "OFF"
            self.push_update()

    async def _update_state(self) -> None:
        state = await self._tv.async_get_state(timeout=3)

        if state and state.get("statetype") != STATE_FAKE_SLEEP:
            self._tv_on = True
            statetype = state.get("statetype")
            if statetype == "app":
                app_key = str(state.get("name", "")).lower()
                if app_key in KNOWN_APPS:
                    self._app = KNOWN_APPS[app_key]
                else:
                    self._app = str(state.get("name", "")).capitalize()
                self._source = self._app
            elif statetype == "sourceswitch":
                self._app = ""
                self._source = state.get("displayname") or state.get("sourcename") or ""

            try:
                volume = await self._tv.async_get_volume(timeout=2)
                if volume is not None:
                    self._volume = int(volume)
                self._muted = self._tv.is_muted
            except Exception as err:
                _LOG.debug("[%s] Volume query failed: %s", self.log_id, err)
        else:
            self._tv_on = False
            self._app = ""

    async def _refresh_device_info(self) -> None:
        if self._device_info_fetched:
            return
        try:
            device_info = await self._tv.async_get_device_info(timeout=5)
        except Exception as err:
            _LOG.debug("[%s] Device info query failed: %s", self.log_id, err)
            return
        if not device_info:
            return

        updates: dict[str, Any] = {}
        model = device_info.get("model_name")
        sw_version = device_info.get("tv_version")

        if model and model != self._device_config.model:
            updates["model"] = model
        if sw_version and sw_version != self._device_config.sw_version:
            updates["sw_version"] = sw_version

        # The MAC is intentionally not updated here: it is the seed for dynamic
        # MQTT credential generation, so it must stay identical to the value
        # established during setup. Changing it would invalidate the session.

        if updates:
            self.update_config(**updates)
        self._device_info_fetched = True

    async def _refresh_lists(self) -> None:
        try:
            sources = await self._tv.async_get_sources(timeout=5)
            if sources and isinstance(sources, list):
                self._sources = [s for s in sources if isinstance(s, dict)]
        except Exception as err:
            _LOG.debug("[%s] Source list query failed: %s", self.log_id, err)

        try:
            apps = await self._tv.async_get_apps(timeout=5)
            if apps and isinstance(apps, list):
                self._apps = [a for a in apps if isinstance(a, dict) and a.get("name")]
        except Exception as err:
            _LOG.debug("[%s] App list query failed: %s", self.log_id, err)

    async def disconnect(self) -> None:
        async with self._connect_lock:
            if self._tv:
                try:
                    await self._tv.async_disconnect()
                except Exception as err:
                    _LOG.debug("[%s] Disconnect error: %s", self.log_id, err)
                self._tv = None
        self._tv_on = False
        self._device_info_fetched = False
        self._state = "UNAVAILABLE"
        await super().disconnect()

    async def power_on(self) -> bool:
        _LOG.info("[%s] Power on", self.log_id)
        if self._device_config.mac:
            host = self._device_config.host
            subnet = host.rsplit(".", 1)[0] if "." in host else None
            try:
                await asyncio.to_thread(wake_tv, self._device_config.mac, subnet)
                _LOG.info("[%s] Sent WoL to %s", self.log_id, self._device_config.mac)
            except Exception as err:
                _LOG.warning("[%s] WoL failed: %s", self.log_id, err)

        if self._tv and self._tv.is_connected:
            try:
                await self._tv.async_power_on()
            except Exception as err:
                _LOG.debug("[%s] Power on command failed: %s", self.log_id, err)

        self._tv_on = True
        self._state = "ON"
        self.push_update()
        return True

    async def power_off(self) -> bool:
        _LOG.info("[%s] Power off", self.log_id)
        if not await self._ensure_connected():
            return False
        try:
            await self._tv.async_power_off()
        except Exception as err:
            _LOG.error("[%s] Power off failed: %s", self.log_id, err)
            return False
        self._tv_on = False
        self._state = "OFF"
        self.push_update()
        return True

    async def power_toggle(self) -> bool:
        if self._tv_on:
            return await self.power_off()
        return await self.power_on()

    async def _ensure_connected(self) -> bool:
        """Make sure the client is connected before sending a command."""
        if not self._tv:
            return False
        if self._tv.is_connected:
            return True
        return await self._reconnect()

    async def send_key(self, key: str) -> bool:
        if not await self._ensure_connected():
            _LOG.warning("[%s] Cannot send key %s: not connected", self.log_id, key)
            return False
        try:
            return await self._tv.async_send_key(key)
        except Exception as err:
            _LOG.error("[%s] Send key %s failed: %s", self.log_id, key, err)
            return False

    async def set_volume(self, volume: int) -> bool:
        if not await self._ensure_connected():
            return False
        volume = max(0, min(100, int(volume)))
        try:
            ok = await self._tv.async_set_volume(volume)
        except Exception as err:
            _LOG.error("[%s] Set volume failed: %s", self.log_id, err)
            return False
        if ok:
            self._volume = volume
            self.push_update()
        return ok

    async def volume_up(self) -> bool:
        ok = await self.send_key("KEY_VOLUMEUP")
        if ok:
            self._volume = min(100, self._volume + 1)
            self.push_update()
        return ok

    async def volume_down(self) -> bool:
        ok = await self.send_key("KEY_VOLUMEDOWN")
        if ok:
            self._volume = max(0, self._volume - 1)
            self.push_update()
        return ok

    async def mute_toggle(self) -> bool:
        ok = await self.send_key("KEY_MUTE")
        if ok:
            self._muted = not self._muted
            self.push_update()
        return ok

    def _find_source(self, query: str) -> dict[str, Any] | None:
        """Find a TV source entry by display name or source name (space/case tolerant)."""
        normalized = query.lower().replace(" ", "")
        if not normalized:
            return None
        for src in self._sources:
            for key in ("displayname", "sourcename"):
                name = str(src.get(key) or "")
                if name and name.lower().replace(" ", "") == normalized:
                    return src
        return None

    async def _send_changesource(self, source: dict[str, Any]) -> bool:
        """Publish changesource with the full source entry (id + name).

        VIDAA firmwares ignore changesource for physical HDMI inputs unless
        sourcename is sent alongside sourceid (vidaa-control only sends the id).
        """
        tv = self._tv
        payload = {
            "sourceid": source.get("sourceid"),
            "sourcename": source.get("sourcename"),
        }

        def _send() -> bool:
            client = tv._ensure_client()
            topic = get_topic(TOPIC_SET_SOURCE, client.client_id)
            return client._publish(topic, payload)

        try:
            return await tv._run_in_executor(_send)
        except Exception as err:
            _LOG.error("[%s] changesource failed: %s", self.log_id, err)
            return False

    async def select_source(self, source: str) -> bool:
        if not await self._ensure_connected():
            return False

        src = self._find_source(source)
        if src:
            ok = await self._send_changesource(src)
            if ok:
                self._source = src.get("displayname") or src.get("sourcename") or source
                self._app = ""
                self.push_update()
            return ok

        source_key = INPUT_SOURCES.get(source)
        if source_key:
            ok = await self._set_source(source_key)
            if ok:
                self._source = source
                self._app = ""
                self.push_update()
            return ok

        return await self.launch_app(source)

    async def _set_source(self, source: str) -> bool:
        try:
            return await self._tv.async_set_source(source)
        except Exception as err:
            _LOG.error("[%s] Set source %s failed: %s", self.log_id, source, err)
            return False

    async def set_input(self, source_key: str) -> bool:
        """Switch to an input by vidaa-control source key (e.g. 'hdmi1')."""
        if not await self._ensure_connected():
            return False

        src = self._find_source(source_key)
        if src:
            ok = await self._send_changesource(src)
        else:
            ok = await self._set_source(source_key)

        if ok:
            if src:
                self._source = src.get("displayname") or src.get("sourcename") or source_key
            else:
                for display, key in INPUT_SOURCES.items():
                    if key == source_key:
                        self._source = display
                        break
            self._app = ""
            self.push_update()
        return ok

    async def launch_app(self, app_name: str) -> bool:
        if not await self._ensure_connected():
            return False

        target: Any = app_name
        for app in self._apps:
            if app.get("name", "").upper() == app_name.upper():
                target = app
                break

        try:
            ok = await self._tv.async_launch_app(target)
        except Exception as err:
            _LOG.error("[%s] Launch app %s failed: %s", self.log_id, app_name, err)
            return False
        if ok:
            display = target.get("name") if isinstance(target, dict) else app_name
            self._app = display
            self._source = display
            self.push_update()
        return ok
