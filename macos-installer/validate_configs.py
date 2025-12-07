#!/usr/bin/env python3
"""
Pre-distribution validation script for Capybara VPN configs.
Ensures all configurations are accurate before building installers.
"""

import os
import sys
import re
from pathlib import Path

# Expected server configuration
EXPECTED_SERVER_IP = "66.42.119.38"
EXPECTED_UDP2RAW_PASSWORD = "SecureVPN2025Obfuscate"
EXPECTED_SERVER_PUBLIC_KEY = "D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A="

def validate_wireguard_config(config_path):
    """Validate WireGuard configuration file."""
    errors = []

    if not config_path.exists():
        return [f"Config file not found: {config_path}"]

    content = config_path.read_text()

    # Check for required sections
    if '[Interface]' not in content:
        errors.append("Missing [Interface] section")
    if '[Peer]' not in content:
        errors.append("Missing [Peer] section")

    # Check PrivateKey exists
    if not re.search(r'PrivateKey\s*=\s*\S+', content):
        errors.append("Missing PrivateKey")

    # Check Address exists and is in correct subnet
    addr_match = re.search(r'Address\s*=\s*([\d.]+)/\d+', content)
    if not addr_match:
        errors.append("Missing Address")
    else:
        ip = addr_match.group(1)
        if not ip.startswith("10.7.0."):
            errors.append(f"Invalid VPN subnet: {ip} (expected 10.7.0.x)")

    # Check Server PublicKey
    pubkey_match = re.search(r'\[Peer\].*?PublicKey\s*=\s*(\S+)', content, re.DOTALL)
    if not pubkey_match:
        errors.append("Missing server PublicKey")
    elif pubkey_match.group(1) != EXPECTED_SERVER_PUBLIC_KEY:
        errors.append(f"Wrong server PublicKey (expected {EXPECTED_SERVER_PUBLIC_KEY})")

    # Check Endpoint points to localhost (udp2raw)
    endpoint_match = re.search(r'Endpoint\s*=\s*(\S+)', content)
    if not endpoint_match:
        errors.append("Missing Endpoint")
    elif endpoint_match.group(1) != "127.0.0.1:4096":
        errors.append(f"Wrong Endpoint: {endpoint_match.group(1)} (expected 127.0.0.1:4096)")

    # Check for obfuscation setup (PreUp with udp2raw)
    if 'PreUp' in content:
        # Validate PreUp has correct settings
        if EXPECTED_SERVER_IP not in content:
            errors.append(f"PreUp missing server IP: {EXPECTED_SERVER_IP}")
        if EXPECTED_UDP2RAW_PASSWORD not in content:
            errors.append("PreUp missing correct udp2raw password")
        if '--raw-mode faketcp' not in content:
            errors.append("PreUp missing faketcp mode")
    else:
        errors.append("Missing PreUp hook for udp2raw (config won't work with wg-quick)")

    # Check MTU
    if 'MTU = 1280' not in content:
        errors.append("Missing or wrong MTU (should be 1280 for obfuscation)")

    # Check PersistentKeepalive
    if not re.search(r'PersistentKeepalive\s*=\s*\d+', content):
        errors.append("Missing PersistentKeepalive")

    return errors

def validate_launchdaemon(plist_path):
    """Validate LaunchDaemon plist file."""
    errors = []

    if not plist_path.exists():
        return [f"LaunchDaemon not found: {plist_path}"]

    content = plist_path.read_text()

    # Check label
    if 'com.capybara.udp2raw' not in content:
        errors.append("Missing or wrong Label")

    # Check server IP
    if EXPECTED_SERVER_IP not in content:
        errors.append(f"Missing server IP: {EXPECTED_SERVER_IP}")

    # Check password
    if EXPECTED_UDP2RAW_PASSWORD not in content:
        errors.append("Missing or wrong udp2raw password")

    # Check for required flags
    required_flags = ['--raw-mode', 'faketcp', '--cipher-mode', 'xor', '--auth-mode', 'hmac_sha1']
    for flag in required_flags:
        if flag not in content:
            errors.append(f"Missing flag: {flag}")

    # Check localhost endpoint
    if '127.0.0.1:4096' not in content:
        errors.append("Missing localhost:4096 listen address")

    # Check RunAtLoad
    if '<key>RunAtLoad</key>' not in content or '<true/>' not in content:
        errors.append("LaunchDaemon won't run at boot (missing RunAtLoad=true)")

    # Check KeepAlive
    if '<key>KeepAlive</key>' not in content:
        errors.append("LaunchDaemon won't restart on crash (missing KeepAlive)")

    return errors

def validate_user_configs(username, generated_dir):
    """Validate all configs for a user."""
    print(f"\n🔍 Validating configs for user: {username}")
    print("=" * 60)

    all_errors = []

    # Validate WireGuard config
    wg_config = generated_dir / f"{username}_wireguard.conf"
    wg_errors = validate_wireguard_config(wg_config)
    if wg_errors:
        print(f"❌ WireGuard config errors:")
        for error in wg_errors:
            print(f"   • {error}")
        all_errors.extend(wg_errors)
    else:
        print(f"✅ WireGuard config valid")

    # Validate LaunchDaemon
    launchdaemon = generated_dir / "com.capybara.udp2raw.plist"
    ld_errors = validate_launchdaemon(launchdaemon)
    if ld_errors:
        print(f"❌ LaunchDaemon errors:")
        for error in ld_errors:
            print(f"   • {error}")
        all_errors.extend(ld_errors)
    else:
        print(f"✅ LaunchDaemon valid")

    return len(all_errors) == 0

def main():
    script_dir = Path(__file__).parent
    generated_dir = script_dir / "generated_configs"

    if len(sys.argv) > 1:
        # Validate specific user
        username = sys.argv[1]
        if not validate_user_configs(username, generated_dir):
            sys.exit(1)
    else:
        # Validate all users
        project_root = script_dir.parent
        vpn_clients_dir = project_root / "vpn_clients"

        users = [f.stem.replace('_wireguard', '') for f in vpn_clients_dir.glob('*_wireguard.conf')]

        print(f"\n🔍 Validating configs for all users")
        print("=" * 60)

        all_valid = True
        for username in sorted(users):
            if not validate_user_configs(username, generated_dir):
                all_valid = False

        print("\n" + "=" * 60)
        if all_valid:
            print("✅ All configurations valid!")
            print("=" * 60)
        else:
            print("❌ Validation failed - fix errors before distribution!")
            print("=" * 60)
            sys.exit(1)

if __name__ == "__main__":
    main()
