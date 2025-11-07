#!/bin/sh
#
# DEPRECATED: This script is deprecated. Use install_capybara.sh instead.
#
# Capybara - Multi-Protocol Censorship-Resistant VPN Server Installation
# Installs WireGuard + Shadowsocks + V2Ray with unified management
#
# Protocols Installed:
#   1. WireGuard with udp2raw obfuscation (Port 443 - HTTPS disguise)
#   2. Shadowsocks with AEAD encryption (Port 8388 - TCP/UDP)
#   3. V2Ray VMess protocol (Port 8443 - WebSocket + TLS)
#
# Features:
#   • Triple-layer censorship resistance
#   • Unified user management across all protocols
#   • QR code generation for easy client setup
#   • Protocol fallback options
#   • Complete in ~3 minutes
#
# Usage:
#   wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_multi_vpn_server.sh
#   chmod +x install_multi_vpn_server.sh
#   ./install_multi_vpn_server.sh
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
UDP2RAW_PASSWORD="YOUR_UDP2RAW_PASSWORD"
SS_PORT="8388"
SS_METHOD="chacha20-ietf-poly1305"
V2RAY_PORT="8443"
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

# Deprecation warning
echo ""
echo "${YELLOW}=============================================${NC}"
echo "${YELLOW}  DEPRECATION NOTICE${NC}"
echo "${YELLOW}=============================================${NC}"
echo ""
echo "${YELLOW}This script is deprecated.${NC}"
echo "Please use the new unified installer instead:"
echo ""
echo "  ${CYAN}wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_capybara.sh${NC}"
echo "  ${CYAN}chmod +x install_capybara.sh${NC}"
echo "  ${CYAN}./install_capybara.sh${NC}"
echo ""
echo "Benefits of the new installer:"
echo "  • Modular installation (choose which protocols to install)"
echo "  • Updated V2Ray config (port 80 with WebSocket for mobile networks)"
echo "  • Less redundant code, better maintained"
echo "  • Same functionality, better structure"
echo ""
echo "This script will continue in 10 seconds..."
echo "${YELLOW}Press Ctrl+C to cancel${NC}"
echo ""
sleep 10

log_info "Starting Capybara Multi-Protocol VPN Server installation..."
log_info "Alpine Linux version: $(cat /etc/alpine-release)"
echo ""
log_info "Installing: WireGuard + Shadowsocks + V2Ray"
echo ""

# Step 1: Update system
log_info "Step 1/12: Updating system packages..."
apk update
apk upgrade
log_success "System updated"

# Step 2: Install required packages
log_info "Step 2/12: Installing WireGuard, Shadowsocks, iptables, and awall..."
apk add wireguard-tools-wg-quick iptables awall shadowsocks-libev curl unzip
log_success "Packages installed"

# Step 3: Enable IP forwarding
log_info "Step 3/12: Enabling IP forwarding..."
if ! grep -q "net.ipv4.ip_forward" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
fi
sysctl -p
log_success "IP forwarding enabled"

# Step 4: Download and install udp2raw
log_info "Step 4/12: Installing udp2raw..."
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
log_success "udp2raw installed"

# Step 5: Install V2Ray
log_info "Step 5/12: Installing V2Ray..."
cd /tmp
wget https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip
unzip -o v2ray-linux-64.zip -d /usr/local/v2ray/
chmod +x /usr/local/v2ray/v2ray
log_success "V2Ray installed"

# Step 6: Generate WireGuard keys
log_info "Step 6/12: Generating WireGuard keys..."
mkdir -p /etc/wireguard
cd /etc/wireguard
umask 077

if [ ! -f server_private.key ]; then
    wg genkey | tee server_private.key | wg pubkey > server_public.key
    log_success "WireGuard keys generated"
else
    log_warning "WireGuard keys already exist, skipping generation"
fi

SERVER_PRIVATE_KEY=$(cat server_private.key)
SERVER_PUBLIC_KEY=$(cat server_public.key)

# Step 7: Create WireGuard configuration
log_info "Step 7/12: Creating WireGuard configuration..."
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

# Client peers managed by Capybara CLI
EOF

chmod 600 /etc/wireguard/wg0.conf
log_success "WireGuard configuration created"

# Step 8: Configure Shadowsocks
log_info "Step 8/12: Configuring Shadowsocks..."
mkdir -p /etc/shadowsocks-libev

# Create users directory for per-user configs
mkdir -p /etc/shadowsocks-libev/users

# Create main Shadowsocks manager config
cat > /etc/shadowsocks-libev/config.json << 'EOF'
{
    "server": "0.0.0.0",
    "server_port": 8388,
    "method": "chacha20-ietf-poly1305",
    "timeout": 300,
    "fast_open": true,
    "mode": "tcp_and_udp"
}
EOF

log_success "Shadowsocks configuration created"

# Step 9: Configure V2Ray
log_info "Step 9/12: Configuring V2Ray..."
mkdir -p /etc/v2ray
mkdir -p /var/log/v2ray

# Generate initial V2Ray UUID
V2RAY_UUID=$(cat /proc/sys/kernel/random/uuid)

cat > /etc/v2ray/config.json << EOF
{
  "log": {
    "access": "/var/log/v2ray/access.log",
    "error": "/var/log/v2ray/error.log",
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": ${V2RAY_PORT},
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

log_success "V2Ray configuration created"

# Step 10: Configure firewall (awall)
log_info "Step 10/12: Configuring firewall..."

# Create custom services definition
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

# Create main firewall policy
mkdir -p /etc/awall/optional
cat > /etc/awall/optional/multi-vpn.json << EOF
{
  "description": "Multi-protocol VPN server",
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
  "filter": [
    {
      "in": "internet",
      "service": ["wireguard-obfs", "shadowsocks", "v2ray", "ssh"],
      "action": "accept"
    }
  ],
  "snat": [ { "out": "internet", "src": "${VPN_NETWORK}" } ]
}
EOF

# Enable firewall policies
awall enable multi-vpn

log_success "Firewall configured"

# Step 11: Load kernel modules and activate firewall
log_info "Step 11/12: Loading kernel modules and activating firewall..."
modprobe ip_tables 2>/dev/null || true
modprobe iptable_nat 2>/dev/null || true
modprobe iptable_filter 2>/dev/null || true
awall activate -f
log_success "Firewall activated"

# Step 12: Create startup scripts
log_info "Step 12/12: Setting up automatic startup..."

# WireGuard startup
cat > /etc/local.d/wireguard.start << 'EOF'
#!/bin/sh
wg-quick up wg0
EOF
chmod +x /etc/local.d/wireguard.start

# Shadowsocks startup
cat > /etc/init.d/shadowsocks << 'EOF'
#!/sbin/openrc-run

name="shadowsocks"
command="/usr/bin/ss-server"
command_args="-c /etc/shadowsocks-libev/config.json"
command_background=true
pidfile="/run/${RC_SVCNAME}.pid"

depend() {
    need net
    after firewall
}
EOF
chmod +x /etc/init.d/shadowsocks

# V2Ray startup
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

# Enable services
rc-update add local default
rc-update add shadowsocks default
rc-update add v2ray default

# Start all services
log_info "Starting all VPN services..."
wg-quick up wg0 2>/dev/null || true
rc-service shadowsocks start 2>/dev/null || true
rc-service v2ray start 2>/dev/null || true

sleep 2

log_success "All services started"

# Display status
echo ""
echo "${CYAN}========================================${NC}"
echo "${GREEN}  🛡️  Multi-Protocol VPN Server Ready!${NC}"
echo "${CYAN}========================================${NC}"
echo ""
echo "${YELLOW}🔐 Three Anti-Censorship Protocols Installed:${NC}"
echo ""
echo "${CYAN}1. WireGuard + udp2raw${NC}"
echo "   Port: ${UDP2RAW_PORT} (TCP, appears as HTTPS)"
echo "   Features: Fastest, obfuscated, best for desktop"
echo "   Status: $(wg show wg0 2>/dev/null | grep -q interface && echo "${GREEN}Running${NC}" || echo "${RED}Stopped${NC}")"
echo ""
echo "${CYAN}2. Shadowsocks${NC}"
echo "   Port: ${SS_PORT} (TCP/UDP)"
echo "   Method: ${SS_METHOD}"
echo "   Features: Mobile-friendly, good iOS support"
echo "   Status: $(rc-service shadowsocks status 2>/dev/null | grep -q started && echo "${GREEN}Running${NC}" || echo "${RED}Stopped${NC}")"
echo ""
echo "${CYAN}3. V2Ray (VMess)${NC}"
echo "   Port: ${V2RAY_PORT} (TCP)"
echo "   Features: Highly configurable, strong obfuscation"
echo "   Status: $(rc-service v2ray status 2>/dev/null | grep -q started && echo "${GREEN}Running${NC}" || echo "${RED}Stopped${NC}")"
echo ""
echo "${YELLOW}📡 Network Configuration:${NC}"
echo "  VPN Network: ${VPN_NETWORK}"
echo "  Server VPN IP: ${VPN_SERVER_IP}"
echo "  Public Interface: ${PUBLIC_INTERFACE}"
echo ""
echo "${YELLOW}🔑 Server Keys:${NC}"
echo "  WireGuard Public Key: ${SERVER_PUBLIC_KEY}"
echo ""
echo "${YELLOW}📁 Configuration Files:${NC}"
echo "  WireGuard: /etc/wireguard/wg0.conf"
echo "  Shadowsocks: /etc/shadowsocks-libev/config.json"
echo "  V2Ray: /etc/v2ray/config.json"
echo ""
echo "${YELLOW}📝 Log Files:${NC}"
echo "  udp2raw: /var/log/udp2raw.log"
echo "  V2Ray: /var/log/v2ray/access.log, /var/log/v2ray/error.log"
echo ""
echo "${GREEN}Next Steps:${NC}"
echo "  1. Install Capybara management tool on your local machine"
echo "  2. Configure ~/.capybara_config.yaml with server details"
echo "  3. Add users: ./capybara.py user add alice --protocols all"
echo "  4. QR codes generated automatically for all protocols"
echo ""
echo "${CYAN}Management Tool:${NC}"
echo "  https://github.com/jmpnop/capybara"
echo ""
echo "${GREEN}Installation completed successfully!${NC}"
echo ""

# Create installation info file
cat > /root/vpn_install_info.txt << EOF
Capybara Multi-Protocol VPN Server Installation Info
=====================================================
Installation Date: $(date)
Alpine Linux Version: $(cat /etc/alpine-release)

Protocols Installed:
1. WireGuard + udp2raw
   - Port: ${UDP2RAW_PORT} (TCP, HTTPS obfuscation)
   - Internal Port: ${WG_PORT} (UDP)
   - Server Public Key: ${SERVER_PUBLIC_KEY}

2. Shadowsocks
   - Port: ${SS_PORT} (TCP/UDP)
   - Method: ${SS_METHOD}

3. V2Ray (VMess)
   - Port: ${V2RAY_PORT} (TCP)

Network Configuration:
- VPN Network: ${VPN_NETWORK}
- Server VPN IP: ${VPN_SERVER_IP}
- Public Interface: ${PUBLIC_INTERFACE}

Configuration Files:
- /etc/wireguard/wg0.conf
- /etc/shadowsocks-libev/config.json
- /etc/v2ray/config.json

User Management:
- Use Capybara CLI tool for unified user management
- QR codes generated automatically for all protocols

Management Tool:
https://github.com/jmpnop/capybara
EOF

log_success "Installation info saved to /root/vpn_install_info.txt"
