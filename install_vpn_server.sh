#!/bin/sh
#
# Capybara VPN Server Installation Script
# Automated setup of WireGuard + udp2raw obfuscation on Alpine Linux
#
# Usage:
#   1. Upload to Alpine Linux server: scp install_vpn_server.sh root@YOUR_SERVER_IP:/root/
#   2. SSH into server: ssh root@YOUR_SERVER_IP
#   3. Make executable: chmod +x /root/install_vpn_server.sh
#   4. Run: /root/install_vpn_server.sh
#
# Or run remotely:
#   ssh root@YOUR_SERVER_IP 'bash -s' < install_vpn_server.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VPN_NETWORK="10.7.0.0/24"
VPN_SERVER_IP="10.7.0.1"
WG_INTERFACE="wg0"
WG_PORT="51820"
UDP2RAW_PORT="443"
UDP2RAW_PASSWORD="SecureVPN2025Obfuscate"
PUBLIC_INTERFACE="eth0"

# Log functions
log_info() {
    echo "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

# Check if running on Alpine Linux
if [ ! -f /etc/alpine-release ]; then
    log_error "This script is designed for Alpine Linux"
    exit 1
fi

log_info "Starting Capybara VPN Server installation..."
log_info "Alpine Linux version: $(cat /etc/alpine-release)"

# Step 1: Update system
log_info "Step 1/10: Updating system packages..."
apk update
apk upgrade
log_success "System updated"

# Step 2: Install required packages
log_info "Step 2/10: Installing WireGuard, iptables, and awall..."
apk add wireguard-tools-wg-quick iptables awall
log_success "Packages installed"

# Step 3: Enable IP forwarding
log_info "Step 3/10: Enabling IP forwarding..."
if ! grep -q "net.ipv4.ip_forward" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
fi
sysctl -p
log_success "IP forwarding enabled"

# Step 4: Download and install udp2raw
log_info "Step 4/10: Installing udp2raw..."
cd /tmp
if [ ! -f udp2raw_binaries.tar.gz ]; then
    wget https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_binaries.tar.gz
fi
tar -xzf udp2raw_binaries.tar.gz

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        UDP2RAW_BINARY="udp2raw_amd64"
        ;;
    aarch64)
        UDP2RAW_BINARY="udp2raw_arm"
        ;;
    *)
        log_error "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

mv "$UDP2RAW_BINARY" /usr/local/bin/udp2raw
chmod +x /usr/local/bin/udp2raw
log_success "udp2raw installed (/usr/local/bin/udp2raw)"

# Step 5: Generate WireGuard keys
log_info "Step 5/10: Generating WireGuard keys..."
mkdir -p /etc/wireguard
cd /etc/wireguard
umask 077

if [ ! -f server_private.key ]; then
    wg genkey | tee server_private.key | wg pubkey > server_public.key
    log_success "Server keys generated"
    log_info "Server public key: $(cat server_public.key)"
else
    log_warning "Server keys already exist, skipping generation"
fi

SERVER_PRIVATE_KEY=$(cat server_private.key)
SERVER_PUBLIC_KEY=$(cat server_public.key)

# Step 6: Create WireGuard configuration
log_info "Step 6/10: Creating WireGuard configuration..."
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = ${VPN_SERVER_IP}/24
PrivateKey = ${SERVER_PRIVATE_KEY}
ListenPort = ${WG_PORT}
MTU = 1280

# udp2raw obfuscation (faketcp mode)
PreUp = /usr/local/bin/udp2raw -s -l 0.0.0.0:${UDP2RAW_PORT} -r 127.0.0.1:${WG_PORT} -k "${UDP2RAW_PASSWORD}" --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro >/var/log/udp2raw.log 2>&1 &
PostDown = killall udp2raw || true

# Enable NAT for clients
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ${PUBLIC_INTERFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ${PUBLIC_INTERFACE} -j MASQUERADE

# Client peers will be added here by capybara.py
# Example:
# [Peer]
# PublicKey = <client_public_key>
# AllowedIPs = 10.7.0.2/32
EOF

chmod 600 /etc/wireguard/wg0.conf
log_success "WireGuard configuration created"

# Step 7: Configure firewall (awall)
log_info "Step 7/10: Configuring firewall (awall)..."

# Create custom services definition
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

# Create main firewall policy
mkdir -p /etc/awall/optional
cat > /etc/awall/optional/cloud-server.json << EOF
{
  "description": "Protect cloud server",
  "import": "custom-services",
  "variable": { "internet_if": "${PUBLIC_INTERFACE}" },
  "zone": {
    "internet": { "iface": "\$internet_if" },
    "vpn": { "iface": "${WG_INTERFACE}" }
  },
  "policy": [
    { "in": "internet", "action": "drop" },
    { "in": "vpn", "out": "internet", "action": "accept" },
    { "out": "vpn", "in": "internet", "action": "accept" },
    { "action": "reject" }
  ],
  "snat": [ { "out": "internet", "src": "${VPN_NETWORK}" } ]
}
EOF

# Allow obfuscated WireGuard traffic
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

# Allow SSH access
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

# Enable firewall policies
awall enable cloud-server
awall enable wireguard-obfs
awall enable ssh-access

log_success "Firewall configured"

# Step 8: Load kernel modules
log_info "Step 8/10: Loading required kernel modules..."
modprobe ip_tables 2>/dev/null || true
modprobe iptable_nat 2>/dev/null || true
modprobe iptable_filter 2>/dev/null || true
log_success "Kernel modules loaded"

# Step 9: Activate firewall
log_info "Step 9/10: Activating firewall..."
awall activate -f
log_success "Firewall activated"

# Step 10: Create startup script
log_info "Step 10/10: Setting up automatic startup..."

# Create local startup script for WireGuard
cat > /etc/local.d/wireguard.start << 'EOF'
#!/bin/sh
# Start WireGuard on boot
wg-quick up wg0
EOF

chmod +x /etc/local.d/wireguard.start

# Enable local service
rc-update add local default

# Start WireGuard now
log_info "Starting WireGuard..."
wg-quick up wg0

# Wait a moment for services to start
sleep 2

log_success "WireGuard started"

# Display status
echo ""
echo "${CYAN}========================================${NC}"
echo "${GREEN}  Capybara VPN Server Installation Complete!${NC}"
echo "${CYAN}========================================${NC}"
echo ""
echo "${YELLOW}Server Information:${NC}"
echo "  VPN Network: ${VPN_NETWORK}"
echo "  Server VPN IP: ${VPN_SERVER_IP}"
echo "  WireGuard Port: ${WG_PORT} (UDP, direct)"
echo "  Obfuscated Port: ${UDP2RAW_PORT} (TCP, disguised as HTTPS)"
echo "  Public Interface: ${PUBLIC_INTERFACE}"
echo ""
echo "${YELLOW}Server Keys:${NC}"
echo "  Private Key: $(cat /etc/wireguard/server_private.key)"
echo "  Public Key: $(cat /etc/wireguard/server_public.key)"
echo ""
echo "${YELLOW}Configuration:${NC}"
echo "  WireGuard Config: /etc/wireguard/wg0.conf"
echo "  udp2raw Binary: /usr/local/bin/udp2raw"
echo "  udp2raw Log: /var/log/udp2raw.log"
echo ""
echo "${YELLOW}Services Status:${NC}"
wg show
echo ""
ps aux | grep udp2raw | grep -v grep || log_warning "udp2raw process not found"
echo ""
echo "${YELLOW}Firewall Status:${NC}"
awall list | grep -E "enabled|cloud-server|wireguard-obfs|ssh-access"
echo ""
echo "${YELLOW}Network Interfaces:${NC}"
ip -br addr show | grep UP
echo ""
echo "${GREEN}Next Steps:${NC}"
echo "  1. Note down your server's public IP address"
echo "  2. Install Capybara VPN Manager on your local machine"
echo "  3. Configure ~/.capybara_config.yaml with server details"
echo "  4. Add VPN users: ./capybara.py user add alice"
echo "  5. Share client config files from ./vpn_clients/"
echo ""
echo "${CYAN}Useful Commands:${NC}"
echo "  Check WireGuard status: wg show"
echo "  Check udp2raw log: tail -f /var/log/udp2raw.log"
echo "  Restart WireGuard: wg-quick down wg0 && wg-quick up wg0"
echo "  Check firewall: awall list"
echo "  View open ports: netstat -tulpn | grep -E '443|51820|22'"
echo ""
echo "${GREEN}Installation completed successfully!${NC}"
echo ""

# Create installation info file
cat > /root/vpn_install_info.txt << EOF
Capybara VPN Server Installation Info
======================================
Installation Date: $(date)
Alpine Linux Version: $(cat /etc/alpine-release)
Server VPN IP: ${VPN_SERVER_IP}
VPN Network: ${VPN_NETWORK}
WireGuard Port: ${WG_PORT}
Obfuscated Port: ${UDP2RAW_PORT}
Server Public Key: ${SERVER_PUBLIC_KEY}

Configuration Files:
- /etc/wireguard/wg0.conf
- /etc/wireguard/server_private.key
- /etc/wireguard/server_public.key
- /usr/local/bin/udp2raw
- /var/log/udp2raw.log

Firewall Policies:
- cloud-server (main VPN routing)
- wireguard-obfs (allow port 443)
- ssh-access (allow SSH)

Startup:
- /etc/local.d/wireguard.start

Management Tool:
https://github.com/jmpnop/capybara
EOF

log_success "Installation info saved to /root/vpn_install_info.txt"
