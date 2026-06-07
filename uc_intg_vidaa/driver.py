"""
VIDAA TV driver for Unfolded Circle Remote.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging

from ucapi_framework import BaseIntegrationDriver

from uc_intg_vidaa.config import VidaaConfig
from uc_intg_vidaa.device import VidaaDevice
from uc_intg_vidaa.media_player import VidaaMediaPlayer
from uc_intg_vidaa.remote import VidaaRemote
from uc_intg_vidaa.select import VidaaAppSelect, VidaaSourceSelect
from uc_intg_vidaa.sensor import (
    VidaaConnectionSensor,
    VidaaFirmwareSensor,
    VidaaModelSensor,
    VidaaSourceSensor,
)

_LOG = logging.getLogger(__name__)


class VidaaDriver(BaseIntegrationDriver[VidaaDevice, VidaaConfig]):
    """VIDAA TV integration driver."""

    def __init__(self):
        super().__init__(
            device_class=VidaaDevice,
            entity_classes=[
                VidaaMediaPlayer,
                VidaaRemote,
                VidaaSourceSelect,
                VidaaAppSelect,
                VidaaConnectionSensor,
                VidaaSourceSensor,
                VidaaModelSensor,
                VidaaFirmwareSensor,
            ],
            driver_id="vidaa",
        )
