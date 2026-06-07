"""
VIDAA TV remote entity.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ucapi import remote, StatusCodes
from ucapi.ui import Buttons, create_btn_mapping, create_ui_text, create_ui_icon, UiPage, Size
from ucapi_framework import RemoteEntity

from uc_intg_vidaa.const import APP_COMMANDS, KEY_COMMANDS, SIMPLE_COMMANDS, SOURCE_COMMANDS

if TYPE_CHECKING:
    from uc_intg_vidaa.config import VidaaConfig
    from uc_intg_vidaa.device import VidaaDevice

_LOG = logging.getLogger(__name__)


class VidaaRemote(RemoteEntity):
    """Remote entity for VIDAA TVs."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"remote.{device_config.identifier}"

        super().__init__(
            entity_id,
            f"{device_config.name} Remote",
            features=[remote.Features.ON_OFF, remote.Features.TOGGLE, remote.Features.SEND_CMD],
            attributes={remote.Attributes.STATE: remote.States.UNKNOWN},
            simple_commands=SIMPLE_COMMANDS,
            button_mapping=[
                create_btn_mapping(Buttons.HOME, short="HOME", long="MENU"),
                create_btn_mapping(Buttons.BACK, short="BACK"),
                create_btn_mapping(Buttons.DPAD_UP, short="UP"),
                create_btn_mapping(Buttons.DPAD_DOWN, short="DOWN"),
                create_btn_mapping(Buttons.DPAD_LEFT, short="LEFT"),
                create_btn_mapping(Buttons.DPAD_RIGHT, short="RIGHT"),
                create_btn_mapping(Buttons.DPAD_MIDDLE, short="OK", long="OK_LONG"),
                create_btn_mapping(Buttons.VOLUME_UP, short="VOLUME_UP"),
                create_btn_mapping(Buttons.VOLUME_DOWN, short="VOLUME_DOWN"),
                create_btn_mapping(Buttons.MUTE, short="MUTE"),
                create_btn_mapping(Buttons.CHANNEL_UP, short="CHANNEL_UP"),
                create_btn_mapping(Buttons.CHANNEL_DOWN, short="CHANNEL_DOWN"),
                create_btn_mapping(Buttons.PLAY, short="PLAY"),
                create_btn_mapping(Buttons.STOP, short="STOP"),
                create_btn_mapping(Buttons.PREV, short="REWIND"),
                create_btn_mapping(Buttons.NEXT, short="FAST_FORWARD"),
                create_btn_mapping(Buttons.RED, short="RED"),
                create_btn_mapping(Buttons.GREEN, short="GREEN"),
                create_btn_mapping(Buttons.YELLOW, short="YELLOW"),
                create_btn_mapping(Buttons.BLUE, short="BLUE"),
                create_btn_mapping(Buttons.POWER, short="POWER"),
                create_btn_mapping(Buttons.MENU, short="MENU"),
            ],
            ui_pages=[
                UiPage("main", "Main", grid=Size(4, 6), items=[
                    create_ui_icon("uc:power-on", 0, 0, cmd="POWER"),
                    create_ui_icon("uc:info", 1, 0, cmd="INFO"),
                    create_ui_icon("uc:menu", 2, 0, cmd="MENU"),
                    create_ui_text("Exit", 3, 0, cmd="EXIT"),
                    create_ui_icon("uc:up-arrow", 1, 1, cmd="UP"),
                    create_ui_icon("uc:plus", 3, 1, cmd="VOLUME_UP"),
                    create_ui_icon("uc:left-arrow", 0, 2, cmd="LEFT"),
                    create_ui_text("OK", 1, 2, cmd="OK"),
                    create_ui_icon("uc:right-arrow", 2, 2, cmd="RIGHT"),
                    create_ui_icon("uc:minus", 3, 2, cmd="VOLUME_DOWN"),
                    create_ui_icon("uc:down-arrow", 1, 3, cmd="DOWN"),
                    create_ui_icon("uc:mute", 3, 3, cmd="MUTE"),
                    create_ui_icon("uc:back", 0, 4, cmd="BACK"),
                    create_ui_icon("uc:home", 1, 4, cmd="HOME"),
                    create_ui_text("CH+", 2, 4, cmd="CHANNEL_UP"),
                    create_ui_text("CH-", 3, 4, cmd="CHANNEL_DOWN"),
                    create_ui_text("On", 0, 5, cmd="POWER_ON"),
                    create_ui_text("Off", 1, 5, cmd="POWER_OFF"),
                    create_ui_text("Subtitle", 2, 5, Size(2, 1), cmd="SUBTITLE"),
                ]),
                UiPage("numbers", "Numbers", grid=Size(3, 4), items=[
                    create_ui_text("1", 0, 0, cmd="DIGIT_1"),
                    create_ui_text("2", 1, 0, cmd="DIGIT_2"),
                    create_ui_text("3", 2, 0, cmd="DIGIT_3"),
                    create_ui_text("4", 0, 1, cmd="DIGIT_4"),
                    create_ui_text("5", 1, 1, cmd="DIGIT_5"),
                    create_ui_text("6", 2, 1, cmd="DIGIT_6"),
                    create_ui_text("7", 0, 2, cmd="DIGIT_7"),
                    create_ui_text("8", 1, 2, cmd="DIGIT_8"),
                    create_ui_text("9", 2, 2, cmd="DIGIT_9"),
                    create_ui_text(".", 0, 3, cmd="CHANNEL_DOT"),
                    create_ui_text("0", 1, 3, cmd="DIGIT_0"),
                ]),
                UiPage("playback", "Playback", grid=Size(4, 6), items=[
                    create_ui_text("Playback", 0, 0, Size(4, 1)),
                    create_ui_icon("uc:play", 0, 1, cmd="PLAY"),
                    create_ui_icon("uc:pause", 1, 1, cmd="PAUSE"),
                    create_ui_icon("uc:stop", 2, 1, cmd="STOP"),
                    create_ui_icon("uc:bw", 0, 2, cmd="REWIND"),
                    create_ui_icon("uc:ff", 1, 2, cmd="FAST_FORWARD"),
                    create_ui_text("Color Buttons", 0, 3, Size(4, 1)),
                    create_ui_text("Red", 0, 4, cmd="RED"),
                    create_ui_text("Green", 1, 4, cmd="GREEN"),
                    create_ui_text("Yellow", 2, 4, cmd="YELLOW"),
                    create_ui_text("Blue", 3, 4, cmd="BLUE"),
                ]),
                UiPage("sources", "Sources & Apps", grid=Size(4, 6), items=[
                    create_ui_text("Inputs", 0, 0, Size(4, 1)),
                    create_ui_text("TV", 0, 1, cmd="SOURCE_TV"),
                    create_ui_text("AV", 1, 1, cmd="SOURCE_AV"),
                    create_ui_text("Comp", 2, 1, cmd="SOURCE_COMPONENT"),
                    create_ui_text("HDMI 1", 0, 2, cmd="SOURCE_HDMI1"),
                    create_ui_text("HDMI 2", 1, 2, cmd="SOURCE_HDMI2"),
                    create_ui_text("HDMI 3", 2, 2, cmd="SOURCE_HDMI3"),
                    create_ui_text("HDMI 4", 3, 2, cmd="SOURCE_HDMI4"),
                    create_ui_text("Apps", 0, 3, Size(4, 1)),
                    create_ui_text("Netflix", 0, 4, Size(2, 1), cmd="APP_NETFLIX"),
                    create_ui_text("YouTube", 2, 4, Size(2, 1), cmd="APP_YOUTUBE"),
                    create_ui_text("Prime", 0, 5, Size(1, 1), cmd="APP_PRIME_VIDEO"),
                    create_ui_text("Disney+", 1, 5, Size(2, 1), cmd="APP_DISNEY"),
                    create_ui_text("tubi", 3, 5, Size(1, 1), cmd="APP_TUBI"),
                ]),
            ],
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        if self._device.state == "UNAVAILABLE":
            self.update({remote.Attributes.STATE: remote.States.UNAVAILABLE})
            return
        state = remote.States.ON if self._device.tv_on else remote.States.OFF
        self.update({remote.Attributes.STATE: state})

    async def _handle_command(
        self, entity: remote.Remote, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        try:
            if cmd_id == remote.Commands.ON:
                ok = await self._device.power_on()
                return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

            if cmd_id == remote.Commands.OFF:
                ok = await self._device.power_off()
                return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

            if cmd_id == remote.Commands.TOGGLE:
                ok = await self._device.power_toggle()
                return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

            if cmd_id != remote.Commands.SEND_CMD:
                return StatusCodes.NOT_IMPLEMENTED

            command = params.get("command", "") if params else ""
            if not command:
                return StatusCodes.BAD_REQUEST

            return await self._dispatch(command)
        except Exception as err:
            _LOG.error("[%s] Remote command error: %s", self.id, err)
            return StatusCodes.SERVER_ERROR

    async def _dispatch(self, command: str) -> StatusCodes:
        d = self._device

        if command == "POWER":
            ok = await d.power_toggle()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if command == "POWER_ON":
            # Sends Wake-on-LAN magic packet, works even when the TV is fully off
            ok = await d.power_on()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if command == "POWER_OFF":
            ok = await d.power_off()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        key = KEY_COMMANDS.get(command)
        if key:
            ok = await d.send_key(key)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        source = SOURCE_COMMANDS.get(command)
        if source:
            ok = await d.set_input(source)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        app = APP_COMMANDS.get(command)
        if app:
            ok = await d.launch_app(app)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        return StatusCodes.NOT_IMPLEMENTED
