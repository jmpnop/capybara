#!/usr/bin/env python3
"""
Generate properly configured WireGuard configs and LaunchDaemon plist files
with obfuscation settings from templates.
"""

import os
import sys
import re
from pathlib import Path

# Server configuration (from CLAUDE.md)
SERVER_IP = "66.42.119.38"
UDP2RAW_PASSWORD = "SecureVPN2025Obfuscate"

def read_wireguard_config(config_path):
    """Parse existing WireGuard config to extract values."""
    config = {}

    with open(config_path, 'r') as f:
        content = f.read()

    # Extract PrivateKey
    match = re.search(r'PrivateKey\s*=\s*(\S+)', content)
    if match:
        config['CLIENT_PRIVATE_KEY'] = match.group(1)

    # Extract Address (IP)
    match = re.search(r'Address\s*=\s*([\d.]+)/\d+', content)
    if match:
        config['CLIENT_VPN_IP'] = match.group(1)

    # Extract Server PublicKey
    match = re.search(r'PublicKey\s*=\s*(\S+)', content)
    if match:
        config['SERVER_PUBLIC_KEY'] = match.group(1)

    return config

def generate_wireguard_config(username, vpn_clients_dir, templates_dir, output_dir):
    """Generate WireGuard config with obfuscation from template."""

    # Read existing config
    existing_config = vpn_clients_dir / f"{username}_wireguard.conf"
    if not existing_config.exists():
        print(f"❌ ERROR: Config not found: {existing_config}")
        return False

    values = read_wireguard_config(existing_config)

    # Validate required values
    required = ['CLIENT_PRIVATE_KEY', 'CLIENT_VPN_IP', 'SERVER_PUBLIC_KEY']
    missing = [k for k in required if k not in values]
    if missing:
        print(f"❌ ERROR: Missing values in config: {missing}")
        return False

    # Add server values
    values['SERVER_IP'] = SERVER_IP
    values['UDP2RAW_PASSWORD'] = UDP2RAW_PASSWORD

    # Read template
    template_path = templates_dir / "wireguard_template.conf"
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    output = template
    for key, value in values.items():
        output = output.replace(f"{{{{{key}}}}}", value)

    # Verify no placeholders remain
    if '{{' in output:
        remaining = re.findall(r'\{\{([^}]+)\}\}', output)
        print(f"❌ ERROR: Unreplaced placeholders: {remaining}")
        return False

    # Write output
    output_path = output_dir / f"{username}_wireguard.conf"
    with open(output_path, 'w') as f:
        f.write(output)

    print(f"✅ Generated: {output_path.name}")
    return True

def generate_launchdaemon(templates_dir, output_dir):
    """Generate LaunchDaemon plist with server settings."""

    values = {
        'SERVER_IP': SERVER_IP,
        'UDP2RAW_PASSWORD': UDP2RAW_PASSWORD
    }

    # Read template
    template_path = templates_dir / "com.capybara.udp2raw.plist"
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    output = template
    for key, value in values.items():
        output = output.replace(f"{{{{{key}}}}}", value)

    # Verify no placeholders remain
    if '{{' in output:
        remaining = re.findall(r'\{\{([^}]+)\}\}', output)
        print(f"❌ ERROR: Unreplaced placeholders in LaunchDaemon: {remaining}")
        return False

    # Write output
    output_path = output_dir / "com.capybara.udp2raw.plist"
    with open(output_path, 'w') as f:
        f.write(output)

    print(f"✅ Generated: {output_path.name}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_configs.py <username>")
        sys.exit(1)

    username = sys.argv[1]

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    vpn_clients_dir = project_root / "vpn_clients"
    templates_dir = script_dir / "templates"
    output_dir = script_dir / "generated_configs"

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print(f"\n🔧 Generating configs for user: {username}")
    print("=" * 60)

    # Generate WireGuard config
    if not generate_wireguard_config(username, vpn_clients_dir, templates_dir, output_dir):
        sys.exit(1)

    # Generate LaunchDaemon (same for all users, but regenerate for consistency)
    if not generate_launchdaemon(templates_dir, output_dir):
        sys.exit(1)

    print("=" * 60)
    print("✅ All configs generated successfully!\n")

if __name__ == "__main__":
    main()
