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
from pathlib import Path
from datetime import datetime
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

    def add_user(self, username, description=""):
        """Add a new VPN user"""
        with SSHConnection(self.config) as ssh:
            click.echo(f"{Fore.YELLOW}Generating keys for user '{username}'...")

            # Generate keys
            private_key, public_key = self.generate_client_keys(ssh)

            # Get next available IP
            client_ip = self.get_next_ip(ssh)

            # Save keys to server with username
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            key_prefix = f"/etc/wireguard/clients/{username}_{timestamp}"

            # Create clients directory
            ssh.execute("mkdir -p /etc/wireguard/clients")

            # Save keys
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

            # Escape for shell
            cmd = f"cat >> {self.config['vpn']['config_path']} << 'EOFPEER'\n{peer_config}\nEOFPEER"
            ssh.execute(cmd)

            # Reload WireGuard
            click.echo(f"{Fore.YELLOW}Reloading WireGuard configuration...")
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

            # Save client config locally
            client_dir = Path.cwd() / 'vpn_clients'
            client_dir.mkdir(exist_ok=True)

            config_file = client_dir / f"{username}_{timestamp}.conf"
            config_file.write_text(client_config)

            click.echo(f"{Fore.GREEN}✓ User '{username}' added successfully!")
            click.echo(f"{Fore.CYAN}IP Address: {client_ip}")
            click.echo(f"{Fore.CYAN}Public Key: {public_key}")
            click.echo(f"{Fore.CYAN}Client config saved to: {config_file}")

            # Generate QR code
            try:
                qr_file = client_dir / f"{username}_{timestamp}_qr.png"
                qr = qrcode.QRCode(
                    version=None,  # Auto-size
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(client_config)
                qr.make(fit=True)

                # Save as PNG
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(str(qr_file))

                click.echo(f"{Fore.CYAN}QR code saved to: {qr_file}")

                # Display QR code in terminal
                click.echo(f"\n{Fore.YELLOW}QR Code (scan with mobile device):")
                qr_terminal = qrcode.QRCode()
                qr_terminal.add_data(client_config)
                qr_terminal.print_ascii(invert=True)
                click.echo("")

            except Exception as e:
                click.echo(f"{Fore.YELLOW}⚠ QR code generation failed: {e}")
                click.echo(f"{Fore.YELLOW}  Install qrcode: pip install qrcode pillow")

            return {
                'username': username,
                'ip': client_ip,
                'public_key': public_key,
                'private_key': private_key,
                'config_file': str(config_file)
            }

    def remove_user(self, identifier):
        """Remove a user by username or IP"""
        with SSHConnection(self.config) as ssh:
            # Find the user's peer section
            cmd = f"cat {self.config['vpn']['config_path']}"
            config_content, _, _ = ssh.execute(cmd)

            # Parse config to find peer
            lines = config_content.split('\n')
            peer_start = None
            peer_end = None
            found = False

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
                    found = True
                    break

            if not found:
                click.echo(f"{Fore.RED}User '{identifier}' not found")
                return False

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

            click.echo(f"{Fore.GREEN}✓ User '{identifier}' removed successfully")
            return True

    def list_users(self):
        """List all VPN users"""
        with SSHConnection(self.config) as ssh:
            # Get WireGuard status
            wg_output, _, _ = ssh.execute(f"wg show {self.config['vpn']['interface']}")

            # Get config file for metadata
            config_output, _, _ = ssh.execute(f"cat {self.config['vpn']['config_path']}")

            # Parse users from config
            users = []
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
                        'status': 'Active'
                    }
                elif line.startswith('# Description:') and current_user:
                    current_user['description'] = line.replace('# Description:', '').strip()
                elif line.startswith('PublicKey =') and current_user:
                    current_user['public_key'] = line.replace('PublicKey =', '').strip()
                elif line.startswith('AllowedIPs =') and current_user:
                    current_user['allowed_ips'] = line.replace('AllowedIPs =', '').strip()
                    users.append(current_user.copy())
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

            # Add connection info
            for user in users:
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

            return users

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

            if service == 'system' or service == 'all':
                click.echo(f"{Fore.CYAN}=== System Logs (relevant) ===")
                cmd = f"dmesg | grep -i 'wireguard\\|udp2raw\\|wg0' | tail -n {lines}"
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

            # Firewall status
            output, _, code = ssh.execute("rc-service iptables status", check_error=False)
            status['firewall'] = 'running' if code == 0 else 'stopped'

            return status

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

            # Extract backup
            ssh.execute(f"cd /root/vpn_backups && tar -xzf {backup_name}.tar.gz")

            # Restore WireGuard config
            ssh.execute(f"cp /root/vpn_backups/{backup_name}/wg0.conf {self.config['vpn']['config_path']}")

            # Restore keys
            ssh.execute(f"cp /root/vpn_backups/{backup_name}/*.key /etc/wireguard/ 2>/dev/null || true")
            ssh.execute(f"cp -r /root/vpn_backups/{backup_name}/clients /etc/wireguard/ 2>/dev/null || true")

            # Restore iptables
            ssh.execute(f"iptables-restore < /root/vpn_backups/{backup_name}/iptables.rules 2>/dev/null || true")

            # Cleanup
            ssh.execute(f"rm -rf /root/vpn_backups/{backup_name}")

            # Restart services
            ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")

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
@click.version_option(version='2.0.0')
def cli():
    """
    🦫 Capybara v2.0 - Censorship-Resistant VPN Infrastructure

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
    """Add a new VPN user"""
    config = load_config()
    manager = VPNManager(config)

    try:
        result = manager.add_user(username, description)
        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.GREEN}Client Configuration File Created")
        click.echo(f"{Fore.CYAN}{'='*60}")
        click.echo(f"\nShare this file with the user: {result['config_file']}")
        click.echo(f"\n{Fore.YELLOW}Client Setup Instructions:")
        click.echo("1. Run udp2raw client: ./udp2raw -c -l 127.0.0.1:4096 -r 66.42.119.38:443 -k SecureVPN2025Obfuscate --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro")
        click.echo(f"2. Import {result['config_file']} into WireGuard app")
        click.echo("3. Connect!")
    except Exception as e:
        click.echo(f"{Fore.RED}Error adding user: {e}")
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
                click.echo(f"\n{Fore.CYAN}{'='*60}")
                click.echo(f"{Fore.GREEN}User: {user.get('username', 'N/A')}")
                click.echo(f"{Fore.CYAN}{'='*60}")
                click.echo(f"IP Address:      {user.get('ip', 'N/A')}")
                click.echo(f"Created:         {user.get('created', 'N/A')}")
                click.echo(f"Description:     {user.get('description', 'N/A')}")
                click.echo(f"Public Key:      {user.get('public_key', 'N/A')[:40]}...")
                click.echo(f"Endpoint:        {user.get('endpoint', 'Never connected')}")
                click.echo(f"Last Handshake:  {user.get('last_handshake', 'Never')}")
                click.echo(f"Data RX:         {user.get('transfer_rx', '0 B')}")
                click.echo(f"Data TX:         {user.get('transfer_tx', '0 B')}")
        else:
            table_data = []
            for user in users:
                table_data.append([
                    user.get('username', 'N/A'),
                    user.get('ip', 'N/A'),
                    user.get('endpoint', 'Never')[:25],
                    user.get('last_handshake', 'Never')[:20],
                    user.get('transfer_rx', '0 B'),
                    user.get('transfer_tx', '0 B')
                ])

            headers = ['Username', 'IP Address', 'Endpoint', 'Last Handshake', 'RX', 'TX']
            click.echo(f"\n{Fore.CYAN}VPN Users:")
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
            click.echo(f"\n{Fore.GREEN}Total users: {len(users)}")

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

        click.echo(f"\n{Fore.CYAN}{'='*60}")
        click.echo(f"{Fore.GREEN}VPN Server Status")
        click.echo(f"{Fore.CYAN}{'='*60}\n")

        wg_running = 'interface:' in stats_data.get('wg_status', '')
        udp_running = stats_data.get('udp2raw_running', False)

        status_color = Fore.GREEN if (wg_running and udp_running) else Fore.RED
        status_text = "RUNNING" if (wg_running and udp_running) else "ERROR"

        click.echo(f"Overall Status:      {status_color}{status_text}")
        click.echo(f"{Fore.YELLOW}WireGuard:           {Fore.GREEN + 'Running' if wg_running else Fore.RED + 'Stopped'}")
        click.echo(f"{Fore.YELLOW}udp2raw:             {Fore.GREEN + 'Running' if udp_running else Fore.RED + 'Stopped'}")
        click.echo(f"{Fore.YELLOW}Server:              {config['server']['host']}")
        click.echo(f"{Fore.YELLOW}Interface:           {config['vpn']['interface']}")
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
    View server logs (WireGuard, udp2raw, system).

    Examples:
      capybara.py logs show                       # View all logs
      capybara.py logs show --service udp2raw     # Service-specific
      capybara.py logs show --lines 100           # Show more lines
      capybara.py logs tail                       # Follow logs live
    """
    pass


@logs.command('show')
@click.option('--service', '-s', type=click.Choice(['all', 'wireguard', 'udp2raw', 'system']), default='all', help='Service to show logs for')
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
@click.option('--service', '-s', type=click.Choice(['udp2raw', 'wireguard', 'system']), default='udp2raw', help='Service to follow')
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
    Manage individual services (WireGuard, udp2raw, firewall).

    Examples:
      capybara.py service status                  # Check all services
      capybara.py service restart wireguard       # Restart WireGuard only
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
@click.argument('service_name', type=click.Choice(['wireguard', 'udp2raw', 'firewall']))
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
