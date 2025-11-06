# Capybara Command Cheatsheet

Quick reference for all capybara.py commands.

## Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Make executable
chmod +x capybara.py

# Create alias (optional)
alias vpn="python3 /Users/pasha/PycharmProjects/o/capybara.py"
```

## User Commands

### Add User
```bash
./capybara.py user add <username>
./capybara.py user add <username> --description "Description"
./capybara.py user add alice
./capybara.py user add bob --description "Sales Team"
```

### List Users
```bash
./capybara.py user list                    # Simple table
./capybara.py user list --detailed         # Full details
./capybara.py user list -d                 # Short flag
```

### Remove User
```bash
./capybara.py user remove <identifier>
./capybara.py user remove alice            # By username
./capybara.py user remove 10.7.0.2         # By IP
```

### Block User
```bash
./capybara.py user block <identifier>
./capybara.py user block alice             # By username
./capybara.py user block 10.7.0.2          # By IP
```

## Statistics Commands

### Show Stats
```bash
./capybara.py stats show                   # Current statistics
```

### Live Monitoring
```bash
./capybara.py stats live                   # Live (5s refresh)
./capybara.py stats live --interval 10     # Custom interval
./capybara.py stats live -i 3              # Short flag
# Press Ctrl+C to exit
```

## Block Commands

### Block Domain
```bash
./capybara.py block add <domain>
./capybara.py block add facebook.com
./capybara.py block add instagram.com --type domain
```

### Block IP
```bash
./capybara.py block add <ip> --type ip
./capybara.py block add 1.2.3.4 --type ip
./capybara.py block add 192.168.1.0/24 --type ip
```

### List Blocked
```bash
./capybara.py block list
```

### Unblock
```bash
./capybara.py block remove <resource>
./capybara.py block remove facebook.com
./capybara.py block remove 1.2.3.4 --type ip
```

## Server Commands

### Check Status
```bash
./capybara.py server status
```

### Stop Server
```bash
./capybara.py server stop
```

### Start Server
```bash
./capybara.py server start
```

### Restart Server
```bash
./capybara.py server restart
```

## Configuration

### View Config
```bash
./capybara.py config
```

### Edit Config
```bash
nano ~/.capybara_config.yaml
vi ~/.capybara_config.yaml
```

## General Commands

### Help
```bash
./capybara.py --help                       # Main help
./capybara.py user --help                  # User commands help
./capybara.py stats --help                 # Stats commands help
./capybara.py block --help                 # Block commands help
./capybara.py server --help                # Server commands help
```

### Version
```bash
./capybara.py --version
```

## Common Workflows

### Onboard New User
```bash
# 1. Add user
./capybara.py user add alice --description "Remote Worker"

# 2. Config file created at:
#    ./vpn_clients/alice_TIMESTAMP.conf

# 3. Send config to user

# 4. Verify connection
./capybara.py user list
```

### Daily Health Check
```bash
./capybara.py server status
./capybara.py user list
./capybara.py stats show
```

### Investigate Problem User
```bash
./capybara.py user list --detailed
./capybara.py stats live
# If needed:
./capybara.py user block alice
# Or:
./capybara.py user remove alice
```

### Setup Content Filtering
```bash
./capybara.py block add facebook.com
./capybara.py block add instagram.com
./capybara.py block add twitter.com
./capybara.py block add tiktok.com
./capybara.py block list
```

### Troubleshoot Connection
```bash
./capybara.py server status
./capybara.py stats show
./capybara.py user list --detailed
./capybara.py server restart  # If needed
```

## Output Examples

### user list (simple)
```
+----------+------------+-------------------+----------------+-------+-------+
| Username | IP Address | Endpoint          | Last Handshake | RX    | TX    |
+----------+------------+-------------------+----------------+-------+-------+
| alice    | 10.7.0.2   | 192.168.1.10:1234 | 2 minutes ago  | 15 MB | 8 MB  |
| bob      | 10.7.0.3   | Never connected   | Never          | 0 B   | 0 B   |
+----------+------------+-------------------+----------------+-------+-------+
```

### user list --detailed
```
============================================================
User: alice
============================================================
IP Address:      10.7.0.2
Created:         20250106_123456
Description:     Remote Worker
Public Key:      kkFtFxmLRVNguNO/xx9avIaK5p8cmVEsYiBD1HhZ...
Endpoint:        192.168.1.10:1234
Last Handshake:  2 minutes ago
Data RX:         15 MB
Data TX:         8 MB
```

### server status
```
============================================================
VPN Server Status
============================================================

Overall Status:      RUNNING
WireGuard:           Running
udp2raw:             Running
Server:              66.42.119.38
Interface:           wg0
Uptime:              up 2 days, 5 hours
```

### stats show
```
============================================================
VPN Server Statistics
============================================================

Server Status:
  Uptime:              up 2 days, 5 hours
  Total Users:         5
  Active Connections:  3
  udp2raw Running:     Yes

System Resources:
  Mem:         960.1M    57.8M    830.0M    372.0K    72.2M    796.4M

WireGuard Interface:
interface: wg0
  public key: D1m+SC4pa0UDNLXcKb/+cWO1rMXgvEQYl1CZlEFD/1A=
  ...
```

### stats live
```
============================================================
VPN Server Live Monitor (Updates every 5s)
============================================================

Server: 66.42.119.38
Uptime: up 2 days, 5 hours
Total Users: 5 | Active: 3

Active Connections:
User     IP         Endpoint              RX      TX
alice    10.7.0.2   192.168.1.10:1234     15 MB   8 MB
bob      10.7.0.3   203.0.113.45:5678     102 MB  45 MB

Press Ctrl+C to exit
```

## Error Messages & Solutions

### "Failed to connect to server"
```bash
# Check SSH access
ssh root@66.42.119.38

# Verify config
./capybara.py config

# Edit if needed
nano ~/.capybara_config.yaml
```

### "No module named 'paramiko'"
```bash
pip3 install -r requirements.txt
```

### "User not found"
```bash
# List all users to see exact names/IPs
./capybara.py user list
```

### "Permission denied"
```bash
chmod +x capybara.py
# Or use:
python3 capybara.py <command>
```

## Advanced Usage

### Batch Operations
```bash
# Add multiple users
for user in alice bob charlie dave; do
    ./capybara.py user add $user --description "Team Member"
done

# Block multiple domains
for site in facebook.com instagram.com twitter.com; do
    ./capybara.py block add $site
done
```

### Scripting
```python
import subprocess

# Add user programmatically
subprocess.run(['./capybara.py', 'user', 'add', 'alice'])

# Get stats
result = subprocess.run(
    ['./capybara.py', 'user', 'list'],
    capture_output=True,
    text=True
)
print(result.stdout)
```

### Monitoring with tmux
```bash
# Start monitoring session
tmux new -s vpn-monitor "./capybara.py stats live"

# Detach: Ctrl+B, then D

# Reattach later
tmux attach -t vpn-monitor
```

### Export User List
```bash
# Save to file
./capybara.py user list > users_$(date +%Y%m%d).txt

# With details
./capybara.py user list --detailed > users_detailed_$(date +%Y%m%d).txt
```

## Keyboard Shortcuts

### In Live Monitoring
- `Ctrl+C` - Exit monitoring

### In Terminal
- `Ctrl+C` - Cancel current command
- `Ctrl+Z` - Suspend (use `fg` to resume)
- `Up Arrow` - Previous command
- `Tab` - Auto-complete

## File Locations Quick Reference

```
~/.capybara_config.yaml       # Local config
./vpn_clients/                   # Generated configs (local)
/etc/wireguard/wg0.conf          # Server config (remote)
/etc/wireguard/clients/          # Client keys (remote)
/var/log/vpn_blocks.log          # Block log (remote)
```

## Configuration File Structure

```yaml
server:
  host: 66.42.119.38
  port: 22
  username: root
  password: your_password
  # Or use key:
  # key_file: /path/to/key

vpn:
  interface: wg0
  config_path: /etc/wireguard/wg0.conf
  network: 10.7.0.0/24
  server_ip: 10.7.0.1
  next_client_ip: 2
```

## Tips

1. **Always verify before removing:**
   ```bash
   ./capybara.py user list --detailed  # Check first
   ./capybara.py user remove alice     # Then remove
   ```

2. **Use live monitoring for troubleshooting:**
   ```bash
   ./capybara.py stats live
   ```

3. **Block testing:**
   ```bash
   ./capybara.py block add testsite.com
   # Test from VPN client
   ./capybara.py block remove testsite.com
   ```

4. **Regular backups:**
   ```bash
   # Weekly backup
   ./capybara.py user list --detailed > backup_weekly.txt
   ```

5. **Monitor after changes:**
   ```bash
   ./capybara.py user add newuser
   ./capybara.py stats live  # Watch for connection
   ```

## Color Coding (Terminal Output)

- 🟢 **Green** - Success, running, active
- 🔴 **Red** - Error, stopped, failed
- 🟡 **Yellow** - Warning, information, processing
- 🔵 **Cyan** - Headers, titles, info

---

**Quick Help:** `./capybara.py --help`
**Full Documentation:** `VPN_MANAGER_README.md`
**Quick Start:** `QUICK_START.md`
