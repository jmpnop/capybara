# Capybara VPN - macOS Installer Builder

This directory contains tools to build user-specific macOS `.pkg` installers for Capybara VPN.

## Features

✅ **One-Click Installation** - Users just double-click the .pkg file
✅ **Pre-Configured** - All VPN settings embedded in the installer
✅ **GUI Application** - Simple menu to Connect/Disconnect VPN
✅ **No Manual Setup** - Automatically installs dependencies
✅ **macOS 10.13+** - Supports High Sierra through latest macOS
✅ **Universal** - Works on both Intel and Apple Silicon Macs

## What Gets Installed

The installer creates:

```
/Applications/Capybara VPN.app          # GUI launcher application
~/Library/Application Support/CapybaraVPN/
    ├── config.txt                       # Username
    ├── <username>_wireguard.conf        # WireGuard configuration
    ├── vpn.log                          # Connection logs
    ├── udp2raw.pid                      # Process tracking
    └── uninstall.sh                     # Uninstaller script
/usr/local/bin/udp2raw                   # udp2raw binary (symlink)
```

## Prerequisites

### On the Build Machine (Your Mac)

You need:

1. **Xcode Command Line Tools** (for pkgbuild/productbuild)
   ```bash
   xcode-select --install
   ```

2. **Capybara CLI** with user configs already created
   ```bash
   cd /path/to/capybara
   python3 capybara.py user add alice
   ```

3. **udp2raw installed** (optional, will be embedded for Intel Macs)
   ```bash
   brew install udp2raw-multiplatform
   ```

### On the User's Machine (End User)

The installer will check for and require:

1. **WireGuard** - Can be installed from:
   - Mac App Store (recommended)
   - Homebrew: `brew install wireguard-tools`

2. **udp2raw** - Will be:
   - Embedded for Intel Macs (automatic)
   - Must install via Homebrew on Apple Silicon: `brew install udp2raw-multiplatform`

## Quick Start

### 1. Create VPN User

First, add a user using Capybara CLI:

```bash
cd /path/to/capybara
python3 capybara.py user add sergej --description "Sergej's devices"
```

This creates:
- `vpn_clients/sergej_wireguard.conf`
- `vpn_clients/sergej_shadowsocks.txt`
- `vpn_clients/sergej_v2ray.txt`

### 2. Build Installer for User

```bash
python3 macos-installer/build_installer.py sergej
```

Output:
```
🚀 Building Capybara VPN Installer
   User: sergej
============================================================
📁 Preparing build directory...
   Copying application bundle...
   Copying installer scripts...
   Copying VPN configs for 'sergej'...
✅ Build directory prepared
📥 Checking udp2raw binary...
   Using local udp2raw binary
📦 Building installer package...
   Package: installers/CapybaraVPN-sergej.pkg
✅ Component package built
✅ Installer package created successfully!

📦 Installer: installers/CapybaraVPN-sergej.pkg
   Size: 1.23 MB
============================================================
✅ SUCCESS! Installer ready for distribution
============================================================

Share this file with sergej:
   installers/CapybaraVPN-sergej.pkg

They can double-click to install.
```

### 3. Distribute to User

Send the `.pkg` file to the user via:
- Email (if < 25MB)
- File sharing service (Dropbox, Google Drive, etc.)
- USB drive

### 4. User Installation

User simply:
1. Double-clicks `CapybaraVPN-sergej.pkg`
2. Follows the installer wizard
3. Enters admin password when prompted
4. Finds "Capybara VPN" in Applications folder
5. Launches and clicks "Connect"

## Usage

### Command Line Options

```bash
# Build installer for a user
python3 macos-installer/build_installer.py <username>

# Specify output directory
python3 macos-installer/build_installer.py alice -o ~/Desktop

# Keep build directory for debugging
python3 macos-installer/build_installer.py alice --keep-build
```

### Batch Build for Multiple Users

```bash
# Build installers for all users
for user in alice bob charlie; do
    python3 macos-installer/build_installer.py $user
done

# Or using Capybara user list
python3 capybara.py user list | grep "User:" | cut -d: -f2 | xargs -I{} \
    python3 macos-installer/build_installer.py {}
```

## End User Guide

### Installing

1. Download `CapybaraVPN-<username>.pkg`
2. Double-click the file
3. Follow the installation wizard
4. Enter your Mac password when prompted

### Using the VPN

**Launch the App:**
- Open "Capybara VPN" from Applications folder
- Or use Spotlight (⌘-Space, type "Capybara")

**Connect to VPN:**
1. Click "Connect" button
2. Enter admin password (once per session)
3. Wait for "Connected successfully!" notification
4. Your public IP will be shown (should be VPN server IP)

**Disconnect:**
1. Launch "Capybara VPN" again
2. Click "Disconnect"
3. Wait for "Disconnected" notification

**Check Status:**
- When connected, click "Status" to see current IP

### What Happens Behind the Scenes

When you click "Connect":
1. **udp2raw** starts and creates encrypted tunnel to port 443 (appears as HTTPS)
2. **WireGuard** connects through the udp2raw tunnel
3. All traffic is routed through VPN

When you click "Disconnect":
1. WireGuard connection is closed
2. udp2raw tunnel is terminated
3. Normal internet routing is restored

### Troubleshooting

**"VPN not configured"**
- Reinstall the .pkg file

**"Failed to start udp2raw"**
- Check if you have admin rights
- Verify udp2raw is installed:
  ```bash
  which udp2raw
  /usr/local/bin/udp2raw --help
  ```
- Apple Silicon users: `brew install udp2raw-multiplatform`

**"VPN started but connection test failed"**
- Check server is running: Contact VPN admin
- Check firewall settings
- View logs: `~/Library/Application Support/CapybaraVPN/vpn.log`

**WireGuard not found**
- Install from Mac App Store: https://apps.apple.com/us/app/wireguard/id1451685025
- Or via Homebrew: `brew install wireguard-tools`

**Permission denied errors**
- Make sure you enter admin password correctly
- Check you have administrator access on your Mac

### Logs

Check connection logs:
```bash
# VPN launcher logs
tail -f ~/Library/Application\ Support/CapybaraVPN/vpn.log

# udp2raw logs
tail -f /tmp/udp2raw.log

# System logs
log show --predicate 'process == "udp2raw"' --last 5m
```

### Uninstalling

To completely remove Capybara VPN:

```bash
# Run the uninstaller
~/Library/Application\ Support/CapybaraVPN/uninstall.sh

# Or manually:
sudo rm -rf "/Applications/Capybara VPN.app"
rm -rf ~/Library/Application\ Support/CapybaraVPN
```

## Advanced Usage

### Command Line Control

The VPN can also be controlled via command line:

```bash
# Show menu
"/Applications/Capybara VPN.app/Contents/MacOS/vpn-launcher"

# Connect
"/Applications/Capybara VPN.app/Contents/MacOS/vpn-launcher" start

# Disconnect
"/Applications/Capybara VPN.app/Contents/MacOS/vpn-launcher" stop

# Check status
"/Applications/Capybara VPN.app/Contents/MacOS/vpn-launcher" status
```

### Creating Aliases

Add to `~/.zshrc` or `~/.bash_profile`:

```bash
alias vpn-connect="/Applications/Capybara\ VPN.app/Contents/MacOS/vpn-launcher start"
alias vpn-disconnect="/Applications/Capybara\ VPN.app/Contents/MacOS/vpn-launcher stop"
alias vpn-status="/Applications/Capybara\ VPN.app/Contents/MacOS/vpn-launcher status"
```

## Project Structure

```
macos-installer/
├── README.md                    # This file
├── build_installer.py           # Main installer builder script
│
├── app-source/                  # Application source code
│   ├── vpn-launcher.sh          # Main launcher script
│   └── VPNLauncher.applescript  # AppleScript version (not used)
│
├── payload/                     # Files to be installed
│   └── Applications/
│       └── Capybara VPN.app/
│           └── Contents/
│               ├── Info.plist
│               ├── MacOS/
│               │   └── vpn-launcher
│               └── Resources/
│
├── scripts/                     # Installer scripts
│   └── postinstall              # Runs after installation
│
├── resources/                   # Installer UI resources
│   ├── welcome.html
│   └── conclusion.html
│
└── build/                       # Temporary build directory
    └── <username>/              # Per-user build (auto-generated)
```

## Customization

### Changing Server IP

Edit `app-source/vpn-launcher.sh` and `build_installer.py`:

```bash
# Find and replace
66.42.119.38  # Current server IP
```

### Changing udp2raw Password

The password is embedded in the launcher script. Update:

```bash
# In app-source/vpn-launcher.sh
-k SecureVPN2025Obfuscate
```

### Custom App Icon

Create an `.icns` file and place it in:
```
payload/Applications/Capybara VPN.app/Contents/Resources/AppIcon.icns
```

### Branding

Edit these files to customize appearance:
- `resources/welcome.html` - Installation welcome screen
- `resources/conclusion.html` - Post-installation screen
- `payload/Applications/Capybara VPN.app/Contents/Info.plist` - App metadata

## Security Notes

⚠️ **Important Security Considerations:**

1. **Credentials in Installer** - The .pkg file contains:
   - WireGuard private keys
   - VPN server configuration
   - Treat .pkg files as sensitive and distribute securely

2. **Code Signing** - The installer is not code-signed. To sign it:
   ```bash
   productsign --sign "Developer ID Installer: Your Name" \
       installers/CapybaraVPN-user.pkg \
       installers/CapybaraVPN-user-signed.pkg
   ```

3. **Notarization** - For macOS 10.15+, consider notarizing:
   ```bash
   xcrun altool --notarize-app \
       --primary-bundle-id "com.capybara.vpn" \
       --username "your@apple.id" \
       --password "@keychain:AC_PASSWORD" \
       --file installers/CapybaraVPN-user.pkg
   ```

4. **Secure Distribution** - Share .pkg files via:
   - Encrypted email
   - Password-protected archives
   - Private file sharing with access controls

## Compatibility

### Supported macOS Versions

- ✅ macOS 10.13 (High Sierra) - 2017
- ✅ macOS 10.14 (Mojave) - 2018
- ✅ macOS 10.15 (Catalina) - 2019
- ✅ macOS 11 (Big Sur) - 2020
- ✅ macOS 12 (Monterey) - 2021
- ✅ macOS 13 (Ventura) - 2022
- ✅ macOS 14 (Sonoma) - 2023
- ✅ macOS 15 (Sequoia) - 2024

### Architecture Support

- ✅ Intel Macs (x86_64)
- ✅ Apple Silicon (ARM64/M1/M2/M3)

### Known Issues

1. **Apple Silicon + udp2raw** - Must install via Homebrew, can't embed binary
2. **Gatekeeper warnings** - Unsigned apps show security warning on first launch
3. **Old WireGuard versions** - Some older WireGuard versions use different paths

## Troubleshooting Build Issues

**"pkgbuild: command not found"**
```bash
xcode-select --install
```

**"User config not found"**
```bash
# Make sure user exists in Capybara
python3 capybara.py user list

# If not, add them first
python3 capybara.py user add <username>
```

**"Permission denied" during build**
```bash
# Make sure scripts are executable
chmod +x macos-installer/scripts/*
chmod +x macos-installer/build_installer.py
```

**Binary compatibility issues**
- Intel Macs: Use `udp2raw_amd64` binary
- Apple Silicon: Users install via Homebrew (can't embed ARM64 binary easily)

## Future Improvements

Potential enhancements:

- [ ] Auto-detect and install WireGuard if missing
- [ ] Menu bar icon with status indicator
- [ ] Automatic updates via Sparkle framework
- [ ] Support for multiple VPN profiles
- [ ] Kill switch (block all traffic if VPN drops)
- [ ] Split tunneling configuration
- [ ] Code signing and notarization support
- [ ] Custom DNS server configuration
- [ ] Statistics (bandwidth usage, uptime)
- [ ] Dark mode support for GUI

## License

Same license as Capybara VPN project.

## Support

For issues:
1. Check logs: `~/Library/Application Support/CapybaraVPN/vpn.log`
2. Contact VPN administrator
3. File issue at: https://github.com/yourorg/capybara

---

**Created:** 2025-12-04
**Version:** 1.0
**Tested on:** macOS 14.5 (Sonoma), macOS 11.7 (Big Sur)
