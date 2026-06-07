"""
VIDAA TV select entities.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ucapi import select, StatusCodes
from ucapi_framework import SelectEntity

if TYPE_CHECKING:
    from uc_intg_vidaa.config import VidaaConfig
    from uc_intg_vidaa.device import VidaaDevice

_LOG = logging.getLogger(__name__)


class VidaaSourceSelect(SelectEntity):
    """Input source select for VIDAA TV."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"select.{device_config.identifier}.input"
        super().__init__(
            entity_id,
            f"{device_config.name} Input",
            {
                select.Attributes.STATE: select.States.UNKNOWN,
                select.Attributes.OPTIONS: [],
                select.Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return

        options = self._device.input_source_names
        current = self._device.source if self._device.source in options else ""
        self.update({
            select.Attributes.STATE: select.States.ON,
            select.Attributes.OPTIONS: options,
            select.Attributes.CURRENT_OPTION: current,
        })

    async def _handle_command(
        self, entity: select.Select, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == select.Commands.SELECT_OPTION:
            option = params.get("option", "") if params else ""
            if not option:
                return StatusCodes.BAD_REQUEST
            ok = await self._device.select_source(option)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED


class VidaaAppSelect(SelectEntity):
    """App launcher select for VIDAA TV."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"select.{device_config.identifier}.app"
        super().__init__(
            entity_id,
            f"{device_config.name} App",
            {
                select.Attributes.STATE: select.States.UNKNOWN,
                select.Attributes.OPTIONS: [],
                select.Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return

        options = self._device.app_names
        if not options:
            options = ["No apps available"]
        current = self._device.app if self._device.app in options else ""
        self.update({
            select.Attributes.STATE: select.States.ON,
            select.Attributes.OPTIONS: options,
            select.Attributes.CURRENT_OPTION: current,
        })

    async def _handle_command(
        self, entity: select.Select, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == select.Commands.SELECT_OPTION:
            option = params.get("option", "") if params else ""
            if not option or option == "No apps available":
                return StatusCodes.BAD_REQUEST
            ok = await self._device.launch_app(option)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED
