#!/bin/bash
# Capybara VPN Launcher
# GUI launcher for udp2raw + WireGuard VPN

set -e

# Paths
APP_SUPPORT="$HOME/Library/Application Support/CapybaraVPN"
CONFIG_FILE="$APP_SUPPORT/config.txt"
LOG_FILE="$APP_SUPPORT/vpn.log"
PID_FILE="$APP_SUPPORT/udp2raw.pid"

# Read configuration
if [ ! -f "$CONFIG_FILE" ]; then
    osascript -e 'display dialog "VPN not configured. Please reinstall." buttons {"OK"} default button 1 with icon stop'
    exit 1
fi

USERNAME=$(head -1 "$CONFIG_FILE")
WG_CONFIG="$APP_SUPPORT/${USERNAME}_wireguard.conf"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if VPN is running
is_running() {
    if pgrep -f "udp2raw.*127.0.0.1:4096" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Start VPN
start_vpn() {
    log "Starting VPN for user: $USERNAME"

    # Check if already running
    if is_running; then
        osascript -e 'display notification "VPN is already running" with title "Capybara VPN"'
        return 0
    fi

    # Start udp2raw
    osascript -e 'display notification "Starting udp2raw tunnel..." with title "Capybara VPN"'
    log "Starting udp2raw..."

    osascript -e 'do shell script "sudo /usr/local/bin/udp2raw -c -l 127.0.0.1:4096 -r 66.42.119.38:443 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 > /tmp/udp2raw.log 2>&1 &" with administrator privileges' 2>&1 | tee -a "$LOG_FILE"

    sleep 2

    # Verify udp2raw started
    if ! pgrep -f "udp2raw" > /dev/null; then
        log "ERROR: udp2raw failed to start"
        osascript -e 'display dialog "Failed to start udp2raw. Check logs." buttons {"OK"} with icon stop'
        return 1
    fi

    # Save PID
    pgrep -f "udp2raw.*127.0.0.1:4096" > "$PID_FILE"

    # Start WireGuard
    osascript -e 'display notification "Starting WireGuard..." with title "Capybara VPN"'
    log "Starting WireGuard..."

    osascript -e "do shell script \"sudo /usr/local/bin/wg-quick up '$WG_CONFIG'\" with administrator privileges" 2>&1 | tee -a "$LOG_FILE"

    sleep 2

    # Test connection
    if ping -c 1 -W 3 10.7.0.1 > /dev/null 2>&1; then
        log "VPN connected successfully"
        osascript -e 'display notification "Connected successfully!" with title "Capybara VPN" sound name "Glass"'

        # Show public IP
        PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "Unknown")
        log "Public IP: $PUBLIC_IP"
        osascript -e "display dialog \"VPN Connected!\\n\\nPublic IP: $PUBLIC_IP\" buttons {\"OK\"} default button 1 with icon note giving up after 5"
    else
        log "WARNING: VPN started but connection test failed"
        osascript -e 'display dialog "VPN started but connection test failed. Check settings." buttons {"OK"} with icon caution'
    fi
}

# Stop VPN
stop_vpn() {
    log "Stopping VPN..."

    osascript -e 'display notification "Disconnecting VPN..." with title "Capybara VPN"'

    # Stop WireGuard
    log "Stopping WireGuard..."
    osascript -e "do shell script \"sudo /usr/local/bin/wg-quick down '$WG_CONFIG' 2>/dev/null || true\" with administrator privileges" 2>&1 | tee -a "$LOG_FILE"

    # Stop udp2raw
    log "Stopping udp2raw..."
    osascript -e 'do shell script "sudo killall udp2raw 2>/dev/null || true" with administrator privileges' 2>&1 | tee -a "$LOG_FILE"

    # Clean up PID file
    rm -f "$PID_FILE"

    log "VPN stopped"
    osascript -e 'display notification "Disconnected" with title "Capybara VPN" sound name "Glass"'
}

# Show status
show_status() {
    if is_running; then
        STATUS="🟢 Connected"
        PUBLIC_IP=$(curl -s --max-time 3 ifconfig.me 2>/dev/null || echo "Unknown")
        osascript -e "display dialog \"Capybara VPN Status\\n\\nUser: $USERNAME\\nStatus: $STATUS\\nPublic IP: $PUBLIC_IP\" buttons {\"OK\"} default button 1 with icon note"
    else
        STATUS="🔴 Disconnected"
        osascript -e "display dialog \"Capybara VPN Status\\n\\nUser: $USERNAME\\nStatus: $STATUS\" buttons {\"OK\"} default button 1 with icon note"
    fi
}

# Main menu
show_menu() {
    if is_running; then
        CHOICE=$(osascript -e 'button returned of (display dialog "Capybara VPN Manager\n\nUser: '"$USERNAME"'\nStatus: 🟢 Connected" buttons {"Disconnect", "Status", "Cancel"} default button "Disconnect" with icon note)')
    else
        CHOICE=$(osascript -e 'button returned of (display dialog "Capybara VPN Manager\n\nUser: '"$USERNAME"'\nStatus: 🔴 Disconnected" buttons {"Connect", "Cancel"} default button "Connect" with icon note)')
    fi

    case "$CHOICE" in
        "Connect")
            start_vpn
            show_menu
            ;;
        "Disconnect")
            stop_vpn
            show_menu
            ;;
        "Status")
            show_status
            show_menu
            ;;
        "Cancel")
            exit 0
            ;;
    esac
}

# Command line interface
case "${1:-menu}" in
    start)
        start_vpn
        ;;
    stop)
        stop_vpn
        ;;
    status)
        show_status
        ;;
    menu|*)
        show_menu
        ;;
esac
