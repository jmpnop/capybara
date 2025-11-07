# 🦫 Capybara VPN - Multi-Protocol Client Setup Guide

Complete guide for setting up Capybara VPN clients with **WireGuard**, **Shadowsocks**, and **V2Ray** on macOS, iOS, and Android.

**Capybara v3.0** provides three censorship-resistant protocols:
- **WireGuard + udp2raw** - Maximum speed with obfuscation (desktop)
- **Shadowsocks** - Easy mobile setup with QR codes (iOS/Android)
- **V2Ray** - Advanced obfuscation for highly restrictive networks

Every user automatically gets configurations for all three protocols!

---

## 🎯 Quick Start - Which Protocol Should I Use?

### Mobile Users (iPhone/iPad/Android)

**You have TWO great options - both work perfectly on mobile:**

| Protocol | Speed | Obfuscation | Best For | iOS App |
|----------|-------|-------------|----------|---------|
| **Shadowsocks** ⭐ | ⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐ Good | Normal use, daily browsing | Shadowrocket ($2.99) |
| **V2Ray** 🔒 | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Maximum | Heavy censorship (China, Iran) | Shadowrocket ($2.99) |

**💡 Pro Tip:** Shadowrocket supports BOTH protocols! Buy it once, scan both QR codes, switch with one tap.

### Desktop Users (macOS/Windows/Linux)

| Your Situation | Recommended Protocol | Why? |
|----------------|---------------------|------|
| **MacOS desktop** | WireGuard + udp2raw | Fastest (⭐⭐⭐⭐⭐), excellent obfuscation |
| **Need backup** | Shadowsocks or V2Ray | Also available on macOS |

### By Network Conditions

| Your Location/Network | Try First | If Blocked, Use |
|----------------------|-----------|-----------------|
| **Normal internet** | Shadowsocks | V2Ray |
| **China 🇨🇳** | V2Ray | Shadowsocks |
| **Russia 🇷🇺** | Shadowsocks | V2Ray |
| **Iran 🇮🇷** | V2Ray | Shadowsocks |
| **Corporate network** | WireGuard (desktop) | Shadowsocks |
| **Traveling** | Shadowsocks | V2Ray |

**⚡ Quick Answer:**
- **iPhone in USA/Europe?** → Use Shadowsocks (faster)
- **iPhone in China/Iran?** → Use V2Ray (stronger)
- **Have Shadowrocket?** → Set up BOTH, switch when needed!

---

## 📋 Prerequisites

Before setting up a client, you need:

1. **A user account created on the VPN server:**
   ```bash
   ./capybara.py user add alice --description "Alice's device"
   ```

2. **Your configuration files** from `./vpn_clients/` - you get **6 files**:
   ```
   ✅ alice_20251106_123456_wireguard.conf
   ✅ alice_20251106_123456_wireguard_qr.png
   ✅ alice_20251106_123456_shadowsocks.txt
   ✅ alice_20251106_123456_shadowsocks_qr.png
   ✅ alice_20251106_123456_v2ray.txt
   ✅ alice_20251106_123456_v2ray_qr.png
   ```

3. **Server information:**
   - Server IP: Your VPN server's public IP
   - WireGuard (obfuscated): Port `443` (TCP, disguised as HTTPS)
   - Shadowsocks: Port `8388` (TCP/UDP)
   - V2Ray: Port `80` (WebSocket)
   - VPN network: `10.7.0.0/24`

---

## 📱 iPhone/iPad Users - Start Here!

**Good news:** Both Shadowsocks AND V2Ray work perfectly on iPhone!

### One App for Both Protocols

**Buy Shadowrocket ($2.99)** - It supports BOTH Shadowsocks and V2Ray!

**Setup takes 1 minute:**
1. Open App Store → Buy "Shadowrocket" ($2.99)
2. Open Shadowrocket → Tap **+** → **Scan QR Code**
3. Scan your `shadowsocks_qr.png` ✅
4. Tap **+** again → **Scan QR Code**
5. Scan your `v2ray_qr.png` ✅
6. Now you have BOTH protocols!

**Switching protocols:** Just tap the server name in Shadowrocket.

### Which One to Use?

| Situation | Use This |
|-----------|----------|
| 🌍 **Normal browsing** (USA, Europe) | Shadowsocks (faster) |
| 🇨🇳 **In China** | V2Ray (stronger obfuscation) |
| 🇷🇺 **In Russia** | Try Shadowsocks first, V2Ray if blocked |
| 🇮🇷 **In Iran** | V2Ray (most reliable) |
| 🏢 **Corporate WiFi** | Try Shadowsocks, then V2Ray |
| ✈️ **Traveling** | Have both ready! |

**Jump to instructions:**
- [Shadowsocks iOS Setup](#-ios-setup-shadowsocks) (recommended for most users)
- [V2Ray iOS Setup](#-ios-setup-v2ray) (recommended for heavy censorship)

---

## 📑 Table of Contents

### 📱 Mobile Setup (iPhone/iPad/Android)
Both Shadowsocks and V2Ray work great on mobile!

- **[Shadowsocks on iOS](#-ios-setup-shadowsocks)** - Fast, easy QR setup
- **[Shadowsocks on Android](#-android-setup-shadowsocks)** - Free app, QR setup
- **[V2Ray on iOS](#-ios-setup-v2ray)** - Strongest obfuscation (same Shadowrocket app!)
- **[V2Ray on Android](#-android-setup-v2ray)** - Free v2rayNG app

### 💻 Desktop Setup (macOS/Windows/Linux)

- **[WireGuard + udp2raw on macOS](#-macos-setup-wireguard--udp2raw)** - Fastest option
- **[Shadowsocks on macOS](#-macos-setup-shadowsocks)** - Alternative option
- **[V2Ray on macOS](#-macos-setup-v2ray)** - Backup option

### 📚 Additional Resources

- **[Troubleshooting All Protocols](#-troubleshooting)** - Common issues and fixes
- **[Testing Your Connection](#-testing-your-connection)** - Verify it works
- **[Country-Specific Notes](#-country-specific-notes)** - China, Russia, Iran, etc.
- **[Emergency Procedures](#-emergency-procedures)** - Protocol switching guide

### 📖 Full Protocol Documentation

- [Protocol 1: WireGuard + udp2raw (Desktop)](#protocol-1-wireguard--udp2raw)
- [Protocol 2: Shadowsocks (Mobile & Desktop)](#protocol-2-shadowsocks)
- [Protocol 3: V2Ray (Mobile & Desktop)](#protocol-3-v2ray)

---

# Protocol 1: WireGuard + udp2raw

**Best for:** Desktop users (macOS, Linux, Windows)
**Speed:** ⭐⭐⭐⭐⭐ (Fastest)
**Mobile:** ⭐⭐ (Requires travel router or Mac gateway)
**Obfuscation:** ⭐⭐⭐⭐⭐ (Excellent - looks like HTTPS)

WireGuard with udp2raw provides maximum speed with excellent obfuscation by disguising VPN traffic as HTTPS on port 443.

## 🍎 macOS Setup (WireGuard + udp2raw)

macOS supports obfuscated WireGuard connections using udp2raw, which disguises VPN traffic as HTTPS on port 443.

### Step 1: Install Requirements

```bash
# Install WireGuard command-line tools
brew install wireguard-tools

# Download udp2raw binary
cd /usr/local/bin
sudo curl -L -o udp2raw https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_amd64
sudo chmod +x udp2raw

# For Apple Silicon (M1/M2/M3), use arm64 version instead:
# sudo curl -L -o udp2raw https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_arm

# Verify installation
udp2raw --help
wg --version
```

### Step 2: Configure Client

The configuration file generated by Capybara is already set up for obfuscation. It should look like this:

**Example: `alice_20251106_123456.conf`**
```ini
[Interface]
PrivateKey = aL6+fXETtv/i01j7jBQDKtnlNXHBfTy9eE2oAcyxfWM=
Address = 10.7.0.3/24
MTU = 1280
DNS = 1.1.1.1, 8.8.8.8

# Start udp2raw client on connection
PreUp = sudo /usr/local/bin/udp2raw -c -l 127.0.0.1:4096 -r YOUR_SERVER_IP:443 -k YOUR_UDP2RAW_PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a &
PostDown = sudo killall udp2raw

[Peer]
PublicKey = D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
AllowedIPs = 0.0.0.0/0
Endpoint = 127.0.0.1:4096  # Points to local udp2raw
PersistentKeepalive = 25
```

**Key components:**
- `Endpoint = 127.0.0.1:4096` - Connects to local udp2raw client
- `PreUp` - Starts udp2raw client, which forwards to server's port 443
- `PostDown` - Stops udp2raw when disconnecting
- Port 443 traffic looks like HTTPS to network inspectors

### Step 3: Grant Sudo Permissions (Required)

udp2raw requires root privileges for raw socket access:

```bash
# Edit sudoers file
sudo visudo

# Add these lines (replace 'yourusername' with your macOS username):
yourusername ALL=(ALL) NOPASSWD: /usr/local/bin/udp2raw
yourusername ALL=(ALL) NOPASSWD: /usr/bin/killall udp2raw

# Save and exit (Ctrl+X, then Y, then Enter in nano)
```

**Why needed:** udp2raw creates raw TCP packets to disguise UDP traffic, requiring root privileges.

### Step 4: Install Configuration

Copy the configuration file to WireGuard directory:

```bash
# Create WireGuard directory
sudo mkdir -p /etc/wireguard

# Copy configuration (use your actual filename)
sudo cp alice_20251106_123456.conf /etc/wireguard/alice.conf

# Set permissions
sudo chmod 600 /etc/wireguard/alice.conf
```

### Step 5: Connect

```bash
# Start the VPN tunnel
sudo wg-quick up alice

# Check status
sudo wg show

# Verify your IP changed
curl ifconfig.me

# Should show your VPN server's IP
```

### Step 6: Disconnect

```bash
# Stop the VPN tunnel
sudo wg-quick down alice
```

### Optional: Create Connection Script

For easier connection, create a script:

```bash
# Create script
cat > ~/vpn-connect.sh << 'EOF'
#!/bin/bash
sudo wg-quick up alice
echo "VPN connected!"
curl ifconfig.me
EOF

chmod +x ~/vpn-connect.sh

# Create disconnect script
cat > ~/vpn-disconnect.sh << 'EOF'
#!/bin/bash
sudo wg-quick down alice
echo "VPN disconnected!"
EOF

chmod +x ~/vpn-disconnect.sh
```

Usage:
```bash
~/vpn-connect.sh      # Connect to VPN
~/vpn-disconnect.sh   # Disconnect from VPN
```

---

## 📱 iOS Setup (Workarounds Required)

**⚠️ Important:** iOS does **not support udp2raw** natively (requires jailbreak). You must use one of these workarounds:

### Option 1: GL.iNet Travel Router (Recommended)

Use a portable router that handles obfuscation for all your devices:

**Hardware:** GL.iNet GL-MT300N-V2 (~$20) or similar OpenWrt-compatible router

**Setup:**
1. **Install OpenWrt** on the router (usually pre-installed on GL.iNet)
2. **Install packages** via SSH:
   ```bash
   opkg update
   opkg install wireguard-tools kmod-wireguard
   # Install udp2raw from GitHub releases
   ```
3. **Configure WireGuard** on router with udp2raw
4. **Connect iOS device** to router's WiFi

**Benefits:**
- ✅ Works with any device (iPhone, iPad, Android, laptop)
- ✅ No jailbreak needed
- ✅ Portable - take it anywhere
- ✅ One-time setup
- ✅ Handles obfuscation for all connected devices

**Recommended routers:**
- GL.iNet GL-MT300N-V2 (Mango) - $20
- GL.iNet GL-AR750S-Ext (Slate) - $50
- GL.iNet GL-AXT1800 (Slate AX) - $90

### Option 2: Mac as VPN Gateway

Use your Mac as a proxy for iOS devices:

**Setup:**
1. **On Mac:** Connect to VPN using obfuscated connection (see macOS setup above)
2. **Enable Internet Sharing:**
   - Open System Preferences → Sharing
   - Select "Internet Sharing"
   - Share your connection from: **WireGuard (wg0)**
   - To computers using: **Wi-Fi**
   - Click the checkbox to enable

3. **On iOS:** Connect to Mac's shared WiFi network

**Benefits:**
- ✅ No extra hardware needed
- ✅ Works immediately
- ✅ All iOS traffic goes through obfuscated VPN

**Drawbacks:**
- ❌ Mac must be on and connected
- ❌ Not portable

---

# Protocol 2: Shadowsocks

**Best for:** Mobile devices (iOS, Android) + macOS
**Speed:** ⭐⭐⭐⭐ (Fast)
**Mobile:** ⭐⭐⭐⭐⭐ (Excellent - iOS/Android native apps with QR codes)
**Obfuscation:** ⭐⭐⭐⭐ (Good - AEAD encryption)
**iOS App:** Shadowrocket ($2.99) - also supports V2Ray!

Shadowsocks is perfect for mobile devices with native app support and QR code setup. Uses AEAD encryption (chacha20-ietf-poly1305) for security and obfuscation.

**iOS Users:** Shadowrocket supports BOTH Shadowsocks and V2Ray - buy once, use both!

## 📱 iOS Setup (Shadowsocks)

### Step 1: Install Shadowsocks App

**Recommended apps:**
- **Shadowrocket** ($2.99) - Best overall, supports QR codes
- **Quantumult X** ($7.99) - Advanced features
- **Shadowsocks** (Free) - Basic but functional

**Installation:**
1. Open App Store on your iPhone/iPad
2. Search for "Shadowrocket" (recommended)
3. Purchase and install

### Step 2: Get Your Configuration

Your admin provided you with:
- `alice_20251106_123456_shadowsocks.txt` - Connection details
- `alice_20251106_123456_shadowsocks_qr.png` - QR code for instant setup

**Configuration file looks like:**
```
Shadowsocks Configuration
Username: alice
Server: YOUR_SERVER_IP
Port: 8388
Password: a0xp4kKpSoJPeUxCVjactg==
Method: chacha20-ietf-poly1305

Connection URL:
ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTphMHhwNGtLcFNvSlBlVXhDVmphY3RnPT0=@YOUR_SERVER_IP:8388
```

### Step 3: Setup via QR Code (Easiest)

1. Open **Shadowrocket** app
2. Tap the **+** button (top right)
3. Select **Scan QR Code**
4. Scan your `shadowsocks_qr.png` file
5. Tap **Done**
6. Toggle the connection switch **ON**

**That's it!** Your VPN is connected.

### Step 4: Manual Setup (Alternative)

If QR code doesn't work:

1. Open **Shadowrocket**
2. Tap **+** (top right)
3. Select **Type: Shadowsocks**
4. Enter details from your `.txt` file:
   - **Address:** Your server IP
   - **Port:** 8388 (or from your config)
   - **Password:** Copy from config file
   - **Algorithm:** chacha20-ietf-poly1305
5. Tap **Done**
6. Toggle connection **ON**

### Step 5: Verify Connection

```
1. Open Safari
2. Visit: https://ifconfig.me
3. Should show your VPN server's IP (not your home IP)
```

## 🤖 Android Setup (Shadowsocks)

### Step 1: Install Shadowsocks App

**Recommended app:**
- **Shadowsocks for Android** (Free) - Official app

**Installation:**
1. Open **Google Play Store**
2. Search for "Shadowsocks"
3. Install "Shadowsocks" by Max Lv
4. Open the app

### Step 2: Setup via QR Code (Easiest)

1. Open **Shadowsocks** app
2. Tap the **+** button
3. Select **Scan QR Code**
4. Scan your `shadowsocks_qr.png` file
5. Tap the **paper plane icon** to connect

**Connected!** Check your IP to verify.

### Step 3: Manual Setup (Alternative)

If QR code doesn't work:

1. Open **Shadowsocks** app
2. Tap **+** button
3. Select **Manual Settings**
4. Enter details:
   - **Server:** Your server IP
   - **Remote Port:** 8388
   - **Password:** From your config
   - **Encrypt Method:** chacha20-ietf-poly1305
5. Tap **Save** (checkmark icon)
6. Tap **Paper plane icon** to connect

### Step 4: Verify Connection

```
1. Open Chrome browser
2. Visit: https://ifconfig.me
3. Should show VPN server IP
```

## 💻 macOS Setup (Shadowsocks)

### Step 1: Install Shadowsocks Client

**Recommended:** ShadowsocksX-NG (Free)

```bash
# Install via Homebrew
brew install shadowsocks-libev

# Or download GUI: ShadowsocksX-NG
# https://github.com/shadowsocks/ShadowsocksX-NG/releases
```

### Step 2: Configure

**Using ShadowsocksX-NG (GUI):**
1. Open **ShadowsocksX-NG**
2. Click menu bar icon → **Servers** → **Server Preferences**
3. Click **+** to add server
4. Enter details from your `.txt` file:
   - **Address:** Server IP
   - **Port:** 8388
   - **Encryption:** chacha20-ietf-poly1305
   - **Password:** From config
5. Click **OK**
6. Click menu bar icon → **Turn Shadowsocks On**

**Using command-line:**
```bash
# Create config file
cat > ~/shadowsocks.json << 'EOF'
{
  "server": "YOUR_SERVER_IP",
  "server_port": 8388,
  "local_port": 1080,
  "password": "YOUR_PASSWORD",
  "timeout": 300,
  "method": "chacha20-ietf-poly1305"
}
EOF

# Start Shadowsocks client
ss-local -c ~/shadowsocks.json

# Configure system to use SOCKS5 proxy at 127.0.0.1:1080
# System Preferences → Network → Advanced → Proxies
```

---

# Protocol 3: V2Ray

**Best for:** Highly restrictive networks (China, Iran), maximum obfuscation
**Speed:** ⭐⭐⭐ (Medium - slower due to heavy obfuscation)
**Mobile:** ⭐⭐⭐⭐⭐ (Excellent - iOS/Android native apps with QR codes)
**Obfuscation:** ⭐⭐⭐⭐⭐ (Maximum - hardest to block)
**iOS App:** Shadowrocket ($2.99) - same app as Shadowsocks!

V2Ray provides the strongest obfuscation using the VMess protocol. Perfect as a backup when other protocols are blocked, and essential for heavily censored networks.

**iOS Users:** If you already bought Shadowrocket for Shadowsocks, you can use V2Ray too - just scan the V2Ray QR code!

## 📱 iOS Setup (V2Ray)

### Step 1: Install V2Ray App

**Recommended apps:**
- **Shadowrocket** ($2.99) - Supports V2Ray + Shadowsocks
- **Kitsunebi** ($4.99) - Dedicated V2Ray client
- **Quantumult X** ($7.99) - Advanced features

**Note:** Shadowrocket supports both Shadowsocks and V2Ray, so you only need one app!

### Step 2: Get Your Configuration

Your admin provided:
- `alice_20251106_123456_v2ray.txt` - Connection details
- `alice_20251106_123456_v2ray_qr.png` - QR code

**Configuration file looks like:**
```
V2Ray VMess Configuration
Username: alice
Server: YOUR_SERVER_IP
Port: 80
UUID: 20411e00-3571-5874-a809-609bc91618ec
AlterID: 0
Network: tcp
Type: none

Connection URL:
vmess://eyJ2IjogIjIiLCAicHMiOiAi...
```

### Step 3: Setup via QR Code (Easiest)

1. Open **Shadowrocket** app
2. Tap **+** button (top right)
3. Select **Scan QR Code**
4. Scan your `v2ray_qr.png` file
5. Tap **Done**
6. Toggle connection **ON**

**Done!** V2Ray connection established.

### Step 4: Manual Setup (Alternative)

If QR code doesn't work:

1. Open **Shadowrocket**
2. Tap **+**
3. Select **Type: VMess**
4. Enter details from `.txt` file:
   - **Address:** Server IP
   - **Port:** 80
   - **UUID:** From your config
   - **AlterID:** 0
   - **Security:** auto
   - **Network:** tcp
5. Tap **Done**
6. Toggle connection **ON**

## 🤖 Android Setup (V2Ray)

### Step 1: Install V2Ray App

**Recommended app:**
- **v2rayNG** (Free) - Official Android client

**Installation:**
1. Open **Google Play Store**
2. Search for "v2rayNG"
3. Install app by CenmRev
4. Open the app

### Step 2: Setup via QR Code (Easiest)

1. Open **v2rayNG** app
2. Tap **+** button (bottom right)
3. Select **Import config from QR code**
4. Scan your `v2ray_qr.png` file
5. Tap the **connection** to activate
6. Tap the **V icon** at bottom to connect

**Connected!**

### Step 3: Manual Setup (Alternative)

If QR code doesn't work:

1. Open **v2rayNG**
2. Tap **+** button
3. Select **Manually input [VMess]**
4. Enter details:
   - **Remarks:** alice (your username)
   - **Address:** Server IP
   - **Port:** 80
   - **UUID:** From config
   - **AlterID:** 0
   - **Security:** auto
   - **Network:** tcp
5. Tap **Save** (checkmark)
6. Tap connection to activate
7. Tap **V icon** to connect

## 💻 macOS Setup (V2Ray)

### Step 1: Install V2Ray Client

**Recommended:** V2rayU (Free GUI)

```bash
# Download V2rayU
# https://github.com/yanue/V2rayU/releases

# Or use command-line v2ray-core
brew install v2ray
```

### Step 2: Configure V2rayU (GUI)

1. Open **V2rayU**
2. Click menu bar icon → **Configure**
3. Click **+** to add server
4. Select **VMess**
5. Enter details from your `.txt` file:
   - **Address:** Server IP
   - **Port:** 80
   - **UUID:** From config
   - **AlterID:** 0
   - **Security:** auto
   - **Network:** tcp
6. Click **OK**
7. Click menu bar icon → **Turn V2Ray On**

### Step 3: Command-Line Setup (Alternative)

```bash
# Create V2Ray config
cat > ~/v2ray-config.json << 'EOF'
{
  "inbounds": [{
    "port": 1080,
    "protocol": "socks",
    "settings": {"udp": true}
  }],
  "outbounds": [{
    "protocol": "vmess",
    "settings": {
      "vnext": [{
        "address": "YOUR_SERVER_IP",
        "port": 80,
        "users": [{"id": "YOUR_UUID", "alterId": 0}]
      }]
    }
  }]
}
EOF

# Start V2Ray
v2ray run -c ~/v2ray-config.json

# Configure system to use SOCKS5 proxy at 127.0.0.1:1080
```

---

## 🔧 Troubleshooting

### WireGuard Issues (macOS)

#### "Operation not permitted" Error
**Problem:** udp2raw can't create raw sockets
**Solution:**
```bash
# Check System Integrity Protection
csrutil status

# Grant Full Disk Access to Terminal:
System Preferences → Security & Privacy → Privacy → Full Disk Access
Click the lock to make changes
Add Terminal app
```

#### VPN Connects but No Internet
**Problem:** DNS not working or routing issues
**Solution:**
```bash
# Check DNS
scutil --dns | grep nameserver

# Manually set DNS if needed
sudo networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8

# Check routing table
netstat -nr | grep wg

# Verify WireGuard interface
ifconfig wg0
```

#### udp2raw Process Won't Start
**Problem:** Binary not executable or wrong architecture
**Solution:**
```bash
# Check your architecture
uname -m
# x86_64 = Intel (use amd64 binary)
# arm64 = Apple Silicon (use arm binary)

# Verify binary
file /usr/local/bin/udp2raw
ls -la /usr/local/bin/udp2raw

# Re-download correct version if needed
cd /usr/local/bin
sudo rm udp2raw
# Download correct version from GitHub
```

#### Connection Drops Frequently
**Problem:** MTU size too large
**Solution:**
```ini
# In your .conf file, reduce MTU
[Interface]
MTU = 1200  # Try 1200, 1000, or even 900
```

#### Can't Start wg-quick
**Problem:** Configuration file errors
**Solution:**
```bash
# Check configuration syntax
sudo wg-quick up alice

# View detailed errors
sudo wg-quick up alice --verbose

# Verify file exists and has correct permissions
ls -la /etc/wireguard/alice.conf
```

### WireGuard iOS Issues (with workarounds)

#### Travel Router Not Working
**Problem:** Router can't connect to VPN
**Solution:**
1. Check router's WireGuard configuration
2. Verify udp2raw is running on router
3. Check router's firewall rules
4. Verify port 443 is not blocked

#### Mac Internet Sharing Not Working
**Problem:** iOS device can't access internet through Mac
**Solution:**
1. Verify Mac's VPN is connected: `sudo wg show`
2. Check Internet Sharing is enabled
3. Restart Internet Sharing service
4. Forget WiFi network on iOS and reconnect

### Shadowsocks Issues

#### QR Code Won't Scan
**Problem:** App can't read QR code
**Solution:**
1. Ensure good lighting and focus
2. Try manual entry instead (use details from `.txt` file)
3. Verify QR code image is not corrupted (should be ~1-2 KB PNG)
4. Try different QR scanner app

#### Connection Fails with "Invalid Password"
**Problem:** Authentication error
**Solution:**
1. Copy password exactly from `.txt` file (no extra spaces)
2. Verify encryption method is: `chacha20-ietf-poly1305`
3. Check server IP is correct
4. Verify port (usually 8388)

#### Connected but No Internet
**Problem:** Shadowsocks connected but no data flow
**Solution:**
```bash
# iOS: Check app settings
1. Open Shadowrocket
2. Settings → Global Routing → Proxy
3. Verify "Proxy" is selected (not "Direct")

# Android: Check routing
1. Open Shadowsocks
2. Settings → Route → All
3. Ensure "All" traffic is routed

# macOS: Check proxy settings
System Preferences → Network → Advanced → Proxies
Ensure SOCKS Proxy is enabled: 127.0.0.1:1080
```

#### App Shows "Connection Timeout"
**Problem:** Can't reach server
**Solution:**
1. Verify server is running: Ask admin to check status
2. Test with ping (may not work if ICMP blocked)
3. Try different network (switch from WiFi to cellular)
4. Check if port 8388 is blocked by local firewall
5. Switch to V2Ray as backup

### V2Ray Issues

#### QR Code Not Recognized
**Problem:** App doesn't recognize VMess QR code
**Solution:**
1. Ensure using V2Ray-compatible app (Shadowrocket, v2rayNG)
2. QR should start with `vmess://`
3. Try manual entry with UUID from `.txt` file
4. Verify QR code PNG is valid (~2 KB)

#### "Bad Request" or "Invalid UUID"
**Problem:** Server rejects connection
**Solution:**
1. Copy UUID exactly from config file (no spaces)
2. Verify AlterID is set to `0`
3. Check server address and port (80)
4. Ensure Network type is `tcp`
5. Security should be `auto` or `aes-128-gcm`

#### Connection Drops Frequently
**Problem:** V2Ray disconnects often
**Solution:**
```bash
# iOS/Android: Enable auto-reconnect
Settings → Connection → Auto Reconnect

# Try different network settings
1. Switch from tcp to ws (WebSocket)
2. Add TLS if available
3. Reduce timeout values
```

#### Slow Speed
**Problem:** V2Ray is very slow
**Solution:**
1. **Normal:** V2Ray is slower than WireGuard due to obfuscation overhead
2. Try Shadowsocks instead (faster with good obfuscation)
3. Check server load: Ask admin for server stats
4. Use speed test to isolate issue: https://speed.cloudflare.com/
5. Consider using WireGuard on desktop for maximum speed

### General Multi-Protocol Issues

#### None of the Protocols Work
**Problem:** All three protocols fail to connect
**Solution:**
1. **Check server status:** Ask admin to verify server is running
2. **Test basic connectivity:** Can you ping server IP?
3. **Firewall issue:** Your network may block all VPN traffic
4. **Server IP changed:** Verify server IP hasn't changed
5. **Account issue:** Confirm your username is active

#### How to Switch Protocols
**Problem:** Want to try different protocol
**Solution:**
- **iOS:** Install Shadowrocket - supports all 3 protocols in one app
- **Android:** Install separate apps (Shadowsocks, v2rayNG, WireGuard)
- **macOS:** Install all clients, use whichever works best

#### Which Protocol for Censored Networks?
**Recommendation priority:**
1. **Try Shadowsocks first** - Good balance of speed and obfuscation
2. **If blocked, use V2Ray** - Strongest obfuscation
3. **On desktop, use WireGuard** - Fastest but may be blocked

---

## 📊 Configuration File Explained

Understanding your obfuscated `.conf` file:

```ini
[Interface]
PrivateKey = aL6+fXETtv/i01j7jBQDKtnlNXHBfTy9eE2oAcyxfWM=
# Your device's private key (KEEP SECRET!)

Address = 10.7.0.3/24
# Your VPN IP address (unique per user)

MTU = 1280
# Maximum transmission unit (packet size)
# Lower = slower but more reliable through obfuscation

DNS = 1.1.1.1, 8.8.8.8
# DNS servers while connected
# 1.1.1.1 = Cloudflare (fast, private)
# 8.8.8.8 = Google (reliable)

# udp2raw obfuscation (THE KEY FEATURE!)
PreUp = sudo /usr/local/bin/udp2raw -c -l 127.0.0.1:4096 -r SERVER_IP:443 -k YOUR_UDP2RAW_PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a &
# Starts udp2raw client in fake TCP mode on port 443
# -c = client mode
# -l = local listen address (127.0.0.1:4096)
# -r = remote server (YOUR_SERVER_IP:443)
# -k = encryption password
# --raw-mode faketcp = disguise as TCP traffic
# --cipher-mode xor = encryption method
# --auth-mode hmac_sha1 = authentication

PostDown = sudo killall udp2raw
# Stops udp2raw when disconnecting

[Peer]
PublicKey = D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
# Server's public key

AllowedIPs = 0.0.0.0/0
# Routes ALL traffic through VPN
# For split tunnel: 10.7.0.0/24 (VPN traffic only)

Endpoint = 127.0.0.1:4096
# Connects to LOCAL udp2raw client
# udp2raw then forwards to server's port 443

PersistentKeepalive = 25
# Sends keepalive every 25 seconds
# Maintains connection through NAT
```

---

## 🎯 How Obfuscation Works

### Normal WireGuard (Easily Detected)
```
Your Device → WireGuard UDP packets → VPN Server
                   ↑
              DPI detects & blocks
```

### Capybara with udp2raw (DPI Evasion)
```
Your Device → WireGuard → udp2raw → Fake HTTPS/TCP → VPN Server
                                              ↑
                              DPI sees normal HTTPS traffic
```

**Port 443 = HTTPS port** - Networks allow HTTPS traffic
**Fake TCP packets** - Looks like legitimate web traffic
**Encrypted payload** - WireGuard data hidden inside

---

## 🔍 Testing Your Connection

### Basic Connectivity Test (All Protocols)

**Test 1: Check Your IP Changed**
```bash
# Visit in browser or use curl
curl ifconfig.me
# OR
curl https://api.ipify.org

# Should show VPN server's IP, not your home/mobile IP
```

**Test 2: DNS Resolution**
```bash
# Check DNS is working
nslookup google.com
dig google.com
```

**Test 3: Protocol-Specific Tests**

**WireGuard:**
```bash
# Check WireGuard interface
sudo wg show

# Test VPN gateway
ping 10.7.0.1

# Check routing
netstat -nr | grep wg

# Verify udp2raw is running
ps aux | grep udp2raw
```

**Shadowsocks:**
```bash
# macOS: Check Shadowsocks process
ps aux | grep ss-local

# Check SOCKS proxy
curl --socks5 127.0.0.1:1080 https://ifconfig.me

# iOS/Android: Use in-app connection test
# Shadowrocket: Home → Test Connection
# Shadowsocks Android: Long press server → Test Latency
```

**V2Ray:**
```bash
# macOS: Check V2Ray process
ps aux | grep v2ray

# Check SOCKS proxy
curl --socks5 127.0.0.1:1080 https://ifconfig.me

# iOS/Android: Use in-app test
# Shadowrocket: Home → Test Connection
# v2rayNG: Long press server → Real ping
```

### Verify Obfuscation is Working

**WireGuard with udp2raw:**
```bash
# Check udp2raw is running
ps aux | grep udp2raw
# Should see: udp2raw -c -l 127.0.0.1:4096 -r SERVER_IP:443 ...

# Monitor traffic (requires network access)
sudo tcpdump -i any port 443 -n
# Should show TCP packets on port 443 (not UDP WireGuard)
```

**Shadowsocks:**
```bash
# Monitor encrypted traffic
sudo tcpdump -i any port 8388 -n
# Should show encrypted packets (unreadable payload)
```

**V2Ray:**
```bash
# Monitor VMess traffic
sudo tcpdump -i any port 80 -n
# Should show encrypted TCP streams
```

### Advanced Tests

**Security Tests:**
```bash
# Check for DNS leaks
# Visit: https://www.dnsleaktest.com/
# Should show VPN server's DNS, not your ISP's

# Check for IPv6 leaks
# Visit: https://test-ipv6.com/
# Should show "IPv6 not detected" if VPN doesn't support IPv6

# Check for WebRTC leaks
# Visit: https://browserleaks.com/webrtc
# Should NOT show your real IP
```

**Performance Tests:**
```bash
# Speed test (all protocols)
# Visit: https://speed.cloudflare.com/
# Or use: https://fast.com

# Command line speed test
curl -o /dev/null https://speed.cloudflare.com/__down?bytes=100000000

# Latency test (WireGuard)
ping -c 10 10.7.0.1

# Expected speeds:
# WireGuard: 50-200 Mbps (depends on server)
# Shadowsocks: 30-100 Mbps
# V2Ray: 20-80 Mbps (slower due to heavy obfuscation)
```

**Protocol Comparison Test:**
```bash
# Test all three protocols on same device
# Record speeds for each:

1. Connect with WireGuard → Run speed test → Record result
2. Connect with Shadowsocks → Run speed test → Record result
3. Connect with V2Ray → Run speed test → Record result

# Use fastest for normal use, others as backups
```

---

## 🌍 Country-Specific Notes

### China 🇨🇳
- **Status:** Heavy VPN blocking with advanced DPI
- **Protocol Recommendations:**
  1. **V2Ray** - Works best, strongest obfuscation
  2. **Shadowsocks** - Good alternative, faster than V2Ray
  3. **WireGuard** - May be blocked, use as last resort
- **Best Practice:** Set up all 3 protocols before traveling
- **Mobile:** Use Shadowrocket with V2Ray config

### Russia 🇷🇺
- **Status:** Increasing VPN restrictions
- **Protocol Recommendations:**
  1. **Shadowsocks** - Currently works well
  2. **V2Ray** - Backup option
  3. **WireGuard + udp2raw** - Desktop only
- **Best Practice:** Monitor news for protocol blocks
- **Mobile:** Shadowsocks on port 8388 recommended

### Iran 🇮🇷
- **Status:** Aggressive blocking during protests
- **Protocol Recommendations:**
  1. **V2Ray** - Most reliable
  2. **Shadowsocks** - Secondary option
  3. **WireGuard** - Often blocked
- **Best Practice:** Have multiple servers in different countries
- **Mobile:** V2Ray with v2rayNG app

### Turkey 🇹🇷
- **Status:** Periodic VPN blocking
- **Protocol Recommendations:**
  1. **Shadowsocks** - Generally works
  2. **V2Ray** - Backup
  3. **WireGuard** - May work during non-restricted periods
- **Best Practice:** Switch protocols if one stops working

### UAE 🇦🇪
- **Status:** VPN usage illegal but rarely enforced for personal use
- **Protocol Recommendations:**
  1. **Shadowsocks** - Low profile
  2. **V2Ray** - Maximum stealth
  3. **WireGuard** - Avoid (easily detected)
- **Warning:** Check local laws before use

### Corporate Networks
- **Status:** Port 443 usually allowed (required for web access)
- **Protocol Recommendations:**
  1. **WireGuard + udp2raw on port 443** - Looks like HTTPS
  2. **Shadowsocks on port 443** - Also looks legitimate
  3. **V2Ray** - If others blocked
- **Note:** Check company VPN policy before bypassing
- **Best Practice:** Use only for personal devices, not company hardware

### General Guidelines by Censorship Level

| Censorship Level | Try First | Backup | Desktop Bonus |
|-----------------|-----------|--------|---------------|
| **Low** (US, EU, Canada) | WireGuard | Shadowsocks | WireGuard |
| **Medium** (Russia, Turkey) | Shadowsocks | V2Ray | WireGuard+udp2raw |
| **High** (China, Iran) | V2Ray | Shadowsocks | V2Ray |
| **Corporate** | WireGuard+udp2raw | Shadowsocks | WireGuard+udp2raw |

---

## 📞 Getting Help

### Check VPN Status from Server

Your VPN admin can help diagnose issues across all protocols:

```bash
# User management
./capybara.py user list --detailed
./capybara.py connection list

# Protocol-specific diagnostics
./capybara.py diag handshake alice      # WireGuard
./capybara.py diag ping alice           # WireGuard
./capybara.py logs show --service wireguard
./capybara.py logs show --service shadowsocks
./capybara.py logs show --service v2ray
./capybara.py logs show --service udp2raw

# Server health
./capybara.py server status
./capybara.py health check
```

### Common Diagnostic Commands

**WireGuard:**
```bash
# macOS - Check WireGuard status
sudo wg show

# Check udp2raw process
ps aux | grep udp2raw

# Restart connection
sudo wg-quick down alice
sudo killall udp2raw
sudo wg-quick up alice
```

**Shadowsocks:**
```bash
# macOS - Check Shadowsocks process
ps aux | grep ss-local

# Test SOCKS proxy
curl --socks5 127.0.0.1:1080 https://ifconfig.me

# iOS/Android - Reconnect
# Close and reopen app, toggle connection
```

**V2Ray:**
```bash
# macOS - Check V2Ray process
ps aux | grep v2ray

# Test SOCKS proxy
curl --socks5 127.0.0.1:1080 https://ifconfig.me

# Restart V2Ray (macOS)
killall v2ray
v2ray run -c ~/v2ray-config.json
```

---

## 🆘 Emergency Procedures

### If Current Protocol Stops Working

**Step 1: Switch to Another Protocol**

You have all three protocols! Switch immediately:

```
Current protocol failing?
├─ Using WireGuard? → Try Shadowsocks
├─ Using Shadowsocks? → Try V2Ray
└─ Using V2Ray? → Try WireGuard or Shadowsocks
```

**iOS/Android:** If using Shadowrocket, all protocols are in one app - just tap a different server

**macOS:** Start the client for a different protocol

### If All Protocols Stop Working

1. **Check server status (ask admin):**
   ```bash
   ./capybara.py server status
   ./capybara.py health check
   ./capybara.py service status
   ```

2. **Restart specific protocol client:**

   **WireGuard:**
   ```bash
   sudo wg-quick down alice
   sudo killall udp2raw
   sudo wg-quick up alice
   ```

   **Shadowsocks:**
   ```bash
   # macOS
   killall ss-local
   ss-local -c ~/shadowsocks.json

   # iOS/Android: Close and reopen app
   ```

   **V2Ray:**
   ```bash
   # macOS
   killall v2ray
   v2ray run -c ~/v2ray-config.json

   # iOS/Android: Close and reopen app
   ```

3. **Test basic connectivity:**
   ```bash
   # Can you reach the server?
   ping YOUR_SERVER_IP

   # Can you reach specific ports?
   nc -zv YOUR_SERVER_IP 443    # WireGuard
   nc -zv YOUR_SERVER_IP 8388   # Shadowsocks
   nc -zv YOUR_SERVER_IP 80   # V2Ray
   ```

4. **Regenerate all configurations (last resort):**
   ```bash
   # Ask admin to regenerate
   ./capybara.py user remove alice
   ./capybara.py user add alice --description "Regenerated"

   # Download all 6 new files and reinstall
   ```

### If Specific Protocol Detected/Blocked

**WireGuard blocked:**
- Switch to Shadowsocks (faster) or V2Ray (more obfuscation)
- If desktop: Try changing udp2raw mode to `icmp` instead of `faketcp`

**Shadowsocks blocked:**
- Switch to V2Ray (stronger obfuscation)
- Ask admin if server can move Shadowsocks to port 443

**V2Ray blocked:**
- Unlikely (strongest obfuscation)
- Try Shadowsocks (may be less suspicious)
- Contact admin about enabling TLS for V2Ray

### Quick Protocol Switch Guide

**Scenario: You're traveling to China tomorrow**
1. **Before you leave:**
   - Install Shadowrocket on iOS ($2.99)
   - Scan all 3 QR codes (takes 2 minutes)
   - Test all 3 protocols work

2. **In China:**
   - Try V2Ray first (best for China)
   - If slow, try Shadowsocks
   - Keep WireGuard as last resort

**Scenario: Corporate network blocks your VPN**
1. Try WireGuard+udp2raw (looks like HTTPS)
2. If blocked, try Shadowsocks on port 8388
3. If blocked, try V2Ray on port 80
4. If all blocked, network has deep inspection - may need different server IP

---

## 📚 Additional Resources

### Official Documentation

**WireGuard:**
- Official Site: https://www.wireguard.com/
- Quick Start: https://www.wireguard.com/quickstart/
- udp2raw: https://github.com/wangyu-/udp2raw

**Shadowsocks:**
- Official Site: https://shadowsocks.org/
- GitHub: https://github.com/shadowsocks
- iOS App (Shadowrocket): https://apps.apple.com/app/shadowrocket/id932747118
- Android App: https://github.com/shadowsocks/shadowsocks-android
- macOS (ShadowsocksX-NG): https://github.com/shadowsocks/ShadowsocksX-NG

**V2Ray:**
- Official Site: https://www.v2fly.org/
- GitHub: https://github.com/v2fly/v2ray-core
- iOS App (Shadowrocket): Supports V2Ray
- Android App (v2rayNG): https://github.com/2dust/v2rayNG
- macOS (V2rayU): https://github.com/yanue/V2rayU

### Mobile Apps Summary

**iOS (Choose one):**
- **Shadowrocket** ($2.99) - ⭐ Recommended - Supports all 3 protocols
- **Quantumult X** ($7.99) - Advanced features, all protocols
- **Kitsunebi** ($4.99) - V2Ray specialist

**Android:**
- **Shadowsocks** (Free) - For Shadowsocks only
- **v2rayNG** (Free) - For V2Ray only
- **WireGuard** (Free) - For WireGuard only (no udp2raw support)

### Hardware (For WireGuard on iOS)
- **GL.iNet Routers:** https://www.gl-inet.com/
- **OpenWrt:** https://openwrt.org/

### Testing Tools
- **IP Check:** https://ifconfig.me
- **DNS Leak Test:** https://www.dnsleaktest.com/
- **IPv6 Test:** https://test-ipv6.com/
- **WebRTC Leak Test:** https://browserleaks.com/webrtc
- **Speed Test:** https://speed.cloudflare.com/ or https://fast.com

### Censorship Circumvention Resources
- **OONI Probe:** Test network censorship - https://ooni.org/
- **Censored Planet:** Research on internet censorship
- **GreatFire:** Track censorship in China - https://en.greatfire.org/

---

## 📝 Quick Reference Card

**For Copy-Paste Reference:**

```
🦫 CAPYBARA MULTI-PROTOCOL VPN

FILES YOU RECEIVED:
- username_wireguard.conf + QR
- username_shadowsocks.txt + QR
- username_v2ray.txt + QR

QUICK SETUP:
✅ iOS: Install Shadowrocket → Scan all 3 QR codes → Done!
✅ Android: Install Shadowsocks + v2rayNG → Scan QR codes → Done!
✅ macOS: Follow WireGuard setup for desktop

WHICH TO USE:
📱 Mobile: Shadowsocks (fastest setup, good speed)
💻 Desktop: WireGuard (maximum speed)
🔒 Censored: V2Ray (maximum obfuscation)
🚨 Blocked: Switch to another protocol!

TROUBLESHOOTING:
1. Check IP: curl ifconfig.me
2. Try different protocol
3. Contact admin

PORTS:
- WireGuard: 443 (via udp2raw)
- Shadowsocks: 8388
- V2Ray: 80
```

---

**🦫 Capybara VPN - Multi-Protocol Client Setup Complete!**

**Version:** 3.0.0 (Multi-Protocol Edition)
**Last Updated:** November 6, 2025
**Protocols:** WireGuard + udp2raw, Shadowsocks, V2Ray
**Support:** Check main README.md or run `./capybara.py --help`

**Remember:** You have 3 protocols - if one doesn't work, try another! 🎯
