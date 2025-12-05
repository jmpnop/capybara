#!/bin/bash
# Create macOS .icns icon from image file
# Usage: ./create_icon.sh input_image.png

set -e

INPUT_IMAGE="$1"
ICONSET_DIR="AppIcon.iconset"
OUTPUT_ICON="AppIcon.icns"

if [ -z "$INPUT_IMAGE" ]; then
    echo "Usage: $0 <input_image.png>"
    exit 1
fi

if [ ! -f "$INPUT_IMAGE" ]; then
    echo "Error: Input image not found: $INPUT_IMAGE"
    exit 1
fi

echo "Creating macOS icon from: $INPUT_IMAGE"

# Create iconset directory
mkdir -p "$ICONSET_DIR"

# Generate all required icon sizes for macOS
# Standard resolutions
sips -z 16 16     "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_16x16.png"
sips -z 32 32     "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_16x16@2x.png"
sips -z 32 32     "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_32x32.png"
sips -z 64 64     "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_32x32@2x.png"
sips -z 128 128   "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_128x128.png"
sips -z 256 256   "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_128x128@2x.png"
sips -z 256 256   "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_256x256.png"
sips -z 512 512   "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_256x256@2x.png"
sips -z 512 512   "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_512x512.png"
sips -z 1024 1024 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_512x512@2x.png"

echo "Generated all icon sizes"

# Convert iconset to icns
iconutil -c icns "$ICONSET_DIR" -o "$OUTPUT_ICON"

echo "✅ Created: $OUTPUT_ICON"

# Clean up
rm -rf "$ICONSET_DIR"

# Move to resources directory
RESOURCES_DIR="payload/Applications/Capybara VPN.app/Contents/Resources"
mkdir -p "$RESOURCES_DIR"
cp "$OUTPUT_ICON" "$RESOURCES_DIR/"

echo "✅ Copied icon to: $RESOURCES_DIR/AppIcon.icns"
echo ""
echo "Icon is ready! Rebuild installers to include the new icon."
