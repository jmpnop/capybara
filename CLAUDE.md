# Multi-Protocol Censorship-Resistant VPN Server Setup Guide

Complete step-by-step guide for setting up a multi-protocol VPN server on Alpine Linux with three anti-censorship protocols: WireGuard (with udp2raw), Shadowsocks, and V2Ray.

## Server Information
- **Provider**: Vultr.com
- **OS**: Alpine Linux v3.22
- **Server IP**: YOUR_SERVER_IP
- **VPN Network**: 10.7.0.0/24

## Protocols Installed
1. **WireGuard + udp2raw** - Port 443 (UDP disguised as TCP, HTTPS obfuscation)
2. **Shadowsocks** - Port 8388 (TCP/UDP, AEAD encryption)
3. **V2Ray VMess** - Port 8443 (TCP, highly configurable)

## Prerequisites
- Alpine Linux VPS with root access
- Public IP address
- SSH access configured

---

## Step 1: Connect and Verify System

```bash
ssh root@YOUR_SERVER_IP
uname -a
cat /etc/os-release
```

**Expected Output**: Alpine Linux v3.22.x

---

## Step 2: Update System and Install Required Packages

```bash
apk update
apk upgrade
apk add wireguard-tools-wg-quick iptables awall curl unzip
```

**Packages Installed**:
- `wireguard-tools-wg-quick` - WireGuard VPN tools and wg-quick utility
- `iptables` - Firewall and NAT
- `awall` - Alpine Wall firewall configuration tool
- `curl` - For downloading V2Ray and Shadowsocks
- `unzip` - For extracting V2Ray archive

**Note**: Shadowsocks and V2Ray will be installed manually from GitHub releases as Alpine packages may be outdated

---

## Step 3: Generate WireGuard Server Keys

```bash
mkdir -p /etc/wireguard
cd /etc/wireguard
umask 077
wg genkey | tee server_private.key | wg pubkey > server_public.key
```

**View the keys**:
```bash
echo "Private key:"
cat server_private.key
echo "Public key:"
cat server_public.key
```

**Generated Keys** (example):
- Private: `6Ofz/9BXTfHQmR/rHj9zJI6f3JkAL7KMnEO1dP0/TXM=`
- Public: `D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=`

---

## Step 4: Identify Network Interface

```bash
ip -br a | grep UP
```

**Expected Output**: `eth0` (or similar) - note this interface name for later use

---

## Step 5: Download and Install udp2raw

```bash
cd /tmp
wget https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_binaries.tar.gz
tar -xzf udp2raw_binaries.tar.gz
mv udp2raw_amd64 /usr/local/bin/udp2raw
chmod +x /usr/local/bin/udp2raw
```

**Verify installation**:
```bash
/usr/local/bin/udp2raw -h | head -5
```

---

## Step 6: Install Shadowsocks

```bash
cd /tmp
wget https://github.com/shadowsocks/shadowsocks-rust/releases/download/v1.23.1/shadowsocks-v1.23.1.x86_64-unknown-linux-musl.tar.xz
tar -xf shadowsocks-v1.23.1.x86_64-unknown-linux-musl.tar.xz
mv ssserver sslocal ssmanager ssservice ssurl /usr/local/bin/
chmod +x /usr/local/bin/ss*
```

**Verify installation**:
```bash
/usr/local/bin/ssserver --version
```

**Expected Output**: `shadowsocks 1.23.1`

---

## Step 7: Install V2Ray

```bash
cd /tmp
wget https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip
mkdir -p /usr/local/v2ray
unzip -o v2ray-linux-64.zip -d /usr/local/v2ray/
chmod +x /usr/local/v2ray/v2ray
```

**Verify installation**:
```bash
/usr/local/v2ray/v2ray version | head -3
```

**Expected Output**: `V2Ray 5.41.0 (or later)`

---

## Step 8: Configure WireGuard with Obfuscation

Create the WireGuard configuration file:

```bash
cat > /etc/wireguard/wg0.conf << 'EOF'
[Interface]
Address = 10.7.0.1/24
PrivateKey = 6Ofz/9BXTfHQmR/rHj9zJI6f3JkAL7KMnEO1dP0/TXM=
ListenPort = 51820
MTU = 1280

# udp2raw obfuscation (faketcp mode)
PreUp = /usr/local/bin/udp2raw -s -l 0.0.0.0:443 -r 127.0.0.1:51820 -k YOUR_UDP2RAW_PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro >/var/log/udp2raw.log 2>&1 &
PostDown = killall udp2raw || true

# Enable NAT for clients
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Add client peers below - each client needs a unique PublicKey and IP
# [Peer]
# PublicKey = <client1_public_key>
# AllowedIPs = 10.7.0.2/32
EOF
```

**Set correct permissions**:
```bash
chmod 600 /etc/wireguard/wg0.conf
```

**Important Notes**:
- Replace `PrivateKey` with your generated server private key
- Replace `eth0` with your actual internet interface name
- Password `YOUR_UDP2RAW_PASSWORD` must match on client and server
- Port 443 is used to mimic HTTPS traffic (helps bypass DPI)

---

## Step 9: Configure Shadowsocks

```bash
mkdir -p /etc/shadowsocks-rust

cat > /etc/shadowsocks-rust/config.json << 'EOF'
{
    "server": "0.0.0.0",
    "server_port": 8388,
    "password": "YOUR_SHADOWSOCKS_PASSWORD",
    "method": "chacha20-ietf-poly1305",
    "timeout": 300,
    "fast_open": true,
    "mode": "tcp_and_udp"
}
EOF
```

**Important**: Change the password to a strong, unique password.

---

## Step 10: Configure V2Ray

```bash
mkdir -p /etc/v2ray
mkdir -p /var/log/v2ray

cat > /etc/v2ray/config.json << 'EOF'
{
  "log": {
    "access": "/var/log/v2ray/access.log",
    "error": "/var/log/v2ray/error.log",
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": 8443,
      "protocol": "vmess",
      "settings": {
        "clients": []
      },
      "streamSettings": {
        "network": "tcp",
        "security": "none"
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "settings": {}
    }
  ]
}
EOF
```

**Note**: Users will be added to the `clients` array using the Capybara management tool.

---

## Step 11: Enable IP Forwarding

```bash
grep -q 'net.ipv4.ip_forward' /etc/sysctl.conf || echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
sysctl -p
sysctl net.ipv4.ip_forward
```

**Expected Output**: `net.ipv4.ip_forward = 1`

---

## Step 12: Configure Firewall with Awall

### 12.1 Create Custom Service Definition

```bash
mkdir -p /etc/awall/private
cat > /etc/awall/private/custom-services.json << 'EOF'
{
    "service": {
        "wireguard-obfs": [
            { "proto": "tcp", "port": 443 }
        ],
        "shadowsocks": [
            { "proto": "tcp", "port": 8388 },
            { "proto": "udp", "port": 8388 }
        ],
        "v2ray": [
            { "proto": "tcp", "port": 8443 }
        ]
    }
}
EOF
```

### 12.2 Create Multi-Protocol VPN Policy

**IMPORTANT**: This configuration allows outbound traffic for DNS resolution and proper NAT for all protocols.

```bash
mkdir -p /etc/awall/optional
cat > /etc/awall/optional/multi-vpn.json << 'EOF'
{
  "description": "Multi-protocol VPN server",
  "import": "custom-services",
  "variable": { "internet_if": "eth0" },
  "zone": {
    "internet": { "iface": "$internet_if" },
    "vpn": { "iface": "wg0" }
  },
  "policy": [
    { "in": "internet", "action": "drop" },
    { "out": "internet", "action": "accept" },
    { "in": "vpn", "out": "internet", "action": "accept" },
    { "out": "vpn", "in": "internet", "action": "accept" },
    { "action": "reject" }
  ],
  "filter": [
    {
      "in": "internet",
      "service": ["wireguard-obfs", "shadowsocks", "v2ray", "ssh"],
      "action": "accept"
    },
    {
      "out": "internet",
      "service": ["dns", "http", "https"],
      "action": "accept"
    }
  ],
  "snat": [
    { "out": "internet", "src": "10.7.0.0/24" },
    { "out": "internet" }
  ]
}
EOF
```

**Key Configuration Points**:
- `"out": "internet", "action": "accept"` - Allows server to make outbound connections (DNS, downloads)
- `"out": "internet", "service": ["dns", "http", "https"]` - Explicitly allows DNS and web traffic
- Two SNAT rules - one for WireGuard network, one for all other traffic (Shadowsocks/V2Ray)

### 12.3 Reboot to Load New Kernel (if system was upgraded)

```bash
reboot
```

Wait 30-60 seconds, then reconnect:
```bash
ssh root@YOUR_SERVER_IP
```

### 12.4 Load Required Kernel Modules

```bash
modprobe ip_tables
modprobe iptable_nat
modprobe iptable_filter
```

**Verify modules loaded**:
```bash
lsmod | grep -E 'ip_tables|iptable_nat|nf_nat'
```

### 12.5 Enable and Activate Awall Policies

```bash
awall enable multi-vpn
awall activate -f
```

### 12.6 Add Additional NAT Rule and Save iptables

**IMPORTANT**: Add a catchall NAT rule for non-WireGuard traffic (Shadowsocks/V2Ray):

```bash
iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
rc-update add iptables
rc-service iptables save
```

**Verify firewall rules**:
```bash
iptables -L -n | head -30
iptables -t nat -L POSTROUTING -n -v
```

You should see:
- SSH (port 22), port 443, 8388, 8443 accepted
- Default DROP policy on INPUT
- ACCEPT policy on OUTPUT (for DNS and outbound connections)
- MASQUERADE rules in NAT table

---

## Step 13: Create Service Init Scripts

### 13.1 Create Shadowsocks Init Script

```bash
cat > /etc/init.d/shadowsocks-rust << 'EOF'
#!/sbin/openrc-run

name="shadowsocks-rust"
command="/usr/local/bin/ssserver"
command_args="-c /etc/shadowsocks-rust/config.json"
command_background=true
pidfile="/run/${RC_SVCNAME}.pid"
output_log="/var/log/shadowsocks.log"
error_log="/var/log/shadowsocks.log"

depend() {
    need net
    after firewall
}
EOF

chmod +x /etc/init.d/shadowsocks-rust
```

### 13.2 Create V2Ray Init Script

```bash
cat > /etc/init.d/v2ray << 'EOF'
#!/sbin/openrc-run

name="v2ray"
command="/usr/local/v2ray/v2ray"
command_args="run -c /etc/v2ray/config.json"
command_background=true
pidfile="/run/${RC_SVCNAME}.pid"

depend() {
    need net
    after firewall
}
EOF

chmod +x /etc/init.d/v2ray
```

### 13.3 Create WireGuard Startup Script

```bash
cat > /etc/local.d/wireguard.start << 'EOF'
#!/bin/sh
wg-quick up wg0
EOF

chmod +x /etc/local.d/wireguard.start
```

---

## Step 14: Enable and Start All Services

### 14.1 Enable Services at Boot

```bash
rc-update add local default
rc-update add shadowsocks-rust default
rc-update add v2ray default
```

### 14.2 Start All Services

```bash
# Start WireGuard
wg-quick up wg0

# Start Shadowsocks
rc-service shadowsocks-rust start

# Start V2Ray
rc-service v2ray start
```

### 14.3 Verify All Services Are Running

```bash
# Check WireGuard
wg show
ps aux | grep udp2raw | grep -v grep

# Check Shadowsocks
rc-service shadowsocks-rust status
netstat -tulpn | grep 8388

# Check V2Ray
rc-service v2ray status
netstat -tulpn | grep 8443
```

**Expected Output**:
- WireGuard interface `wg0` should be listed
- udp2raw process running on port 443
- Shadowsocks listening on 0.0.0.0:8388 (TCP/UDP)
- V2Ray listening on :::8443 (TCP)

---

## Step 15: User Management with Capybara CLI

**IMPORTANT**: Instead of manually configuring users, use the Capybara management tool which automatically creates configs for all three protocols.

### 15.1 Install Capybara on Your Local Machine

```bash
git clone https://github.com/jmpnop/capybara.git
cd capybara
pip3 install -r requirements.txt
```

### 15.2 Configure Capybara

Create `~/.capybara_config.yaml`:

```yaml
server:
  host: YOUR_SERVER_IP
  port: 22
  username: root
  password: YOUR_SERVER_PASSWORD
vpn:
  interface: wg0
  config_path: /etc/wireguard/wg0.conf
  network: 10.7.0.0/24
  server_ip: 10.7.0.1
  next_client_ip: 2
```

### 15.3 Add Users (All Protocols)

```bash
./capybara.py user add alice --description "Alice's devices"
```

This automatically creates:
- ✅ WireGuard config + QR code
- ✅ Shadowsocks config + QR code
- ✅ V2Ray config + QR code

All configs are saved to `vpn_clients/` directory.

### 15.4 Manual User Addition (Advanced)

If you prefer manual setup or Capybara isn't available:

**For WireGuard:**
```bash
cd /etc/wireguard
wg genkey | tee client_private.key | wg pubkey > client_public.key
cat >> /etc/wireguard/wg0.conf << 'EOF'

[Peer]
PublicKey = <client_public_key>
AllowedIPs = 10.7.0.2/32
EOF
wg syncconf wg0 <(wg-quick strip wg0)
```

**For V2Ray:**
Generate a UUID and add to `/etc/v2ray/config.json` clients array:
```json
{
  "id": "YOUR-UUID-HERE",
  "alterId": 0,
  "email": "user@capybara"
}
```
Then restart: `rc-service v2ray restart`

**For Shadowsocks:**
Each user shares the server password or you can run multiple instances with different ports.

---

## Client Configuration (macOS)

### Step 1: Download udp2raw for macOS

Visit https://github.com/wangyu-/udp2raw/releases and download the appropriate binary for your Mac (amd64 for Intel, arm64 for M1/M2/M3).

```bash
# Extract and make executable
tar -xzf udp2raw_binaries.tar.gz
chmod +x udp2raw_mac_amd64  # or udp2raw_mac_arm64
```

### Step 2: Run udp2raw Client

Open a terminal and run:
```bash
./udp2raw_mac_amd64 -c -l 127.0.0.1:4096 -r YOUR_SERVER_IP:443 -k YOUR_UDP2RAW_PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro
```

**Important**: Keep this terminal window open while using the VPN.

### Step 3: Install WireGuard App

Download from Mac App Store: https://apps.apple.com/us/app/wireguard/id1451685025

### Step 4: Create WireGuard Configuration

In the WireGuard app, add a new tunnel with this configuration:

```ini
[Interface]
PrivateKey = 2MkhVZASXn/bBrOjrolSdNrIckiFBcu0GXOMjoiwDUc=
Address = 10.7.0.2/24
MTU = 1280
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
AllowedIPs = 0.0.0.0/0
Endpoint = 127.0.0.1:4096
PersistentKeepalive = 25
```

**Key Points**:
- `PrivateKey`: Use the client1 private key generated on the server
- `Address`: Must match the IP assigned to this client (10.7.0.2/24)
- `PublicKey`: The server's public key
- `Endpoint`: Points to local udp2raw client (127.0.0.1:4096)
- `AllowedIPs`: 0.0.0.0/0 routes all traffic through VPN
- `DNS`: Optional, use preferred DNS servers

### Step 5: Connect

1. Ensure udp2raw client is running in terminal
2. Activate the tunnel in WireGuard app
3. Verify connection: `ping 10.7.0.1`
4. Check your public IP: `curl ifconfig.me`

---

## Adding Additional Clients

For each new client, repeat this process:

### 1. Generate New Client Keys

```bash
ssh root@YOUR_SERVER_IP "cd /etc/wireguard && wg genkey | tee client2_private.key | wg pubkey > client2_public.key && cat client2_private.key && cat client2_public.key"
```

### 2. Add Peer to Server

```bash
ssh root@YOUR_SERVER_IP "cat >> /etc/wireguard/wg0.conf << 'EOF'

[Peer]
PublicKey = <client2_public_key>
AllowedIPs = 10.7.0.3/32
EOF
wg syncconf wg0 <(wg-quick strip wg0)"
```

**Important**: Increment the IP address for each client:
- Client 1: 10.7.0.2/32
- Client 2: 10.7.0.3/32
- Client 3: 10.7.0.4/32
- etc.

### 3. Configure Client

Same as above, but with:
- The new client's private key
- The new client's assigned IP address in the `Address` field

---

## Verification and Monitoring

### Check All Services Status

```bash
# Using Capybara
./capybara.py server status

# Or manually
ssh root@YOUR_SERVER_IP << 'EOF'
echo "=== WireGuard ==="
wg show
ps aux | grep udp2raw | grep -v grep

echo "=== Shadowsocks ==="
rc-service shadowsocks-rust status

echo "=== V2Ray ==="
rc-service v2ray status
EOF
```

### Verify All Listening Ports

```bash
ssh root@YOUR_SERVER_IP "netstat -tulpn | grep -E '443|8388|8443|51820'"
```

**Expected**:
- Port 51820: WireGuard (localhost only, UDP)
- Port 443: udp2raw (all interfaces, TCP)
- Port 8388: Shadowsocks (0.0.0.0, TCP/UDP)
- Port 8443: V2Ray (:::, TCP)

### View Protocol Logs

```bash
# Using Capybara
./capybara.py logs show --service wireguard
./capybara.py logs show --service shadowsocks
./capybara.py logs show --service v2ray

# Or manually
ssh root@YOUR_SERVER_IP "tail -f /var/log/udp2raw.log"
ssh root@YOUR_SERVER_IP "tail -f /var/log/shadowsocks.log"
ssh root@YOUR_SERVER_IP "tail -f /var/log/v2ray/access.log"
ssh root@YOUR_SERVER_IP "tail -f /var/log/v2ray/error.log"
```

### Check Firewall and NAT Rules

```bash
ssh root@YOUR_SERVER_IP "iptables -L -n -v | head -30"
ssh root@YOUR_SERVER_IP "iptables -t nat -L POSTROUTING -n -v"
```

**Must have**:
- Multiple MASQUERADE rules in NAT/POSTROUTING
- ACCEPT policy on OUTPUT (or explicit DNS/HTTP/HTTPS rules)

---

## Troubleshooting

### CRITICAL: VPN Connects But Websites Don't Load

**Symptoms**: Client shows connected, can see traffic in logs, but browsers timeout or show "can't resolve host"

**Root Cause**: Server can't resolve DNS or NAT is misconfigured

**Solution**:
```bash
# 1. Test if server can resolve DNS
ssh root@YOUR_SERVER_IP "nslookup google.com"

# If it fails, check OUTPUT policy
ssh root@YOUR_SERVER_IP "iptables -L OUTPUT -n | head -5"

# 2. If OUTPUT policy is DROP, verify awall config allows outbound traffic
ssh root@YOUR_SERVER_IP "cat /etc/awall/optional/multi-vpn.json | grep -A 3 policy"

# Should have: { "out": "internet", "action": "accept" }

# 3. Check NAT rules include catchall
ssh root@YOUR_SERVER_IP "iptables -t nat -L POSTROUTING -n -v"

# Must have: MASQUERADE  all  --  *      eth0    0.0.0.0/0    0.0.0.0/0

# 4. Fix if missing
ssh root@YOUR_SERVER_IP "iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE && rc-service iptables save"
```

### WireGuard Won't Start

1. Check config syntax:
   ```bash
   cat /etc/wireguard/wg0.conf
   ```

2. Check permissions:
   ```bash
   ls -la /etc/wireguard/wg0.conf
   ```
   Should be: `-rw------- 1 root root`

3. Manual start with verbose output:
   ```bash
   wg-quick up wg0
   ```

### Shadowsocks Won't Start

1. Check config has password:
   ```bash
   cat /etc/shadowsocks-rust/config.json
   ```
   Must have `"password": "your_password_here"`

2. Check binary exists:
   ```bash
   which ssserver
   ls -la /usr/local/bin/ssserver
   ```

3. View logs:
   ```bash
   cat /var/log/shadowsocks.log
   ```

### V2Ray Not Accepting Connections

1. Check V2Ray is running:
   ```bash
   rc-service v2ray status
   netstat -tulpn | grep 8443
   ```

2. Check user UUID is in config:
   ```bash
   cat /etc/v2ray/config.json
   ```

3. View error logs:
   ```bash
   tail -20 /var/log/v2ray/error.log
   tail -20 /var/log/v2ray/access.log
   ```

### Client Can't Connect to Any Protocol

1. Check firewall allows all ports:
   ```bash
   ssh root@YOUR_SERVER_IP "iptables -L -n | grep -E '443|8388|8443'"
   ```

2. Verify services are listening:
   ```bash
   ssh root@YOUR_SERVER_IP "netstat -tulpn | grep -E '443|8388|8443'"
   ```

3. Check firewall activated:
   ```bash
   ssh root@YOUR_SERVER_IP "awall list"
   ```

### High Latency or Packet Loss

1. Adjust MTU (try 1200 or 1400):
   ```ini
   MTU = 1200
   ```

2. Check server load:
   ```bash
   ssh root@YOUR_SERVER_IP "top -bn1 | head -20"
   ```

---

## Security Considerations

1. **Change the obfuscation password**: Replace `YOUR_UDP2RAW_PASSWORD` with a strong, unique password
2. **Rotate keys regularly**: Generate new server/client keys periodically
3. **Monitor connections**: Regularly check `wg show` for unauthorized peers
4. **Firewall**: The awall configuration provides good default security
5. **SSH access**: Consider using SSH keys instead of password authentication
6. **Updates**: Keep Alpine Linux and all packages updated

---

## Important File Locations

| File/Directory | Purpose |
|---|---|
| **WireGuard** | |
| `/etc/wireguard/wg0.conf` | WireGuard server configuration |
| `/etc/wireguard/server_private.key` | Server private key |
| `/etc/wireguard/server_public.key` | Server public key |
| `/usr/local/bin/udp2raw` | udp2raw binary |
| `/var/log/udp2raw.log` | udp2raw logs |
| `/etc/local.d/wireguard.start` | WireGuard auto-start script |
| **Shadowsocks** | |
| `/etc/shadowsocks-rust/config.json` | Shadowsocks configuration |
| `/usr/local/bin/ssserver` | Shadowsocks server binary |
| `/var/log/shadowsocks.log` | Shadowsocks logs |
| `/etc/init.d/shadowsocks-rust` | Shadowsocks init script |
| **V2Ray** | |
| `/etc/v2ray/config.json` | V2Ray configuration (users in clients array) |
| `/usr/local/v2ray/v2ray` | V2Ray binary |
| `/var/log/v2ray/access.log` | V2Ray access logs |
| `/var/log/v2ray/error.log` | V2Ray error logs |
| `/etc/init.d/v2ray` | V2Ray init script |
| **Firewall** | |
| `/etc/awall/private/custom-services.json` | Custom service definitions (all 3 protocols) |
| `/etc/awall/optional/multi-vpn.json` | Multi-protocol VPN firewall policy |

---

## Server Credentials Summary

**Server Access**:
- Email: admin@example.com
- Password: YOUR_PROVIDER_PASSWORD
- Root Password: YOUR_SERVER_PASSWORD
- IP: YOUR_SERVER_IP

**VPN Configuration**:
- Server Public Key: `D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=`
- Obfuscation Password: `YOUR_UDP2RAW_PASSWORD`
- VPN Network: 10.7.0.0/24
- Server VPN IP: 10.7.0.1
- Client 1 VPN IP: 10.7.0.2

---

## Quick Reference Commands

### Restart All Services
```bash
ssh root@YOUR_SERVER_IP << 'EOF'
wg-quick down wg0 && wg-quick up wg0
rc-service shadowsocks-rust restart
rc-service v2ray restart
EOF
```

### Check All Services Status
```bash
./capybara.py server status
# Or manually:
ssh root@YOUR_SERVER_IP "wg show; rc-service shadowsocks-rust status; rc-service v2ray status"
```

### Add New User (All Protocols)
```bash
./capybara.py user add username --description "Description"
```

This automatically generates configs for all three protocols with QR codes.

### View Logs for All Protocols
```bash
./capybara.py logs show --service wireguard
./capybara.py logs show --service shadowsocks
./capybara.py logs show --service v2ray
```

### Test Server DNS Resolution
```bash
ssh root@YOUR_SERVER_IP "nslookup google.com"
```

If DNS fails, check firewall allows outbound traffic

---

## iOS Client Setup (Alternative Methods)

Since udp2raw requires root access not available on iOS without jailbreak:

**Option 1**: Use a router with udp2raw
- Install udp2raw on a home router running OpenWRT
- Connect iOS device to home WiFi
- Configure iOS WireGuard app to connect to router

**Option 2**: Use alternative obfuscation apps
- Consider apps like Passepartout or IVPN that support V2Ray obfuscation
- These can provide similar DPI evasion capabilities

**Option 3**: Run udp2raw on macOS and share connection
- Run udp2raw on Mac
- Enable Internet Sharing on Mac
- Connect iOS to Mac's shared connection
- Configure iOS WireGuard to use the Mac's local IP

---

## Performance Optimization

### Reduce Latency
- Choose a VPS geographically closer to your location
- Use `--cipher-mode none` in udp2raw (less secure but faster)
- Increase MTU if network supports it

### Increase Throughput
- Consider using `--cipher-mode aes128cbc` instead of `xor`
- Enable hardware acceleration if available
- Monitor server CPU usage

### Battery Optimization (Mobile)
- Adjust `PersistentKeepalive` (higher = better battery, less stable connection)
- Use split tunneling (don't route all traffic through VPN)

---

*Documentation created: 2025-01-06*
*Server setup tested and verified on Alpine Linux 3.22.2*
