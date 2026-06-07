"""
VIDAA TV media browser.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ucapi import StatusCodes
from ucapi.api_definitions import Pagination
from ucapi.media_player import (
    BrowseMediaItem,
    BrowseOptions,
    BrowseResults,
    MediaClass,
)

if TYPE_CHECKING:
    from uc_intg_vidaa.device import VidaaDevice

_LOG = logging.getLogger(__name__)


async def browse(device: VidaaDevice, options: BrowseOptions) -> BrowseResults | StatusCodes:
    media_id = options.media_id if hasattr(options, "media_id") else None

    if not media_id or media_id == "root":
        return _browse_root(device)

    if media_id == "apps":
        return _browse_apps(device)

    if media_id == "sources":
        return _browse_sources(device)

    return StatusCodes.NOT_FOUND


def _browse_root(device: VidaaDevice) -> BrowseResults:
    items = [
        BrowseMediaItem(
            title="Apps",
            media_class=MediaClass.APP,
            media_type="directory",
            media_id="apps",
            can_browse=True,
            can_play=False,
            thumbnail="icon://uc:grid",
        ),
        BrowseMediaItem(
            title="Input Sources",
            media_class=MediaClass.DIRECTORY,
            media_type="directory",
            media_id="sources",
            can_browse=True,
            can_play=False,
            thumbnail="icon://uc:input-hdmi",
        ),
    ]

    return BrowseResults(
        media=BrowseMediaItem(
            title=device.name,
            media_class=MediaClass.DIRECTORY,
            media_type="root",
            media_id="root",
            can_browse=True,
            items=items,
        ),
        pagination=Pagination(page=1, limit=len(items), count=len(items)),
    )


def _browse_apps(device: VidaaDevice) -> BrowseResults:
    items = []
    for app in device.apps:
        name = app.get("name")
        if not name:
            continue
        icon = app.get("icon") or app.get("iconSmall") or None
        items.append(BrowseMediaItem(
            title=name,
            media_class=MediaClass.APP,
            media_type="app",
            media_id=f"app:{name}",
            can_browse=False,
            can_play=True,
            thumbnail=icon if icon else "icon://uc:grid",
        ))

    return BrowseResults(
        media=BrowseMediaItem(
            title="Apps",
            media_class=MediaClass.APP,
            media_type="directory",
            media_id="apps",
            can_browse=True,
            items=items,
        ),
        pagination=Pagination(page=1, limit=len(items), count=len(items)),
    )


def _browse_sources(device: VidaaDevice) -> BrowseResults:
    items = []
    for name in device.input_source_names:
        items.append(BrowseMediaItem(
            title=name,
            media_class=MediaClass.VIDEO,
            media_type="video",
            media_id=f"source:{name}",
            can_browse=False,
            can_play=True,
            thumbnail="icon://uc:input-hdmi",
        ))

    return BrowseResults(
        media=BrowseMediaItem(
            title="Input Sources",
            media_class=MediaClass.DIRECTORY,
            media_type="directory",
            media_id="sources",
            can_browse=True,
            items=items,
        ),
        pagination=Pagination(page=1, limit=len(items), count=len(items)),
    )
