# WireGuard Capybara

A comprehensive Python-based command-line tool for managing your remote WireGuard VPN server via SSH.

## Features

- **User Management**: Add, remove, list, and block VPN users
- **Statistics & Monitoring**: Real-time and static statistics viewing
- **Resource Blocking**: Block specific domains and IP addresses
- **Server Management**: Check status and restart services
- **Automatic Configuration**: Generates client configs automatically
- **Beautiful CLI**: Color-coded output with tables and progress indicators

## Installation

### Prerequisites

- Python 3.7 or higher
- SSH access to your VPN server
- WireGuard VPN server already set up (see CLAUDE.md)

### Install Dependencies

```bash
cd /Users/pasha/PycharmProjects/o
pip install -r requirements.txt
```

Or install system-wide:

```bash
pip3 install -r requirements.txt
```

### Make Script Executable

```bash
chmod +x capybara.py
```

### Optional: Add to PATH

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export PATH="$PATH:/Users/pasha/PycharmProjects/o"' >> ~/.zshrc
source ~/.zshrc

# Now you can run from anywhere
capybara.py --help
```

Or create an alias:

```bash
echo 'alias vpn="python3 /Users/pasha/PycharmProjects/o/capybara.py"' >> ~/.zshrc
source ~/.zshrc

# Now use: vpn user list
```

## Configuration

On first run, the tool creates a configuration file at `~/.capybara_config.yaml` with your server details.

### View Current Configuration

```bash
./capybara.py config
```

### Edit Configuration

```bash
nano ~/.capybara_config.yaml
```

**Default Configuration:**

```yaml
server:
  host: 66.42.119.38
  port: 22
  username: root
  password: H7)a4(72PGSnN4Hh
  # Or use SSH key:
  # key_file: /path/to/private_key

vpn:
  interface: wg0
  config_path: /etc/wireguard/wg0.conf
  network: 10.7.0.0/24
  server_ip: 10.7.0.1
  next_client_ip: 2
```

## Usage

### User Management

#### Add a New User

```bash
./capybara.py user add alice
./capybara.py user add bob --description "Bob from Marketing"
```

**Output:**
- Generates unique keys for the user
- Assigns next available IP address
- Creates client configuration file in `./vpn_clients/`
- Updates server configuration
- Shows setup instructions

**Example:**
```
✓ User 'alice' added successfully!
IP Address: 10.7.0.2
Public Key: kkFtFxmLRVNguNO/xx9avIaK5p8cmVEsYiBD1HhZBzQ=
Client config saved to: /Users/pasha/PycharmProjects/o/vpn_clients/alice_20250106_123456.conf

Client Setup Instructions:
1. Run udp2raw client: ./udp2raw -c -l 127.0.0.1:4096 -r 66.42.119.38:443 -k SecureVPN2025Obfuscate...
2. Import alice_20250106_123456.conf into WireGuard app
3. Connect!
```

#### List All Users

**Simple list:**
```bash
./capybara.py user list
```

**Detailed view:**
```bash
./capybara.py user list --detailed
```

**Example Output:**
```
VPN Users:
+----------+-------------+-------------------------+---------------------+--------+--------+
| Username | IP Address  | Endpoint                | Last Handshake      | RX     | TX     |
+==========+=============+=========================+=====================+========+========+
| alice    | 10.7.0.2    | 192.168.1.100:54321     | 2 minutes ago       | 15 MiB | 8 MiB  |
+----------+-------------+-------------------------+---------------------+--------+--------+
| bob      | 10.7.0.3    | Never connected         | Never               | 0 B    | 0 B    |
+----------+-------------+-------------------------+---------------------+--------+--------+

Total users: 2
```

#### Remove a User

```bash
./capybara.py user remove alice
# Or remove by IP:
./capybara.py user remove 10.7.0.2
```

You'll be prompted for confirmation.

#### Block a User

Blocks a user temporarily (keeps config commented out):

```bash
./capybara.py user block alice
# Or by IP:
./capybara.py user block 10.7.0.2
```

### Statistics & Monitoring

#### View Current Statistics

```bash
./capybara.py stats show
```

**Example Output:**
```
============================================================
VPN Server Statistics
============================================================

Server Status:
  Uptime:              up 2 days, 5 hours, 30 minutes
  Total Users:         5
  Active Connections:  3
  udp2raw Running:     Yes

System Resources:
  Mem:           970Mi       250Mi       120Mi       30Mi        600Mi

WireGuard Interface:
interface: wg0
  public key: D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
  private key: (hidden)
  listening port: 51820

peer: kkFtFxmLRVNguNO/xx9avIaK5p8cmVEsYiBD1HhZBzQ=
  endpoint: 192.168.1.100:54321
  allowed ips: 10.7.0.2/32
  latest handshake: 2 minutes, 15 seconds ago
  transfer: 15.50 MiB received, 8.20 MiB sent
```

#### Live Monitoring

Real-time monitoring with auto-refresh:

```bash
./capybara.py stats live
# Custom interval (default 5 seconds):
./capybara.py stats live --interval 10
```

**Example Output:**
```
============================================================
VPN Server Live Monitor (Updates every 5s)
============================================================

Server: 66.42.119.38
Uptime: up 2 days, 5 hours, 30 minutes
Total Users: 5 | Active: 3

Active Connections:
User            IP           Endpoint                  RX        TX
alice           10.7.0.2     192.168.1.100:54321       15 MiB    8 MiB
charlie         10.7.0.4     203.0.113.45:41234        102 MiB   45 MiB
david           10.7.0.5     198.51.100.23:38291       5.2 GiB   1.8 GiB

Press Ctrl+C to exit
```

Press `Ctrl+C` to stop monitoring.

### Resource Blocking

Block specific domains or IP addresses from being accessed through the VPN.

#### Block a Domain

```bash
./capybara.py block add facebook.com
./capybara.py block add example.com --type domain
```

#### Block an IP Address

```bash
./capybara.py block add 1.2.3.4 --type ip
./capybara.py block add 192.168.100.0/24 --type ip
```

#### List Blocked Resources

```bash
./capybara.py block list
```

#### Unblock a Resource

```bash
./capybara.py block remove facebook.com
./capybara.py block remove 1.2.3.4 --type ip
```

### Server Management

#### Check Server Status

```bash
./capybara.py server status
```

**Example Output:**
```
============================================================
VPN Server Status
============================================================

Overall Status:      RUNNING
WireGuard:           Running
udp2raw:             Running
Server:              66.42.119.38
Interface:           wg0
Uptime:              up 2 days, 5 hours, 30 minutes
```

#### Stop VPN Server

```bash
./capybara.py server stop
```

Stops the WireGuard service. You'll be prompted for confirmation.

#### Start VPN Server

```bash
./capybara.py server start
```

Starts the WireGuard service if it's not running.

#### Restart VPN Server

```bash
./capybara.py server restart
```

Restarts the WireGuard service. You'll be prompted for confirmation.

## Complete Command Reference

### Global Options

```bash
./capybara.py --version    # Show version
./capybara.py --help       # Show help
```

### User Commands

```bash
./capybara.py user add <username> [--description TEXT]
./capybara.py user remove <identifier>
./capybara.py user list [--detailed]
./capybara.py user block <identifier>
```

### Statistics Commands

```bash
./capybara.py stats show
./capybara.py stats live [--interval SECONDS]
```

### Block Commands

```bash
./capybara.py block add <resource> [--type domain|ip]
./capybara.py block remove <resource> [--type domain|ip]
./capybara.py block list
```

### Server Commands

```bash
./capybara.py server status
./capybara.py server stop
./capybara.py server start
./capybara.py server restart
```

### Configuration

```bash
./capybara.py config       # Show current configuration
```

## Client Configuration Files

When you add a user, a configuration file is created in `./vpn_clients/`. This directory structure:

```
vpn_clients/
├── alice_20250106_123456.conf
├── bob_20250106_234567.conf
└── charlie_20250107_101112.conf
```

### Share Configuration with Users

**Method 1: Send the file directly**
```bash
# Email or send via secure channel
cat ./vpn_clients/alice_20250106_123456.conf
```

**Method 2: Generate QR code (for mobile)**
```bash
# Install qrencode
brew install qrencode  # macOS
# apt install qrencode  # Linux

# Generate QR code
qrencode -t ansiutf8 < ./vpn_clients/alice_20250106_123456.conf
```

User can scan the QR code with their mobile WireGuard app.

## Common Workflows

### Onboarding a New User

1. **Add user:**
   ```bash
   ./capybara.py user add john --description "John Doe - Engineering"
   ```

2. **Send config file to user:**
   ```bash
   # The config file path is shown in output
   cat ./vpn_clients/john_TIMESTAMP.conf
   ```

3. **Verify connection:**
   ```bash
   ./capybara.py user list
   # Check if user appears and is connected
   ```

### Troubleshooting User Connection

1. **Check server status:**
   ```bash
   ./capybara.py server status
   ```

2. **Check user details:**
   ```bash
   ./capybara.py user list --detailed
   ```

3. **View live monitoring:**
   ```bash
   ./capybara.py stats live
   ```

4. **Restart server if needed:**
   ```bash
   ./capybara.py server restart
   ```

### Managing Bandwidth Abusers

1. **Monitor usage:**
   ```bash
   ./capybara.py stats live
   # Watch for users with excessive transfer
   ```

2. **Block the user:**
   ```bash
   ./capybara.py user block alice
   ```

3. **Or remove completely:**
   ```bash
   ./capybara.py user remove alice
   ```

### Blocking Content

1. **Block social media:**
   ```bash
   ./capybara.py block add facebook.com
   ./capybara.py block add twitter.com
   ./capybara.py block add instagram.com
   ```

2. **Block specific IPs:**
   ```bash
   ./capybara.py block add 1.2.3.4 --type ip
   ```

3. **Review blocks:**
   ```bash
   ./capybara.py block list
   ```

## Advanced Usage

### Using SSH Keys Instead of Password

Edit `~/.capybara_config.yaml`:

```yaml
server:
  host: 66.42.119.38
  port: 22
  username: root
  key_file: /Users/pasha/.ssh/vpn_server_key
  # Remove or comment out password:
  # password: H7)a4(72PGSnN4Hh
```

### Automation with Cron

Monitor and send daily reports:

```bash
# Add to crontab
crontab -e

# Daily stats report at 9 AM
0 9 * * * /usr/bin/python3 /Users/pasha/PycharmProjects/o/capybara.py user list > /tmp/vpn_daily_report.txt && mail -s "VPN Daily Report" you@example.com < /tmp/vpn_daily_report.txt
```

### Scripting

```python
#!/usr/bin/env python3
import subprocess
import json

# Get user list programmatically
result = subprocess.run(
    ['./capybara.py', 'user', 'list'],
    capture_output=True,
    text=True
)

print(result.stdout)
```

## Troubleshooting

### Connection Issues

**Problem:** `Failed to connect to server`

**Solution:**
1. Check server is accessible:
   ```bash
   ssh root@66.42.119.38
   ```

2. Verify credentials in config:
   ```bash
   ./capybara.py config
   ```

3. Check firewall allows SSH (port 22)

### Permission Errors

**Problem:** Permission denied errors

**Solution:**
```bash
chmod +x capybara.py
# Or ensure Python has correct permissions
python3 capybara.py user list
```

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'paramiko'`

**Solution:**
```bash
pip3 install -r requirements.txt
# Or install individually
pip3 install paramiko click pyyaml tabulate colorama
```

### Config File Issues

**Problem:** Configuration errors

**Solution:**
```bash
# Delete and recreate config
rm ~/.capybara_config.yaml
./capybara.py config
# Edit with correct values
nano ~/.capybara_config.yaml
```

## Security Considerations

1. **Protect Config File:**
   ```bash
   chmod 600 ~/.capybara_config.yaml
   ```

2. **Use SSH Keys:** Prefer SSH key authentication over passwords

3. **Secure Client Configs:** Delete client config files after sharing:
   ```bash
   rm ./vpn_clients/old_user_*.conf
   ```

4. **Regular Audits:** Regularly review users:
   ```bash
   ./capybara.py user list
   ```

5. **Monitor Activity:** Use live monitoring to detect suspicious activity:
   ```bash
   ./capybara.py stats live
   ```

## File Locations

| File/Directory | Purpose |
|---|---|
| `capybara.py` | Main script |
| `requirements.txt` | Python dependencies |
| `~/.capybara_config.yaml` | Configuration file |
| `./vpn_clients/` | Generated client configurations |
| `/etc/wireguard/clients/` | Client keys on server |
| `/var/log/vpn_blocks.log` | Block/unblock log on server |

## Server-Side Changes

The tool makes the following changes to your VPN server:

1. **Directory Creation:**
   - `/etc/wireguard/clients/` - Stores client keys

2. **File Modifications:**
   - `/etc/wireguard/wg0.conf` - Adds/removes peer configurations
   - Creates backups before modifications

3. **iptables Rules:**
   - Adds REJECT rules for blocked resources
   - Saves rules to persist across reboots

4. **Log Files:**
   - `/var/log/vpn_blocks.log` - Tracks blocked resources

## Examples

### Complete User Lifecycle

```bash
# 1. Add user
./capybara.py user add alice --description "Alice Johnson - Remote Team"

# 2. Share config file
cat ./vpn_clients/alice_20250106_120000.conf

# 3. Monitor connection
./capybara.py stats live

# 4. After some time, check usage
./capybara.py user list --detailed

# 5. Block if needed
./capybara.py user block alice

# 6. Or remove
./capybara.py user remove alice
```

### Daily Monitoring Routine

```bash
# Morning check
./capybara.py server status
./capybara.py user list

# Review stats
./capybara.py stats show

# Check for issues with live monitoring
./capybara.py stats live --interval 10
```

### Content Filtering Setup

```bash
# Block social media
./capybara.py block add facebook.com
./capybara.py block add instagram.com
./capybara.py block add twitter.com
./capybara.py block add tiktok.com

# Block gambling sites
./capybara.py block add bet365.com
./capybara.py block add pokerstars.com

# Block specific IPs
./capybara.py block add 1.2.3.4 --type ip

# Review all blocks
./capybara.py block list
```

## Comparison with Manual Management

| Task | Manual (SSH) | Capybara |
|---|---|---|
| Add user | 8-10 commands | 1 command |
| View active users | Parse wg output | Pretty table |
| Monitor connections | Multiple commands | Live dashboard |
| Block domain | Complex iptables | 1 command |
| Generate client config | Manual editing | Automatic |

## Future Enhancements

Potential features for future versions:

- Web dashboard
- Email notifications for new connections
- Bandwidth limits per user
- Traffic analytics and graphs
- Multi-server management
- Backup and restore
- User expiration dates
- Two-factor authentication

## Contributing

This is a personal tool, but feel free to extend it for your needs!

## License

Free to use and modify for personal use.

---

**Created:** 2025-01-06
**Version:** 1.0.0
**Author:** VPN Management Team
