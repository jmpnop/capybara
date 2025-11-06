# 🦫 Capybara - Complete WireGuard VPN Solution

**Capybara** is a complete WireGuard VPN solution that includes:
1. **🔧 Automated Server Setup** - One-command installation script for Alpine Linux with udp2raw obfuscation
2. **💻 Management CLI Tool** - Comprehensive Python-based command-line tool for managing your VPN server via SSH

Deploy a censorship-resistant VPN server with DPI evasion and manage it effortlessly. It's like having a friendly capybara 🦫 helping you set up and manage your entire VPN infrastructure!

## Why Capybara?

Capybaras are known for being calm, social, and excellent at managing their environments - just like this tool helps you calmly set up and efficiently manage your VPN server and users!

## 🚀 Quick Start

### Part 1: Server Installation (One Command!)

Set up a WireGuard VPN server with udp2raw obfuscation on Alpine Linux:

```bash
# On your Alpine Linux VPS, run:
wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_vpn_server.sh
chmod +x install_vpn_server.sh
./install_vpn_server.sh
```

**What it does:**
- Installs WireGuard + udp2raw (DPI evasion)
- Configures firewall (awall)
- Generates server keys
- Sets up automatic startup
- Configures obfuscation on port 443 (disguised as HTTPS)

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

## Features

### Core Features
- 🧑‍💼 **User Management** - Add, remove, list, and block VPN users with a single command
- 📊 **Statistics & Monitoring** - Real-time and static statistics viewing
- 🚫 **Resource Blocking** - Block specific domains and IP addresses
- ⚙️ **Server Management** - Start, stop, restart, and check status of your VPN server
- 📁 **Auto Config Generation** - Automatically creates client configuration files
- 🎨 **Beautiful CLI** - Color-coded output with tables and progress indicators

### Advanced Features (NEW!)
- 📝 **Logs Management** - View and follow server logs in real-time
- 🔌 **Connection Control** - Disconnect users immediately for security
- 🔧 **Service Management** - Restart individual services (WireGuard, udp2raw, firewall)
- 💾 **Backup & Restore** - Complete backup and disaster recovery system
- 🔍 **Network Diagnostics** - Ping users, check ports, verify handshakes
- 🏥 **System Health** - Monitor CPU, memory, disk, and network
- 📈 **Reports & Analytics** - Generate usage reports in text, JSON, or CSV

## Basic Usage

After completing both Part 1 (Server Installation) and Part 2 (Management Tool Installation), you can start managing your VPN:

```bash
# Add a new VPN user
./capybara.py user add alice --description "Alice from Engineering"

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

### Create an Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias vpn="python3 /Users/pasha/PycharmProjects/o/capybara.py"
```

Then use:
```bash
vpn user list
vpn stats show
vpn server status
```

## Documentation

### Server Setup
- **[install_vpn_server.sh](install_vpn_server.sh)** - 🔧 Automated server installation script
- **[VPN Server Setup Guide](CLAUDE.md)** - Manual step-by-step server setup

### Management Tool
- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Full Features Guide](FULL_FEATURES_GUIDE.md)** - Complete guide for all features
- **[Command Cheatsheet](CHEATSHEET.md)** - Quick reference for all commands
- **[Complete Documentation](VPN_MANAGER_README.md)** - Full feature documentation

### Client Setup
- **[Client Setup Guide](CLIENT_SETUP.md)** - ⭐ Complete guide for macOS and iOS clients
  - **[Russian version](CLIENT_SETUP_RU.md)** - 🇷🇺 Руководство на русском языке

### Reference
- **[Documentation Index](DOCUMENTATION_INDEX.md)** - Complete documentation catalog
- **[Feature Ideas](FEATURE_IDEAS.md)** - Future enhancements and roadmap

## Command Overview

### User Management
```bash
capybara.py user add <username>           # Add new user
capybara.py user list                     # List all users
capybara.py user list --detailed          # Detailed user info
capybara.py user remove <user>            # Remove user
capybara.py user block <user>             # Block user
```

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
# 1. Add user
./capybara.py user add bob --description "Bob from Sales"

# 2. Share config file (created in ./vpn_clients/)
cat ./vpn_clients/bob_20250106_123456.conf

# 3. Monitor connection
./capybara.py stats live
```

### Daily Health Check

```bash
./capybara.py server status
./capybara.py user list
./capybara.py stats show
```

### Troubleshooting

```bash
# Check server status
./capybara.py server status

# View detailed user info
./capybara.py user list --detailed

# Restart server if needed
./capybara.py server restart
```

## Configuration

On first run, Capybara creates a configuration file at `~/.capybara_config.yaml`:

```yaml
server:
  host: 66.42.119.38
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

Previously named "vpn_manager", we renamed it to Capybara because:
- 🦫 Capybaras are friendly and approachable (like this CLI)
- 🦫 They're great at socializing (like managing multiple VPN users)
- 🦫 They're calm under pressure (like handling server management)
- 🦫 Everyone loves capybaras!

## Support

- Run `./capybara.py --help` for command help
- Check [VPN_MANAGER_README.md](VPN_MANAGER_README.md) for detailed docs
- Review [CHEATSHEET.md](CHEATSHEET.md) for quick reference

## What's New

### Version 2.0.0 (Latest - Full Featured!)
- ✨ **Logs Management** - View and follow logs in real-time
- ✨ **Connection Control** - Kick users immediately
- ✨ **Service Management** - Restart individual services
- ✨ **Backup & Restore** - Complete disaster recovery
- ✨ **Network Diagnostics** - Ping, ports, handshake checks
- ✨ **System Health** - Monitor CPU, memory, disk
- ✨ **Reports & Analytics** - Generate reports in multiple formats

### Version 1.0.0
- ✨ Renamed from vpn_manager to Capybara
- ✨ Added `server stop` and `server start` commands
- ✅ Full user management
- ✅ Real-time monitoring
- ✅ Resource blocking
- ✅ Auto config generation

## Server Credentials

**Server Access:**
- Server: 66.42.119.38
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

**Version:** 2.0.0 (Full Featured)
**License:** Free for personal use
