# Capybara Multi-Protocol Quick Reference

## New Features (2025-01-06)

### Service Management (All Protocols)

```bash
# Check status of all services
./capybara.py service status

# Restart individual services
./capybara.py service restart wireguard
./capybara.py service restart shadowsocks    # NEW
./capybara.py service restart v2ray          # NEW
./capybara.py service restart udp2raw
./capybara.py service restart firewall

# Check overall server status (all protocols)
./capybara.py server status
```

### User Management (WireGuard + V2Ray)

```bash
# Add user to ALL protocols (WG + SS + V2Ray)
./capybara.py user add alice

# List users from WireGuard + V2Ray
./capybara.py user list
./capybara.py user list --detailed

# Remove user from WireGuard + V2Ray
./capybara.py user remove alice

# Note: Shadowsocks uses shared password
# - All users share same credentials
# - No per-user add/remove/list
```

### Backup & Restore (All Protocols)

```bash
# Create backup of ALL configs (WG + SS + V2Ray)
./capybara.py backup create
./capybara.py backup create --name pre-upgrade

# List backups
./capybara.py backup list

# Restore all configs
./capybara.py backup restore pre-upgrade
```

## Protocol-Specific Commands

### WireGuard Only
These commands only work for WireGuard due to protocol design:

```bash
# Connection management (WG only)
./capybara.py connection list
./capybara.py connection kick alice
./capybara.py connection kick-all

# Network diagnostics (WG only - requires VPN IPs)
./capybara.py diag ping alice
./capybara.py diag ping 10.7.0.2
./capybara.py diag handshake alice

# User blocking (WG only)
./capybara.py user block alice
```

**Why WireGuard only?**
- Shadowsocks/V2Ray are proxies, not VPNs
- No individual VPN IP addresses to ping
- No peer handshake mechanism
- Limited per-connection control

## Protocol Comparison

| Feature | WireGuard | Shadowsocks | V2Ray |
|---------|-----------|-------------|-------|
| Add user | ✅ | ✅ (shared) | ✅ |
| Remove user | ✅ | ❌ | ✅ |
| List users | ✅ | ❌ | ✅ |
| Block user | ✅ | ❌ | ❌ |
| Kick user | ✅ | ❌ | ❌ |
| Connection stats | ✅ | ❌ | ❌ |
| Service restart | ✅ | ✅ | ✅ |
| Backup/restore | ✅ | ✅ | ✅ |
| View logs | ✅ | ✅ | ✅ |

Legend:
- ✅ Supported
- ❌ Not supported (architectural limitation)
- ✅ (shared) All users share same credentials

## Common Workflows

### Adding a New User
```bash
# 1. Add user to all protocols
./capybara.py user add bob --description "Bob from Sales"

# 2. Share configs with user
# Configs saved to: ./vpn_clients/
# - bob_wireguard.conf + bob_wireguard_qr.png
# - bob_shadowsocks.txt + bob_shadowsocks_qr.png
# - bob_v2ray.txt + bob_v2ray_qr.png
```

### Removing a User
```bash
# 1. Remove from WireGuard + V2Ray
./capybara.py user remove bob

# 2. For Shadowsocks (manual):
#    - Change server password in /etc/shadowsocks-rust/config.json
#    - Restart: ./capybara.py service restart shadowsocks
#    - Redistribute new password to authorized users
```

### Backing Up Before Maintenance
```bash
# 1. Create backup
./capybara.py backup create --name before-maintenance

# 2. Perform maintenance
# ... make changes ...

# 3. If something breaks, restore
./capybara.py backup restore before-maintenance
```

### Monitoring All Services
```bash
# Quick health check
./capybara.py server status

# Detailed service status
./capybara.py service status

# View logs for specific protocol
./capybara.py logs show --service wireguard
./capybara.py logs show --service shadowsocks
./capybara.py logs show --service v2ray
./capybara.py logs show --service udp2raw

# Real-time log monitoring
./capybara.py logs tail --service v2ray
```

## Troubleshooting

### Service Not Running
```bash
# 1. Check status
./capybara.py service status

# 2. Restart the service
./capybara.py service restart shadowsocks

# 3. Check logs for errors
./capybara.py logs show --service shadowsocks
```

### User Can't Connect (V2Ray)
```bash
# 1. Verify user exists
./capybara.py user list --detailed

# 2. Check V2Ray service
./capybara.py service status

# 3. Check V2Ray logs
./capybara.py logs show --service v2ray --lines 100
```

### Need to Remove User from Shadowsocks
```bash
# Shadowsocks uses shared password - you must:
# 1. SSH to server
# 2. Edit /etc/shadowsocks-rust/config.json
# 3. Change the "password" field
# 4. Restart: ./capybara.py service restart shadowsocks
# 5. Update all authorized users with new password
```

## Understanding Protocol Limitations

### Shadowsocks
**Design**: Simple SOCKS5 proxy with shared password

**Limitations**:
- All users share one password
- No per-user tracking
- No connection statistics
- Can't remove individual users

**Best for**: Simple, hard-to-detect proxy access

### V2Ray
**Design**: Advanced proxy with user UUIDs

**Capabilities**:
- Per-user UUIDs
- User add/remove supported
- WebSocket transport on port 80

**Limitations**:
- No simple connection stats (requires API)
- No kick user (no disconnect mechanism)
- Can't track bandwidth per user (without API)

**Best for**: Mobile networks, works on restricted networks

### WireGuard
**Design**: Modern VPN with cryptokey routing

**Capabilities**:
- Everything! Full feature support
- Per-peer stats
- Connection management
- Network diagnostics

**Limitations**:
- Can be detected by DPI (use udp2raw!)

**Best for**: Performance, security, full VPN features

## Tips

1. **Use all three protocols**: Each user gets configs for all three
2. **WireGuard for laptops**: Best performance and features
3. **V2Ray for mobile**: Port 80 works on most mobile networks
4. **Shadowsocks as fallback**: Simple and reliable
5. **Regular backups**: `./capybara.py backup create` before changes
6. **Monitor logs**: Use `logs tail` to watch for issues
7. **Check all services**: Run `server status` regularly

## Getting Help

```bash
# Main help
./capybara.py --help

# Command-specific help
./capybara.py user --help
./capybara.py service --help
./capybara.py backup --help

# Subcommand help
./capybara.py user list --help
./capybara.py service restart --help
```

## Version Info
- Capybara v3.0
- Multi-protocol support added: 2025-01-06
- Features: WireGuard + Shadowsocks + V2Ray unified management
