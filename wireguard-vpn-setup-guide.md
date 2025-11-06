# WireGuard VPN Server Setup Guide with udp2raw Obfuscation

Complete step-by-step guide for setting up a WireGuard VPN server on Alpine Linux with udp2raw obfuscation to bypass Deep Packet Inspection (DPI).

## Server Information
- **Provider**: Vultr.com
- **OS**: Alpine Linux v3.22
- **Server IP**: 66.42.119.38
- **VPN Network**: 10.7.0.0/24
- **Obfuscation Port**: 443 (UDP disguised as TCP)
- **WireGuard Port**: 51820 (localhost only)

## Prerequisites
- Alpine Linux VPS with root access
- Public IP address
- SSH access configured

---

## Step 1: Connect and Verify System

```bash
ssh root@66.42.119.38
uname -a
cat /etc/os-release
```

**Expected Output**: Alpine Linux v3.22.x

---

## Step 2: Update System and Install Required Packages

```bash
apk update
apk upgrade
apk add wireguard-tools-wg-quick iptables awall
```

**Packages Installed**:
- `wireguard-tools-wg-quick` - WireGuard VPN tools and wg-quick utility
- `iptables` - Firewall and NAT
- `awall` - Alpine Wall firewall configuration tool

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

## Step 6: Configure WireGuard with Obfuscation

Create the WireGuard configuration file:

```bash
cat > /etc/wireguard/wg0.conf << 'EOF'
[Interface]
Address = 10.7.0.1/24
PrivateKey = 6Ofz/9BXTfHQmR/rHj9zJI6f3JkAL7KMnEO1dP0/TXM=
ListenPort = 51820
MTU = 1280

# udp2raw obfuscation (faketcp mode)
PreUp = /usr/local/bin/udp2raw -s -l 0.0.0.0:443 -r 127.0.0.1:51820 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro >/var/log/udp2raw.log 2>&1 &
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
- Password `SecureVPN2025Obfuscate` must match on client and server
- Port 443 is used to mimic HTTPS traffic (helps bypass DPI)

---

## Step 7: Enable IP Forwarding

```bash
grep -q 'net.ipv4.ip_forward' /etc/sysctl.conf || echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
sysctl -p
sysctl net.ipv4.ip_forward
```

**Expected Output**: `net.ipv4.ip_forward = 1`

---

## Step 8: Configure Firewall with Awall

### 8.1 Create Custom Service Definition

```bash
mkdir -p /etc/awall/private
cat > /etc/awall/private/custom-services.json << 'EOF'
{
    "service": {
        "wireguard-obfs": [
            { "proto": "udp", "port": 443 }
        ]
    }
}
EOF
```

### 8.2 Create Base Cloud Server Policy

```bash
mkdir -p /etc/awall/optional
cat > /etc/awall/optional/cloud-server.json << 'EOF'
{
  "description": "Protect cloud server",
  "import": "custom-services",
  "variable": { "internet_if": "eth0" },
  "zone": {
    "internet": { "iface": "$internet_if" },
    "vpn": { "iface": "wg0" }
  },
  "policy": [
    { "in": "internet", "action": "drop" },
    { "in": "vpn", "out": "internet", "action": "accept" },
    { "out": "vpn", "in": "internet", "action": "accept" },
    { "action": "reject" }
  ],
  "snat": [ { "out": "internet", "src": "10.7.0.0/24" } ]
}
EOF
```

### 8.3 Allow WireGuard Traffic

```bash
cat > /etc/awall/optional/wireguard-obfs.json << 'EOF'
{
    "description": "Allow incoming obfuscated WireGuard on port 443",
    "filter": [
        {
            "in": "internet",
            "service": "wireguard-obfs",
            "action": "accept"
        }
    ]
}
EOF
```

### 8.4 Allow SSH Access

```bash
cat > /etc/awall/optional/ssh-access.json << 'EOF'
{
    "description": "Allow incoming SSH access",
    "filter": [
        {
            "in": "internet",
            "service": "ssh",
            "action": "accept"
        }
    ]
}
EOF
```

### 8.5 Reboot to Load New Kernel (if system was upgraded)

```bash
reboot
```

Wait 30-60 seconds, then reconnect:
```bash
ssh root@66.42.119.38
```

### 8.6 Load Required Kernel Modules

```bash
modprobe ip_tables
modprobe iptable_nat
modprobe iptable_filter
```

**Verify modules loaded**:
```bash
lsmod | grep -E 'ip_tables|iptable_nat|nf_nat'
```

### 8.7 Enable and Activate Awall Policies

```bash
awall enable cloud-server
awall enable wireguard-obfs
awall enable ssh-access
echo '' | awall activate -f
```

### 8.8 Save and Enable iptables at Boot

```bash
rc-update add iptables
rc-service iptables save
```

**Verify firewall rules**:
```bash
iptables -L -n | head -30
```

You should see:
- SSH (port 22) accepted
- UDP port 443 accepted
- Default DROP policy

---

## Step 9: Start WireGuard Service

```bash
wg-quick up wg0
```

**Expected Output**:
```
[#] ip link add dev wg0 type wireguard
[#] /usr/local/bin/udp2raw -s -l 0.0.0.0:443 -r 127.0.0.1:51820...
[#] wg setconf wg0 /dev/fd/63
[#] ip -4 address add 10.7.0.1/24 dev wg0
[#] ip link set mtu 1280 up dev wg0
[#] iptables -A FORWARD -i wg0 -j ACCEPT...
```

**Verify WireGuard is running**:
```bash
wg show
ps aux | grep udp2raw | grep -v grep
```

---

## Step 10: Enable WireGuard at Boot

Create startup script:
```bash
cat > /etc/local.d/wireguard.start << 'EOF'
#!/bin/sh
wg-quick up wg0
EOF

chmod +x /etc/local.d/wireguard.start
rc-update add local default
```

---

## Step 11: Generate Client Keys and Add First Client

### 11.1 Generate Client Keys

```bash
cd /etc/wireguard
wg genkey | tee client1_private.key | wg pubkey > client1_public.key
cat client1_private.key
cat client1_public.key
```

**Example Generated Keys**:
- Private: `2MkhVZASXn/bBrOjrolSdNrIckiFBcu0GXOMjoiwDUc=`
- Public: `kkFtFxmLRVNguNO/xx9avIaK5p8cmVEsYiBD1HhZBzQ=`

### 11.2 Add Client Peer to Server

```bash
cat >> /etc/wireguard/wg0.conf << 'EOF'

[Peer]
PublicKey = kkFtFxmLRVNguNO/xx9avIaK5p8cmVEsYiBD1HhZBzQ=
AllowedIPs = 10.7.0.2/32
EOF
```

### 11.3 Reload WireGuard Configuration

```bash
wg syncconf wg0 <(wg-quick strip wg0)
wg show
```

You should now see the peer listed.

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
./udp2raw_mac_amd64 -c -l 127.0.0.1:4096 -r 66.42.119.38:443 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro
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
ssh root@66.42.119.38 "cd /etc/wireguard && wg genkey | tee client2_private.key | wg pubkey > client2_public.key && cat client2_private.key && cat client2_public.key"
```

### 2. Add Peer to Server

```bash
ssh root@66.42.119.38 "cat >> /etc/wireguard/wg0.conf << 'EOF'

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

### Check WireGuard Status

```bash
ssh root@66.42.119.38 "wg show"
```

### Check udp2raw Process

```bash
ssh root@66.42.119.38 "ps aux | grep udp2raw | grep -v grep"
```

### View udp2raw Logs

```bash
ssh root@66.42.119.38 "tail -f /var/log/udp2raw.log"
```

### Check Active Connections

```bash
ssh root@66.42.119.38 "wg show wg0 endpoints"
ssh root@66.42.119.38 "wg show wg0 transfer"
```

### Verify Listening Ports

```bash
ssh root@66.42.119.38 "netstat -ulnp | grep -E '443|51820'"
```

Expected:
- Port 51820: WireGuard (localhost only)
- Port 443: udp2raw (all interfaces)

### Check Firewall Rules

```bash
ssh root@66.42.119.38 "iptables -L -n -v"
ssh root@66.42.119.38 "iptables -t nat -L -n -v"
```

---

## Troubleshooting

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

### Client Can't Connect

1. Verify udp2raw is running on client
2. Check server firewall allows UDP 443
3. Verify keys match (client private <-> client public on server)
4. Check IP addresses don't conflict

### No Internet on Client

1. Verify IP forwarding enabled on server:
   ```bash
   sysctl net.ipv4.ip_forward
   ```

2. Check NAT rules:
   ```bash
   iptables -t nat -L -n -v | grep MASQUERADE
   ```

3. Verify client AllowedIPs is set to `0.0.0.0/0`

### High Latency or Packet Loss

1. Adjust MTU (try 1200 or 1400):
   ```ini
   MTU = 1200
   ```

2. Check server load:
   ```bash
   ssh root@66.42.119.38 "top -bn1 | head -20"
   ```

---

## Security Considerations

1. **Change the obfuscation password**: Replace `SecureVPN2025Obfuscate` with a strong, unique password
2. **Rotate keys regularly**: Generate new server/client keys periodically
3. **Monitor connections**: Regularly check `wg show` for unauthorized peers
4. **Firewall**: The awall configuration provides good default security
5. **SSH access**: Consider using SSH keys instead of password authentication
6. **Updates**: Keep Alpine Linux and all packages updated

---

## Important File Locations

| File/Directory | Purpose |
|---|---|
| `/etc/wireguard/wg0.conf` | WireGuard server configuration |
| `/etc/wireguard/server_private.key` | Server private key |
| `/etc/wireguard/server_public.key` | Server public key |
| `/etc/wireguard/client*_*.key` | Client keys |
| `/usr/local/bin/udp2raw` | udp2raw binary |
| `/var/log/udp2raw.log` | udp2raw logs |
| `/etc/awall/private/custom-services.json` | Custom service definitions |
| `/etc/awall/optional/*.json` | Firewall policies |
| `/etc/local.d/wireguard.start` | WireGuard auto-start script |

---

## Server Credentials Summary

**Server Access**:
- Email: polikashin@gmail.com
- Password: myhdos-sywsox-6dojmU
- Root Password: H7)a4(72PGSnN4Hh
- IP: 66.42.119.38

**VPN Configuration**:
- Server Public Key: `D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=`
- Obfuscation Password: `SecureVPN2025Obfuscate`
- VPN Network: 10.7.0.0/24
- Server VPN IP: 10.7.0.1
- Client 1 VPN IP: 10.7.0.2

---

## Quick Reference Commands

### Restart WireGuard
```bash
ssh root@66.42.119.38 "wg-quick down wg0 && wg-quick up wg0"
```

### Add New Client (Complete Process)
```bash
# Generate keys
ssh root@66.42.119.38 "cd /etc/wireguard && wg genkey | tee client_new_private.key | wg pubkey > client_new_public.key && echo 'Private:' && cat client_new_private.key && echo 'Public:' && cat client_new_public.key"

# Add to server (replace PUBLIC_KEY and IP)
ssh root@66.42.119.38 "echo -e '\n[Peer]\nPublicKey = PUBLIC_KEY\nAllowedIPs = 10.7.0.X/32' >> /etc/wireguard/wg0.conf && wg syncconf wg0 <(wg-quick strip wg0)"
```

### Remove Client
```bash
# Remove from config file manually, then:
ssh root@66.42.119.38 "wg syncconf wg0 <(wg-quick strip wg0)"
```

### View All Peers
```bash
ssh root@66.42.119.38 "wg show wg0 peers"
```

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
