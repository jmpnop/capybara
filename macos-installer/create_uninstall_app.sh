#!/bin/bash
# Create Uninstall.app for Capybara VPN
# This creates a standalone uninstaller application

set -e

echo "🗑️  Creating Capybara VPN Uninstaller..."

# Paths
APP_NAME="Uninstall Capybara VPN.app"
APP_DIR="payload/Applications/$APP_NAME"
CONTENTS="$APP_DIR/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

# Clean and create app bundle structure
rm -rf "$APP_DIR"
mkdir -p "$MACOS"
mkdir -p "$RESOURCES"

echo "📁 Created app bundle structure"

# Create Info.plist
cat > "$CONTENTS/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>en</string>
	<key>CFBundleExecutable</key>
	<string>uninstall</string>
	<key>CFBundleIconFile</key>
	<string>UninstallIcon</string>
	<key>CFBundleIdentifier</key>
	<string>com.capybara.vpn.uninstall</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>Uninstall Capybara VPN</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleVersion</key>
	<string>1</string>
	<key>LSMinimumSystemVersion</key>
	<string>10.13</string>
	<key>LSUIElement</key>
	<false/>
	<key>NSHighResolutionCapable</key>
	<true/>
	<key>NSAppleScriptEnabled</key>
	<true/>
</dict>
</plist>
EOF

echo "✅ Created Info.plist"

# Create uninstaller script
cat > "$MACOS/uninstall" << 'UNINSTALL_SCRIPT'
#!/bin/bash
# Capybara VPN Uninstaller
# Interactive GUI uninstaller

set -e

APP_SUPPORT="$HOME/Library/Application Support/CapybaraVPN"
VPN_APP="/Applications/Capybara VPN.app"
UNINSTALL_APP="/Applications/Uninstall Capybara VPN.app"

# Function to show dialog
show_dialog() {
    osascript -e "display dialog \"$1\" buttons {\"$2\"} default button 1 with icon caution with title \"Capybara VPN Uninstaller\""
}

show_question() {
    osascript -e "button returned of (display dialog \"$1\" buttons {\"Cancel\", \"$2\"} default button 2 with icon caution with title \"Capybara VPN Uninstaller\")"
}

show_success() {
    osascript -e "display dialog \"$1\" buttons {\"OK\"} default button 1 with icon note with title \"Capybara VPN Uninstaller\""
}

# Welcome screen
RESPONSE=$(osascript -e 'button returned of (display dialog "This will uninstall Capybara VPN from your Mac.\n\nThe following will be removed:\n• Capybara VPN application\n• VPN configurations\n• Connection logs\n• udp2raw binary\n• This uninstaller\n\nDo you want to continue?" buttons {"Cancel", "Uninstall"} default button 2 with icon caution with title "Capybara VPN Uninstaller")' 2>/dev/null)

if [ "$RESPONSE" != "Uninstall" ]; then
    echo "User cancelled"
    exit 0
fi

# Stop VPN if running
osascript -e 'display notification "Stopping VPN connections..." with title "Capybara VPN Uninstaller"'

# Stop udp2raw
sudo killall udp2raw 2>/dev/null || true

# Stop WireGuard
if [ -d "$APP_SUPPORT" ]; then
    for conf in "$APP_SUPPORT"/*_wireguard.conf; do
        if [ -f "$conf" ]; then
            sudo /usr/local/bin/wg-quick down "$conf" 2>/dev/null || true
        fi
    done
fi

osascript -e 'display notification "Removing application..." with title "Capybara VPN Uninstaller"'

# Remove VPN app
if [ -d "$VPN_APP" ]; then
    sudo rm -rf "$VPN_APP"
    echo "✓ Removed Capybara VPN app"
fi

# Remove udp2raw binary
if [ -f "/usr/local/bin/udp2raw" ]; then
    sudo rm -f /usr/local/bin/udp2raw
    echo "✓ Removed udp2raw binary"
fi

# Ask about configurations
KEEP_CONFIGS=$(osascript -e 'button returned of (display dialog "Do you want to remove VPN configurations and logs?\n\nIf you plan to reinstall later, you can keep them." buttons {"Keep Configs", "Remove All"} default button 1 with icon caution with title "Capybara VPN Uninstaller")' 2>/dev/null)

if [ "$KEEP_CONFIGS" = "Remove All" ]; then
    rm -rf "$APP_SUPPORT"
    echo "✓ Removed configurations and logs"
    CONFIG_MSG="All VPN data has been removed."
else
    echo "✓ Kept configurations"
    CONFIG_MSG="VPN configurations were kept in:\n~/Library/Application Support/CapybaraVPN/"
fi

# Remove uninstaller itself
sudo rm -rf "$UNINSTALL_APP"
echo "✓ Removed uninstaller"

# Success message
osascript -e "display dialog \"Capybara VPN has been successfully uninstalled.\n\n$CONFIG_MSG\" buttons {\"OK\"} default button 1 with icon note with title \"Uninstall Complete\"" 2>/dev/null

echo "Uninstall complete!"
exit 0
UNINSTALL_SCRIPT

chmod +x "$MACOS/uninstall"

echo "✅ Created uninstaller script"

# Check if uninstall icon exists
if [ -f "uninstall-icon.png" ]; then
    echo "📸 Creating uninstaller icon..."

    # Create iconset
    ICONSET="UninstallIcon.iconset"
    mkdir -p "$ICONSET"

    # Generate all sizes
    sips -z 16 16     "uninstall-icon.png" --out "$ICONSET/icon_16x16.png"
    sips -z 32 32     "uninstall-icon.png" --out "$ICONSET/icon_16x16@2x.png"
    sips -z 32 32     "uninstall-icon.png" --out "$ICONSET/icon_32x32.png"
    sips -z 64 64     "uninstall-icon.png" --out "$ICONSET/icon_32x32@2x.png"
    sips -z 128 128   "uninstall-icon.png" --out "$ICONSET/icon_128x128.png"
    sips -z 256 256   "uninstall-icon.png" --out "$ICONSET/icon_128x128@2x.png"
    sips -z 256 256   "uninstall-icon.png" --out "$ICONSET/icon_256x256.png"
    sips -z 512 512   "uninstall-icon.png" --out "$ICONSET/icon_256x256@2x.png"
    sips -z 512 512   "uninstall-icon.png" --out "$ICONSET/icon_512x512.png"
    sips -z 1024 1024 "uninstall-icon.png" --out "$ICONSET/icon_512x512@2x.png"

    # Convert to icns
    iconutil -c icns "$ICONSET" -o "$RESOURCES/UninstallIcon.icns"
    rm -rf "$ICONSET"

    echo "✅ Created uninstaller icon"
else
    echo "⚠️  Warning: uninstall-icon.png not found, skipping icon creation"
fi

echo ""
echo "✅ Uninstall app created successfully!"
echo "   Location: $APP_DIR"
echo ""
echo "The uninstaller will be included in the next installer build."
