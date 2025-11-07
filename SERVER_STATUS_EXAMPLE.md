# Enhanced Server Status Display

## New Output Format

The `./capybara.py server status` command now shows protocol-specific configuration details for all three protocols.

### Example Output:

```
============================================================
VPN Server Status
============================================================

Overall Status:      RUNNING

Protocol Status:
WireGuard:           Running
udp2raw:             Running
Shadowsocks:         Running
V2Ray:               Running

Protocol Configuration:

WireGuard:
  Interface:         wg0
  Port:              51820 (internal)
  Obfuscation Port:  443 (udp2raw → HTTPS)
  Network:           10.7.0.0/24

Shadowsocks:
  Port:              8388
  Method:            chacha20-ietf-poly1305
  Mode:              TCP + UDP

V2Ray:
  Port:              80
  Protocol:          vmess
  Transport:         ws
  WebSocket Path:    /api/v2/download
  Configured Users:  3

Server Information:
Server IP:           66.42.119.38
Uptime:              04:46:51 up 22:14,  0 users,  load average: 0.00, 0.00, 0.00
```

## What's New?

### Before
Only showed WireGuard-specific information:
- Server IP
- Interface (wg0 only)
- Uptime

### After
Now shows configuration details for ALL protocols:

#### WireGuard
- Interface name (wg0)
- Internal port (51820)
- Obfuscation port (443 - the port clients actually connect to)
- VPN network (10.7.0.0/24)

#### Shadowsocks
- Port (8388)
- Encryption method (chacha20-ietf-poly1305)
- Mode (TCP + UDP)

#### V2Ray
- Port (80 - works on mobile networks)
- Protocol (vmess)
- Transport type (WebSocket)
- WebSocket path (/api/v2/download - disguised as API)
- Number of configured users

## Benefits

1. **Complete visibility** - See all protocol configurations at a glance
2. **Quick troubleshooting** - Verify ports and settings are correct
3. **User count tracking** - See how many V2Ray users are configured
4. **Protocol-appropriate details** - Each protocol shows its relevant settings

## Usage

```bash
# Check complete server status with all protocol configs
./capybara.py server status

# Compare with service-only status
./capybara.py service status
```

## Implementation Details

### New Method: `get_protocol_configs()`

This method connects to the server and parses configuration files for each protocol:

- **WireGuard**: Parses `/etc/wireguard/wg0.conf` for ListenPort and udp2raw settings
- **Shadowsocks**: Parses `/etc/shadowsocks-rust/config.json` for server configuration
- **V2Ray**: Parses `/etc/v2ray/config.json` for inbound configuration and user count

### Error Handling

If any protocol's configuration can't be read, it shows:
```
WireGuard: Config error
```

This prevents one protocol's error from breaking the entire status display.

## Technical Notes

### Configuration Parsing

**WireGuard:**
- Reads ListenPort from config (default: 51820)
- Extracts udp2raw port from PreUp command (default: 443)
- Shows VPN network from config file

**Shadowsocks:**
- Reads JSON config directly
- Shows server_port, method, and mode
- Converts "tcp_and_udp" to user-friendly "TCP + UDP"

**V2Ray:**
- Parses JSON config
- Extracts inbound port, protocol, and transport settings
- Counts configured users in clients array
- Shows WebSocket path if configured

### Why These Details Matter

**Port Information:**
- WireGuard: Port 51820 is internal, clients connect to 443 (udp2raw)
- Shadowsocks: Port 8388 is directly accessible
- V2Ray: Port 80 works on restrictive mobile networks

**Transport Details:**
- V2Ray WebSocket makes traffic look like HTTP
- Path `/api/v2/download` disguises VPN as API traffic
- Helps bypass deep packet inspection (DPI)

**User Count:**
- Shows how many V2Ray users are configured
- Helps track user management
- Shadowsocks uses shared password (no per-user count)
