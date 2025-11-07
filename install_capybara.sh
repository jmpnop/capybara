#!/bin/sh
#
# Capybara - Multi-Protocol VPN Server Installation
# Unified installer for WireGuard, Shadowsocks, and V2Ray on Alpine Linux
#
# Protocols:
#   • WireGuard + udp2raw (Port 443 - HTTPS disguise, DPI evasion)
#   • Shadowsocks (Port 8388 - AEAD encryption, mobile-friendly)
#   • V2Ray + WebSocket (Port 80 - HTTP disguise, mobile networks)
#
# Usage:
#   ./install_capybara.sh              # Install all protocols (recommended)
#   ./install_capybara.sh --wireguard  # WireGuard only
#   ./install_capybara.sh --shadowsocks --v2ray  # Add to existing WireGuard
#
# Quick start:
#   wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_capybara.sh
#   chmod +x install_capybara.sh
#   ./install_capybara.sh
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
VPN_NETWORK="10.7.0.0/24"
VPN_SERVER_IP="10.7.0.1"
WG_INTERFACE="wg0"
WG_PORT="51820"
UDP2RAW_PORT="443"
UDP2RAW_PASSWORD="YOUR_UDP2RAW_PASSWORD"
SS_PORT="8388"
SS_PASSWORD="YOUR_SHADOWSOCKS_PASSWORD"
SS_METHOD="chacha20-ietf-poly1305"
V2RAY_PORT="80"
V2RAY_WS_PATH="/api/v2/download"
PUBLIC_INTERFACE="eth0"

# Parse command line arguments
INSTALL_WIREGUARD=false
INSTALL_SHADOWSOCKS=false
INSTALL_V2RAY=false

if [ $# -eq 0 ]; then
    # No arguments = install all
    INSTALL_WIREGUARD=true
    INSTALL_SHADOWSOCKS=true
    INSTALL_V2RAY=true
else
    # Parse flags
    for arg in "$@"; do
        case $arg in
            --wireguard|-w)
                INSTALL_WIREGUARD=true
                ;;
            --shadowsocks|-s)
                INSTALL_SHADOWSOCKS=true
                ;;
            --v2ray|-v)
                INSTALL_V2RAY=true
                ;;
            --all|-a)
                INSTALL_WIREGUARD=true
                INSTALL_SHADOWSOCKS=true
                INSTALL_V2RAY=true
                ;;
            --help|-h)
                echo "Capybara Multi-Protocol VPN Installer"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --all, -a          Install all protocols (default)"
                echo "  --wireguard, -w    Install WireGuard only"
                echo "  --shadowsocks, -s  Install Shadowsocks only"
                echo "  --v2ray, -v        Install V2Ray only"
                echo "  --help, -h         Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                 # Install all protocols"
                echo "  $0 --wireguard     # WireGuard only"
                echo "  $0 -s -v           # Add Shadowsocks + V2Ray to existing server"
                exit 0
                ;;
            *)
                echo "Unknown option: $arg"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
fi

# Logging functions
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

# Display banner
echo ""
echo "${CYAN}=============================================${NC}"
echo "${GREEN}   Capybara VPN Server Installation${NC}"
echo "${CYAN}=============================================${NC}"
echo ""
log_info "Alpine Linux version: $(cat /etc/alpine-release)"
echo ""
log_info "Installing protocols:"
$INSTALL_WIREGUARD && echo "  ${GREEN}✓${NC} WireGuard + udp2raw (Port 443)"
$INSTALL_SHADOWSOCKS && echo "  ${GREEN}✓${NC} Shadowsocks (Port 8388)"
$INSTALL_V2RAY && echo "  ${GREEN}✓${NC} V2Ray + WebSocket (Port 80)"
echo ""

# Function: System setup (shared by all protocols)
setup_system() {
    log_info "Updating system packages..."
    apk update >/dev/null 2>&1
    apk upgrade >/dev/null 2>&1
    log_success "System updated"

    log_info "Enabling IP forwarding..."
    if ! grep -q "net.ipv4.ip_forward" /etc/sysctl.conf; then
        echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
    fi
    sysctl -p >/dev/null 2>&1
    log_success "IP forwarding enabled"
}

# Function: Install WireGuard + udp2raw
install_wireguard() {
    log_info "Installing WireGuard..."

    apk add wireguard-tools-wg-quick iptables awall >/dev/null 2>&1

    # Download udp2raw
    cd /tmp
    wget -q https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_binaries.tar.gz
    tar -xzf udp2raw_binaries.tar.gz
    mv udp2raw_amd64 /usr/local/bin/udp2raw
    chmod +x /usr/local/bin/udp2raw
    rm -f udp2raw_binaries.tar.gz

    # Generate server keys
    mkdir -p /etc/wireguard
    cd /etc/wireguard
    umask 077
    wg genkey | tee server_private.key | wg pubkey > server_public.key

    # Create WireGuard configuration
    cat > /etc/wireguard/${WG_INTERFACE}.conf << EOF
[Interface]
Address = ${VPN_SERVER_IP}/24
PrivateKey = $(cat server_private.key)
ListenPort = ${WG_PORT}
MTU = 1280

# udp2raw obfuscation (faketcp mode)
PreUp = /usr/local/bin/udp2raw -s -l 0.0.0.0:${UDP2RAW_PORT} -r 127.0.0.1:${WG_PORT} -k "${UDP2RAW_PASSWORD}" --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro >/var/log/udp2raw.log 2>&1 &
PostDown = killall udp2raw || true

# Enable NAT for clients
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ${PUBLIC_INTERFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ${PUBLIC_INTERFACE} -j MASQUERADE
EOF

    # Configure firewall
    setup_firewall_wireguard

    # Enable and start WireGuard
    rc-update add wg-quick.${WG_INTERFACE} default >/dev/null 2>&1
    rc-service wg-quick.${WG_INTERFACE} start >/dev/null 2>&1

    log_success "WireGuard installed and running"
}

# Function: Install Shadowsocks
install_shadowsocks() {
    log_info "Installing Shadowsocks..."

    apk add shadowsocks-libev >/dev/null 2>&1

    # Create Shadowsocks configuration
    mkdir -p /etc/shadowsocks-libev
    cat > /etc/shadowsocks-libev/config.json << EOF
{
    "server": "0.0.0.0",
    "server_port": ${SS_PORT},
    "password": "${SS_PASSWORD}",
    "timeout": 300,
    "method": "${SS_METHOD}",
    "mode": "tcp_and_udp",
    "fast_open": true
}
EOF

    # Configure firewall for Shadowsocks
    setup_firewall_shadowsocks

    # Enable and start Shadowsocks
    rc-update add shadowsocks-libev default >/dev/null 2>&1
    rc-service shadowsocks-libev start >/dev/null 2>&1

    log_success "Shadowsocks installed and running"
}

# Function: Install V2Ray
install_v2ray() {
    log_info "Installing V2Ray..."

    # Download V2Ray
    cd /tmp
    wget -q https://github.com/v2fly/v2ray-core/releases/download/v5.4.1/v2ray-linux-64.zip
    unzip -q v2ray-linux-64.zip -d v2ray
    mv v2ray/v2ray /usr/local/bin/
    chmod +x /usr/local/bin/v2ray
    rm -rf v2ray v2ray-linux-64.zip

    # Create V2Ray configuration directory
    mkdir -p /etc/v2ray
    mkdir -p /var/log/v2ray

    # Create V2Ray configuration with WebSocket
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

    # Create V2Ray init script
    cat > /etc/init.d/v2ray << 'INITEOF'
#!/sbin/openrc-run

name="V2Ray"
command="/usr/local/bin/v2ray"
command_args="run -config /etc/v2ray/config.json"
command_background=true
pidfile="/var/run/v2ray.pid"

depend() {
    need net
    after firewall
}
INITEOF

    chmod +x /etc/init.d/v2ray

    # Configure firewall for V2Ray
    setup_firewall_v2ray

    # Enable and start V2Ray
    rc-update add v2ray default >/dev/null 2>&1
    rc-service v2ray start >/dev/null 2>&1

    log_success "V2Ray installed and running"
}

# Function: Setup firewall for WireGuard
setup_firewall_wireguard() {
    mkdir -p /etc/awall/private
    cat > /etc/awall/private/custom-services.json << EOF
{
    "service": {
        "wireguard-obfs": [
            { "proto": "tcp", "port": ${UDP2RAW_PORT} }
        ]
    }
}
EOF

    mkdir -p /etc/awall/optional
    cat > /etc/awall/optional/wireguard-obfs.json << 'EOF'
{
    "description": "Allow WireGuard with udp2raw obfuscation",
    "import": "custom-services",
    "filter": [
        {
            "in": "internet",
            "service": "wireguard-obfs",
            "action": "accept"
        }
    ]
}
EOF

    cat > /etc/awall/optional/vpn-base.json << EOF
{
  "description": "Base VPN server policy",
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

    awall enable vpn-base >/dev/null 2>&1
    awall enable wireguard-obfs >/dev/null 2>&1
}

# Function: Setup firewall for Shadowsocks
setup_firewall_shadowsocks() {
    mkdir -p /etc/awall/private
    if [ ! -f /etc/awall/private/custom-services.json ]; then
        cat > /etc/awall/private/custom-services.json << 'EOF'
{
    "service": {}
}
EOF
    fi

    # Add Shadowsocks service
    cat > /etc/awall/optional/shadowsocks.json << EOF
{
    "description": "Allow Shadowsocks",
    "filter": [
        {
            "in": "internet",
            "proto": "tcp",
            "dport": ${SS_PORT},
            "action": "accept"
        },
        {
            "in": "internet",
            "proto": "udp",
            "dport": ${SS_PORT},
            "action": "accept"
        }
    ]
}
EOF

    awall enable shadowsocks >/dev/null 2>&1
}

# Function: Setup firewall for V2Ray
setup_firewall_v2ray() {
    # V2Ray on port 80 - HTTP port
    cat > /etc/awall/optional/v2ray.json << EOF
{
    "description": "Allow V2Ray WebSocket on port 80",
    "filter": [
        {
            "in": "internet",
            "proto": "tcp",
            "dport": ${V2RAY_PORT},
            "action": "accept"
        }
    ]
}
EOF

    awall enable v2ray >/dev/null 2>&1
}

# Function: Setup SSH access
setup_ssh_access() {
    if [ ! -f /etc/awall/optional/ssh-access.json ]; then
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
        awall enable ssh-access >/dev/null 2>&1
    fi
}

# Function: Finalize firewall
finalize_firewall() {
    log_info "Configuring firewall..."
    setup_ssh_access
    awall activate >/dev/null 2>&1
    rc-update add iptables default >/dev/null 2>&1
    rc-service iptables restart >/dev/null 2>&1
    log_success "Firewall configured"
}

# Function: Add catchall NAT rule for non-WireGuard traffic
add_catchall_nat() {
    if ! iptables -t nat -C POSTROUTING -o ${PUBLIC_INTERFACE} -j MASQUERADE 2>/dev/null; then
        iptables -t nat -A POSTROUTING -o ${PUBLIC_INTERFACE} -j MASQUERADE
        rc-service iptables save >/dev/null 2>&1
        log_success "Catchall NAT rule added for Shadowsocks/V2Ray"
    fi
}

# Function: Display installation summary
display_summary() {
    echo ""
    echo "${CYAN}=============================================${NC}"
    echo "${GREEN}   Installation Complete!${NC}"
    echo "${CYAN}=============================================${NC}"
    echo ""

    log_info "Installed Protocols:"
    if $INSTALL_WIREGUARD; then
        echo "  ${GREEN}✓${NC} WireGuard + udp2raw"
        echo "    - Port: ${UDP2RAW_PORT} (HTTPS obfuscation)"
        echo "    - Network: ${VPN_NETWORK}"
    fi

    if $INSTALL_SHADOWSOCKS; then
        echo "  ${GREEN}✓${NC} Shadowsocks"
        echo "    - Port: ${SS_PORT} (TCP/UDP)"
        echo "    - Method: ${SS_METHOD}"
    fi

    if $INSTALL_V2RAY; then
        echo "  ${GREEN}✓${NC} V2Ray + WebSocket"
        echo "    - Port: ${V2RAY_PORT} (HTTP/WebSocket)"
        echo "    - Path: ${V2RAY_WS_PATH}"
    fi

    echo ""
    log_info "Next Steps:"
    echo ""
    echo "1. Install Capybara management tool:"
    echo "   ${CYAN}git clone https://github.com/jmpnop/capybara.git${NC}"
    echo "   ${CYAN}cd capybara && pip3 install -r requirements.txt${NC}"
    echo ""
    echo "2. Add users:"
    echo "   ${CYAN}./capybara.py user add alice${NC}"
    echo ""
    echo "3. Users will get configuration files for all protocols:"
    if $INSTALL_WIREGUARD; then
        echo "   - WireGuard .conf + QR code"
    fi
    if $INSTALL_SHADOWSOCKS; then
        echo "   - Shadowsocks JSON + QR code"
    fi
    if $INSTALL_V2RAY; then
        echo "   - V2Ray VMess URL + QR code"
    fi
    echo ""
    echo "4. Check status:"
    if $INSTALL_WIREGUARD; then
        echo "   ${CYAN}wg show${NC}"
    fi
    if $INSTALL_SHADOWSOCKS; then
        echo "   ${CYAN}rc-service shadowsocks-libev status${NC}"
    fi
    if $INSTALL_V2RAY; then
        echo "   ${CYAN}rc-service v2ray status${NC}"
    fi
    echo ""
    log_success "Installation complete! Server is ready."
    echo ""
}

# Main installation flow
main() {
    setup_system

    if $INSTALL_WIREGUARD; then
        install_wireguard
    fi

    if $INSTALL_SHADOWSOCKS; then
        install_shadowsocks
    fi

    if $INSTALL_V2RAY; then
        install_v2ray
    fi

    # Add catchall NAT if Shadowsocks or V2Ray is installed
    if $INSTALL_SHADOWSOCKS || $INSTALL_V2RAY; then
        add_catchall_nat
    fi

    finalize_firewall
    display_summary
}

# Run main installation
main
