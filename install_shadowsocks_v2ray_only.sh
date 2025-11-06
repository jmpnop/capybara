#!/bin/sh
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

log_info "Installing Shadowsocks and V2Ray..."

# Install Shadowsocks
log_info "Step 1/5: Installing Shadowsocks..."
# shadowsocks-libev not available in Alpine 3.22, use shadowsocks-rust
apk add shadowsocks-rust curl unzip
log_success "Shadowsocks installed"

# Install V2Ray
log_info "Step 2/5: Installing V2Ray..."
cd /tmp
wget -q https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip
mkdir -p /usr/local/v2ray
unzip -oq v2ray-linux-64.zip -d /usr/local/v2ray/
chmod +x /usr/local/v2ray/v2ray
log_success "V2Ray installed"

# Configure Shadowsocks
log_info "Step 3/5: Configuring Shadowsocks..."
mkdir -p /etc/shadowsocks-libev/users

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
log_success "Shadowsocks configured"

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
log_info "Step 5/5: Setting up services..."

# Shadowsocks service
cat > /etc/init.d/shadowsocks << 'EOF'
#!/sbin/openrc-run

name="shadowsocks"
command="/usr/bin/ssserver"
command_args="-c /etc/shadowsocks-libev/config.json"
command_background=true
pidfile="/run/${RC_SVCNAME}.pid"

depend() {
    need net
    after firewall
}
EOF
chmod +x /etc/init.d/shadowsocks

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

# Check if multi-vpn policy exists, if not create it
if [ ! -f /etc/awall/optional/multi-vpn.json ]; then
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
  "snat": [ { "out": "internet", "src": "10.7.0.0/24" } ]
}
EOF
    awall enable multi-vpn
fi

awall activate -f

# Enable and start services
rc-update add shadowsocks default
rc-update add v2ray default
rc-service shadowsocks start
rc-service v2ray start

log_success "All services started"

echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}  Shadowsocks and V2Ray installed!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "${CYAN}Shadowsocks:${NC} Port 8388 (TCP/UDP)"
echo "${CYAN}V2Ray:${NC} Port 8443 (TCP)"
echo ""
echo "Use Capybara CLI to add users:"
echo "  ./capybara.py user add alice --protocols all"
echo ""
