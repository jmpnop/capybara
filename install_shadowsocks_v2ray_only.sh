#!/bin/sh
#
# DEPRECATED: This script is deprecated. Use install_capybara.sh instead.
#
# Add Shadowsocks and V2Ray to existing WireGuard setup
# Does NOT modify WireGuard configuration
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo "${CYAN}[INFO]${NC} $1"; }
log_success() { echo "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo "${RED}[ERROR]${NC} $1"; }

# Check root
if [ "$(id -u)" -ne 0 ]; then
    log_error "Must be run as root"
    exit 1
fi

# Deprecation warning
echo ""
echo "${YELLOW}=============================================${NC}"
echo "${YELLOW}  DEPRECATION NOTICE${NC}"
echo "${YELLOW}=============================================${NC}"
echo ""
echo "${YELLOW}This script is deprecated.${NC}"
echo "Please use the new unified installer:"
echo ""
echo "  ${CYAN}wget https://raw.githubusercontent.com/jmpnop/capybara/main/install_capybara.sh${NC}"
echo "  ${CYAN}chmod +x install_capybara.sh${NC}"
echo "  ${CYAN}./install_capybara.sh --shadowsocks --v2ray${NC}"
echo ""
echo "Benefits:"
echo "  • Updated V2Ray config (port 80 with WebSocket for mobile)"
echo "  • Better maintained unified codebase"
echo "  • Same functionality"
echo ""
echo "This script will continue in 10 seconds... Press Ctrl+C to cancel"
sleep 10
echo ""

log_info "Installing Shadowsocks and V2Ray..."

# Install dependencies
log_info "Step 1/6: Installing dependencies..."
apk add curl unzip
log_success "Dependencies installed"

# Install Shadowsocks from GitHub (Alpine package often outdated)
log_info "Step 2/6: Installing Shadowsocks from GitHub..."
cd /tmp
wget https://github.com/shadowsocks/shadowsocks-rust/releases/download/v1.23.1/shadowsocks-v1.23.1.x86_64-unknown-linux-musl.tar.xz
tar -xf shadowsocks-v1.23.1.x86_64-unknown-linux-musl.tar.xz
mv ssserver sslocal ssmanager ssservice ssurl /usr/local/bin/
chmod +x /usr/local/bin/ss*
/usr/local/bin/ssserver --version
log_success "Shadowsocks installed"

# Install V2Ray
log_info "Step 3/6: Installing V2Ray..."
cd /tmp
wget https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip
mkdir -p /usr/local/v2ray
unzip -o v2ray-linux-64.zip -d /usr/local/v2ray/
chmod +x /usr/local/v2ray/v2ray
/usr/local/v2ray/v2ray version | head -3
log_success "V2Ray installed"

# Configure Shadowsocks
log_info "Step 4/6: Configuring Shadowsocks..."
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
log_success "Shadowsocks configured"
log_info "⚠️  Remember to change the default password in /etc/shadowsocks-rust/config.json"

# Configure V2Ray
log_info "Step 4/5: Configuring V2Ray..."
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
log_success "V2Ray configured"

# Setup services
log_info "Step 5/6: Setting up services..."

# Shadowsocks service
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

# V2Ray service
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

# Update firewall
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

# Update firewall configuration with critical DNS and NAT fixes
log_info "Step 6/6: Configuring firewall with DNS and NAT fixes..."

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

awall enable multi-vpn
awall activate -f

# Add catchall NAT rule for Shadowsocks/V2Ray traffic
iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
rc-service iptables save

log_success "Firewall configured with DNS and NAT support"

# Enable and start services
rc-update add shadowsocks-rust default
rc-update add v2ray default
rc-service shadowsocks-rust start
rc-service v2ray start

sleep 2

log_success "All services started"

# Verify services
echo ""
echo "${CYAN}Verifying service status...${NC}"
rc-service shadowsocks-rust status
rc-service v2ray status

echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}  ✅ Shadowsocks and V2Ray installed!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "${CYAN}Installed Services:${NC}"
echo "  • Shadowsocks: Port 8388 (TCP/UDP)"
echo "  • V2Ray: Port 8443 (TCP)"
echo ""
echo "${CYAN}Firewall Configured:${NC}"
echo "  ✅ Inbound: Ports 443, 8388, 8443, SSH"
echo "  ✅ Outbound: DNS, HTTP, HTTPS enabled"
echo "  ✅ NAT: Configured for all VPN traffic"
echo ""
echo "${CYAN}Log Locations:${NC}"
echo "  • Shadowsocks: /var/log/shadowsocks.log"
echo "  • V2Ray: /var/log/v2ray/access.log, /var/log/v2ray/error.log"
echo ""
echo "${YELLOW}Next Steps:${NC}"
echo "  1. Change Shadowsocks password in /etc/shadowsocks-rust/config.json"
echo "  2. Use Capybara CLI to add users:"
echo "     ./capybara.py user add alice --description \"User description\""
echo "  3. QR codes will be generated automatically for all protocols"
echo ""
echo "${CYAN}Verify Installation:${NC}"
echo "  netstat -tulpn | grep -E '8388|8443'"
echo "  nslookup google.com  # Test DNS resolution"
echo ""
