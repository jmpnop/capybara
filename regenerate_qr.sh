#!/bin/bash
# Regenerate all QR codes with username overlay

cd /Users/pasha/PycharmProjects/capybara

echo "=== Deleting old QR code files ==="
rm -f vpn_clients/*_qr.png
echo "✓ Deleted old QR codes"

echo ""
echo "=== Regenerating QR codes for all users ==="

# Get list of users from wireguard configs
for config in vpn_clients/*_wireguard.conf; do
    if [ -f "$config" ]; then
        username=$(basename "$config" _wireguard.conf)
        echo ""
        echo "============================================================"
        echo "Regenerating: $username"
        echo "============================================================"
        python3 capybara.py user add "$username" --description "Regenerated QR" 2>&1 | tail -20
    fi
done

echo ""
echo "============================================================"
echo "✓ All QR codes regenerated with username overlay!"
echo "============================================================"
echo ""
echo "Checking results:"
ls -lh vpn_clients/*_qr.png 2>/dev/null | wc -l | xargs echo "Total QR codes:"
