# VIDAA TV Integration for Unfolded Circle Remote

Control your Hisense VIDAA Smart TV from your Unfolded Circle Remote 2/3.

![VIDAA](https://img.shields.io/badge/VIDAA-TV-blue)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow.svg)](https://buymeacoffee.com/meirmiyara)

## Features

### 📺 Media Player
- Power on/off (Wake-on-LAN supported for full power on)
- Volume control (set, up/down, mute)
- Input source selection (TV, AV, Component, HDMI 1-4)
- App launching directly from the source list
- Playback controls (play/pause, stop, fast forward, rewind)
- D-Pad navigation, numpad, color buttons, channel switching
- **Media Browser**: browse and launch installed apps and input sources

### 🎮 Remote Control
- Full remote entity with physical button mapping
- 4 custom UI pages: Main, Numbers, Playback, Sources & Apps
- Quick app shortcuts: Netflix, YouTube, Prime Video, Disney+, tubi
- All VIDAA remote keys available as simple commands for activities

### 🔽 Select Entities
- **Input Select**: switch between TV inputs
- **App Select**: launch any installed app

### 📊 Sensors
- Connection status
- Current app/source
- TV model
- Firmware version

## Requirements

- Hisense TV running VIDAA OS (most 2019+ models)
- TV connected to the same network as the Remote
- Unfolded Circle Remote 2 or 3 with firmware 2.0+

**Important**: For Wake-on-LAN power on to work, enable **Wake on LAN** / **Wake on Wireless Network** in the TV network settings. Also make sure the TV's remote control over network setting is enabled (Settings → System → Mobile Device Connection on most models).

## Installation

### Option 1: Upload to Remote (Recommended)

1. Download the latest `uc-intg-vidaa-<version>-aarch64.tar.gz` from [Releases](https://github.com/mase1981/uc-intg-vidaa/releases)
2. Open the web configurator of your Remote
3. Go to **Integrations** → **Add new** → **Install custom**
4. Upload the `.tar.gz` file
5. Complete the setup flow

### Option 2: Docker

```yaml
services:
  vidaa-integration:
    image: ghcr.io/mase1981/uc-intg-vidaa:latest
    container_name: uc-intg-vidaa
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./data:/data
    environment:
      - UC_CONFIG_HOME=/data
```

## Setup

1. **Turn the TV ON** before starting setup
2. Start the integration setup on the Remote
3. Enter the TV name and IP address (MAC address is optional - it is auto-detected when possible)
4. A 4-digit PIN appears on the TV screen
5. Enter the PIN to complete pairing

The pairing token is stored on the Remote and survives reboots and integration updates.

## Notes

- When the TV is fully powered off, it can only be turned on via Wake-on-LAN (MAC address required - auto-detected during setup)
- When the TV is in fast standby ("fake sleep"), it stays reachable and powers on instantly
- TV state, volume and current app are polled every 10 seconds

## Credits

- Protocol implementation: [vidaa-control](https://github.com/tombabolewski/vidaa-control) by Tom Babolewski
- Reference implementation: [ha-vidaa-tv](https://github.com/tombabolewski/ha-vidaa-tv)

## Author

Meir Miyara - [GitHub](https://github.com/mase1981)

## License

MPL-2.0 - see [LICENSE](LICENSE)
