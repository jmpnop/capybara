# 🦫 Capybara VPN - Client Setup Guide

Complete guide for setting up WireGuard VPN clients on macOS and iOS with udp2raw obfuscation.

---

## 📋 Prerequisites

Before setting up a client, you need:

1. **A user account created on the VPN server:**
   ```bash
   ./capybara.py user add alice --description "Alice's device"
   ```

2. **The generated client configuration file** from `./vpn_clients/`:
   - Example: `alice_20251106_123456.conf`
   - This file contains your private key and connection details

3. **Server information:**
   - Server IP: `66.42.119.38`
   - Obfuscated port: `443` (TCP, disguised as HTTPS)
   - Direct WireGuard port: `51820` (UDP, may be blocked in restricted networks)

---

## 🍎 macOS Setup

macOS supports both direct WireGuard connections and obfuscated connections using udp2raw.

### Option 1: Standard WireGuard (Recommended for Most Users)

**Best for:** Unrestricted networks, fastest performance, easiest setup.

#### Step 1: Install WireGuard

Download and install from one of these sources:
- **Mac App Store** (Recommended): [WireGuard](https://apps.apple.com/us/app/wireguard/id1451685025)
- **Homebrew**: `brew install --cask wireguard-tools`
- **Official Website**: https://www.wireguard.com/install/

#### Step 2: Import Configuration

**Method A: Via WireGuard App GUI**
1. Open WireGuard app
2. Click **"+"** button or **"Import tunnel(s) from file..."**
3. Select your `.conf` file (e.g., `alice_20251106_123456.conf`)
4. Click **"Activate"** to connect

**Method B: Via File Association**
1. Locate your `.conf` file in Finder
2. Double-click the file
3. WireGuard will open and import automatically
4. Click **"Activate"** to connect

**Method C: Via QR Code (for mobile import)**
```bash
# Generate QR code from config file
brew install qrencode
qrencode -t ansiutf8 < alice_20251106_123456.conf
```

#### Step 3: Verify Connection

Once activated:
```bash
# Check your new IP address
curl ifconfig.me

# Should show server IP (66.42.119.38) instead of your real IP

# Ping the VPN gateway
ping 10.7.0.1

# Check DNS resolution
nslookup google.com
```

---

### Option 2: Obfuscated Connection (For Restricted Networks)

**Best for:** Networks with DPI (Deep Packet Inspection), China, Russia, Iran, or corporate firewalls blocking VPN traffic.

This method disguises WireGuard traffic as regular HTTPS traffic on port 443.

#### Step 1: Install Requirements

```bash
# Install WireGuard
brew install wireguard-tools

# Download udp2raw (pre-built binary)
cd /usr/local/bin
sudo curl -L -o udp2raw https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_amd64
sudo chmod +x udp2raw

# Verify installation
udp2raw --help
```

#### Step 2: Modify Configuration File

Edit your `.conf` file to use udp2raw:

**Original configuration:**
```ini
[Interface]
PrivateKey = aL6+fXETtv/i01j7jBQDKtnlNXHBfTy9eE2oAcyxfWM=
Address = 10.7.0.3/24
MTU = 1280
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
AllowedIPs = 0.0.0.0/0
Endpoint = 66.42.119.38:51820  # Direct connection
PersistentKeepalive = 25
```

**Modified for obfuscation:**
```ini
[Interface]
PrivateKey = aL6+fXETtv/i01j7jBQDKtnlNXHBfTy9eE2oAcyxfWM=
Address = 10.7.0.3/24
MTU = 1280
DNS = 1.1.1.1, 8.8.8.8

# Start udp2raw on connection
PreUp = sudo /usr/local/bin/udp2raw -c -l 127.0.0.1:4096 -r 66.42.119.38:443 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a &
PostDown = sudo killall udp2raw

[Peer]
PublicKey = D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
AllowedIPs = 0.0.0.0/0
Endpoint = 127.0.0.1:4096  # Changed to local udp2raw
PersistentKeepalive = 25
```

**Key changes:**
- `Endpoint` changed from `66.42.119.38:51820` to `127.0.0.1:4096` (local udp2raw)
- Added `PreUp` to start udp2raw client
- Added `PostDown` to stop udp2raw when disconnecting

#### Step 3: Grant Sudo Permissions (Required)

udp2raw requires root privileges for raw socket access:

```bash
# Edit sudoers file
sudo visudo

# Add this line (replace 'yourusername' with your macOS username):
yourusername ALL=(ALL) NOPASSWD: /usr/local/bin/udp2raw
yourusername ALL=(ALL) NOPASSWD: /usr/bin/killall udp2raw

# Save and exit (Ctrl+X, then Y, then Enter)
```

**Why this is needed:** udp2raw creates raw TCP packets to disguise UDP traffic, which requires root privileges.

#### Step 4: Connect Using Command Line

```bash
# Activate the VPN tunnel
sudo wg-quick up alice

# Check status
sudo wg show

# Deactivate
sudo wg-quick down alice
```

#### Step 5: Verify Obfuscation is Working

```bash
# Check that udp2raw is running
ps aux | grep udp2raw

# Test connection
curl ifconfig.me

# Verify traffic appears as HTTPS (from another machine)
sudo tcpdump -i any port 443 -nn
```

---

## 📱 iOS Setup

iOS supports WireGuard natively through the official app, but **does not support udp2raw** (requires jailbreak).

### Standard WireGuard Connection (No Obfuscation)

**Limitations:** May be blocked in restricted networks (China, Russia, corporate firewalls).

#### Step 1: Install WireGuard App

Download from the App Store:
- **App Store**: [WireGuard](https://apps.apple.com/us/app/wireguard/id1441195209)

#### Step 2: Import Configuration

**Method A: QR Code (Easiest)**

1. On your Mac, generate a QR code:
   ```bash
   brew install qrencode
   qrencode -t ansiutf8 < alice_20251106_123456.conf

   # Or save as image
   qrencode -t png -o alice_qr.png < alice_20251106_123456.conf
   open alice_qr.png
   ```

2. On your iPhone/iPad:
   - Open WireGuard app
   - Tap **"+"** button
   - Select **"Create from QR code"**
   - Scan the QR code
   - Tap **"Save"**

**Method B: AirDrop**

1. On your Mac:
   - Right-click the `.conf` file
   - Select **"Share" → "AirDrop"**
   - Select your iPhone/iPad

2. On your iPhone/iPad:
   - Accept the AirDrop transfer
   - Tap the file
   - Select **"Open in WireGuard"**
   - Tap **"Save"**

**Method C: iCloud Drive**

1. Upload the `.conf` file to iCloud Drive
2. On iPhone/iPad, open Files app
3. Navigate to the `.conf` file
4. Tap and select **"Share" → "WireGuard"**
5. Tap **"Save"**

#### Step 3: Connect

1. Open WireGuard app
2. Toggle the switch next to your tunnel name
3. Tap **"Allow"** when prompted to add VPN configuration
4. Enter your device passcode or use Face ID/Touch ID

#### Step 4: Verify Connection

1. In WireGuard app, you should see:
   - **Status**: Active
   - **Transfer**: Data sent/received
   - **Latest handshake**: Recent timestamp

2. Test in Safari:
   ```
   Visit: https://ifconfig.me
   Should show: 66.42.119.38 (server IP)
   ```

---

### iOS with Obfuscation (Advanced - Requires Separate Device)

Since iOS doesn't support udp2raw directly, you have these options:

#### Option 1: GL.iNet Travel Router (Recommended)

Use a portable router that runs udp2raw:

1. **Hardware needed:** GL.iNet GL-MT300N-V2 (~$20)
2. **Setup:**
   - Install OpenWrt on router
   - Install WireGuard and udp2raw packages
   - Configure router to handle obfuscation
   - Connect iOS device to router's WiFi
3. **Benefits:**
   - Works with any device (iOS, Android, laptop)
   - No jailbreak needed
   - Portable solution

#### Option 2: Mac as Proxy

Use your Mac as a VPN gateway:

1. **On Mac:** Run obfuscated WireGuard connection (see macOS Option 2)
2. **Enable Internet Sharing:**
   ```bash
   # Share VPN connection over WiFi
   System Preferences → Sharing → Internet Sharing
   Share from: WireGuard (wg0)
   To computers using: Wi-Fi
   ```
3. **On iOS:** Connect to Mac's shared WiFi
4. **Benefits:** All iOS traffic goes through obfuscated VPN

#### Option 3: Shadowsocks/V2Ray (Alternative)

Instead of WireGuard, use mobile-friendly obfuscation:

1. Install Shadowsocks/V2Ray on server
2. Use iOS apps (Shadowrocket, QuantumultX)
3. These have built-in obfuscation support

---

## 🔧 Troubleshooting

### macOS Issues

#### "Operation not permitted" Error
**Problem:** udp2raw can't create raw sockets
**Solution:**
```bash
# Check System Integrity Protection status
csrutil status

# Grant Full Disk Access to Terminal:
System Preferences → Security & Privacy → Full Disk Access → Add Terminal
```

#### VPN Connects but No Internet
**Problem:** DNS not working or routing issues
**Solution:**
```bash
# Check DNS
scutil --dns

# Manually set DNS
sudo networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8

# Check routing
netstat -nr | grep wg
```

#### udp2raw Process Won't Start
**Problem:** Binary not executable or wrong architecture
**Solution:**
```bash
# Check architecture
uname -m
# If arm64 (Apple Silicon), download arm64 binary
# If x86_64 (Intel), download amd64 binary

# Verify binary
file /usr/local/bin/udp2raw

# Check permissions
ls -la /usr/local/bin/udp2raw
sudo chmod +x /usr/local/bin/udp2raw
```

#### Connection Drops Frequently
**Problem:** MTU size too large
**Solution:**
```ini
# In your .conf file, reduce MTU
[Interface]
MTU = 1280  # Try 1280, 1200, or 1000
```

### iOS Issues

#### Can't Import Configuration
**Problem:** File format incorrect
**Solution:**
- Ensure file ends with `.conf` extension
- Check file is valid WireGuard format
- Try QR code method instead

#### Connection Established but No Internet
**Problem:** DNS or AllowedIPs misconfigured
**Solution:**
1. Edit tunnel in WireGuard app
2. Verify DNS servers: `1.1.1.1, 8.8.8.8`
3. Verify AllowedIPs: `0.0.0.0/0` (routes all traffic)

#### "Unable to Create Tunnel" Error
**Problem:** Invalid private key or configuration
**Solution:**
- Regenerate configuration on server: `./capybara.py user remove alice && ./capybara.py user add alice`
- Re-import fresh configuration

#### VPN Blocked by Network
**Problem:** DPI detecting WireGuard
**Solution:**
- Use travel router with obfuscation (see Option 1 above)
- Or use Mac as proxy (see Option 2 above)
- Consider alternative protocols (Shadowsocks, V2Ray)

---

## 📊 Configuration File Explained

Understanding your `.conf` file:

```ini
[Interface]
PrivateKey = aL6+fXETtv/i01j7jBQDKtnlNXHBfTy9eE2oAcyxfWM=
# Your device's private key (keep secret!)

Address = 10.7.0.3/24
# Your VPN IP address (unique per user)

MTU = 1280
# Maximum transmission unit (packet size)
# Lower = slower but more reliable
# Higher = faster but may cause issues

DNS = 1.1.1.1, 8.8.8.8
# DNS servers to use while connected
# 1.1.1.1 = Cloudflare (fast, privacy-focused)
# 8.8.8.8 = Google (reliable)

[Peer]
PublicKey = D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
# Server's public key (identifies server)

AllowedIPs = 0.0.0.0/0
# Routes all traffic through VPN
# For split tunnel: 10.7.0.0/24 (VPN traffic only)

Endpoint = 66.42.119.38:443
# Server address and port
# :443 = obfuscated (HTTPS-like)
# :51820 = direct WireGuard

PersistentKeepalive = 25
# Send keepalive packet every 25 seconds
# Keeps connection alive through NAT
```

---

## 🎯 Best Practices

### Security

1. **Never share your private key** - It's in the `[Interface]` section
2. **Protect your .conf file** - Contains sensitive credentials
3. **Use strong device passcode** - Protects stored VPN config
4. **Enable auto-lock** - Prevents unauthorized VPN access

### Performance

1. **Use nearest server** - Lower latency
2. **Test different MTU sizes** - Find optimal value
3. **Use DNS over HTTPS** - Additional privacy layer
4. **Disable on trusted networks** - Save battery and bandwidth

### Privacy

1. **Always use VPN on public WiFi** - Protect from sniffing
2. **Enable on-demand rules (iOS)** - Auto-connect on untrusted networks
3. **Use privacy-focused DNS** - 1.1.1.1 or 9.9.9.9
4. **Disable IPv6 leaks** - Or use VPN IPv6 addresses

---

## 📱 On-Demand Rules (iOS Only)

Auto-connect VPN based on network conditions:

1. Open WireGuard app
2. Edit your tunnel
3. Tap **"On-Demand Activation"**
4. Configure rules:

**Example: Auto-connect on untrusted WiFi**
```
Cellular networks: Off
Wi-Fi: Off
Ethernet: Off
SSIDs to activate on:
  ☐ Home-WiFi (trusted)
  ☐ Office-WiFi (trusted)
  ☑ Any other WiFi (untrusted)
```

**Example: Always-on VPN**
```
Cellular networks: On
Wi-Fi: On
Ethernet: On
```

---

## 🔍 Testing Your Connection

### Basic Connectivity Test

```bash
# Check your external IP
curl ifconfig.me
# Should show: 66.42.119.38

# Check DNS resolution
nslookup google.com
# Should use VPN DNS servers

# Test VPN gateway
ping 10.7.0.1
# Should respond

# Check routing
# macOS:
netstat -nr | grep wg
# iOS: Not available
```

### Advanced Tests

```bash
# Check for DNS leaks
curl https://www.dnsleaktest.com/

# Check for IPv6 leaks
curl https://test-ipv6.com/

# Speed test
curl -o /dev/null https://speed.cloudflare.com/__down?bytes=100000000

# Latency test
ping -c 10 10.7.0.1
```

### Verify Obfuscation (macOS)

```bash
# Check udp2raw is running
ps aux | grep udp2raw

# Monitor obfuscated traffic (requires root)
sudo tcpdump -i any port 443 -nn -v
# Should show TCP packets (not UDP)
```

---

## 📞 Getting Help

### Check VPN Status from Server

Your VPN admin can check your connection:

```bash
./capybara.py user list --detailed
./capybara.py connection list
./capybara.py diag handshake alice
./capybara.py diag ping alice
```

### Common Commands for Troubleshooting

```bash
# macOS - Check WireGuard status
sudo wg show

# macOS - Restart WireGuard
sudo wg-quick down alice
sudo wg-quick up alice

# iOS - In WireGuard app
Settings → Export log file → Share with admin
```

---

## 🌍 Country-Specific Notes

### China
- **Standard WireGuard:** Usually blocked
- **Obfuscated (udp2raw):** Works well on port 443
- **Recommendation:** Use macOS Option 2 or travel router

### Russia
- **Standard WireGuard:** Often blocked
- **Obfuscated (udp2raw):** Recommended
- **Alternative:** Shadowsocks or V2Ray

### Iran
- **Standard WireGuard:** Blocked
- **Obfuscated (udp2raw):** May work, frequently updated blocking
- **Recommendation:** Use multiple protocols

### Corporate Networks
- **Standard WireGuard:** May be blocked
- **Obfuscated on port 443:** Usually works (appears as HTTPS)
- **Note:** Check company policy before bypassing

---

## 📚 Additional Resources

### Official Documentation
- **WireGuard:** https://www.wireguard.com/
- **udp2raw:** https://github.com/wangyu-/udp2raw

### macOS WireGuard
- **App Store:** https://apps.apple.com/us/app/wireguard/id1451685025
- **Homebrew:** https://formulae.brew.sh/cask/wireguard-tools

### iOS WireGuard
- **App Store:** https://apps.apple.com/us/app/wireguard/id1441195209
- **TestFlight:** Available for beta testing

### VPN Testing Tools
- **DNS Leak Test:** https://www.dnsleaktest.com/
- **IPv6 Test:** https://test-ipv6.com/
- **Speed Test:** https://speed.cloudflare.com/

---

## 🆘 Emergency Procedures

### If VPN Stops Working

1. **Check server status:**
   ```bash
   ./capybara.py server status
   ./capybara.py health check
   ```

2. **Restart VPN on device:**
   - macOS: `sudo wg-quick down alice && sudo wg-quick up alice`
   - iOS: Toggle off/on in app

3. **Regenerate configuration:**
   ```bash
   ./capybara.py user remove alice
   ./capybara.py user add alice
   # Re-import new .conf file on device
   ```

### If Locked Out

1. **Check if you're blocked:**
   ```bash
   ./capybara.py user list
   # Look for 'blocked' status
   ```

2. **Contact admin to unblock:**
   ```bash
   ./capybara.py user unblock alice
   ```

---

**🦫 Capybara VPN - Client Setup Complete!**

**Version:** 2.0.0
**Last Updated:** November 6, 2025
**Support:** Check main README.md or run `./capybara.py --help`
