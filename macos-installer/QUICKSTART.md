# Quick Start Guide - macOS Installer

## For VPN Administrators

### Build an Installer (3 Easy Steps)

```bash
# 1. Navigate to Capybara directory
cd /Users/pasha/PycharmProjects/capybara

# 2. Add a new VPN user (if not already added)
python3 capybara.py user add <username> --description "User's devices"

# 3. Build the installer
python3 macos-installer/build_installer.py <username>
```

**Output:** `installers/CapybaraVPN-<username>.pkg`

### Examples

```bash
# Build installer for sergej
python3 macos-installer/build_installer.py sergej

# Build for multiple users
for user in alice bob charlie; do
    python3 macos-installer/build_installer.py $user
done

# Custom output directory
python3 macos-installer/build_installer.py alice -o ~/Desktop
```

---

## For End Users

### Installation (1-2-3)

1. **Download** the `.pkg` file sent to you
2. **Double-click** `CapybaraVPN-<yourname>.pkg`
3. **Follow** the installer wizard (enter password when asked)

### Using VPN

**Connect:**
1. Open "Capybara VPN" from Applications
2. Click "Connect"
3. Enter admin password
4. Wait for "Connected successfully!" ✅

**Disconnect:**
1. Open "Capybara VPN" again
2. Click "Disconnect"
3. Wait for "Disconnected" ✅

### First-Time Setup

If you see warnings about missing dependencies:

**Install WireGuard:**
- Mac App Store: Search "WireGuard"
- Or: `brew install wireguard-tools`

**Install udp2raw (Apple Silicon only):**
```bash
brew install udp2raw-multiplatform
```

### Troubleshooting

**Can't find the app?**
- Press ⌘-Space, type "Capybara VPN"

**Connection fails?**
- Check logs: `~/Library/Application Support/CapybaraVPN/vpn.log`
- Make sure WireGuard and udp2raw are installed
- Contact your VPN administrator

**Uninstall:**
```bash
~/Library/Application\ Support/CapybaraVPN/uninstall.sh
```

---

## Key Features

✅ **One-Click Connection** - No manual configuration needed
✅ **Pre-Configured** - All settings embedded in installer
✅ **Universal** - Works on Intel and Apple Silicon Macs
✅ **Compatible** - macOS High Sierra (10.13) through latest
✅ **Secure** - Encrypted tunnel disguised as HTTPS traffic

---

## Quick Reference

| Task | Command |
|------|---------|
| Build installer | `python3 macos-installer/build_installer.py <user>` |
| Add new user | `python3 capybara.py user add <user>` |
| List users | `python3 capybara.py user list` |
| Check server status | `python3 capybara.py server status` |
| View logs | `python3 capybara.py logs show --service wireguard` |

---

## File Locations

**On Build Machine:**
- Installer builder: `macos-installer/build_installer.py`
- Generated installers: `installers/CapybaraVPN-*.pkg`
- User configs: `vpn_clients/*_wireguard.conf`

**On User's Mac:**
- Application: `/Applications/Capybara VPN.app`
- Configs: `~/Library/Application Support/CapybaraVPN/`
- Logs: `~/Library/Application Support/CapybaraVPN/vpn.log`
- Uninstaller: `~/Library/Application Support/CapybaraVPN/uninstall.sh`

---

For detailed documentation, see [README.md](README.md)
