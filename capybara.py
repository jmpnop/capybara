#!/usr/bin/env python3
"""
Capybara - Censorship-Resistant VPN Infrastructure
Advanced WireGuard VPN management with DPI evasion and obfuscation

Features: udp2raw obfuscation, enterprise monitoring, QR provisioning,
automated backups, real-time analytics, and professional diagnostics.
"""

import sys
import json
import yaml
import paramiko
import click
import qrcode
import base64
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
CONFIG_FILE = Path.home() / '.capybara_config.yaml'
DEFAULT_CONFIG = {
    'server': {
        'host': '66.42.119.38',
        'port': 22,
        'username': 'root',
        'password': 'H7)a4(72PGSnN4Hh',
    },
    'vpn': {
        'interface': 'wg0',
        'config_path': '/etc/wireguard/wg0.conf',
        'network': '10.7.0.0/24',
        'server_ip': '10.7.0.1',
        'next_client_ip': 2,  # Next available IP (10.7.0.2)
    }
}


class SSHConnection:
    """Manage SSH connection to VPN server"""

    def __init__(self, config):
        self.config = config
        self.client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            server_cfg = self.config['server']
            self.client.connect(
                hostname=server_cfg['host'],
                port=server_cfg['port'],
                username=server_cfg['username'],
                password=server_cfg.get('password'),
                key_filename=server_cfg.get('key_file'),
                timeout=10
            )
            return True
        except Exception as e:
            click.echo(f"{Fore.RED}Failed to connect to server: {e}")
            return False

    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()

    def execute(self, command, check_error=True):
        """Execute command on remote server"""
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if check_error and exit_status != 0:
                raise Exception(f"Command failed: {error or output}")

            return output, error, exit_status
        except Exception as e:
            raise Exception(f"Command execution failed: {e}")


class VPNManager:
    """Main VPN management class"""

    def __init__(self, config):
        self.config = config

    def generate_client_keys(self, ssh):
        """Generate new client keys"""
        cmd = "cd /etc/wireguard && wg genkey | tee temp_private.key | wg pubkey"
        output, _, _ = ssh.execute(cmd)
        public_key = output.strip()

        cmd = "cat /etc/wireguard/temp_private.key && rm /etc/wireguard/temp_private.key"
        output, _, _ = ssh.execute(cmd)
        private_key = output.strip()

        return private_key, public_key

    def get_next_ip(self, ssh):
        """Get next available IP address"""
        # Parse current config to find used IPs
        cmd = f"grep 'AllowedIPs' {self.config['vpn']['config_path']} | grep -o '10.7.0.[0-9]*'"
        output, _, status = ssh.execute(cmd, check_error=False)

        used_ips = set()
        if status == 0 and output:
            for ip in output.split('\n'):
                if ip:
                    used_ips.add(int(ip.split('.')[-1]))

        # Find next available IP (starting from .2)
        next_ip = 2
        while next_ip in used_ips:
            next_ip += 1

        if next_ip > 254:
            raise Exception("No available IP addresses in the subnet")

        return f"10.7.0.{next_ip}"

    def generate_ss_password(self, username, ssh=None):
        """Get Shadowsocks password from server config

        Note: Shadowsocks-rust uses a shared password for all users.
        This method fetches the password from the server's configuration.
        """
        if ssh is None:
            # Fallback to deterministic password if SSH not provided (backwards compat)
            salt = b'capybara_ss_salt_2025'
            key = hashlib.pbkdf2_hmac('sha256', username.encode(), salt, 100000, dklen=16)
            return base64.b64encode(key).decode('utf-8')

        try:
            # Fetch password from server config
            output, _, _ = ssh.execute("cat /etc/shadowsocks-rust/config.json")
            config = json.loads(output)
            return config.get('password', 'CapybaraVPN2025!DefaultPassword')
        except Exception:
            # Fallback to default if config can't be read
            return 'CapybaraVPN2025!DefaultPassword'

    def generate_v2ray_uuid(self, username):
        """Generate deterministic V2Ray UUID from username"""
        # Generate UUID v5 from namespace UUID and username
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
        return str(uuid.uuid5(namespace, f'capybara-v2ray-{username}'))

    def create_ss_qr(self, method, password, server, port):
        """Create Shadowsocks QR code"""
        # Format: ss://base64(method:password)@server:port
        credential = f"{method}:{password}"
        encoded = base64.b64encode(credential.encode()).decode()
        ss_url = f"ss://{encoded}@{server}:{port}"
        return ss_url

    def create_v2ray_qr(self, uuid_str, server, port, alterId=0):
        """Create V2Ray VMess QR code with WebSocket transport"""
        # VMess format with WebSocket
        vmess_config = {
            "v": "2",
            "ps": f"Capybara-{server}",
            "add": server,
            "port": str(port),
            "id": uuid_str,
            "aid": str(alterId),
            "net": "ws",
            "type": "none",
            "host": "",
            "path": "/api/v2/download",
            "tls": ""
        }
        json_str = json.dumps(vmess_config)
        encoded = base64.b64encode(json_str.encode()).decode()
        return f"vmess://{encoded}"

    def generate_qr_with_overlay(self, data, username, output_path):
        """Generate QR code with username overlay on capybara background"""
        try:
            # Generate base QR code
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
                box_size=10,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Create QR code image at fixed size
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_fixed_size = 700
            qr_img = qr_img.resize((qr_fixed_size, qr_fixed_size), Image.Resampling.LANCZOS)

            # Define padding
            desired_padding = 50

            # Load capybara background
            capy_path = Path(__file__).parent / 'capy.png'
            if capy_path.exists():
                background = Image.open(capy_path)

                # Get original aspect ratio
                original_aspect = background.width / background.height

                # Calculate required background size
                required_width = qr_fixed_size + (2 * desired_padding)
                required_height = int(required_width / original_aspect)

                # Ensure enough height for QR code
                min_height = qr_fixed_size + (2 * desired_padding)
                if required_height < min_height:
                    required_height = min_height
                    required_width = int(required_height * original_aspect)

                # Resize background
                background = background.resize((required_width, required_height), Image.Resampling.LANCZOS)
                result = background.copy()
            else:
                # No background - create white canvas
                required_width = qr_fixed_size + (2 * desired_padding)
                required_height = required_width
                result = Image.new('RGB', (required_width, required_height), 'white')

            # Paste QR code
            x_pos = desired_padding
            y_pos = desired_padding
            result.paste(qr_img, (x_pos, y_pos))

            # Add username text overlay
            draw = ImageDraw.Draw(result)
            font_size = 60
            font_loaded = False

            # Try different font paths
            font_paths = [
                "/System/Library/Fonts/Courier.ttc",
                "/System/Library/Fonts/Monaco.dfont",
                "/Library/Fonts/Courier New.ttf",
                "/System/Library/Fonts/Supplemental/Courier New.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            ]

            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    font_loaded = True
                    break
                except:
                    continue

            if not font_loaded:
                font = ImageFont.load_default()

            # Center text
            bbox = draw.textbbox((0, 0), username, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (result.width - text_width) // 2
            text_y = (result.height - text_height) // 2

            # Draw text
            draw.text((text_x, text_y), username, fill="black", font=font)

            # Save result
            result.save(str(output_path))
            return True

        except Exception as e:
            click.echo(f"{Fore.YELLOW}⚠ QR overlay failed: {e}, using standard QR")
            # Fallback to standard QR code
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(str(output_path))
            return False

    def add_shadowsocks_user(self, ssh, username, password, port=8388):
        """Add user to Shadowsocks

        Note: Currently uses shared Shadowsocks server with single password.
        For per-user passwords, you would need to run multiple ssserver instances.
        """
        # Shadowsocks-rust uses a shared server configuration
        # Users are not added individually but share the server password
        # The password used in client configs is the server's password

        # This method primarily exists to maintain compatibility with the add_user workflow
        # The actual Shadowsocks server password is configured in /etc/shadowsocks-rust/config.json

        # Return the standard port - all users connect to the same port
        return port

    def add_v2ray_user(self, ssh, username, user_uuid):
        """Add user to V2Ray"""
        # Read current V2Ray config
        output, _, _ = ssh.execute("cat /etc/v2ray/config.json")
        v2ray_config = json.loads(output)

        # Add user to clients
        new_client = {
            "id": user_uuid,
            "alterId": 0,
            "email": f"{username}@capybara"
        }

        if "inbounds" in v2ray_config and len(v2ray_config["inbounds"]) > 0:
            if "settings" not in v2ray_config["inbounds"][0]:
                v2ray_config["inbounds"][0]["settings"] = {}
            if "clients" not in v2ray_config["inbounds"][0]["settings"]:
                v2ray_config["inbounds"][0]["settings"]["clients"] = []

            # Check if user already exists
            existing = False
            for client in v2ray_config["inbounds"][0]["settings"]["clients"]:
                if client.get("email") == f"{username}@capybara":
                    existing = True
                    break

            if not existing:
                v2ray_config["inbounds"][0]["settings"]["clients"].append(new_client)

        # Write updated config
        config_json = json.dumps(v2ray_config, indent=2)
        ssh.execute(f"cat > /etc/v2ray/config.json << 'EOFV2'\n{config_json}\nEOFV2")

        # Restart V2Ray
        ssh.execute("rc-service v2ray restart", check_error=False)

    def remove_v2ray_user(self, ssh, username):
        """Remove user from V2Ray"""
        # Read current V2Ray config
        output, _, _ = ssh.execute("cat /etc/v2ray/config.json")
        v2ray_config = json.loads(output)

        # Remove user from clients
        if "inbounds" in v2ray_config and len(v2ray_config["inbounds"]) > 0:
            if "settings" in v2ray_config["inbounds"][0] and "clients" in v2ray_config["inbounds"][0]["settings"]:
                clients = v2ray_config["inbounds"][0]["settings"]["clients"]

                # Filter out the user
                original_count = len(clients)
                v2ray_config["inbounds"][0]["settings"]["clients"] = [
                    client for client in clients
                    if client.get("email") != f"{username}@capybara"
                ]

                new_count = len(v2ray_config["inbounds"][0]["settings"]["clients"])

                if original_count == new_count:
                    return False  # User not found

                # Write updated config
                config_json = json.dumps(v2ray_config, indent=2)
                ssh.execute(f"cat > /etc/v2ray/config.json << 'EOFV2'\n{config_json}\nEOFV2")

                # Restart V2Ray
                ssh.execute("rc-service v2ray restart", check_error=False)
                return True

        return False

    def list_v2ray_users(self, ssh):
        """List all V2Ray users"""
        try:
            # Read V2Ray config
            output, _, _ = ssh.execute("cat /etc/v2ray/config.json")
            v2ray_config = json.loads(output)

            users = []
            if "inbounds" in v2ray_config and len(v2ray_config["inbounds"]) > 0:
                if "settings" in v2ray_config["inbounds"][0] and "clients" in v2ray_config["inbounds"][0]["settings"]:
                    for client in v2ray_config["inbounds"][0]["settings"]["clients"]:
                        username = client.get("email", "").replace("@capybara", "")
                        users.append({
                            'username': username,
                            'uuid': client.get("id", "N/A"),
                            'alterId': client.get("alterId", 0),
                            'email': client.get("email", "N/A"),
                            'protocol': 'v2ray'
                        })

            return users
        except Exception as e:
            click.echo(f"{Fore.YELLOW}⚠ Could not list V2Ray users: {e}")
            return []

    def add_user(self, username, description=""):
        """Add a new VPN user to all protocols (WireGuard, Shadowsocks, V2Ray)

        Args:
            username: Username for the VPN user
            description: Optional description
        """
        with SSHConnection(self.config) as ssh:
            # Always use all three protocols
            protocols_list = ["wireguard", "shadowsocks", "v2ray"]

            # Timestamp for server-side tracking only (not used in client filenames)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            client_dir = Path.cwd() / 'vpn_clients'
            client_dir.mkdir(exist_ok=True)

            # Get server IP
            server_ip = self.config['server']['host']

            results = {
                'username': username,
                'description': description,
                'protocols': {},
                'qr_codes': {}
            }

            # ========== WireGuard Setup ==========
            if "wireguard" in protocols_list:
                click.echo(f"\n{Fore.CYAN}{'='*60}")
                click.echo(f"{Fore.YELLOW}Setting up WireGuard for '{username}'...")

                # Generate keys
                private_key, public_key = self.generate_client_keys(ssh)

                # Get next available IP
                client_ip = self.get_next_ip(ssh)

                # Save keys to server
                key_prefix = f"/etc/wireguard/clients/{username}_{timestamp}"
                ssh.execute("mkdir -p /etc/wireguard/clients")
                ssh.execute(f"echo '{private_key}' > {key_prefix}_private.key")
                ssh.execute(f"echo '{public_key}' > {key_prefix}_public.key")
                ssh.execute(f"chmod 600 {key_prefix}_*.key")

                # Add peer to server config
                peer_config = f"""
# User: {username} | IP: {client_ip} | Created: {timestamp}
# Description: {description}
[Peer]
PublicKey = {public_key}
AllowedIPs = {client_ip}/32
"""
                cmd = f"cat >> {self.config['vpn']['config_path']} << 'EOFPEER'\n{peer_config}\nEOFPEER"
                ssh.execute(cmd)

                # Reload WireGuard
                ssh.execute(f"wg syncconf {self.config['vpn']['interface']} <(wg-quick strip {self.config['vpn']['interface']})")

                # Generate client config
                server_output, _, _ = ssh.execute(f"cat /etc/wireguard/server_public.key")
                server_pubkey = server_output.strip()

                client_config = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}/24
MTU = 1280
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {server_pubkey}
AllowedIPs = 0.0.0.0/0
Endpoint = 127.0.0.1:4096
PersistentKeepalive = 25
"""

                # Save client config
                config_file = client_dir / f"{username}_wireguard.conf"
                config_file.write_text(client_config)

                # Generate QR code with username overlay
                try:
                    qr_file = client_dir / f"{username}_wireguard_qr.png"
                    self.generate_qr_with_overlay(client_config, username, qr_file)
                    results['qr_codes']['wireguard'] = str(qr_file)

                    click.echo(f"{Fore.GREEN}✓ WireGuard setup complete!")
                    click.echo(f"{Fore.CYAN}  IP Address: {client_ip}")
                    click.echo(f"{Fore.CYAN}  Config: {config_file}")
                    click.echo(f"{Fore.CYAN}  QR Code: {qr_file}")

                except Exception as e:
                    click.echo(f"{Fore.YELLOW}⚠ QR code generation failed: {e}")

                results['protocols']['wireguard'] = {
                    'ip': client_ip,
                    'public_key': public_key,
                    'private_key': private_key,
                    'config_file': str(config_file)
                }

            # ========== Shadowsocks Setup ==========
            if "shadowsocks" in protocols_list:
                click.echo(f"\n{Fore.CYAN}{'='*60}")
                click.echo(f"{Fore.YELLOW}Setting up Shadowsocks for '{username}'...")

                # Get shared password from server config
                ss_password = self.generate_ss_password(username, ssh)
                ss_port = 8388  # Standard port - all users share same server
                ss_method = "chacha20-ietf-poly1305"

                # Note: Shadowsocks uses shared server, no per-user setup needed
                self.add_shadowsocks_user(ssh, username, ss_password, ss_port)

                # Generate Shadowsocks URL
                ss_url = self.create_ss_qr(ss_method, ss_password, server_ip, ss_port)

                # Save Shadowsocks config
                ss_config_content = f"""Shadowsocks Configuration
Username: {username}
Server: {server_ip}
Port: {ss_port}
Password: {ss_password}
Method: {ss_method}

Connection URL:
{ss_url}

Mobile App Setup:
1. Install Shadowsocks client (iOS: Shadowrocket, Android: Shadowsocks)
2. Scan QR code or manually enter details above
3. Connect!
"""
                ss_config_file = client_dir / f"{username}_shadowsocks.txt"
                ss_config_file.write_text(ss_config_content)

                # Generate QR code with username overlay
                try:
                    qr_file = client_dir / f"{username}_shadowsocks_qr.png"
                    self.generate_qr_with_overlay(ss_url, username, qr_file)
                    results['qr_codes']['shadowsocks'] = str(qr_file)

                    click.echo(f"{Fore.GREEN}✓ Shadowsocks setup complete!")
                    click.echo(f"{Fore.CYAN}  Port: {ss_port}")
                    click.echo(f"{Fore.CYAN}  Password: {ss_password}")
                    click.echo(f"{Fore.CYAN}  Config: {ss_config_file}")
                    click.echo(f"{Fore.CYAN}  QR Code: {qr_file}")

                except Exception as e:
                    click.echo(f"{Fore.YELLOW}⚠ QR code generation failed: {e}")

                results['protocols']['shadowsocks'] = {
                    'port': ss_port,
                    'password': ss_password,
                    'method': ss_method,
                    'url': ss_url,
                    'config_file': str(ss_config_file)
                }

            # ========== V2Ray Setup ==========
            if "v2ray" in protocols_list:
                click.echo(f"\n{Fore.CYAN}{'='*60}")
                click.echo(f"{Fore.YELLOW}Setting up V2Ray for '{username}'...")

                v2ray_uuid = self.generate_v2ray_uuid(username)
                v2ray_port = 80

                # Add user to V2Ray
                self.add_v2ray_user(ssh, username, v2ray_uuid)

                # Generate V2Ray VMess URL
                vmess_url = self.create_v2ray_qr(v2ray_uuid, server_ip, v2ray_port)

                # Save V2Ray config
                v2ray_config_content = f"""V2Ray VMess Configuration
Username: {username}
Server: {server_ip}
Port: {v2ray_port}
UUID: {v2ray_uuid}
AlterID: 0
Network: ws (WebSocket)
Path: /api/v2/download
Type: none

Connection URL:
{vmess_url}

Mobile App Setup:
1. Install V2Ray client (iOS: Shadowrocket/Kitsunebi, Android: v2rayNG)
2. Scan QR code or manually enter details above
3. Connect!

Note: Uses WebSocket on port 80 for mobile network compatibility
"""
                v2ray_config_file = client_dir / f"{username}_v2ray.txt"
                v2ray_config_file.write_text(v2ray_config_content)

                # Generate QR code with username overlay
                try:
                    qr_file = client_dir / f"{username}_v2ray_qr.png"
                    self.generate_qr_with_overlay(vmess_url, username, qr_file)
                    results['qr_codes']['v2ray'] = str(qr_file)

                    click.echo(f"{Fore.GREEN}✓ V2Ray setup complete!")
                    click.echo(f"{Fore.CYAN}  Port: {v2ray_port}")
                    click.echo(f"{Fore.CYAN}  UUID: {v2ray_uuid}")
                    click.echo(f"{Fore.CYAN}  Config: {v2ray_config_file}")
                    click.echo(f"{Fore.CYAN}  QR Code: {qr_file}")

                except Exception as e:
                    click.echo(f"{Fore.YELLOW}⚠ QR code generation failed: {e}")

                results['protocols']['v2ray'] = {
                    'port': v2ray_port,
                    'uuid': v2ray_uuid,
                    'url': vmess_url,
                    'config_file': str(v2ray_config_file)
                }

            click.echo(f"\n{Fore.CYAN}{'='*60}")
            click.echo(f"{Fore.GREEN}✓ User '{username}' added to {len(protocols_list)} protocol(s)!")
            click.echo(f"{Fore.CYAN}{'='*60}\n")

            return results

    def remove_user(self, identifier):
        """Remove a user by username or IP from all protocols (WireGuard and V2Ray)

        Note: Shadowsocks uses a shared password model and does not support per-user removal.
        """
        with SSHConnection(self.config) as ssh:
            removed_from = []

            # ========== Remove from WireGuard ==========
            # Find the user's peer section
            cmd = f"cat {self.config['vpn']['config_path']}"
            config_content, _, _ = ssh.execute(cmd)

            # Parse config to find peer
            lines = config_content.split('\n')
            peer_start = None
            peer_end = None
            found_wg = False

            for i, line in enumerate(lines):
                if f"User: {identifier}" in line or f"IP: {identifier}" in line:
                    # Find start of this peer section (look backwards for [Peer])
                    for j in range(i, -1, -1):
                        if '[Peer]' in lines[j]:
                            peer_start = j - 1  # Include comment line before [Peer]
                            break
                    # Find end of this peer section
                    for j in range(i + 1, len(lines)):
                        if '[Peer]' in lines[j] or '[Interface]' in lines[j]:
                            peer_end = j
                            break
                    if peer_end is None:
                        peer_end = len(lines)
                    found_wg = True
                    break

            if found_wg:
                # Remove the peer section
                new_config = '\n'.join(lines[:peer_start] + lines[peer_end:])

                # Backup current config
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                ssh.execute(f"cp {self.config['vpn']['config_path']} {self.config['vpn']['config_path']}.backup_{timestamp}")

                # Write new config
                cmd = f"cat > {self.config['vpn']['config_path']} << 'EOFCONFIG'\n{new_config}\nEOFCONFIG"
                ssh.execute(cmd)

                # Reload WireGuard
                ssh.execute(f"wg syncconf {self.config['vpn']['interface']} <(wg-quick strip {self.config['vpn']['interface']})")

                removed_from.append('WireGuard')

            # ========== Remove from V2Ray ==========
            v2ray_removed = self.remove_v2ray_user(ssh, identifier)
            if v2ray_removed:
                removed_from.append('V2Ray')

            # ========== Report Results ==========
            if removed_from:
                protocols_str = ' and '.join(removed_from)
                click.echo(f"{Fore.GREEN}✓ User '{identifier}' removed from: {protocols_str}")
                if 'WireGuard' not in removed_from:
                    click.echo(f"{Fore.YELLOW}  Note: User not found in WireGuard")
                if 'V2Ray' not in removed_from:
                    click.echo(f"{Fore.YELLOW}  Note: User not found in V2Ray")
                click.echo(f"{Fore.CYAN}  Note: Shadowsocks uses shared credentials - no per-user removal available")
                return True
            else:
                click.echo(f"{Fore.RED}User '{identifier}' not found in any protocol")
                return False

    def list_users(self):
        """List all VPN users from all protocols (WireGuard and V2Ray)

        Note: Shadowsocks uses shared credentials and does not support per-user listing.
        """
        with SSHConnection(self.config) as ssh:
            all_users = []

            # ========== WireGuard Users ==========
            # Get WireGuard status
            wg_output, _, _ = ssh.execute(f"wg show {self.config['vpn']['interface']}")

            # Get config file for metadata
            config_output, _, _ = ssh.execute(f"cat {self.config['vpn']['config_path']}")

            # Parse users from config
            wg_users = []
            lines = config_output.split('\n')

            current_user = {}
            for line in lines:
                line = line.strip()
                if line.startswith('# User:'):
                    # Parse: # User: username | IP: 10.7.0.2 | Created: timestamp
                    parts = line.replace('# User:', '').split('|')
                    current_user = {
                        'username': parts[0].strip(),
                        'ip': parts[1].replace('IP:', '').strip() if len(parts) > 1 else 'N/A',
                        'created': parts[2].replace('Created:', '').strip() if len(parts) > 2 else 'N/A',
                        'description': '',
                        'status': 'Active',
                        'protocol': 'wireguard'
                    }
                elif line.startswith('# Description:') and current_user:
                    current_user['description'] = line.replace('# Description:', '').strip()
                elif line.startswith('PublicKey =') and current_user:
                    current_user['public_key'] = line.replace('PublicKey =', '').strip()
                elif line.startswith('AllowedIPs =') and current_user:
                    current_user['allowed_ips'] = line.replace('AllowedIPs =', '').strip()
                    wg_users.append(current_user.copy())
                    current_user = {}

            # Enrich with connection data from wg show
            peer_data = {}
            current_peer = None
            for line in wg_output.split('\n'):
                if line.startswith('peer:'):
                    current_peer = line.split(':')[1].strip()
                    peer_data[current_peer] = {}
                elif current_peer and ':' in line:
                    key, value = line.split(':', 1)
                    peer_data[current_peer][key.strip()] = value.strip()

            # Add connection info to WireGuard users
            for user in wg_users:
                if 'public_key' in user and user['public_key'] in peer_data:
                    data = peer_data[user['public_key']]
                    user['endpoint'] = data.get('endpoint', 'Never connected')
                    user['last_handshake'] = data.get('latest handshake', 'Never')
                    user['transfer_rx'] = data.get('transfer', 'N/A').split(',')[0] if 'transfer' in data else '0 B'
                    user['transfer_tx'] = data.get('transfer', 'N/A').split(',')[1] if 'transfer' in data else '0 B'
                else:
                    user['endpoint'] = 'Never connected'
                    user['last_handshake'] = 'Never'
                    user['transfer_rx'] = '0 B'
                    user['transfer_tx'] = '0 B'

            all_users.extend(wg_users)

            # ========== V2Ray Users ==========
            v2ray_users = self.list_v2ray_users(ssh)
            # Add default fields for consistency with WireGuard users
            for user in v2ray_users:
                user['ip'] = 'N/A (proxy)'
                user['created'] = 'N/A'
                user['description'] = ''
                user['status'] = 'Active'
                user['endpoint'] = 'N/A (no connection tracking)'
                user['last_handshake'] = 'N/A'
                user['transfer_rx'] = 'N/A'
                user['transfer_tx'] = 'N/A'

            all_users.extend(v2ray_users)

            return all_users

    def get_stats(self):
        """Get VPN server statistics"""
        with SSHConnection(self.config) as ssh:
            stats = {}

            # WireGuard interface stats
            wg_output, _, _ = ssh.execute(f"wg show {self.config['vpn']['interface']}")
            stats['wg_status'] = wg_output

            # Count peers
            peer_count = wg_output.count('peer:')
            stats['total_users'] = peer_count

            # udp2raw status
            udp_output, _, status = ssh.execute("ps aux | grep udp2raw | grep -v grep", check_error=False)
            stats['udp2raw_running'] = status == 0

            # Server uptime (BusyBox compatible)
            uptime_output, _, _ = ssh.execute("uptime")
            stats['uptime'] = uptime_output.strip()

            # Network statistics
            net_output, _, _ = ssh.execute(f"ip -s link show {self.config['vpn']['interface']}")
            stats['interface_stats'] = net_output

            # System resources
            mem_output, _, _ = ssh.execute("free -h | grep Mem")
            stats['memory'] = mem_output

            cpu_output, _, _ = ssh.execute("top -bn1 | grep 'Cpu(s)' | head -1")
            stats['cpu'] = cpu_output

            # Connection count
            conn_output, _, _ = ssh.execute(f"wg show {self.config['vpn']['interface']} endpoints | wc -l")
            stats['active_connections'] = int(conn_output.strip()) if conn_output.strip().isdigit() else 0

            return stats

    def block_user(self, identifier):
        """Block a user (remove from active config but keep backup)"""
        with SSHConnection(self.config) as ssh:
            # Similar to remove but we keep the config commented out
            cmd = f"cat {self.config['vpn']['config_path']}"
            config_content, _, _ = ssh.execute(cmd)

            lines = config_content.split('\n')
            found = False
            new_lines = []

            in_target_peer = False
            for line in lines:
                if f"User: {identifier}" in line or f"IP: {identifier}" in line:
                    in_target_peer = True
                    found = True
                    new_lines.append(f"# BLOCKED: {line}")
                elif in_target_peer:
                    if line.startswith('[Peer]') or line.startswith('[Interface]'):
                        in_target_peer = False
                        new_lines.append(line)
                    else:
                        new_lines.append(f"# {line}" if line and not line.startswith('#') else line)
                else:
                    new_lines.append(line)

            if not found:
                click.echo(f"{Fore.RED}User '{identifier}' not found")
                return False

            # Write new config
            new_config = '\n'.join(new_lines)
            cmd = f"cat > {self.config['vpn']['config_path']} << 'EOFCONFIG'\n{new_config}\nEOFCONFIG"
            ssh.execute(cmd)

            # Reload WireGuard
            ssh.execute(f"wg syncconf {self.config['vpn']['interface']} <(wg-quick strip {self.config['vpn']['interface']})")

            click.echo(f"{Fore.GREEN}✓ User '{identifier}' blocked successfully")
            return True

    def block_resource(self, resource, resource_type='domain'):
        """Block a domain or IP address"""
        with SSHConnection(self.config) as ssh:
            if resource_type == 'domain':
                # Use iptables with string matching for domain blocking
                cmd = f"iptables -I FORWARD -i {self.config['vpn']['interface']} -m string --string '{resource}' --algo bm -j REJECT"
            else:  # IP
                cmd = f"iptables -I FORWARD -i {self.config['vpn']['interface']} -d {resource} -j REJECT"

            ssh.execute(cmd)

            # Save iptables rules
            ssh.execute("rc-service iptables save")

            # Log the block
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp} | BLOCK | {resource_type} | {resource}\n"
            ssh.execute(f"echo '{log_entry}' >> /var/log/vpn_blocks.log")

            click.echo(f"{Fore.GREEN}✓ Blocked {resource_type}: {resource}")
            return True

    def unblock_resource(self, resource, resource_type='domain'):
        """Unblock a domain or IP address"""
        with SSHConnection(self.config) as ssh:
            if resource_type == 'domain':
                cmd = f"iptables -D FORWARD -i {self.config['vpn']['interface']} -m string --string '{resource}' --algo bm -j REJECT"
            else:  # IP
                cmd = f"iptables -D FORWARD -i {self.config['vpn']['interface']} -d {resource} -j REJECT"

            ssh.execute(cmd, check_error=False)

            # Save iptables rules
            ssh.execute("rc-service iptables save")

            # Log the unblock
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp} | UNBLOCK | {resource_type} | {resource}\n"
            ssh.execute(f"echo '{log_entry}' >> /var/log/vpn_blocks.log")

            click.echo(f"{Fore.GREEN}✓ Unblocked {resource_type}: {resource}")
            return True

    def list_blocked_resources(self):
        """List all blocked resources"""
        with SSHConnection(self.config) as ssh:
            # Get iptables rules
            cmd = f"iptables -L FORWARD -n --line-numbers | grep {self.config['vpn']['interface']}"
            output, _, status = ssh.execute(cmd, check_error=False)

            if status != 0 or not output:
                return []

            blocks = []
            for line in output.split('\n'):
                if 'REJECT' in line:
                    blocks.append(line)

            return blocks

    def stop_server(self):
        """Stop WireGuard server"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.YELLOW}Stopping WireGuard...")
            ssh.execute(f"wg-quick down {self.config['vpn']['interface']}")
            click.echo(f"{Fore.GREEN}✓ WireGuard stopped successfully")

    def start_server(self):
        """Start WireGuard server"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.YELLOW}Starting WireGuard...")
            ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
            click.echo(f"{Fore.GREEN}✓ WireGuard started successfully")

    def restart_server(self):
        """Restart WireGuard server"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.YELLOW}Restarting WireGuard...")
            ssh.execute(f"wg-quick down {self.config['vpn']['interface']}")
            ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
            click.echo(f"{Fore.GREEN}✓ WireGuard restarted successfully")

    # ===== LOGS MANAGEMENT =====
    def view_logs(self, service='all', lines=50, follow=False):
        """View server logs"""
        with SSHConnection(self.config) as ssh:
            if service == 'wireguard' or service == 'all':
                click.echo(f"{Fore.CYAN}=== WireGuard Logs ===")
                cmd = f"journalctl -u wg-quick@{self.config['vpn']['interface']} -n {lines} --no-pager"
                output, _, status = ssh.execute(cmd, check_error=False)
                if status == 0:
                    click.echo(output if output else "No logs found")
                else:
                    click.echo(f"{Fore.YELLOW}WireGuard logs not available via journalctl")
                click.echo()

            if service == 'udp2raw' or service == 'all':
                click.echo(f"{Fore.CYAN}=== udp2raw Logs ===")
                cmd = f"tail -n {lines} /var/log/udp2raw.log 2>/dev/null || echo 'No udp2raw logs found'"
                output, _, _ = ssh.execute(cmd, check_error=False)
                click.echo(output if output else "No logs found")
                click.echo()

            if service == 'shadowsocks' or service == 'all':
                click.echo(f"{Fore.CYAN}=== Shadowsocks Logs ===")
                # Try multiple log locations (systemd journal, syslog, or dedicated log file)
                cmd = f"""
                if [ -f /var/log/shadowsocks.log ]; then
                    tail -n {lines} /var/log/shadowsocks.log
                elif command -v journalctl >/dev/null 2>&1; then
                    journalctl -u shadowsocks* -n {lines} --no-pager 2>/dev/null || \
                    journalctl -u ss-server -n {lines} --no-pager 2>/dev/null || \
                    echo "No Shadowsocks systemd logs found"
                else
                    grep -i shadowsocks /var/log/messages 2>/dev/null | tail -n {lines} || \
                    echo "No Shadowsocks logs found"
                fi
                """
                output, _, _ = ssh.execute(cmd, check_error=False)
                click.echo(output if output else "No logs found")
                click.echo()

            if service == 'v2ray' or service == 'all':
                click.echo(f"{Fore.CYAN}=== V2Ray Access Logs ===")
                cmd = f"tail -n {lines} /var/log/v2ray/access.log 2>/dev/null || echo 'No V2Ray access logs found'"
                output, _, _ = ssh.execute(cmd, check_error=False)
                click.echo(output if output else "No logs found")
                click.echo()

                click.echo(f"{Fore.CYAN}=== V2Ray Error Logs ===")
                cmd = f"tail -n {lines} /var/log/v2ray/error.log 2>/dev/null || echo 'No V2Ray error logs found'"
                output, _, _ = ssh.execute(cmd, check_error=False)
                click.echo(output if output else "No logs found")
                click.echo()

            if service == 'system' or service == 'all':
                click.echo(f"{Fore.CYAN}=== System Logs (relevant) ===")
                cmd = f"dmesg | grep -i 'wireguard\\|udp2raw\\|wg0\\|shadowsocks\\|v2ray' | tail -n {lines}"
                output, _, _ = ssh.execute(cmd, check_error=False)
                click.echo(output if output else "No relevant system logs")

    def tail_logs(self, service='udp2raw'):
        """Follow logs in real-time"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.CYAN}Following {service} logs (Ctrl+C to stop)...")
            click.echo()

            if service == 'udp2raw':
                cmd = "tail -f /var/log/udp2raw.log"
            elif service == 'wireguard':
                cmd = f"journalctl -u wg-quick@{self.config['vpn']['interface']} -f"
            elif service == 'shadowsocks':
                # Try multiple locations for Shadowsocks logs
                cmd = """
                if [ -f /var/log/shadowsocks.log ]; then
                    tail -f /var/log/shadowsocks.log
                elif command -v journalctl >/dev/null 2>&1; then
                    journalctl -u shadowsocks* -f 2>/dev/null || journalctl -u ss-server -f 2>/dev/null
                else
                    tail -f /var/log/messages | grep -i shadowsocks
                fi
                """
            elif service == 'v2ray':
                # Follow both access and error logs
                cmd = "tail -f /var/log/v2ray/access.log /var/log/v2ray/error.log"
            else:
                cmd = "dmesg -w"

            # For tail -f, we need to stream output
            stdin, stdout, stderr = ssh.client.exec_command(cmd)
            try:
                for line in iter(stdout.readline, ""):
                    click.echo(line.rstrip())
            except KeyboardInterrupt:
                click.echo(f"\n{Fore.GREEN}Stopped following logs")

    # ===== CONNECTION MANAGEMENT =====
    def kick_user(self, identifier):
        """Disconnect a user immediately"""
        with SSHConnection(self.config) as ssh:
            # Find user's public key
            users = self.list_users()
            target_user = None

            for user in users:
                if user.get('username') == identifier or user.get('ip') == identifier:
                    target_user = user
                    break

            if not target_user:
                raise Exception(f"User '{identifier}' not found")

            pubkey = target_user.get('public_key')
            if not pubkey:
                raise Exception("Could not find user's public key")

            # Remove peer temporarily (will reconnect on next handshake attempt)
            cmd = f"wg set {self.config['vpn']['interface']} peer {pubkey} remove"
            ssh.execute(cmd, check_error=False)

            # Block temporarily in iptables
            user_ip = target_user.get('ip', '').split('/')[0]
            if user_ip:
                cmd = f"iptables -I INPUT -s {user_ip} -j DROP"
                ssh.execute(cmd, check_error=False)

                # Remove block after 5 seconds (allows reconnect)
                cmd = f"sleep 5 && iptables -D INPUT -s {user_ip} -j DROP"
                ssh.execute(cmd, check_error=False)

            click.echo(f"{Fore.GREEN}✓ User '{identifier}' disconnected")
            return True

    def kick_all_users(self):
        """Disconnect all users"""
        with SSHConnection(self.config) as ssh:
            # Get all peers
            output, _, _ = ssh.execute(f"wg show {self.config['vpn']['interface']} peers")
            peers = output.strip().split('\n') if output.strip() else []

            count = 0
            for peer in peers:
                if peer:
                    ssh.execute(f"wg set {self.config['vpn']['interface']} peer {peer} remove", check_error=False)
                    count += 1

            # Reload config to restore peers
            ssh.execute(f"wg syncconf {self.config['vpn']['interface']} <(wg-quick strip {self.config['vpn']['interface']})")

            click.echo(f"{Fore.GREEN}✓ Disconnected {count} user(s)")
            return count

    # ===== SERVICE MANAGEMENT =====
    def restart_service(self, service):
        """Restart individual service"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.YELLOW}Restarting {service}...")

            if service == 'wireguard':
                ssh.execute(f"wg-quick down {self.config['vpn']['interface']}")
                ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
            elif service == 'udp2raw':
                # Kill existing udp2raw
                ssh.execute("killall udp2raw || true")
                # Start it again (from wg config PreUp)
                ssh.execute(f"wg-quick down {self.config['vpn']['interface']}")
                ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
            elif service == 'shadowsocks':
                ssh.execute("rc-service shadowsocks-rust restart")
            elif service == 'v2ray':
                ssh.execute("rc-service v2ray restart")
            elif service == 'firewall':
                ssh.execute("rc-service iptables restart")
            else:
                raise Exception(f"Unknown service: {service}")

            click.echo(f"{Fore.GREEN}✓ {service} restarted successfully")

    def service_status(self):
        """Get status of all services"""
        with SSHConnection(self.config) as ssh:
            status = {}

            # WireGuard status
            output, _, code = ssh.execute(f"wg show {self.config['vpn']['interface']}", check_error=False)
            status['wireguard'] = 'running' if code == 0 and output else 'stopped'

            # udp2raw status
            output, _, code = ssh.execute("ps aux | grep '[u]dp2raw'", check_error=False)
            status['udp2raw'] = 'running' if code == 0 and output else 'stopped'

            # Shadowsocks status
            output, _, code = ssh.execute("rc-service shadowsocks-rust status", check_error=False)
            status['shadowsocks'] = 'running' if code == 0 else 'stopped'

            # V2Ray status
            output, _, code = ssh.execute("rc-service v2ray status", check_error=False)
            status['v2ray'] = 'running' if code == 0 else 'stopped'

            # Firewall status
            output, _, code = ssh.execute("rc-service iptables status", check_error=False)
            status['firewall'] = 'running' if code == 0 else 'stopped'

            return status

    def get_protocol_configs(self):
        """Get configuration details for all protocols"""
        with SSHConnection(self.config) as ssh:
            configs = {}

            # ========== WireGuard Configuration ==========
            try:
                # Get WireGuard listen port
                wg_config, _, _ = ssh.execute(f"cat {self.config['vpn']['config_path']}")
                wg_port = "51820"  # Default
                for line in wg_config.split('\n'):
                    if 'ListenPort' in line:
                        wg_port = line.split('=')[1].strip()
                        break

                # Get udp2raw port from PreUp command
                udp_port = "443"  # Default
                for line in wg_config.split('\n'):
                    if 'PreUp' in line and 'udp2raw' in line and '-l' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == '-l' and i + 1 < len(parts):
                                addr_port = parts[i + 1]
                                if ':' in addr_port:
                                    udp_port = addr_port.split(':')[1]
                                break
                        break

                configs['wireguard'] = {
                    'interface': self.config['vpn']['interface'],
                    'port': wg_port,
                    'obfuscation_port': udp_port,
                    'network': self.config['vpn']['network']
                }
            except Exception as e:
                configs['wireguard'] = {'error': str(e)}

            # ========== Shadowsocks Configuration ==========
            try:
                ss_config, _, _ = ssh.execute("cat /etc/shadowsocks-rust/config.json")
                ss_data = json.loads(ss_config)

                configs['shadowsocks'] = {
                    'port': ss_data.get('server_port', 'N/A'),
                    'method': ss_data.get('method', 'N/A'),
                    'mode': ss_data.get('mode', 'N/A')
                }
            except Exception as e:
                configs['shadowsocks'] = {'error': str(e)}

            # ========== V2Ray Configuration ==========
            try:
                v2_config, _, _ = ssh.execute("cat /etc/v2ray/config.json")
                v2_data = json.loads(v2_config)

                if 'inbounds' in v2_data and len(v2_data['inbounds']) > 0:
                    inbound = v2_data['inbounds'][0]
                    ws_path = 'N/A'
                    transport = 'N/A'

                    if 'streamSettings' in inbound:
                        stream = inbound['streamSettings']
                        transport = stream.get('network', 'N/A')
                        if 'wsSettings' in stream:
                            ws_path = stream['wsSettings'].get('path', 'N/A')

                    # Count users
                    user_count = 0
                    if 'settings' in inbound and 'clients' in inbound['settings']:
                        user_count = len(inbound['settings']['clients'])

                    configs['v2ray'] = {
                        'port': inbound.get('port', 'N/A'),
                        'protocol': inbound.get('protocol', 'N/A'),
                        'transport': transport,
                        'ws_path': ws_path,
                        'users': user_count
                    }
                else:
                    configs['v2ray'] = {'error': 'No inbounds configured'}
            except Exception as e:
                configs['v2ray'] = {'error': str(e)}

            return configs

    # ===== BACKUP & RESTORE =====
    def create_backup(self, name=None):
        """Create backup of VPN configuration"""
        with SSHConnection(self.config) as ssh:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = name or f"backup_{timestamp}"
            backup_dir = f"/root/vpn_backups/{backup_name}"

            click.echo(f"{Fore.YELLOW}Creating backup '{backup_name}'...")

            # Create backup directory
            ssh.execute(f"mkdir -p {backup_dir}")

            # Backup WireGuard config
            ssh.execute(f"cp {self.config['vpn']['config_path']} {backup_dir}/wg0.conf")

            # Backup keys
            ssh.execute(f"cp -r /etc/wireguard/*.key {backup_dir}/ 2>/dev/null || true")
            ssh.execute(f"cp -r /etc/wireguard/clients {backup_dir}/ 2>/dev/null || true")

            # Backup Shadowsocks config
            ssh.execute(f"cp /etc/shadowsocks-rust/config.json {backup_dir}/shadowsocks-config.json 2>/dev/null || true")

            # Backup V2Ray config
            ssh.execute(f"cp /etc/v2ray/config.json {backup_dir}/v2ray-config.json 2>/dev/null || true")

            # Backup iptables rules
            ssh.execute(f"iptables-save > {backup_dir}/iptables.rules")

            # Backup awall config
            ssh.execute(f"cp -r /etc/awall {backup_dir}/ 2>/dev/null || true")

            # Create metadata
            metadata = {
                'name': backup_name,
                'timestamp': timestamp,
                'server': self.config['server']['host'],
                'interface': self.config['vpn']['interface']
            }
            ssh.execute(f"echo '{json.dumps(metadata)}' > {backup_dir}/metadata.json")

            # Create tarball
            ssh.execute(f"cd /root/vpn_backups && tar -czf {backup_name}.tar.gz {backup_name}")
            ssh.execute(f"rm -rf {backup_dir}")

            click.echo(f"{Fore.GREEN}✓ Backup created: {backup_name}.tar.gz")
            return backup_name

    def list_backups(self):
        """List all available backups"""
        with SSHConnection(self.config) as ssh:
            ssh.execute("mkdir -p /root/vpn_backups")
            output, _, _ = ssh.execute("ls -lh /root/vpn_backups/*.tar.gz 2>/dev/null || echo ''")

            if not output:
                return []

            backups = []
            for line in output.split('\n'):
                if '.tar.gz' in line:
                    parts = line.split()
                    if len(parts) >= 9:
                        backups.append({
                            'size': parts[4],
                            'date': f"{parts[5]} {parts[6]} {parts[7]}",
                            'name': parts[8].replace('/root/vpn_backups/', '').replace('.tar.gz', '')
                        })

            return backups

    def restore_backup(self, backup_name):
        """Restore from backup"""
        with SSHConnection(self.config) as ssh:
            backup_file = f"/root/vpn_backups/{backup_name}.tar.gz"

            # Check if backup exists
            _, _, code = ssh.execute(f"test -f {backup_file}", check_error=False)
            if code != 0:
                raise Exception(f"Backup '{backup_name}' not found")

            click.echo(f"{Fore.YELLOW}Restoring from backup '{backup_name}'...")

            # Stop services
            ssh.execute(f"wg-quick down {self.config['vpn']['interface']} || true")
            ssh.execute("rc-service shadowsocks-rust stop || true", check_error=False)
            ssh.execute("rc-service v2ray stop || true", check_error=False)

            # Extract backup
            ssh.execute(f"cd /root/vpn_backups && tar -xzf {backup_name}.tar.gz")

            # Restore WireGuard config
            ssh.execute(f"cp /root/vpn_backups/{backup_name}/wg0.conf {self.config['vpn']['config_path']}")

            # Restore keys
            ssh.execute(f"cp /root/vpn_backups/{backup_name}/*.key /etc/wireguard/ 2>/dev/null || true")
            ssh.execute(f"cp -r /root/vpn_backups/{backup_name}/clients /etc/wireguard/ 2>/dev/null || true")

            # Restore Shadowsocks config
            ssh.execute(f"cp /root/vpn_backups/{backup_name}/shadowsocks-config.json /etc/shadowsocks-rust/config.json 2>/dev/null || true")

            # Restore V2Ray config
            ssh.execute(f"cp /root/vpn_backups/{backup_name}/v2ray-config.json /etc/v2ray/config.json 2>/dev/null || true")

            # Restore iptables
            ssh.execute(f"iptables-restore < /root/vpn_backups/{backup_name}/iptables.rules 2>/dev/null || true")

            # Cleanup
            ssh.execute(f"rm -rf /root/vpn_backups/{backup_name}")

            # Restart services
            ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
            ssh.execute("rc-service shadowsocks-rust start || true", check_error=False)
            ssh.execute("rc-service v2ray start || true", check_error=False)

            click.echo(f"{Fore.GREEN}✓ Backup restored successfully")

    # ===== NETWORK DIAGNOSTICS =====
    def ping_user(self, identifier):
        """Ping a user's VPN IP"""
        with SSHConnection(self.config) as ssh:
            users = self.list_users()
            target_ip = None

            # Find IP
            for user in users:
                if user.get('username') == identifier:
                    target_ip = user.get('ip', '').split('/')[0]
                    break

            if not target_ip:
                # Maybe it's already an IP
                if identifier.startswith('10.7.0.'):
                    target_ip = identifier
                else:
                    raise Exception(f"User '{identifier}' not found")

            click.echo(f"{Fore.CYAN}Pinging {target_ip}...")
            output, _, _ = ssh.execute(f"ping -c 4 {target_ip}")
            click.echo(output)

    def check_ports(self):
        """Show listening ports"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.CYAN}Listening Ports:")
            output, _, _ = ssh.execute("netstat -tulpn | grep -E 'LISTEN|udp'")
            click.echo(output)

    def check_handshake(self, identifier):
        """Check handshake status for a user"""
        with SSHConnection(self.config) as ssh:
            users = self.list_users()

            for user in users:
                if user.get('username') == identifier or user.get('ip') == identifier:
                    click.echo(f"{Fore.CYAN}Handshake Info for {user.get('username')}:")
                    click.echo(f"Last Handshake: {user.get('last_handshake', 'Never')}")
                    click.echo(f"Endpoint: {user.get('endpoint', 'Never connected')}")
                    click.echo(f"Transfer RX: {user.get('transfer_rx', '0 B')}")
                    click.echo(f"Transfer TX: {user.get('transfer_tx', '0 B')}")
                    return

            raise Exception(f"User '{identifier}' not found")

    # ===== SYSTEM HEALTH =====
    def get_health(self):
        """Get system health metrics"""
        with SSHConnection(self.config) as ssh:
            health = {}

            # CPU
            output, _, _ = ssh.execute("top -bn1 | grep 'Cpu(s)' | head -1")
            health['cpu'] = output.strip()

            # Memory
            output, _, _ = ssh.execute("free -h | grep Mem")
            health['memory'] = output.strip()

            # Disk
            output, _, _ = ssh.execute("df -h / | tail -1")
            health['disk'] = output.strip()

            # Load average
            output, _, _ = ssh.execute("uptime")
            health['uptime'] = output.strip()

            # Network traffic on wg interface
            output, _, _ = ssh.execute(f"ip -s link show {self.config['vpn']['interface']} 2>/dev/null || echo 'Interface not found'")
            health['network'] = output.strip()

            return health

    # ===== REPORTS & ANALYTICS =====
    def generate_report(self, report_type='daily'):
        """Generate usage report"""
        with SSHConnection(self.config) as ssh:
            users = self.list_users()
            stats = self.get_stats()

            report = {
                'type': report_type,
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total_users': len(users),
                    'active_users': sum(1 for u in users if u.get('endpoint') != 'Never connected'),
                    'server_uptime': stats.get('uptime', 'Unknown'),
                },
                'users': []
            }

            for user in users:
                report['users'].append({
                    'username': user.get('username', 'N/A'),
                    'ip': user.get('ip', 'N/A'),
                    'status': 'Active' if user.get('endpoint') != 'Never connected' else 'Inactive',
                    'last_seen': user.get('last_handshake', 'Never'),
                    'data_received': user.get('transfer_rx', '0 B'),
                    'data_sent': user.get('transfer_tx', '0 B'),
                })

            return report


def load_config():
    """Load configuration from file"""
    if not CONFIG_FILE.exists():
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        click.echo(f"{Fore.YELLOW}Created default config at {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


# CLI Commands
@click.group()
@click.version_option(version='3.0.0')
def cli():
    """
    🦫 Capybara v3.0 - Multi-Protocol Censorship-Resistant VPN

    Supports WireGuard, Shadowsocks, and V2Ray with unified management.

    Advanced WireGuard VPN with DPI evasion for restricted networks.

    🛡️  Anti-Censorship:
      • udp2raw obfuscation (disguises VPN as HTTPS traffic)
      • Port 443 operation (bypasses DPI in China, Russia, Iran)
      • Fake TCP packets (defeats protocol fingerprinting)

    🎛️  Enterprise Management:
      • Real-time monitoring & analytics
      • QR code provisioning for mobile
      • Zero-downtime service restarts
      • Automated backup & disaster recovery
      • Multi-format reports (text/JSON/CSV)

    🔧 Professional Operations:
      • Connection control (instant kick)
      • Network diagnostics (ping, ports, handshake)
      • System health monitoring
      • Detailed logging with filtering

    Quick Start:
      capybara.py user add alice              Add user (auto QR code)
      capybara.py connection list             View active connections
      capybara.py health check                System health
      capybara.py logs show --service shadowsocks View Shadowsocks logs
      capybara.py logs show --service v2ray View V2Ray logs
      capybara.py logs show --service udp2raw View obfuscation logs

    Documentation: https://github.com/jmpnop/capybara
    """
    pass


@cli.group()
def user():
    """
    Manage VPN users (add, remove, list, block).

    Examples:
      capybara.py user add alice --description "Engineering team"
      capybara.py user list --detailed
      capybara.py user remove alice
      capybara.py user block alice
    """
    pass


@user.command('add')
@click.argument('username')
@click.option('--description', '-d', default='', help='User description')
def user_add(username, description):
    """Add a new VPN user to all protocols (WireGuard, Shadowsocks, V2Ray)

    Automatically generates configs and QR codes for all three protocols.

    Examples:
        ./capybara.py user add alice
        ./capybara.py user add bob --description "Bob from Sales"
    """
    config = load_config()
    manager = VPNManager(config)

    try:
        result = manager.add_user(username, description)

        # Display summary
        click.echo(f"\n{Fore.GREEN}{'='*60}")
        click.echo(f"{Fore.GREEN}User '{username}' Successfully Added to All Protocols!")
        click.echo(f"{Fore.GREEN}{'='*60}\n")

        # Show protocol-specific info
        if 'wireguard' in result['protocols']:
            wg = result['protocols']['wireguard']
            click.echo(f"{Fore.CYAN}WireGuard:")
            click.echo(f"  Config: {wg['config_file']}")
            if 'wireguard' in result['qr_codes']:
                click.echo(f"  QR Code: {result['qr_codes']['wireguard']}")
            click.echo(f"\n  {Fore.YELLOW}Setup Instructions:")
            click.echo(f"  1. Run udp2raw: ./udp2raw -c -l 127.0.0.1:4096 -r {config['server']['host']}:443 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro")
            click.echo(f"  2. Import {wg['config_file']} into WireGuard app")
            click.echo(f"  3. Connect!\n")

        if 'shadowsocks' in result['protocols']:
            ss = result['protocols']['shadowsocks']
            click.echo(f"{Fore.CYAN}Shadowsocks:")
            click.echo(f"  Config: {ss['config_file']}")
            if 'shadowsocks' in result['qr_codes']:
                click.echo(f"  QR Code: {result['qr_codes']['shadowsocks']}")
            click.echo(f"\n  {Fore.YELLOW}Setup Instructions:")
            click.echo(f"  1. Install Shadowsocks client (iOS: Shadowrocket, Android: Shadowsocks)")
            click.echo(f"  2. Scan QR code or add server manually")
            click.echo(f"  3. Connect!\n")

        if 'v2ray' in result['protocols']:
            v2 = result['protocols']['v2ray']
            click.echo(f"{Fore.CYAN}V2Ray:")
            click.echo(f"  Config: {v2['config_file']}")
            if 'v2ray' in result['qr_codes']:
                click.echo(f"  QR Code: {result['qr_codes']['v2ray']}")
            click.echo(f"\n  {Fore.YELLOW}Setup Instructions:")
            click.echo(f"  1. Install V2Ray client (iOS: Shadowrocket/Kitsunebi, Android: v2rayNG)")
            click.echo(f"  2. Scan QR code or add VMess server manually")
            click.echo(f"  3. Connect!\n")

        click.echo(f"{Fore.CYAN}All configuration files saved to: ./vpn_clients/")

    except Exception as e:
        click.echo(f"{Fore.RED}Error adding user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@user.command('remove')
@click.argument('identifier')
@click.confirmation_option(prompt='Are you sure you want to remove this user?')
def user_remove(identifier):
    """Remove a VPN user by username or IP"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.remove_user(identifier)
    except Exception as e:
        click.echo(f"{Fore.RED}Error removing user: {e}")
        sys.exit(1)


@user.command('list')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed information')
def user_list(detailed):
    """List all VPN users"""
    config = load_config()
    manager = VPNManager(config)

    try:
        users = manager.list_users()

        if not users:
            click.echo(f"{Fore.YELLOW}No users found")
            return

        if detailed:
            for user in users:
                protocol = user.get('protocol', 'unknown')
                click.echo(f"\n{Fore.CYAN}{'='*60}")
                click.echo(f"{Fore.GREEN}User: {user.get('username', 'N/A')} ({protocol.upper()})")
                click.echo(f"{Fore.CYAN}{'='*60}")
                click.echo(f"Protocol:        {protocol.upper()}")
                click.echo(f"IP Address:      {user.get('ip', 'N/A')}")
                click.echo(f"Created:         {user.get('created', 'N/A')}")
                click.echo(f"Description:     {user.get('description', 'N/A')}")

                # Protocol-specific details
                if protocol == 'wireguard':
                    pubkey = user.get('public_key', 'N/A')
                    click.echo(f"Public Key:      {pubkey[:40]}..." if len(pubkey) > 40 else f"Public Key:      {pubkey}")
                elif protocol == 'v2ray':
                    click.echo(f"UUID:            {user.get('uuid', 'N/A')}")
                    click.echo(f"AlterID:         {user.get('alterId', 'N/A')}")

                click.echo(f"Endpoint:        {user.get('endpoint', 'Never connected')}")
                click.echo(f"Last Handshake:  {user.get('last_handshake', 'Never')}")
                click.echo(f"Data RX:         {user.get('transfer_rx', '0 B')}")
                click.echo(f"Data TX:         {user.get('transfer_tx', '0 B')}")
        else:
            table_data = []
            for user in users:
                table_data.append([
                    user.get('username', 'N/A'),
                    user.get('protocol', 'N/A').upper(),
                    user.get('ip', 'N/A')[:15],
                    user.get('endpoint', 'Never')[:22],
                    user.get('last_handshake', 'Never')[:18],
                    user.get('transfer_rx', '0 B')[:10],
                    user.get('transfer_tx', '0 B')[:10]
                ])

            headers = ['Username', 'Protocol', 'IP', 'Endpoint', 'Handshake', 'RX', 'TX']
            click.echo(f"\n{Fore.CYAN}VPN Users (All Protocols):")
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
            click.echo(f"\n{Fore.GREEN}Total users: {len(users)}")

            # Show protocol breakdown
            wg_count = sum(1 for u in users if u.get('protocol') == 'wireguard')
            v2_count = sum(1 for u in users if u.get('protocol') == 'v2ray')
            click.echo(f"{Fore.CYAN}  WireGuard: {wg_count} | V2Ray: {v2_count}")
            click.echo(f"{Fore.YELLOW}  Note: Shadowsocks uses shared credentials (no per-user listing)")

    except Exception as e:
        click.echo(f"{Fore.RED}Error listing users: {e}")
        sys.exit(1)


@user.command('block')
@click.argument('identifier')
def user_block(identifier):
    """Block a user by username or IP"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.block_user(identifier)
    except Exception as e:
        click.echo(f"{Fore.RED}Error blocking user: {e}")
        sys.exit(1)


@cli.group()
def stats():
    """
    View VPN statistics and monitor connections.

    Examples:
      capybara.py stats show                  # Current statistics
      capybara.py stats live                  # Real-time monitoring
      capybara.py stats live --interval 10    # Custom refresh rate
    """
    pass


@stats.command('show')
def stats_show():
    """Show current VPN statistics"""
    config = load_config()
    manager = VPNManager(config)

    try:
        stats_data = manager.get_stats()

        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.GREEN}VPN Server Statistics")
        click.echo(f"{Fore.CYAN}{'='*60}\n")

        click.echo(f"{Fore.YELLOW}Server Status:")
        click.echo(f"  Uptime:              {stats_data.get('uptime', 'N/A')}")
        click.echo(f"  Total Users:         {stats_data.get('total_users', 0)}")
        click.echo(f"  Active Connections:  {stats_data.get('active_connections', 0)}")
        click.echo(f"  udp2raw Running:     {Fore.GREEN + 'Yes' if stats_data.get('udp2raw_running') else Fore.RED + 'No'}")

        click.echo(f"\n{Fore.YELLOW}System Resources:")
        click.echo(f"  {stats_data.get('memory', 'N/A')}")

        click.echo(f"\n{Fore.YELLOW}WireGuard Interface:")
        click.echo(stats_data.get('wg_status', 'N/A'))

    except Exception as e:
        click.echo(f"{Fore.RED}Error getting statistics: {e}")
        sys.exit(1)


@stats.command('live')
@click.option('--interval', '-i', default=5, help='Update interval in seconds')
def stats_live(interval):
    """Monitor VPN statistics in real-time"""
    import time

    config = load_config()
    manager = VPNManager(config)

    try:
        while True:
            click.clear()
            stats_data = manager.get_stats()
            users = manager.list_users()

            click.echo(f"{Fore.CYAN}{'='*60}")
            click.echo(f"{Fore.GREEN}VPN Server Live Monitor (Updates every {interval}s)")
            click.echo(f"{Fore.CYAN}{'='*60}\n")

            click.echo(f"{Fore.YELLOW}Server: {config['server']['host']}")
            click.echo(f"Uptime: {stats_data.get('uptime', 'N/A')}")
            click.echo(f"Total Users: {stats_data.get('total_users', 0)} | Active: {stats_data.get('active_connections', 0)}")

            if users:
                click.echo(f"\n{Fore.CYAN}Active Connections:")
                table_data = []
                for user in users:
                    if user.get('endpoint') != 'Never connected':
                        table_data.append([
                            user.get('username', 'N/A')[:15],
                            user.get('ip', 'N/A'),
                            user.get('endpoint', 'N/A')[:25],
                            user.get('transfer_rx', '0 B'),
                            user.get('transfer_tx', '0 B')
                        ])

                if table_data:
                    headers = ['User', 'IP', 'Endpoint', 'RX', 'TX']
                    click.echo(tabulate(table_data, headers=headers, tablefmt='simple'))
                else:
                    click.echo(f"{Fore.YELLOW}No active connections")

            click.echo(f"\n{Fore.YELLOW}Press Ctrl+C to exit")
            time.sleep(interval)

    except KeyboardInterrupt:
        click.echo(f"\n\n{Fore.GREEN}Monitoring stopped")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        sys.exit(1)


@cli.group()
def block():
    """
    Manage blocked resources (domains and IPs).

    Examples:
      capybara.py block add facebook.com              # Block domain
      capybara.py block add 1.2.3.4 --type ip         # Block IP
      capybara.py block list                          # Show all blocks
      capybara.py block remove facebook.com           # Unblock domain
    """
    pass


@block.command('add')
@click.argument('resource')
@click.option('--type', '-t', type=click.Choice(['domain', 'ip']), default='domain', help='Resource type')
def block_add(resource, type):
    """Block a domain or IP address"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.block_resource(resource, type)
    except Exception as e:
        click.echo(f"{Fore.RED}Error blocking resource: {e}")
        sys.exit(1)


@block.command('remove')
@click.argument('resource')
@click.option('--type', '-t', type=click.Choice(['domain', 'ip']), default='domain', help='Resource type')
def block_remove(resource, type):
    """Unblock a domain or IP address"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.unblock_resource(resource, type)
    except Exception as e:
        click.echo(f"{Fore.RED}Error unblocking resource: {e}")
        sys.exit(1)


@block.command('list')
def block_list():
    """List all blocked resources"""
    config = load_config()
    manager = VPNManager(config)

    try:
        blocks = manager.list_blocked_resources()

        if not blocks:
            click.echo(f"{Fore.YELLOW}No blocked resources")
            return

        click.echo(f"\n{Fore.CYAN}Blocked Resources:")
        for block in blocks:
            click.echo(f"  {block}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error listing blocked resources: {e}")
        sys.exit(1)


@cli.group()
def server():
    """
    Manage VPN server (start, stop, restart, status).

    Examples:
      capybara.py server status               # Check server status
      capybara.py server stop                 # Stop VPN server
      capybara.py server start                # Start VPN server
      capybara.py server restart              # Restart VPN server
    """
    pass


@server.command('status')
def server_status():
    """Check VPN server status"""
    config = load_config()
    manager = VPNManager(config)

    try:
        stats_data = manager.get_stats()
        service_status = manager.service_status()
        protocol_configs = manager.get_protocol_configs()

        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.GREEN}VPN Server Status")
        click.echo(f"{Fore.CYAN}{'='*60}\n")

        wg_running = 'interface:' in stats_data.get('wg_status', '')
        udp_running = stats_data.get('udp2raw_running', False)
        ss_running = service_status.get('shadowsocks') == 'running'
        v2ray_running = service_status.get('v2ray') == 'running'

        # Overall status: all critical services must be running
        all_running = wg_running and udp_running and ss_running and v2ray_running
        status_color = Fore.GREEN if all_running else Fore.YELLOW
        status_text = "RUNNING" if all_running else "PARTIAL"

        click.echo(f"Overall Status:      {status_color}{status_text}")
        click.echo(f"\n{Fore.CYAN}Protocol Status:")
        click.echo(f"{Fore.YELLOW}WireGuard:           {Fore.GREEN + 'Running' if wg_running else Fore.RED + 'Stopped'}")
        click.echo(f"{Fore.YELLOW}udp2raw:             {Fore.GREEN + 'Running' if udp_running else Fore.RED + 'Stopped'}")
        click.echo(f"{Fore.YELLOW}Shadowsocks:         {Fore.GREEN + 'Running' if ss_running else Fore.RED + 'Stopped'}")
        click.echo(f"{Fore.YELLOW}V2Ray:               {Fore.GREEN + 'Running' if v2ray_running else Fore.RED + 'Stopped'}")

        # ========== Protocol Configuration Details ==========
        click.echo(f"\n{Fore.CYAN}Protocol Configuration:")

        # WireGuard
        wg_cfg = protocol_configs.get('wireguard', {})
        if 'error' not in wg_cfg:
            click.echo(f"\n{Fore.YELLOW}WireGuard:")
            click.echo(f"  Interface:         {wg_cfg.get('interface', 'N/A')}")
            click.echo(f"  Port:              {wg_cfg.get('port', 'N/A')} (internal)")
            click.echo(f"  Obfuscation Port:  {wg_cfg.get('obfuscation_port', 'N/A')} (udp2raw → HTTPS)")
            click.echo(f"  Network:           {wg_cfg.get('network', 'N/A')}")
        else:
            click.echo(f"\n{Fore.YELLOW}WireGuard: {Fore.RED}Config error")

        # Shadowsocks
        ss_cfg = protocol_configs.get('shadowsocks', {})
        if 'error' not in ss_cfg:
            click.echo(f"\n{Fore.YELLOW}Shadowsocks:")
            click.echo(f"  Port:              {ss_cfg.get('port', 'N/A')}")
            click.echo(f"  Method:            {ss_cfg.get('method', 'N/A')}")
            click.echo(f"  Mode:              {ss_cfg.get('mode', 'N/A').replace('tcp_and_udp', 'TCP + UDP')}")
        else:
            click.echo(f"\n{Fore.YELLOW}Shadowsocks: {Fore.RED}Config error")

        # V2Ray
        v2_cfg = protocol_configs.get('v2ray', {})
        if 'error' not in v2_cfg:
            click.echo(f"\n{Fore.YELLOW}V2Ray:")
            click.echo(f"  Port:              {v2_cfg.get('port', 'N/A')}")
            click.echo(f"  Protocol:          {v2_cfg.get('protocol', 'N/A')}")
            click.echo(f"  Transport:         {v2_cfg.get('transport', 'N/A')}")
            click.echo(f"  WebSocket Path:    {v2_cfg.get('ws_path', 'N/A')}")
            click.echo(f"  Configured Users:  {v2_cfg.get('users', 0)}")
        else:
            click.echo(f"\n{Fore.YELLOW}V2Ray: {Fore.RED}Config error")

        # ========== General Server Info ==========
        click.echo(f"\n{Fore.CYAN}Server Information:")
        click.echo(f"{Fore.YELLOW}Server IP:           {config['server']['host']}")
        click.echo(f"{Fore.YELLOW}Uptime:              {stats_data.get('uptime', 'N/A')}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error checking server status: {e}")
        sys.exit(1)


@server.command('stop')
@click.confirmation_option(prompt='Are you sure you want to stop the VPN server?')
def server_stop():
    """Stop the VPN server"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.stop_server()
    except Exception as e:
        click.echo(f"{Fore.RED}Error stopping server: {e}")
        sys.exit(1)


@server.command('start')
def server_start():
    """Start the VPN server"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.start_server()
    except Exception as e:
        click.echo(f"{Fore.RED}Error starting server: {e}")
        sys.exit(1)


@server.command('restart')
@click.confirmation_option(prompt='Are you sure you want to restart the VPN server?')
def server_restart():
    """Restart the VPN server"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.restart_server()
    except Exception as e:
        click.echo(f"{Fore.RED}Error restarting server: {e}")
        sys.exit(1)


@cli.command()
def config():
    """
    Show current configuration from ~/.capybara_config.yaml

    Examples:
      capybara.py config                              # Display current settings
    """
    cfg = load_config()

    click.echo(f"\n{Fore.CYAN}Current Configuration:")
    click.echo(f"{Fore.YELLOW}Config file: {CONFIG_FILE}\n")

    # Hide password in output
    display_cfg = cfg.copy()
    if 'password' in display_cfg.get('server', {}):
        display_cfg['server']['password'] = '***hidden***'

    click.echo(yaml.dump(display_cfg, default_flow_style=False))


# ===== LOGS COMMANDS =====
@cli.group()
def logs():
    """
    View server logs for all protocols (WireGuard, Shadowsocks, V2Ray, udp2raw, system).

    Examples:
      capybara.py logs show                          # View all logs
      capybara.py logs show --service wireguard      # WireGuard logs only
      capybara.py logs show --service shadowsocks    # Shadowsocks logs only
      capybara.py logs show --service v2ray          # V2Ray logs only
      capybara.py logs show --service udp2raw        # udp2raw logs only
      capybara.py logs show --lines 100              # Show more lines
      capybara.py logs tail                       # Follow logs live
    """
    pass


@logs.command('show')
@click.option('--service', '-s', type=click.Choice(['all', 'wireguard', 'udp2raw', 'shadowsocks', 'v2ray', 'system']), default='all', help='Service to show logs for')
@click.option('--lines', '-n', default=50, help='Number of lines to show')
def logs_show(service, lines):
    """Show server logs"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.view_logs(service, lines)
    except Exception as e:
        click.echo(f"{Fore.RED}Error viewing logs: {e}")
        sys.exit(1)


@logs.command('tail')
@click.option('--service', '-s', type=click.Choice(['udp2raw', 'wireguard', 'shadowsocks', 'v2ray', 'system']), default='udp2raw', help='Service to follow')
def logs_tail(service):
    """Follow logs in real-time (Ctrl+C to stop)"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.tail_logs(service)
    except Exception as e:
        click.echo(f"{Fore.RED}Error tailing logs: {e}")
        sys.exit(1)


# ===== CONNECTION COMMANDS =====
@cli.group()
def connection():
    """
    Manage active connections (list, kick users).

    Examples:
      capybara.py connection list             # Show active connections
      capybara.py connection kick alice       # Disconnect user
      capybara.py connection kick-all         # Emergency disconnect all
    """
    pass


@connection.command('list')
def connection_list():
    """List active connections"""
    config = load_config()
    manager = VPNManager(config)

    try:
        users = manager.list_users()
        active_users = [u for u in users if u.get('endpoint') != 'Never connected']

        if not active_users:
            click.echo(f"{Fore.YELLOW}No active connections")
            return

        table_data = []
        for user in active_users:
            table_data.append([
                user.get('username', 'N/A'),
                user.get('ip', 'N/A'),
                user.get('endpoint', 'N/A')[:30],
                user.get('last_handshake', 'Never')[:20]
            ])

        headers = ['Username', 'IP', 'Endpoint', 'Last Handshake']
        click.echo(f"\n{Fore.CYAN}Active Connections:")
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\n{Fore.GREEN}Total: {len(active_users)}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error listing connections: {e}")
        sys.exit(1)


@connection.command('kick')
@click.argument('identifier')
@click.confirmation_option(prompt='Are you sure you want to disconnect this user?')
def connection_kick(identifier):
    """Disconnect a user immediately"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.kick_user(identifier)
    except Exception as e:
        click.echo(f"{Fore.RED}Error kicking user: {e}")
        sys.exit(1)


@connection.command('kick-all')
@click.confirmation_option(prompt='Are you sure you want to disconnect ALL users?')
def connection_kick_all():
    """Disconnect all users"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.kick_all_users()
    except Exception as e:
        click.echo(f"{Fore.RED}Error disconnecting users: {e}")
        sys.exit(1)


# ===== SERVICE COMMANDS =====
@cli.group()
def service():
    """
    Manage individual services (all protocols).

    Examples:
      capybara.py service status                  # Check all services
      capybara.py service restart wireguard       # Restart WireGuard only
      capybara.py service restart shadowsocks     # Restart Shadowsocks only
      capybara.py service restart v2ray           # Restart V2Ray only
      capybara.py service restart udp2raw         # Restart udp2raw only
      capybara.py service restart firewall        # Restart firewall only
    """
    pass


@service.command('status')
def service_status_cmd():
    """Check status of all services"""
    config = load_config()
    manager = VPNManager(config)

    try:
        status = manager.service_status()

        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.GREEN}Service Status")
        click.echo(f"{Fore.CYAN}{'='*60}\n")

        for svc, state in status.items():
            color = Fore.GREEN if state == 'running' else Fore.RED
            click.echo(f"{svc.capitalize():15} {color}{state.upper()}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error checking service status: {e}")
        sys.exit(1)


@service.command('restart')
@click.argument('service_name', type=click.Choice(['wireguard', 'udp2raw', 'shadowsocks', 'v2ray', 'firewall']))
@click.confirmation_option(prompt='Are you sure you want to restart this service?')
def service_restart_cmd(service_name):
    """Restart a specific service"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.restart_service(service_name)
    except Exception as e:
        click.echo(f"{Fore.RED}Error restarting service: {e}")
        sys.exit(1)


# ===== BACKUP COMMANDS =====
@cli.group()
def backup():
    """
    Backup and restore VPN configuration (disaster recovery).

    Examples:
      capybara.py backup create                   # Auto-named backup
      capybara.py backup create --name friday     # Named backup
      capybara.py backup list                     # List all backups
      capybara.py backup restore friday           # Restore from backup
    """
    pass


@backup.command('create')
@click.option('--name', '-n', help='Backup name (default: backup_TIMESTAMP)')
def backup_create(name):
    """Create a backup"""
    config = load_config()
    manager = VPNManager(config)

    try:
        backup_name = manager.create_backup(name)
        click.echo(f"\n{Fore.CYAN}Backup saved to: /root/vpn_backups/{backup_name}.tar.gz")
    except Exception as e:
        click.echo(f"{Fore.RED}Error creating backup: {e}")
        sys.exit(1)


@backup.command('list')
def backup_list_cmd():
    """List all backups"""
    config = load_config()
    manager = VPNManager(config)

    try:
        backups = manager.list_backups()

        if not backups:
            click.echo(f"{Fore.YELLOW}No backups found")
            return

        table_data = []
        for bkp in backups:
            table_data.append([
                bkp['name'],
                bkp['size'],
                bkp['date']
            ])

        headers = ['Name', 'Size', 'Date']
        click.echo(f"\n{Fore.CYAN}Available Backups:")
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\n{Fore.GREEN}Total: {len(backups)}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error listing backups: {e}")
        sys.exit(1)


@backup.command('restore')
@click.argument('backup_name')
@click.confirmation_option(prompt='Are you sure you want to restore from this backup? Current config will be replaced.')
def backup_restore_cmd(backup_name):
    """Restore from a backup"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.restore_backup(backup_name)
    except Exception as e:
        click.echo(f"{Fore.RED}Error restoring backup: {e}")
        sys.exit(1)


# ===== DIAGNOSTIC COMMANDS =====
@cli.group()
def diag():
    """
    Network diagnostics (ping, ports, handshake).

    Examples:
      capybara.py diag ping alice             # Ping user's VPN IP
      capybara.py diag ping 10.7.0.2          # Ping by IP
      capybara.py diag ports                  # Show listening ports
      capybara.py diag handshake alice        # Check handshake status
    """
    pass


@diag.command('ping')
@click.argument('identifier')
def diag_ping(identifier):
    """Ping a user's VPN IP"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.ping_user(identifier)
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        sys.exit(1)


@diag.command('ports')
def diag_ports():
    """Show listening ports"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.check_ports()
    except Exception as e:
        click.echo(f"{Fore.RED}Error checking ports: {e}")
        sys.exit(1)


@diag.command('handshake')
@click.argument('identifier')
def diag_handshake(identifier):
    """Check handshake status for a user"""
    config = load_config()
    manager = VPNManager(config)

    try:
        manager.check_handshake(identifier)
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        sys.exit(1)


# ===== HEALTH COMMANDS =====
@cli.group()
def health():
    """
    System health monitoring (CPU, memory, disk, network).

    Examples:
      capybara.py health check                # Full system health check
    """
    pass


@health.command('check')
def health_check():
    """Check system health"""
    config = load_config()
    manager = VPNManager(config)

    try:
        health_data = manager.get_health()

        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.GREEN}System Health")
        click.echo(f"{Fore.CYAN}{'='*60}\n")

        click.echo(f"{Fore.YELLOW}Uptime:")
        click.echo(f"  {health_data.get('uptime', 'N/A')}\n")

        click.echo(f"{Fore.YELLOW}CPU:")
        click.echo(f"  {health_data.get('cpu', 'N/A')}\n")

        click.echo(f"{Fore.YELLOW}Memory:")
        click.echo(f"  {health_data.get('memory', 'N/A')}\n")

        click.echo(f"{Fore.YELLOW}Disk:")
        click.echo(f"  {health_data.get('disk', 'N/A')}\n")

        click.echo(f"{Fore.YELLOW}Network Interface (wg0):")
        for line in health_data.get('network', '').split('\n')[:10]:
            if line.strip():
                click.echo(f"  {line}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error checking health: {e}")
        sys.exit(1)


# ===== REPORT COMMANDS =====
@cli.group()
def report():
    """
    Generate usage reports (text, JSON, CSV formats).

    Examples:
      capybara.py report generate                     # Daily report (default)
      capybara.py report generate --type weekly       # Weekly report
      capybara.py report generate --type monthly      # Monthly report
      capybara.py report generate --format json       # JSON output
      capybara.py report generate --format csv        # CSV export for Excel
    """
    pass


@report.command('generate')
@click.option('--type', '-t', type=click.Choice(['daily', 'weekly', 'monthly']), default='daily', help='Report type')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'csv']), default='text', help='Output format')
def report_generate(type, format):
    """Generate a usage report"""
    config = load_config()
    manager = VPNManager(config)

    try:
        report_data = manager.generate_report(type)

        if format == 'json':
            click.echo(json.dumps(report_data, indent=2))
        elif format == 'csv':
            click.echo("Username,IP,Status,Last Seen,Data RX,Data TX")
            for user in report_data['users']:
                click.echo(f"{user['username']},{user['ip']},{user['status']},{user['last_seen']},{user['data_received']},{user['data_sent']}")
        else:  # text
            click.echo(f"\n{Fore.CYAN}{'='*60}")
            click.echo(f"{Fore.GREEN}{type.capitalize()} Report")
            click.echo(f"{Fore.CYAN}{'='*60}\n")

            click.echo(f"{Fore.YELLOW}Generated: {report_data['generated']}")
            click.echo(f"{Fore.YELLOW}Report Type: {report_data['type']}\n")

            click.echo(f"{Fore.CYAN}Summary:")
            click.echo(f"  Total Users: {report_data['summary']['total_users']}")
            click.echo(f"  Active Users: {report_data['summary']['active_users']}")
            click.echo(f"  Server Uptime: {report_data['summary']['server_uptime']}\n")

            table_data = []
            for user in report_data['users']:
                table_data.append([
                    user['username'],
                    user['ip'],
                    user['status'],
                    user['last_seen'][:20],
                    user['data_received'],
                    user['data_sent']
                ])

            headers = ['Username', 'IP', 'Status', 'Last Seen', 'RX', 'TX']
            click.echo(f"{Fore.CYAN}User Details:")
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))

    except Exception as e:
        click.echo(f"{Fore.RED}Error generating report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
