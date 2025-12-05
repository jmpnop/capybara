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
3. **V2Ray VMess + WebSocket** - Port 80 (HTTP/WebSocket, mobile-optimized)

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
      "port": 80,
      "protocol": "vmess",
      "settings": {
        "clients": []
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/api/v2/download"
        }
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

**Configuration Details**:
- **Port 80**: Standard HTTP port - rarely blocked by ISPs or mobile networks
- **WebSocket Transport**: Makes traffic look like normal web application traffic
- **Path `/api/v2/download`**: Disguises VPN traffic as API requests
- **Mobile-Optimized**: Works reliably on Beeline, MTS, Megafon mobile networks where standard ports are often blocked

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
            { "proto": "tcp", "port": 80 }
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
- SSH (port 22), port 443, 8388, 80 accepted
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
netstat -tulpn | grep 80
```

**Expected Output**:
- WireGuard interface `wg0` should be listed
- udp2raw process running on port 443
- Shadowsocks listening on 0.0.0.0:8388 (TCP/UDP)
- V2Ray listening on :::80 (WebSocket)

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

**IMPORTANT**: The official udp2raw GitHub releases do NOT include macOS binaries. You must use Homebrew to install the macOS-compatible version.

### Step 1: Install udp2raw via Homebrew

```bash
# Install udp2raw-multiplatform (native macOS version)
brew install udp2raw-multiplatform

# Create a convenient symlink (optional, requires password)
sudo ln -s /opt/homebrew/opt/udp2raw-multiplatform/bin/udp2raw_mp /usr/local/bin/udp2raw

# Verify installation
udp2raw --help
# Or use full path if symlink not created:
/opt/homebrew/opt/udp2raw-multiplatform/bin/udp2raw_mp --help
```

**Why Homebrew?**
- Official releases only contain Linux binaries (ELF format)
- macOS requires Mach-O binaries compiled specifically for macOS
- Homebrew's `udp2raw-multiplatform` package provides native macOS support for both Intel and Apple Silicon

### Step 2: Run udp2raw Client

Open a terminal and run:

```bash
# Using symlink (if created in Step 1)
sudo udp2raw -c \
  -l 127.0.0.1:4096 \
  -r YOUR_SERVER_IP:443 \
  -k YOUR_UDP2RAW_PASSWORD \
  --raw-mode faketcp \
  --cipher-mode xor \
  --auth-mode hmac_sha1
```

**Or using full path** (if symlink not created):

```bash
sudo /opt/homebrew/opt/udp2raw-multiplatform/bin/udp2raw_mp -c \
  -l 127.0.0.1:4096 \
  -r YOUR_SERVER_IP:443 \
  -k YOUR_UDP2RAW_PASSWORD \
  --raw-mode faketcp \
  --cipher-mode xor \
  --auth-mode hmac_sha1
```

**Important Notes**:
- Replace `YOUR_SERVER_IP` with your actual server IP address
- Replace `YOUR_UDP2RAW_PASSWORD` with the password from your server's `/etc/wireguard/wg0.conf`
- **Keep this terminal window open** while using the VPN
- `sudo` is required for raw socket access
- **Do NOT use `--fix-gro` or `-a`** - these flags are Linux-specific and will cause an error on macOS

### Step 3: Install WireGuard App

**Option A: Mac App Store** (Recommended)
- Download from: https://apps.apple.com/us/app/wireguard/id1451685025

**Option B: Homebrew**
```bash
brew install --cask wireguard-tools
```

### Step 4: Import WireGuard Configuration

You should have received a `.conf` file (e.g., `username_wireguard.conf`) from your server admin or generated via Capybara.

**Method 1: Import via WireGuard App** (Easiest)

1. Open WireGuard app
2. Click **"Import Tunnel(s) from File..."** (bottom left)
3. Select your `.conf` file
4. Click "Open"

**Method 2: Drag and Drop**

1. Open WireGuard app
2. Drag the `.conf` file directly into the WireGuard window

**Method 3: Create Manually**

In the WireGuard app, click "Add Empty Tunnel" and paste:

```ini
[Interface]
PrivateKey = YOUR_CLIENT_PRIVATE_KEY
Address = 10.7.0.2/24
MTU = 1280
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = YOUR_SERVER_PUBLIC_KEY
AllowedIPs = 0.0.0.0/0
Endpoint = 127.0.0.1:4096
PersistentKeepalive = 25
```

**Configuration Parameters Explained**:
- `PrivateKey`: Your client's WireGuard private key (from server admin)
- `Address`: Your assigned VPN IP address (e.g., 10.7.0.2/24)
- `PublicKey`: The server's WireGuard public key
- `Endpoint`: **MUST be 127.0.0.1:4096** (points to local udp2raw client)
- `AllowedIPs`: 0.0.0.0/0 routes all traffic through VPN
- `DNS`: Optional, use your preferred DNS servers

**CRITICAL**: The `Endpoint` must point to `127.0.0.1:4096` (your local udp2raw client), NOT your server's IP. This creates a tunnel-within-a-tunnel:
```
WireGuard → udp2raw (localhost:4096) → Server (SERVER_IP:443)
```

### Step 5: Connect to VPN

**Two-Step Connection Process**:

1. **Terminal Window**: Start udp2raw client (from Step 2)
   ```bash
   sudo udp2raw -c -l 127.0.0.1:4096 -r YOUR_SERVER_IP:443 -k YOUR_PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1
   ```

   You should see:
   ```
   [INFO] client mode
   [INFO] listening on 127.0.0.1:4096
   [INFO] remote address YOUR_SERVER_IP:443
   ```

2. **WireGuard App**: Activate your tunnel
   - Click the toggle switch next to your tunnel name
   - Status should change to "Active"

### Step 6: Verify Connection

```bash
# Test VPN tunnel to server
ping 10.7.0.1

# Check your public IP (should show server IP)
curl ifconfig.me

# Test DNS resolution
nslookup google.com

# Check WireGuard interface
ifconfig | grep -A 5 utun
```

**Expected Results**:
- `ping 10.7.0.1` should succeed (VPN server responds)
- `curl ifconfig.me` should show your server's public IP
- DNS lookups should work
- You should see a `utun` interface with IP 10.7.0.x

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
ssh root@YOUR_SERVER_IP "netstat -tulpn | grep -E '443|8388|80|51820'"
```

**Expected**:
- Port 51820: WireGuard (localhost only, UDP)
- Port 443: udp2raw (all interfaces, TCP)
- Port 8388: Shadowsocks (0.0.0.0, TCP/UDP)
- Port 80: V2Ray (:::, WebSocket)

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
   netstat -tulpn | grep 80
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
   ssh root@YOUR_SERVER_IP "iptables -L -n | grep -E '443|8388|80'"
   ```

2. Verify services are listening:
   ```bash
   ssh root@YOUR_SERVER_IP "netstat -tulpn | grep -E '443|8388|80'"
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

### macOS Client: udp2raw Errors with Linux-Only Flags

**Symptoms**:
- `[FATAL] invalid option --fix-gro`
- `[FATAL] -a not supported in this version, check -g or --raw-mode easyfaketcp`

**Root Cause**: The `--fix-gro` and `-a` flags are Linux-specific and not available on macOS

**Solution**: Remove both `--fix-gro` and `-a` from the command:
```bash
# Correct for macOS
sudo udp2raw -c -l 127.0.0.1:4096 -r SERVER_IP:443 -k PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1

# WRONG - includes Linux-only flags
sudo udp2raw -c -l 127.0.0.1:4096 -r SERVER_IP:443 -k PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro
```

### macOS Client: Wrong Binary Format (ELF)

**Symptoms**:
- `udp2raw: cannot execute binary file`
- `line 1: Not: command not found`
- Running `file /usr/local/bin/udp2raw` shows "ELF 64-bit LSB executable"

**Root Cause**: Linux binary was installed instead of macOS binary

**Solution**:
```bash
# Remove the Linux binary
sudo rm /usr/local/bin/udp2raw

# Install the correct macOS version via Homebrew
brew install udp2raw-multiplatform

# Create symlink
sudo ln -s /opt/homebrew/opt/udp2raw-multiplatform/bin/udp2raw_mp /usr/local/bin/udp2raw
```

### macOS Client: "Operation not permitted" when running udp2raw

**Symptoms**: udp2raw fails with permission errors

**Solution**: Run with `sudo`:
```bash
sudo udp2raw -c -l 127.0.0.1:4096 -r SERVER_IP:443 -k PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1
```

Raw sockets require root privileges on macOS.

### macOS Client: Can't Import WireGuard Config with `open` Command

**Symptoms**:
```
No application knows how to open URL file:///path/to/config.conf
kLSApplicationNotFoundErr
```

**Solution**: Don't use `open`. Instead:

**Method 1**: Import via WireGuard app
```bash
# Launch WireGuard first
open -a WireGuard

# Then in the app: Import Tunnel(s) from File... → select .conf file
```

**Method 2**: Use drag and drop
1. Open WireGuard app
2. Drag `.conf` file into the window

### macOS Client: WireGuard Connects but No Internet

**Check both layers**:

1. Verify udp2raw is running:
   ```bash
   ps aux | grep udp2raw
   lsof -i :4096
   ```
   Should show udp2raw listening on 127.0.0.1:4096

2. Verify WireGuard is running:
   ```bash
   sudo wg show
   ifconfig | grep utun
   ```
   Should show interface with your VPN IP (10.7.0.x)

3. Test the tunnel:
   ```bash
   ping 10.7.0.1  # Server should respond
   ```

4. If ping works but internet doesn't, check server-side NAT (see troubleshooting above)

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

### Server (Alpine Linux)

| File/Directory | Purpose |
|---|---|
| **WireGuard** | |
| `/etc/wireguard/wg0.conf` | WireGuard server configuration |
| `/etc/wireguard/server_private.key` | Server private key |
| `/etc/wireguard/server_public.key` | Server public key |
| `/usr/local/bin/udp2raw` | udp2raw binary (Linux) |
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

### Client (macOS)

| File/Directory | Purpose |
|---|---|
| **udp2raw** | |
| `/opt/homebrew/opt/udp2raw-multiplatform/bin/udp2raw_mp` | udp2raw binary (macOS, via Homebrew) |
| `/usr/local/bin/udp2raw` | Optional symlink to udp2raw_mp |
| **WireGuard** | |
| `~/Library/Application Support/WireGuard/` | WireGuard configs (GUI app stores here) |
| `~/.wireguard/` or any location | WireGuard configs (CLI, user choice) |

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

## Platform Comparison: Server vs Client

### udp2raw Installation

| Platform | Installation Method | Binary Name | Source |
|----------|-------------------|-------------|---------|
| **Server (Alpine Linux)** | Manual download from GitHub | `udp2raw_amd64` → `/usr/local/bin/udp2raw` | https://github.com/wangyu-/udp2raw/releases |
| **Client (macOS)** | Homebrew package | `udp2raw_mp` | `brew install udp2raw-multiplatform` |
| **Client (Linux)** | Manual download from GitHub | `udp2raw_amd64` or `udp2raw_arm` | https://github.com/wangyu-/udp2raw/releases |

### udp2raw Command Differences

| Flag | Server (Linux) | Client (macOS) | Notes |
|------|---------------|----------------|-------|
| `--fix-gro` | ✅ Supported | ❌ **NOT supported** | Linux kernel optimization, causes error on macOS |
| `-a` | ✅ Required | ❌ **NOT supported** | Auto-add iptables rules (Linux only), not needed on macOS |
| `--raw-mode faketcp` | ✅ Required | ✅ Required | Same on both platforms |
| `-s` (server) | ✅ Server only | ❌ Client uses `-c` | Server listens mode |
| `-c` (client) | ❌ Server uses `-s` | ✅ Client only | Client connect mode |

### WireGuard Configuration Differences

| Parameter | Server | Client |
|-----------|--------|--------|
| **Endpoint** | Not used (server doesn't connect to peers) | **MUST be 127.0.0.1:4096** (local udp2raw) |
| **ListenPort** | 51820 (localhost only) | Not specified (auto-assigned) |
| **Address** | 10.7.0.1/24 (VPN gateway) | 10.7.0.x/24 (assigned by admin) |
| **PrivateKey** | Server's private key | Client's unique private key |
| **PreUp/PostDown** | Starts/stops udp2raw | Not needed (run manually) |

### Key Differences Summary

**Why you can't just copy server instructions for macOS client:**

1. **Binary Format**:
   - Linux: ELF format
   - macOS: Mach-O format
   - **They are NOT interchangeable**

2. **udp2raw Source**:
   - GitHub releases = Linux only
   - Homebrew = macOS native builds

3. **Flags**:
   - `--fix-gro` and `-a` work on Linux server ✅
   - `--fix-gro` and `-a` fail on macOS client ❌

4. **Architecture**:
   - Server: Always x86_64 (VPS providers use Intel)
   - macOS: Could be x86_64 (Intel) or ARM64 (Apple Silicon)
   - Homebrew automatically installs correct architecture

---

*Documentation created: 2025-01-06*
*Server setup tested and verified on Alpine Linux 3.22.2*
*macOS client setup updated: 2025-11-11 (Apple Silicon M1/M2/M3)*
