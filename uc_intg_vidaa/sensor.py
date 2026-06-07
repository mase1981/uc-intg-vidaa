"""
VIDAA TV sensor entities.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ucapi import sensor
from ucapi_framework import SensorEntity

if TYPE_CHECKING:
    from uc_intg_vidaa.config import VidaaConfig
    from uc_intg_vidaa.device import VidaaDevice

_LOG = logging.getLogger(__name__)


class VidaaConnectionSensor(SensorEntity):
    """Connection status sensor for VIDAA TV."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"sensor.{device_config.identifier}.connection"
        super().__init__(
            entity_id,
            f"{device_config.name} Connection",
            [],
            {
                sensor.Attributes.STATE: sensor.States.UNKNOWN,
                sensor.Attributes.VALUE: "",
            },
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({
                sensor.Attributes.STATE: sensor.States.UNAVAILABLE,
                sensor.Attributes.VALUE: "Unavailable",
            })
            return
        self.update({
            sensor.Attributes.STATE: sensor.States.ON,
            sensor.Attributes.VALUE: "Connected" if self._device.connected else "Disconnected",
        })


class VidaaSourceSensor(SensorEntity):
    """Current app/source sensor for VIDAA TV."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"sensor.{device_config.identifier}.source"
        super().__init__(
            entity_id,
            f"{device_config.name} Source",
            [],
            {
                sensor.Attributes.STATE: sensor.States.UNKNOWN,
                sensor.Attributes.VALUE: "",
            },
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({
                sensor.Attributes.STATE: sensor.States.UNAVAILABLE,
                sensor.Attributes.VALUE: "Unavailable",
            })
            return
        if not self._device.tv_on:
            self.update({
                sensor.Attributes.STATE: sensor.States.ON,
                sensor.Attributes.VALUE: "Off",
            })
            return
        self.update({
            sensor.Attributes.STATE: sensor.States.ON,
            sensor.Attributes.VALUE: self._device.source or "Unknown",
        })


class VidaaModelSensor(SensorEntity):
    """TV model sensor for VIDAA TV."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"sensor.{device_config.identifier}.model"
        super().__init__(
            entity_id,
            f"{device_config.name} Model",
            [],
            {
                sensor.Attributes.STATE: sensor.States.UNKNOWN,
                sensor.Attributes.VALUE: "",
            },
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({sensor.Attributes.STATE: sensor.States.UNAVAILABLE})
            return
        self.update({
            sensor.Attributes.STATE: sensor.States.ON,
            sensor.Attributes.VALUE: self._device.model or "Unknown",
        })


class VidaaFirmwareSensor(SensorEntity):
    """Firmware version sensor for VIDAA TV."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"sensor.{device_config.identifier}.firmware"
        super().__init__(
            entity_id,
            f"{device_config.name} Firmware",
            [],
            {
                sensor.Attributes.STATE: sensor.States.UNKNOWN,
                sensor.Attributes.VALUE: "",
            },
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: ""},
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({sensor.Attributes.STATE: sensor.States.UNAVAILABLE})
            return
        self.update({
            sensor.Attributes.STATE: sensor.States.ON,
            sensor.Attributes.VALUE: self._device.sw_version or "Unknown",
        })
