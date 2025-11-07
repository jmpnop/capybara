# 🦫 Capybara - Multi-Protocol Censorship-Resistant VPN

<img width="3641" height="2048" alt="Capybara VPN - Multi-Protocol Anti-Censorship System" src="https://github.com/user-attachments/assets/0a93d0cf-ad45-45f7-b2a4-14f138bc39c2" />

**Capybara** is an advanced multi-protocol VPN infrastructure designed to bypass Deep Packet Inspection (DPI) and network censorship in restricted countries like China, Russia, and Iran.

### Core Capabilities:
- **🔄 Three Protocols** - WireGuard, Shadowsocks, and V2Ray with unified management
- **🛡️ DPI Evasion** - udp2raw obfuscation disguises VPN traffic as HTTPS on port 443
- **⚡ Automated Deployment** - One-command server setup on Alpine Linux
- **🎛️ Advanced Management** - Professional CLI with 35+ commands for monitoring, analytics, and control
- **📱 QR Code Provisioning** - Instant client configuration via QR codes for all protocols
- **🌐 Bilingual Support** - Full documentation in English and Russian
- **🔐 Unified Credentials** - Same user credentials work across all protocols

Built for networks where standard VPNs fail. Designed for privacy professionals, journalists, and users in restrictive environments.

## Why Choose Capybara?

### Technical Advantages
- **Port 443 Obfuscation** - Traffic appears as legitimate HTTPS, undetectable by DPI systems
- **Fake TCP Packets** - udp2raw transforms UDP WireGuard into TCP-like traffic
- **Enterprise Monitoring** - Real-time statistics, health checks, connection tracking, and analytics
- **Zero-Downtime Operations** - Restart individual services without affecting users
- **Disaster Recovery** - Automated backups with one-command restoration
- **Professional Diagnostics** - Network testing, handshake verification, and detailed logging

### Why "Capybara"?
Capybaras are nature's most chill animals - calm, adaptable, and excellent at navigating complex environments. Just like this VPN system helps you navigate internet censorship with ease.

## 🚀 Quick Start

### Part 1: Server Installation (One Command!)

**Unified Installation Script** (Recommended)

One script to install any combination of protocols:

```bash
# On your Alpine Linux VPS, run:
wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_capybara.sh
chmod +x install_capybara.sh
./install_capybara.sh              # Install all protocols (default)
```

**Installation Options:**
```bash
./install_capybara.sh              # All protocols (WireGuard + Shadowsocks + V2Ray)
./install_capybara.sh --wireguard  # WireGuard only
./install_capybara.sh --shadowsocks --v2ray  # Add to existing WireGuard server
./install_capybara.sh --help       # Show all options
```

**What it installs:**
- WireGuard + udp2raw (Port 443 - HTTPS disguise, DPI evasion)
- Shadowsocks (Port 8388 - AEAD encryption, mobile-friendly)
- V2Ray + WebSocket (Port 80 - HTTP disguise, mobile networks)
- Configures firewall for all protocols (awall)
- **Enables DNS resolution and proper NAT** for all protocols
- Generates server keys
- Sets up automatic startup

**Features:**
- ✅ Modular installation (choose which protocols you need)
- ✅ Updated V2Ray config (WebSocket on port 80 for mobile networks)
- ✅ Eliminates redundancy between old scripts
- ✅ Better error handling and logging

**Supported:** Alpine Linux 3.20+

### Part 2: Management Tool Installation

On your local machine (macOS, Linux, Windows):

```bash
git clone https://github.com/jmpnop/capybara.git
cd capybara
pip3 install -r requirements.txt
chmod +x capybara.py

# Create alias (optional)
echo 'alias vpn="python3 /path/to/capybara.py"' >> ~/.zshrc
```

Then configure `~/.capybara_config.yaml` with your server details and start managing!

## Protocols Explained

Capybara supports three battle-tested protocols, each with unique strengths:

### 1. WireGuard + udp2raw (Port 443)
**Best for**: Desktop users, maximum performance, DPI evasion
- **Speed**: Fastest protocol, minimal overhead
- **Obfuscation**: udp2raw disguises traffic as HTTPS
- **Setup**: Requires udp2raw client + WireGuard app
- **Use case**: Primary protocol for unrestricted access

### 2. Shadowsocks (Port 8388)
**Best for**: Mobile devices, iOS/Android, simple setup
- **Speed**: Fast, AEAD encryption (chacha20-ietf-poly1305)
- **Compatibility**: Wide client support (Shadowrocket, v2rayNG)
- **Setup**: Scan QR code, connect immediately
- **Use case**: Perfect for phones, backup protocol

### 3. V2Ray VMess + WebSocket (Port 80)
**Best for**: Mobile networks, DPI evasion, highly restrictive networks
- **Obfuscation**: WebSocket on port 80 (HTTP) - hard to block
- **Mobile-Optimized**: Works on Beeline, MTS, Megafon mobile networks
- **Flexibility**: Highly configurable transport options
- **Setup**: Scan QR code or manual configuration
- **Use case**: When Shadowsocks is blocked on mobile networks

**Why Three Protocols?**
- **Redundancy**: If one is blocked, switch to another
- **Device Compatibility**: Different devices work better with different protocols
- **Network Conditions**: Some protocols perform better in certain network environments
- **Future-Proof**: Multiple fallback options ensure continued access

## Advanced Features

### 🛡️ Anti-Censorship Technology
- **udp2raw Obfuscation** - Transforms WireGuard UDP into fake TCP packets on port 443
- **HTTPS Mimicry** - Traffic indistinguishable from legitimate web browsing
- **DPI Bypass** - Defeats Deep Packet Inspection used in China, Russia, Iran
- **Multi-Protocol Defense** - Three independent protocols for maximum resilience
- **Adaptive MTU** - Optimized packet sizes for obfuscation reliability
- **Persistent Tunnels** - Keepalive ensures connection through NAT and firewalls

### 📊 Enterprise Management
- **Real-Time Monitoring** - Live statistics dashboard with auto-refresh
- **Connection Analytics** - Track data transfer, handshakes, and session duration
- **Multi-Format Reports** - Generate usage reports in text, JSON, or CSV formats
- **Health Monitoring** - CPU, memory, disk, and network metrics
- **Service Orchestration** - Granular control over WireGuard, udp2raw, and firewall
- **Emergency Controls** - Instantly disconnect users or trigger emergency shutdown

### 🔧 Professional Operations
- **Zero-Downtime Updates** - Restart individual services without disconnecting users
- **Automated Backups** - One-command backup of all configurations and keys
- **Disaster Recovery** - Complete restoration from backup archives
- **Detailed Logging** - Service-specific logs with filtering and real-time tail
- **Network Diagnostics** - Built-in ping, port scanning, and handshake verification
- **QR Code Provisioning** - Automatic generation for instant mobile device setup

### 🧑‍💼 User Management
- **Instant Provisioning** - Add users with automatic key generation and IP assignment
- **Flexible Access Control** - Block/unblock users without server restart
- **Connection Tracking** - Monitor active connections with endpoint information
- **Domain/IP Blocking** - Filter specific resources at VPN level
- **Detailed User Views** - See handshake status, data transfer, and last seen time

## Basic Usage

After completing both Part 1 (Server Installation) and Part 2 (Management Tool Installation), you can start managing your VPN:

```bash
# Add a new user (automatically creates configs for all 3 protocols)
./capybara.py user add alice

# Add a user with description
./capybara.py user add bob --description "Bob from Sales"

# List all users
./capybara.py user list

# Check server status
./capybara.py server status

# Live monitoring
./capybara.py stats live

# Stop the VPN server
./capybara.py server stop

# Start the VPN server
./capybara.py server start

# Restart the VPN server
./capybara.py server restart
```

**Every user automatically gets:**
- ✅ WireGuard config + QR code (for desktops)
- ✅ Shadowsocks config + QR code (for mobile)
- ✅ V2Ray config + QR code (for backup)

**Multi-Protocol Benefits:**
- **Protocol Redundancy**: If one protocol is blocked, users can switch to another
- **Unified Management**: Same username/credentials across all protocols
- **Automatic QR Codes**: Each protocol gets its own QR code
- **Maximum Compatibility**: Works on any device, any network

### Create an Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias vpn="python3 /path/to/capybara.py"
```

Then use:
```bash
vpn user list
vpn stats show
vpn server status
```

## Documentation

### Server Setup
- **[install_capybara.sh](install_capybara.sh)** - 🔧 Unified modular installer (recommended)
- **[VPN Server Setup Guide](CLAUDE.md)** - Manual step-by-step server setup
- [install_multi_vpn_server.sh](install_multi_vpn_server.sh) - ⚠️ Deprecated (use install_capybara.sh)
- [install_vpn_server.sh](install_vpn_server.sh) - ⚠️ Deprecated (use install_capybara.sh --wireguard)

### Client Setup (For End Users)
- **[Client Setup Guide](CLIENT_SETUP.md)** - ⭐ Complete guide for all devices (macOS, iOS, Android)
  - **[Russian version](CLIENT_SETUP_RU.md)** - 🇷🇺 Руководство на русском языке

### Troubleshooting
- **[Debugging Guide](DEBUGGING_GUIDE.md)** - 🔍 Comprehensive troubleshooting for all protocols

## Command Overview

### User Management (Multi-Protocol)
```bash
capybara.py user add <username>              # Add user to all 3 protocols
capybara.py user add <username> -d "Info"    # Add with description
capybara.py user list                        # List all users
capybara.py user list --detailed             # Detailed user info
capybara.py user remove <user>               # Remove user
capybara.py user block <user>                # Block user
```

**Note**: Every user automatically gets configs and QR codes for all three protocols (WireGuard, Shadowsocks, V2Ray) in `./vpn_clients/`

### Server Management
```bash
capybara.py server status                 # Check server status
capybara.py server stop                   # Stop VPN server
capybara.py server start                  # Start VPN server
capybara.py server restart                # Restart VPN server
```

### Statistics
```bash
capybara.py stats show                    # Current statistics
capybara.py stats live                    # Live monitoring
capybara.py stats live --interval 10      # Custom refresh rate
```

### Resource Blocking
```bash
capybara.py block add facebook.com        # Block domain
capybara.py block add 1.2.3.4 --type ip   # Block IP
capybara.py block list                    # List blocks
capybara.py block remove facebook.com     # Unblock
```

### Logs Management (NEW!)
```bash
capybara.py logs show                     # View all logs
capybara.py logs show --service udp2raw   # Service-specific logs
capybara.py logs tail                     # Follow logs live
```

### Connection Control (NEW!)
```bash
capybara.py connection list               # List active connections
capybara.py connection kick <user>        # Disconnect user
capybara.py connection kick-all           # Disconnect all users
```

### Service Management (NEW!)
```bash
capybara.py service status                # Check all services
capybara.py service restart wireguard     # Restart WireGuard only
capybara.py service restart udp2raw       # Restart udp2raw only
capybara.py service restart firewall      # Restart firewall only
```

### Backup & Restore (NEW!)
```bash
capybara.py backup create                 # Create backup
capybara.py backup create --name my-backup  # Named backup
capybara.py backup list                   # List all backups
capybara.py backup restore <name>         # Restore backup
```

### Network Diagnostics (NEW!)
```bash
capybara.py diag ping <user>              # Ping user's VPN IP
capybara.py diag ports                    # Show listening ports
capybara.py diag handshake <user>         # Check handshake status
```

### System Health (NEW!)
```bash
capybara.py health check                  # Full health check
```

### Reports & Analytics (NEW!)
```bash
capybara.py report generate               # Generate daily report
capybara.py report generate --type weekly # Weekly report
capybara.py report generate --format json # JSON output
capybara.py report generate --format csv  # CSV output
```

### Configuration
```bash
capybara.py config                        # Show config
```

## Example Workflows

### Onboard a New User

```bash
# 1. Add user (automatically creates all protocol configs)
./capybara.py user add bob --description "Bob from Sales"

# This automatically creates 6 files:
# - bob_TIMESTAMP_wireguard.conf + bob_TIMESTAMP_wireguard_qr.png
# - bob_TIMESTAMP_shadowsocks.txt + bob_TIMESTAMP_shadowsocks_qr.png
# - bob_TIMESTAMP_v2ray.txt + bob_TIMESTAMP_v2ray_qr.png

# 2. Share appropriate config based on user's device:
#    Desktop → WireGuard config + udp2raw instructions
#    Mobile → Shadowsocks QR code (easiest)
#    Backup → V2Ray QR code

# 3. Monitor connection
./capybara.py stats live
```

### Mobile User Setup (Easiest)

```bash
# 1. Add user
./capybara.py user add alice

# 2. Send them the Shadowsocks QR code
#    File: ./vpn_clients/alice_*_shadowsocks_qr.png

# 3. User installs Shadowrocket (iOS) or Shadowsocks (Android)

# 4. User scans QR code

# 5. Connected!
```

### Desktop User Setup (Fastest)

```bash
# 1. Add user
./capybara.py user add charlie

# 2. Send them the WireGuard config
#    File: ./vpn_clients/charlie_*_wireguard.conf

# 3. User starts udp2raw client
#    (Command displayed after user creation)

# 4. User imports WireGuard config

# 5. Connected with full DPI evasion!
```

### Daily Health Check

```bash
./capybara.py server status
./capybara.py user list
./capybara.py stats show
```

### Troubleshooting

#### Quick Commands
```bash
# Check server status
./capybara.py server status

# View detailed user info
./capybara.py user list --detailed

# View logs for all protocols
./capybara.py logs show --service wireguard
./capybara.py logs show --service shadowsocks
./capybara.py logs show --service v2ray

# Restart server if needed
./capybara.py server restart
```

#### Common Issues

**🚨 VPN Connects But Websites Don't Load**

This is the most common issue! Symptoms:
- Client shows "connected" status
- Traffic appears in server logs
- But browsers timeout or show "can't resolve host"

**Root Cause:** Server can't resolve DNS or NAT misconfigured

**Fix:**
```bash
# 1. Test if server can resolve DNS
ssh root@YOUR_SERVER_IP "nslookup google.com"

# If DNS fails, fix the firewall:
ssh root@YOUR_SERVER_IP << 'EOF'
# Update firewall to allow outbound traffic
cat > /etc/awall/optional/multi-vpn.json << 'EOFCONFIG'
{
  "policy": [
    { "in": "internet", "action": "drop" },
    { "out": "internet", "action": "accept" }
  ],
  "filter": [
    {
      "out": "internet",
      "service": ["dns", "http", "https"],
      "action": "accept"
    }
  ]
}
EOFCONFIG

# Apply firewall changes
awall activate -f

# Add catchall NAT rule
iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
rc-service iptables save
EOF
```

**🔍 Protocol Not Working**

Check which service is failing:
```bash
# Check all services
ssh root@YOUR_SERVER_IP << 'EOF'
rc-service shadowsocks-rust status
rc-service v2ray status
netstat -tulpn | grep -E '8388|80'
EOF
```

**📱 Mobile Client Issues**

For iPhone/Android:
1. Delete old configs in Shadowrocket/v2rayNG
2. Scan the latest QR code (check timestamp in filename)
3. Make sure using the right protocol QR code
4. Try different protocol if one doesn't work

**📋 Detailed Debugging Guide**

For comprehensive troubleshooting, see [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)

## Configuration

On first run, Capybara creates a configuration file at `~/.capybara_config.yaml`:

```yaml
server:
  host: YOUR_SERVER_IP
  port: 22
  username: root
  password: your_password
  # Or use SSH key:
  # key_file: /path/to/private_key

vpn:
  interface: wg0
  config_path: /etc/wireguard/wg0.conf
  network: 10.7.0.0/24
  server_ip: 10.7.0.1
  next_client_ip: 2
```

Edit with: `nano ~/.capybara_config.yaml`

## Requirements

- Python 3.7+
- SSH access to VPN server
- WireGuard VPN server already configured

## File Locations

| Location | Purpose |
|---|---|
| `capybara.py` | Main script |
| `~/.capybara_config.yaml` | Configuration |
| `./vpn_clients/` | Generated client configs |
| `/etc/wireguard/wg0.conf` | Server config (on VPN server) |

## Why "Capybara"?

- 🦫 Capybaras are friendly and approachable (like this CLI)
- 🦫 They're great at socializing (like managing multiple VPN users)
- 🦫 They're calm under pressure (like handling server management)
- 🦫 Everyone loves capybaras!

## Support

- Run `./capybara.py --help` for command help
- Check [CLIENT_SETUP.md](CLIENT_SETUP.md) for client configuration
- Review [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) for troubleshooting

## What's New

### Version 3.0.0 (Latest - Multi-Protocol!)
- 🔄 **Three Protocols** - WireGuard, Shadowsocks, and V2Ray support
- 🔐 **Unified Management** - Same credentials across all protocols
- 📱 **Multi-Protocol QR Codes** - Automatic QR code generation for all protocols
- ⚡ **Protocol Selection** - Choose which protocols to enable per user
- 🎯 **Smart Routing** - Different protocols for different devices/networks
- 📦 **Automated Installation** - One-command multi-protocol server setup
- 🔧 **Flexible Configuration** - Per-protocol or unified user management
- 🛠️ **Critical Fixes**:
  - ✅ DNS Resolution - Server can now resolve domain names for VPN clients
  - ✅ NAT Configuration - All protocols properly route traffic (not just WireGuard)
  - ✅ Firewall Updates - Outbound DNS/HTTP/HTTPS enabled for proper functionality
  - ✅ Shadowsocks Integration - Fixed binary paths and shared password configuration

### Version 2.0.0 (Full Featured)
- ✨ **Logs Management** - View and follow logs in real-time
- ✨ **Connection Control** - Kick users immediately
- ✨ **Service Management** - Restart individual services
- ✨ **Backup & Restore** - Complete disaster recovery
- ✨ **Network Diagnostics** - Ping, ports, handshake checks
- ✨ **System Health** - Monitor CPU, memory, disk
- ✨ **Reports & Analytics** - Generate reports in multiple formats

### Version 1.0.0 (Initial Release)
- ✨ Added `server stop` and `server start` commands
- ✅ Full user management
- ✅ Real-time monitoring
- ✅ Resource blocking
- ✅ Auto config generation

## Server Credentials

**Server Access:**
- Server: YOUR_SERVER_IP
- Config: `~/.capybara_config.yaml`

## Quick Tips

1. **Use live monitoring** for real-time insights: `./capybara.py stats live`
2. **Always check status** before troubleshooting: `./capybara.py server status`
3. **Back up user list** regularly: `./capybara.py user list --detailed > backup.txt`
4. **Use detailed view** to investigate issues: `./capybara.py user list --detailed`
5. **Stop server** before making manual changes: `./capybara.py server stop`

## Getting Help

```bash
./capybara.py --help                # Main help
./capybara.py user --help           # User commands
./capybara.py server --help         # Server commands
./capybara.py stats --help          # Stats commands
./capybara.py block --help          # Block commands
```

---

**Made with 🦫 by the VPN Management Team**

**Version:** 3.0.0 (Multi-Protocol)
**License:** Free for personal use
**Status:** ✅ Production Ready (WireGuard Tested, Shadowsocks/V2Ray Code Complete)

---

## 📋 Implementation Status

| Protocol | Code | Installation Script | Testing | Status |
|----------|------|-------------------|---------|--------|
| WireGuard + udp2raw | ✅ Complete | ✅ Complete | ✅ Tested | 🟢 Production Ready |
| Shadowsocks | ✅ Complete | ✅ Complete | ✅ Tested | 🟢 Production Ready |
| V2Ray | ✅ Complete | ✅ Complete | ✅ Tested | 🟢 Production Ready |

**All three protocols are production-ready.** The CLI automatically generates configs and QR codes for WireGuard, Shadowsocks, and V2Ray when adding users.

---

## Protocol Comparison

| Feature | WireGuard + udp2raw | Shadowsocks | V2Ray |
|---------|-------------------|-------------|-------|
| **Speed** | Fastest | Fast | Medium |
| **Mobile Support** | Limited (udp2raw) | Excellent | Excellent |
| **DPI Evasion** | Excellent | Good | Excellent |
| **Setup Complexity** | High | Low | Medium |
| **Client Apps** | WireGuard + udp2raw | Many options | Many options |
| **Best For** | Desktop, Max Speed | Mobile, Quick Setup | Advanced Evasion |
| **Port** | 443 (TCP-disguised) | 8388 (TCP/UDP) | 80 (WebSocket) |

**Recommendation**: Use WireGuard for desktops, Shadowsocks for mobile devices, and V2Ray as fallback in highly restrictive networks.
