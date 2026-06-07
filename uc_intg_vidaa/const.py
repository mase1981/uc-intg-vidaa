"""
Constants for the VIDAA TV integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

DEFAULT_PORT = 36669
POLL_INTERVAL = 10

STATE_FAKE_SLEEP = "fake_sleep_0"

TOKEN_FILE = "vidaa_tokens.json"

# Simple command name -> VIDAA key code
KEY_COMMANDS = {
    "POWER": "KEY_POWER",
    "UP": "KEY_UP",
    "DOWN": "KEY_DOWN",
    "LEFT": "KEY_LEFT",
    "RIGHT": "KEY_RIGHT",
    "OK": "KEY_OK",
    "OK_LONG": "KEY_OK_LONG_PRESS",
    "BACK": "KEY_RETURNS",
    "EXIT": "KEY_EXIT",
    "HOME": "KEY_HOME",
    "MENU": "KEY_MENU",
    "VOLUME_UP": "KEY_VOLUMEUP",
    "VOLUME_DOWN": "KEY_VOLUMEDOWN",
    "MUTE": "KEY_MUTE",
    "CHANNEL_UP": "KEY_CHANNELUP",
    "CHANNEL_DOWN": "KEY_CHANNELDOWN",
    "CHANNEL_DOT": "KEY_CHANNELDOT",
    "PLAY": "KEY_PLAY",
    "PAUSE": "KEY_PAUSE",
    "STOP": "KEY_STOP",
    "FAST_FORWARD": "KEY_FORWARDS",
    "REWIND": "KEY_BACK",
    "DIGIT_0": "KEY_0",
    "DIGIT_1": "KEY_1",
    "DIGIT_2": "KEY_2",
    "DIGIT_3": "KEY_3",
    "DIGIT_4": "KEY_4",
    "DIGIT_5": "KEY_5",
    "DIGIT_6": "KEY_6",
    "DIGIT_7": "KEY_7",
    "DIGIT_8": "KEY_8",
    "DIGIT_9": "KEY_9",
    "RED": "KEY_RED",
    "GREEN": "KEY_GREEN",
    "YELLOW": "KEY_YELLOW",
    "BLUE": "KEY_BLUE",
    "SUBTITLE": "KEY_SUBTITLE",
    "INFO": "KEY_INFO",
    "ZOOM_IN": "KEY_ZOOMIN",
    "ZOOM_OUT": "KEY_ZOOMOUT",
}

# Simple command name -> app key understood by vidaa-control
APP_COMMANDS = {
    "APP_NETFLIX": "netflix",
    "APP_YOUTUBE": "youtube",
    "APP_PRIME_VIDEO": "amazon",
    "APP_DISNEY": "disney",
    "APP_TUBI": "tubi",
}

# Simple command name -> source key understood by vidaa-control
SOURCE_COMMANDS = {
    "SOURCE_TV": "tv",
    "SOURCE_AV": "av",
    "SOURCE_COMPONENT": "component",
    "SOURCE_HDMI1": "hdmi1",
    "SOURCE_HDMI2": "hdmi2",
    "SOURCE_HDMI3": "hdmi3",
    "SOURCE_HDMI4": "hdmi4",
}

# Display name -> source key (fallback when the TV source list is unavailable)
INPUT_SOURCES = {
    "TV": "tv",
    "AV": "av",
    "Component": "component",
    "HDMI 1": "hdmi1",
    "HDMI 2": "hdmi2",
    "HDMI 3": "hdmi3",
    "HDMI 4": "hdmi4",
}

# App key -> display name for state reporting
KNOWN_APPS = {
    "netflix": "Netflix",
    "youtube": "YouTube",
    "amazon": "Prime Video",
    "prime": "Prime Video",
    "disney": "Disney+",
    "disney+": "Disney+",
    "tubi": "tubi",
}

# Discrete power commands for activities - POWER_ON sends Wake-on-LAN
POWER_COMMANDS = ["POWER_ON", "POWER_OFF"]

SIMPLE_COMMANDS = (
    POWER_COMMANDS
    + list(KEY_COMMANDS.keys())
    + list(SOURCE_COMMANDS.keys())
    + list(APP_COMMANDS.keys())
)
