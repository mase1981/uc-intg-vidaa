# VIDAA TV Integration for Unfolded Circle Remote 2/3

Control your Hisense VIDAA Smart TV directly from your Unfolded Circle Remote 2 or Remote 3 with comprehensive media player control, **full remote control with app shortcuts**, and **Wake-on-LAN power on**.

![VIDAA](https://img.shields.io/badge/Hisense-VIDAA%20Smart%20TV-blue)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-vidaa?style=flat-square)](https://github.com/mase1981/uc-intg-vidaa/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-vidaa?style=flat-square)](https://github.com/mase1981/uc-intg-vidaa/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://unfolded.community/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-vidaa/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)


## Features

This integration provides comprehensive control of Hisense VIDAA Smart TVs through the native VIDAA MQTT protocol, delivering seamless integration with your Unfolded Circle Remote including power control via Wake-on-LAN, app launching, input switching, and full remote key support.

---
## ❤️ Support Development ❤️

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

### 📺 **Media Player Control**

#### **Power Control**
- **Power On** - Wake-on-LAN magic packet, works even when TV is fully off
- **Power Off** - Put TV into standby
- **Power Toggle** - Smart toggle based on current state
- **Fast Standby Detection** - Instant power on when TV is in fast standby ("fake sleep")

#### **Volume Control**
- **Volume Up/Down** - Precise volume adjustment
- **Set Volume** - Direct volume control (0-100 scale)
- **Volume Slider** - Visual volume control
- **Mute Toggle** - Quick mute/unmute
- **Real-time Updates** - Volume state polled from TV

#### **Source & App Control**
- **Input Selection** - TV, AV, Component, HDMI 1-4
- **App Launching** - Launch any installed app directly from the source list
- **Dynamic Source List** - Inputs and apps fetched live from the TV
- **Current App Display** - Shows active app/input as media title

#### **Media Browser**
- **Browse Apps** - View and launch all installed apps with icons
- **Browse Input Sources** - Quick input switching from the browser
- **One-Touch Launch** - Tap to launch apps or switch inputs

#### **Navigation & Keys**
- **D-Pad Navigation** - Up, Down, Left, Right, Enter
- **Numpad** - Digits 0-9 for direct channel entry
- **Color Buttons** - Red, Green, Yellow, Blue
- **Channel Switching** - Channel Up/Down
- **Playback Controls** - Play/Pause, Stop, Fast Forward, Rewind
- **Menu Keys** - Home, Menu, Info, Back

### 🎛️ **Remote Control Entity**

Dedicated remote entity with physical button mapping and intuitive UI pages:

#### **Page 1: Main**
- Power, Info, Menu, Exit
- Full D-Pad with OK button
- Volume Up/Down and Mute
- Back, Home, Channel Up/Down
- Discrete On (Wake-on-LAN) / Off buttons

#### **Page 2: Numbers**
- Digits 0-9 and channel dot for direct channel entry

#### **Page 3: Playback**
- Play, Pause, Stop, Rewind, Fast Forward
- Color buttons (Red, Green, Yellow, Blue)

#### **Page 4: Sources & Apps**
- Input shortcuts: TV, AV, Component, HDMI 1-4
- App shortcuts: Netflix, YouTube, Prime Video, Disney+, tubi

#### **Activity Support**
- **POWER_ON** simple command - sends Wake-on-LAN, perfect for activity power-on sequences
- **POWER_OFF** simple command - discrete power off for activities
- **50+ simple commands** - every VIDAA remote key available for custom mappings

### 🔽 **Select Entities**

- **Input Select** - Switch TV inputs from a dropdown
- **App Select** - Launch any installed app from a dropdown

### 📊 **Sensor Entities**

Real-time monitoring of TV state:

- **Connection Sensor** - TV connectivity status (Connected/Disconnected)
- **Source Sensor** - Currently active app or input
- **Model Sensor** - TV model name
- **Firmware Sensor** - TV software version

### **Protocol Requirements**

- **Protocol**: VIDAA MQTT over TLS (native mobile app protocol)
- **MQTT Port**: 36669 (default)
- **Pairing**: One-time 4-digit PIN pairing (PIN shown on TV screen)
- **Token Persistence**: Pairing token survives reboots and integration updates
- **Connection**: Periodic polling for state updates (10-second interval)
- **Wake-on-LAN**: UDP ports 9 and 7, broadcast + subnet broadcast

### **Network Requirements**

- **Local Network Access** - Integration requires same network as the TV
- **Static IP Recommended** - TV should have static IP or DHCP reservation
- **Wake on LAN** - Enable "Wake on LAN" / "Wake on Wireless Network" in TV network settings for power on from fully off
- **Remote Control over Network** - Enable mobile device connection on the TV (Settings → System → Mobile Device Connection on most models)

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-vidaa/releases) page
2. Download the latest `uc-intg-vidaa-<version>-aarch64.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration is available as a pre-built Docker image from GitHub Container Registry:

**Image**: `ghcr.io/mase1981/uc-intg-vidaa:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-vidaa:
    image: ghcr.io/mase1981/uc-intg-vidaa:latest
    container_name: uc-intg-vidaa
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-intg-vidaa --restart unless-stopped --network host -v vidaa-config:/app/config -e UC_CONFIG_HOME=/app/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/mase1981/uc-intg-vidaa:latest
```

## Configuration

### Step 1: Prepare Your VIDAA TV

**IMPORTANT**: TV must be powered ON and connected to your network before adding the integration.

#### Verify Network Connection:
1. Check that the TV is connected to your network (Ethernet or WiFi)
2. Note the IP address from TV network settings (Settings → Network → Network Information)
3. Enable **Wake on LAN** / **Wake on Wireless Network** in TV network settings
4. Enable remote control over network (Settings → System → Mobile Device Connection on most models)

#### Network Setup:
- **Static IP**: Recommended via DHCP reservation
- **Same Subnet**: TV must be on same subnet as Remote
- **Wake on LAN**: Required for power on from fully off state

#### Supported Devices:
**Hisense**: Most 2019+ models running VIDAA OS (VIDAA U3 and later)
**Other VIDAA TVs**: Toshiba and other brands running VIDAA OS may also work

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The VIDAA TV integration should appear in **Available Integrations**
3. Click **"Configure"** to begin setup:

#### **Configuration:**
- **TV Name**: Friendly name (e.g., "Living Room TV")
- **IP Address**: Enter TV IP (e.g., 192.168.1.100)
- **MAC Address**: Optional - auto-detected from the TV during setup (used for Wake-on-LAN)
- Click **Next**

#### **PIN Pairing:**
- A 4-digit PIN appears on the TV screen
- Enter the PIN to complete pairing
- The pairing token is stored on the Remote and survives reboots and updates

4. Integration will create entities:
   - **Media Player**: `media_player.vidaa_[device_id]`
   - **Remote**: `remote.vidaa_[device_id]`
   - **Selects**: Input and App selection
   - **Sensors**: Connection, Source, Model, Firmware

## Using the Integration

### Media Player Entity

The media player entity provides complete TV control:

- **Power Control**: On (Wake-on-LAN), Off, Toggle
- **Volume Control**: Volume slider (0-100), Up/Down buttons, Mute toggle
- **Source Selection**: All TV inputs and installed apps in one list
- **Media Browser**: Browse and launch apps, switch inputs
- **Navigation**: D-Pad, numpad, color buttons, channel switching
- **Media Info**: Currently active app or input source

### Remote Control Entity

The remote control entity provides quick access through UI pages:

- **Main Page**: Power, navigation, volume, and channel controls
- **Numbers Page**: Direct channel entry
- **Playback Page**: Transport and color button controls
- **Sources & Apps Page**: One-touch input and app shortcuts

### Activity Integration

For reliable power-on in activities, use the **POWER_ON** simple command (sends Wake-on-LAN) instead of power toggle. When the TV is fully off it can take 5-10 seconds to boot after receiving the magic packet.

### Sensor Entities

| Sensor | Description |
|--------|-------------|
| Connection Sensor | TV connectivity status (Connected/Disconnected) |
| Source Sensor | Currently active app or input (Off when TV is off) |
| Model Sensor | TV model name |
| Firmware Sensor | TV software version |

## Known Limitations

- **Power On from fully off**: Requires Wake-on-LAN enabled on the TV and a valid MAC address (auto-detected during setup)
- **State Polling**: TV state is polled every 10 seconds - state changes made with the original remote may take a few seconds to reflect
- **App IDs vary by region**: App shortcuts use common app IDs which may vary by TV model/region - use the dynamic app list (Media Browser or App Select) when in doubt

## Credits

- **Developer**: Meir Miyara
- **Protocol Library**: [vidaa-control](https://github.com/tombabolewski/vidaa-control) by Tom Babolewski
- **Reference Implementation**: [ha-vidaa-tv](https://github.com/tombabolewski/ha-vidaa-tv) by Tom Babolewski
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-vidaa/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)

---

**Made with ❤️ for the Unfolded Circle and VIDAA Communities**

**Thank You**: Meir Miyara
