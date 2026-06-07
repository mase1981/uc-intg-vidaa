"""
VIDAA TV media player entity.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ucapi import media_player, StatusCodes
from ucapi.media_player import BrowseOptions, BrowseResults, SearchOptions, SearchResults
from ucapi_framework import MediaPlayerEntity

from uc_intg_vidaa import browser

if TYPE_CHECKING:
    from uc_intg_vidaa.config import VidaaConfig
    from uc_intg_vidaa.device import VidaaDevice

_LOG = logging.getLogger(__name__)

FEATURES = [
    media_player.Features.ON_OFF,
    media_player.Features.TOGGLE,
    media_player.Features.VOLUME,
    media_player.Features.VOLUME_UP_DOWN,
    media_player.Features.MUTE_TOGGLE,
    media_player.Features.PLAY_PAUSE,
    media_player.Features.STOP,
    media_player.Features.FAST_FORWARD,
    media_player.Features.REWIND,
    media_player.Features.DPAD,
    media_player.Features.NUMPAD,
    media_player.Features.HOME,
    media_player.Features.MENU,
    media_player.Features.INFO,
    media_player.Features.COLOR_BUTTONS,
    media_player.Features.CHANNEL_SWITCHER,
    media_player.Features.SELECT_SOURCE,
    media_player.Features.MEDIA_TITLE,
    media_player.Features.PLAY_MEDIA,
    media_player.Features.BROWSE_MEDIA,
]

KEY_COMMAND_MAP = {
    media_player.Commands.PLAY_PAUSE: "KEY_PLAY",
    media_player.Commands.STOP: "KEY_STOP",
    media_player.Commands.FAST_FORWARD: "KEY_FORWARDS",
    media_player.Commands.REWIND: "KEY_BACK",
    media_player.Commands.CHANNEL_UP: "KEY_CHANNELUP",
    media_player.Commands.CHANNEL_DOWN: "KEY_CHANNELDOWN",
    media_player.Commands.CURSOR_UP: "KEY_UP",
    media_player.Commands.CURSOR_DOWN: "KEY_DOWN",
    media_player.Commands.CURSOR_LEFT: "KEY_LEFT",
    media_player.Commands.CURSOR_RIGHT: "KEY_RIGHT",
    media_player.Commands.CURSOR_ENTER: "KEY_OK",
    media_player.Commands.DIGIT_0: "KEY_0",
    media_player.Commands.DIGIT_1: "KEY_1",
    media_player.Commands.DIGIT_2: "KEY_2",
    media_player.Commands.DIGIT_3: "KEY_3",
    media_player.Commands.DIGIT_4: "KEY_4",
    media_player.Commands.DIGIT_5: "KEY_5",
    media_player.Commands.DIGIT_6: "KEY_6",
    media_player.Commands.DIGIT_7: "KEY_7",
    media_player.Commands.DIGIT_8: "KEY_8",
    media_player.Commands.DIGIT_9: "KEY_9",
    media_player.Commands.FUNCTION_RED: "KEY_RED",
    media_player.Commands.FUNCTION_GREEN: "KEY_GREEN",
    media_player.Commands.FUNCTION_YELLOW: "KEY_YELLOW",
    media_player.Commands.FUNCTION_BLUE: "KEY_BLUE",
    media_player.Commands.HOME: "KEY_HOME",
    media_player.Commands.MENU: "KEY_MENU",
    media_player.Commands.INFO: "KEY_INFO",
    media_player.Commands.BACK: "KEY_RETURNS",
    media_player.Commands.SUBTITLE: "KEY_SUBTITLE",
}


class VidaaMediaPlayer(MediaPlayerEntity):
    """Media player entity for VIDAA TVs."""

    def __init__(self, device_config: VidaaConfig, device: VidaaDevice) -> None:
        self._device = device
        entity_id = f"media_player.{device_config.identifier}"
        super().__init__(
            entity_id,
            device_config.name,
            features=FEATURES,
            attributes={
                media_player.Attributes.STATE: media_player.States.UNKNOWN,
                media_player.Attributes.VOLUME: 0,
                media_player.Attributes.MUTED: False,
                media_player.Attributes.SOURCE: "",
                media_player.Attributes.SOURCE_LIST: [],
            },
            device_class=media_player.DeviceClasses.TV,
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        d = self._device
        if d.state == "UNAVAILABLE":
            self.update({media_player.Attributes.STATE: media_player.States.UNAVAILABLE})
            return

        state = media_player.States.ON if d.tv_on else media_player.States.OFF
        attrs: dict[str, Any] = {
            media_player.Attributes.STATE: state,
            media_player.Attributes.VOLUME: d.volume,
            media_player.Attributes.MUTED: d.muted,
            media_player.Attributes.SOURCE: d.source,
            media_player.Attributes.SOURCE_LIST: d.source_list,
            media_player.Attributes.MEDIA_TITLE: d.app or d.source,
        }
        self.update(attrs)

    async def browse(self, options: BrowseOptions) -> BrowseResults | StatusCodes:
        if not self._device.connected:
            return StatusCodes.SERVICE_UNAVAILABLE
        return await browser.browse(self._device, options)

    async def search(self, options: SearchOptions) -> SearchResults | StatusCodes:
        return StatusCodes.NOT_IMPLEMENTED

    async def _handle_command(
        self, entity: media_player.MediaPlayer, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        try:
            return await self._dispatch_command(cmd_id, params)
        except Exception as err:
            _LOG.error("[%s] Command error: %s", self.id, err)
            return StatusCodes.SERVER_ERROR

    async def _dispatch_command(self, cmd_id: str, params: dict[str, Any] | None) -> StatusCodes:
        d = self._device

        if cmd_id == media_player.Commands.ON:
            ok = await d.power_on()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.OFF:
            ok = await d.power_off()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.TOGGLE:
            ok = await d.power_toggle()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.VOLUME:
            if params and "volume" in params:
                ok = await d.set_volume(int(params["volume"]))
                return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
            return StatusCodes.BAD_REQUEST

        if cmd_id == media_player.Commands.VOLUME_UP:
            ok = await d.volume_up()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.VOLUME_DOWN:
            ok = await d.volume_down()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.MUTE_TOGGLE:
            ok = await d.mute_toggle()
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.SELECT_SOURCE:
            source = params.get("source", "") if params else ""
            if not source:
                return StatusCodes.BAD_REQUEST
            ok = await d.select_source(source)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if cmd_id == media_player.Commands.PLAY_MEDIA:
            return await self._handle_play_media(params)

        key = KEY_COMMAND_MAP.get(cmd_id)
        if key:
            ok = await d.send_key(key)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        return StatusCodes.NOT_IMPLEMENTED

    async def _handle_play_media(self, params: dict[str, Any] | None) -> StatusCodes:
        if not params:
            return StatusCodes.BAD_REQUEST

        media_id = params.get("media_id", "")
        if not media_id:
            return StatusCodes.BAD_REQUEST

        if media_id.startswith("app:"):
            ok = await self._device.launch_app(media_id[4:])
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        if media_id.startswith("source:"):
            ok = await self._device.select_source(media_id[7:])
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR

        ok = await self._device.launch_app(media_id)
        return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
