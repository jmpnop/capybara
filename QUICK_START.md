# Capybara - Quick Start Guide

## Installation (One-Time Setup)

```bash
cd /path/to
pip3 install -r requirements.txt
chmod +x capybara.py
```

## Quick Reference

### Most Common Commands

```bash
# Add a new VPN user
./capybara.py user add alice --description "Alice Johnson"

# List all users
./capybara.py user list

# Remove a user
./capybara.py user remove alice

# Check server status
./capybara.py server status

# View statistics
./capybara.py stats show

# Live monitoring
./capybara.py stats live
```

## Daily Usage Workflow

### 1. Morning Check

```bash
# Quick health check
./capybara.py server status

# See who's connected
./capybara.py user list
```

### 2. Add New User

```bash
# Create new user
./capybara.py user add bob --description "Bob from Sales"

# Config file will be created in ./vpn_clients/
# Send this file to the user
```

### 3. Monitor Activity

```bash
# Real-time monitoring
./capybara.py stats live --interval 5

# Press Ctrl+C to exit
```

### 4. Troubleshooting

```bash
# Detailed user info
./capybara.py user list --detailed

# Restart if needed
./capybara.py server restart
```

## User Management Examples

### Add Multiple Users

```bash
./capybara.py user add alice --description "Remote Team - Engineering"
./capybara.py user add bob --description "Remote Team - Marketing"
./capybara.py user add charlie --description "Contractor - 3 months"
```

### View All Users with Details

```bash
./capybara.py user list --detailed
```

### Block Problem User

```bash
./capybara.py user block alice
```

### Remove User Permanently

```bash
./capybara.py user remove bob
```

## Content Filtering

### Block Websites

```bash
# Block social media
./capybara.py block add facebook.com
./capybara.py block add instagram.com
./capybara.py block add twitter.com
```

### Block IP Addresses

```bash
./capybara.py block add 1.2.3.4 --type ip
./capybara.py block add 192.168.100.0/24 --type ip
```

### View Blocked Resources

```bash
./capybara.py block list
```

### Unblock Resource

```bash
./capybara.py block remove facebook.com
```

## Monitoring & Stats

### Quick Stats

```bash
./capybara.py stats show
```

**Shows:**
- Server uptime
- Total users
- Active connections
- System resources
- WireGuard interface status

### Live Dashboard

```bash
./capybara.py stats live
```

**Features:**
- Auto-refreshing (default 5 seconds)
- Active connections
- Real-time bandwidth
- Press Ctrl+C to exit

**Custom refresh interval:**
```bash
./capybara.py stats live --interval 10
```

## Server Management

### Check Status

```bash
./capybara.py server status
```

**Verifies:**
- WireGuard running
- udp2raw running
- System uptime

### Stop Server

```bash
./capybara.py server stop
```

**When to stop:**
- Maintenance
- Troubleshooting
- Before making server changes

### Start Server

```bash
./capybara.py server start
```

**When to start:**
- After maintenance
- After stopping for troubleshooting

### Restart Server

```bash
./capybara.py server restart
```

**When to restart:**
- After configuration changes
- If udp2raw stops
- Connection issues

## Configuration

### View Config

```bash
./capybara.py config
```

### Edit Config

```bash
nano ~/.capybara_config.yaml
```

## Client Setup (What to Tell Users)

When you add a user, you get a config file. Send this to your user along with these instructions:

### macOS Setup

1. **Download udp2raw:**
   - Go to: https://github.com/wangyu-/udp2raw/releases
   - Download for Mac (Intel or Apple Silicon)

2. **Run udp2raw:**
   ```bash
   ./udp2raw -c -l 127.0.0.1:4096 -r YOUR_SERVER_IP:443 -k YOUR_UDP2RAW_PASSWORD --raw-mode faketcp --cipher-mode xor --auth-mode hmac_sha1 -a --fix-gro
   ```
   Keep this running in a terminal window.

3. **Install WireGuard:**
   - Mac App Store: "WireGuard"

4. **Import Config:**
   - Open WireGuard app
   - Click "+"
   - Import the .conf file you received

5. **Connect:**
   - Click "Activate"
   - Test: Visit https://ifconfig.me to see your VPN IP

## Common Issues & Solutions

### "Failed to connect to server"

```bash
# Test SSH connection
ssh root@YOUR_SERVER_IP

# Check config
./capybara.py config
```

### "No module named 'paramiko'"

```bash
# Install dependencies
pip3 install -r requirements.txt
```

### User can't connect

```bash
# Check server is running
./capybara.py server status

# View user details
./capybara.py user list --detailed

# Restart if needed
./capybara.py server restart
```

## Tips & Tricks

### Create Alias for Easy Access

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias vpn="python3 /path/to/capybara.py"
```

Then use simply:
```bash
vpn user list
vpn stats show
vpn user add newuser
```

### Monitor in Background

```bash
# Run live monitoring in tmux/screen
tmux new -s vpn-monitor
./capybara.py stats live
# Press Ctrl+B, then D to detach
# Reattach: tmux attach -t vpn-monitor
```

### Quick User Audit

```bash
# See all users with transfer stats
./capybara.py user list | grep -v "Never connected"
```

### Backup User List

```bash
./capybara.py user list --detailed > vpn_users_backup_$(date +%Y%m%d).txt
```

## Security Checklist

- [ ] Change default server password in config
- [ ] Use SSH keys instead of password
- [ ] Regularly review user list
- [ ] Monitor for unusual bandwidth usage
- [ ] Delete old client config files
- [ ] Keep server updated
- [ ] Review blocked resources list

## Getting Help

### Show All Commands

```bash
./capybara.py --help
```

### Command-Specific Help

```bash
./capybara.py user --help
./capybara.py stats --help
./capybara.py block --help
./capybara.py server --help
```

## File Locations

| Location | Contents |
|---|---|
| `~/.capybara_config.yaml` | Configuration |
| `./vpn_clients/` | Generated client configs |
| `/etc/wireguard/wg0.conf` | Server config (on VPN server) |
| `/etc/wireguard/clients/` | Client keys (on VPN server) |

## Next Steps

1. **Read full documentation:** `VPN_MANAGER_README.md`
2. **Server setup guide:** `CLAUDE.md`
3. **Test with a user:** Add yourself as a test user and connect

---

**Quick Help:** `./capybara.py --help`
**Version:** 1.0.0
