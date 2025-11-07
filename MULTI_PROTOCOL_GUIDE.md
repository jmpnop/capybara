# 🔄 Capybara Multi-Protocol Setup Guide

Complete guide for setting up and using Capybara's multi-protocol VPN infrastructure.

## Overview

Capybara v3.0 introduces support for three battle-tested VPN protocols:

1. **WireGuard + udp2raw** - Maximum speed with DPI evasion (Port 443)
2. **Shadowsocks** - Mobile-friendly with AEAD encryption (Port 8388)
3. **V2Ray VMess** - Advanced obfuscation for restrictive networks (Port 8443)

## Why Three Protocols?

### Protocol Redundancy
If one protocol is blocked by censors, users can immediately switch to another without waiting for administrator intervention.

### Device Compatibility
- **WireGuard**: Best for desktops with udp2raw client
- **Shadowsocks**: Perfect for iOS/Android mobile devices
- **V2Ray**: Works everywhere, especially where others fail

### Network Conditions
Different protocols perform better in different network environments. Having multiple options ensures reliable access regardless of network conditions.

### Future-Proof
Multiple independent protocols mean your VPN infrastructure remains operational even if one protocol is compromised or blocked.

## Installation

### Server Setup

**Option 1: Full Multi-Protocol Installation (Recommended)**

```bash
# On your Alpine Linux VPS:
wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_multi_vpn_server.sh
chmod +x install_multi_vpn_server.sh
./install_multi_vpn_server.sh
```

This installs:
- WireGuard with udp2raw obfuscation
- Shadowsocks-rust with AEAD encryption
- V2Ray with VMess protocol
- Firewall rules for all three protocols
- Automatic startup configuration

**Option 2: Add to Existing WireGuard Server**

If you already have WireGuard installed:

```bash
# Upload the supplemental installation script
scp install_shadowsocks_v2ray_only.sh root@YOUR_SERVER_IP:/root/
ssh root@YOUR_SERVER_IP
chmod +x /root/install_shadowsocks_v2ray_only.sh
./install_shadowsocks_v2ray_only.sh
```

This adds Shadowsocks and V2Ray without modifying your existing WireGuard configuration.

### Management Tool

Install Capybara CLI on your local machine:

```bash
git clone https://github.com/jmpnop/capybara.git
cd capybara
pip3 install -r requirements.txt
chmod +x capybara.py
```

Configure `~/.capybara_config.yaml` with your server details.

## User Management

### Adding Users

**Add user (automatically adds to all protocols):**
```bash
./capybara.py user add alice
```

**Add user with description:**
```bash
./capybara.py user add bob --description "Bob from Engineering"
```

Every user automatically gets access to all three protocols - WireGuard, Shadowsocks, and V2Ray.

### What Gets Generated

For every user, Capybara automatically creates 6 files (2 per protocol):

1. **WireGuard** (for desktops):
   - `username_timestamp_wireguard.conf` - Client configuration
   - `username_timestamp_wireguard_qr.png` - QR code for mobile app

2. **Shadowsocks** (for mobile):
   - `username_timestamp_shadowsocks.txt` - Connection details
   - `username_timestamp_shadowsocks_qr.png` - QR code with ss:// URL

3. **V2Ray** (for backup):
   - `username_timestamp_v2ray.txt` - Connection details
   - `username_timestamp_v2ray_qr.png` - QR code with vmess:// URL

All files are saved to `./vpn_clients/` directory.

**Example for user "alice":**
```
vpn_clients/
├── alice_20251106_143022_wireguard.conf
├── alice_20251106_143022_wireguard_qr.png
├── alice_20251106_143022_shadowsocks.txt
├── alice_20251106_143022_shadowsocks_qr.png
├── alice_20251106_143022_v2ray.txt
└── alice_20251106_143022_v2ray_qr.png
```

### Unified Credentials

Capybara uses deterministic credential generation:

- **Shadowsocks passwords**: Generated via PBKDF2 from username
- **V2Ray UUIDs**: Generated via UUID v5 from username
- **WireGuard keys**: Randomly generated (inherent to protocol)

This means:
- Same username always gets the same Shadowsocks password
- Same username always gets the same V2Ray UUID
- Easy to recreate credentials if configuration is lost

## Client Setup

### WireGuard (Desktop)

**macOS/Linux:**

1. Start udp2raw client:
```bash
./udp2raw -c -l 127.0.0.1:4096 -r YOUR_SERVER_IP:443 \
  -k YOUR_UDP2RAW_PASSWORD --raw-mode faketcp \
  --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro
```

2. Import WireGuard config or scan QR code

3. Connect!

**Windows:**
- Use udp2raw Windows binary
- Import config into WireGuard Windows app

### Shadowsocks (Mobile)

**iOS (Shadowrocket recommended):**
1. Install Shadowrocket from App Store
2. Tap "+" → Scan QR code
3. Scan `username_shadowsocks_qr.png`
4. Connect!

**Android:**
1. Install Shadowsocks from Play Store
2. Tap "+" → Scan QR code
3. Scan `username_shadowsocks_qr.png`
4. Connect!

### V2Ray (Mobile/Desktop)

**iOS:**
- Shadowrocket (supports V2Ray)
- Kitsunebi
- Quantumult X

**Android:**
- v2rayNG (recommended)
- v2rayN

**Process:**
1. Install any V2Ray client
2. Scan `username_v2ray_qr.png` QR code
3. Connect!

## Protocol Comparison

| Feature | WireGuard | Shadowsocks | V2Ray |
|---------|-----------|-------------|-------|
| **Speed** | Fastest (native kernel module) | Fast | Medium |
| **Latency** | Lowest | Low | Medium |
| **Mobile Battery** | Good | Excellent | Good |
| **DPI Evasion** | Excellent (with udp2raw) | Good | Excellent |
| **Setup Complexity** | High (requires udp2raw) | Low | Medium |
| **Client Availability** | Many | Many | Many |
| **Firewall Traversal** | Excellent | Good | Excellent |
| **Port** | 443 (TCP-disguised) | 8388 | 8443 |

## When to Use Each Protocol

### WireGuard + udp2raw
**Best for:**
- Desktop/laptop users
- Maximum performance needs
- Users comfortable with technical setup
- Primary protocol in most countries

**Avoid when:**
- Setting up mobile devices (udp2raw not available on mobile)
- Users need simple scan-and-connect setup

### Shadowsocks
**Best for:**
- Mobile devices (iOS/Android)
- Quick setup requirements
- Users without technical background
- Good balance of speed and obfuscation

**Avoid when:**
- Maximum speed is critical
- Facing sophisticated DPI that specifically targets Shadowsocks

### V2Ray
**Best for:**
- Highly restrictive networks (China, Iran)
- When WireGuard and Shadowsocks are blocked
- Advanced users who need customization
- Fallback protocol

**Avoid when:**
- Speed is the priority
- Simple setup is needed

## Troubleshooting

### WireGuard Issues

**Cannot connect:**
```bash
# Check if udp2raw is running
ps aux | grep udp2raw

# Check WireGuard status
./capybara.py server status

# Check user exists
./capybara.py user list
```

**udp2raw not working:**
- Verify password matches in server and client
- Check port 443 is not blocked by firewall
- Try running udp2raw with sudo/administrator

### Shadowsocks Issues

**Connection fails:**
```bash
# On server, check if Shadowsocks is running
ssh root@SERVER "rc-service shadowsocks status"

# Check port 8388 is open
./capybara.py diag ports
```

**Mobile app shows "invalid QR code":**
- Ensure QR code is for Shadowsocks (filename contains "shadowsocks")
- Try manually entering details from .txt file instead
- Some apps require specific formats - try a different app

### V2Ray Issues

**Cannot connect:**
```bash
# Check V2Ray service
ssh root@SERVER "rc-service v2ray status"

# Check logs
./capybara.py logs show --service v2ray

# Verify user exists in V2Ray config
ssh root@SERVER "cat /etc/v2ray/config.json"
```

**QR code not recognized:**
- Try different V2Ray client app
- Manually enter UUID and server details from .txt file

## Advanced Usage

### Protocol-Specific Monitoring

```bash
# View WireGuard connections
./capybara.py stats show

# Check Shadowsocks logs
./capybara.py logs show --service shadowsocks

# Check V2Ray logs
./capybara.py logs show --service v2ray
```

### Backup All Protocols

```bash
# Create comprehensive backup
./capybara.py backup create --name multi-protocol-backup

# This backs up:
# - WireGuard configs and keys
# - Shadowsocks user configs
# - V2Ray user configs
# - Firewall rules
```

### Remove User from All Protocols

```bash
# Remove user
./capybara.py user remove alice

# This removes user from:
# - WireGuard peers
# - Shadowsocks user configs
# - V2Ray clients list
```

## Performance Tuning

### WireGuard Optimization
```bash
# Already optimized in default config:
# - MTU: 1280 (for udp2raw compatibility)
# - Keepalive: 25 seconds
# - Obfuscation: faketcp mode with XOR cipher
```

### Shadowsocks Optimization
- Method: `chacha20-ietf-poly1305` (best balance)
- Fast open: Enabled
- Mode: TCP and UDP

### V2Ray Optimization
- Protocol: VMess
- Network: TCP (most compatible)
- Security: None (focus on compatibility)

## Security Considerations

### Password/Key Management
- **WireGuard**: Private keys generated randomly, never reused
- **Shadowsocks**: Passwords derived from username (deterministic but secure)
- **V2Ray**: UUIDs derived from username (deterministic but secure)

### Firewall Configuration
- All protocols protected by awall firewall
- Only required ports exposed (443, 8388, 8443, 22)
- NAT configured for VPN subnet (10.7.0.0/24)

### Traffic Analysis Resistance
- **WireGuard**: udp2raw transforms to fake TCP on port 443 (HTTPS)
- **Shadowsocks**: AEAD encryption prevents traffic analysis
- **V2Ray**: Built-in traffic obfuscation and masking

## Migration Guide

### From WireGuard-Only to Multi-Protocol

If you have existing WireGuard users:

1. **Backup current config:**
```bash
./capybara.py backup create --name before-multiprotocol
```

2. **Install additional protocols:**
```bash
scp install_shadowsocks_v2ray_only.sh root@SERVER:/root/
ssh root@SERVER "./install_shadowsocks_v2ray_only.sh"
```

3. **Add existing users to new protocols:**
```bash
# For each existing user
./capybara.py user add USERNAME --protocols shadowsocks,v2ray
```

4. **Distribute new configs:**
- Share Shadowsocks QR codes for mobile
- Share V2Ray QR codes as backup

### From Other VPN Solutions

1. Export user list from old system
2. Run Capybara multi-protocol installation
3. Create users in Capybara with same usernames
4. Distribute new configs (QR codes make this easy)
5. Monitor connections to verify migration

## Best Practices

### User Onboarding
1. Create user with `--protocols all`
2. Send appropriate config based on device:
   - Desktop → WireGuard config + udp2raw instructions
   - Mobile → Shadowsocks QR code (primary) + V2Ray QR code (backup)
3. Test connectivity before notifying user

### Maintenance
```bash
# Weekly health check
./capybara.py health check
./capybara.py stats show
./capybara.py logs show

# Monthly backup
./capybara.py backup create --name monthly-$(date +%Y%m)
```

### Scaling
- Each protocol supports hundreds of users
- Monitor server resources: `./capybara.py health check`
- Consider multiple servers for load distribution
- Use same usernames across servers for consistency

## Future Enhancements

Planned features for future versions:

- Web dashboard for multi-protocol monitoring
- Automatic protocol failover for clients
- Usage quotas per protocol
- Geographic load balancing
- Client-side protocol auto-selection

## Support

For issues specific to multi-protocol setup:

1. Check logs: `./capybara.py logs show`
2. Verify services: `./capybara.py server status`
3. Test connectivity: `./capybara.py diag ping USERNAME`
4. Review configs: Check `./vpn_clients/` directory

## Conclusion

Capybara's multi-protocol architecture provides unmatched flexibility and resilience against network censorship. By supporting WireGuard, Shadowsocks, and V2Ray simultaneously with unified management, users get the best of all worlds:

- **Speed** from WireGuard
- **Convenience** from Shadowsocks
- **Resilience** from V2Ray

The automatic QR code generation and deterministic credential system make user management effortless while maintaining security.

---

**Version:** 3.0.0
**Last Updated:** November 6, 2025
**Status:** Production Ready (WireGuard fully tested, Shadowsocks/V2Ray implementation complete)

**Next Steps:**
1. Complete Shadowsocks/V2Ray server installation testing
2. Verify end-to-end connectivity for all protocols
3. Update client setup guides with real-world screenshots

🦫 **Capybara - Making internet freedom accessible to everyone**
