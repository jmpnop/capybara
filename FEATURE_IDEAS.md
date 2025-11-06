# Capybara - Additional Feature Ideas

Useful VPN server parameters and management features that make sense to manage remotely via SSH.

## 🔥 High Priority Features

### 1. **Logs Management**
View server logs for troubleshooting and monitoring.

```bash
capybara.py logs show                    # Show recent logs
capybara.py logs show --lines 100        # Show last 100 lines
capybara.py logs wireguard               # WireGuard specific logs
capybara.py logs udp2raw                 # udp2raw specific logs
capybara.py logs system                  # System logs
capybara.py logs clear                   # Clear old logs
capybara.py logs tail                    # Follow logs in real-time
```

**Use Cases:**
- Debug connection issues
- Monitor for errors
- Track security events
- Investigate performance problems

**Implementation:**
```python
def view_logs(self, service='all', lines=50, follow=False):
    """View server logs"""
    if service == 'wireguard':
        cmd = f"journalctl -u wg-quick@{self.interface} -n {lines}"
    elif service == 'udp2raw':
        cmd = f"tail -n {lines} /var/log/udp2raw.log"
    elif service == 'system':
        cmd = f"dmesg | tail -n {lines}"
```

---

### 2. **Service Management**
Manage individual services separately.

```bash
capybara.py service status               # Status of all services
capybara.py service restart udp2raw      # Restart just udp2raw
capybara.py service restart wireguard    # Restart just WireGuard
capybara.py service restart firewall     # Restart firewall
```

**Why Useful:**
- udp2raw might crash while WireGuard is fine
- Restart only what's needed
- Less disruptive to users

---

### 3. **Connection Management**
Manage active connections.

```bash
capybara.py connection list              # List active connections
capybara.py connection kick alice        # Disconnect user immediately
capybara.py connection kick 10.7.0.2     # Disconnect by IP
capybara.py connection kick-all          # Disconnect all users
```

**Use Cases:**
- Emergency disconnect
- Force user to reconnect
- Clear stuck connections
- Immediate enforcement of policy changes

---

### 4. **Backup & Restore**
Backup configurations and user data.

```bash
capybara.py backup create                # Create backup
capybara.py backup create --name "before-upgrade"
capybara.py backup list                  # List all backups
capybara.py backup restore <backup-id>   # Restore from backup
capybara.py backup download <backup-id>  # Download backup locally
capybara.py backup delete <backup-id>    # Delete old backup
```

**What Gets Backed Up:**
- WireGuard configuration
- All user keys
- Firewall rules
- Block list
- Server keys

---

### 5. **User Quotas & Limits**
Set data limits and bandwidth throttling.

```bash
capybara.py user quota alice --limit 10GB      # Monthly data limit
capybara.py user quota alice --bandwidth 5Mbps # Speed limit
capybara.py user quota list                    # Show all quotas
capybara.py user quota alice --reset           # Reset usage counter
capybara.py user expire alice --days 30        # Auto-expire in 30 days
```

**Use Cases:**
- Prevent bandwidth abuse
- Trial accounts with limits
- Fair usage policies
- Temporary access

---

### 6. **Network Diagnostics**
Test connectivity and troubleshoot network issues.

```bash
capybara.py diag ping <user>             # Ping user's VPN IP
capybara.py diag ping 10.7.0.2           # Ping specific IP
capybara.py diag traceroute <target>     # Traceroute from server
capybara.py diag ports                   # Show listening ports
capybara.py diag dns                     # Test DNS resolution
capybara.py diag bandwidth               # Test bandwidth
capybara.py diag handshake alice         # Show handshake status
```

**Why Useful:**
- Verify user connectivity
- Troubleshoot routing issues
- Check if ports are open
- Diagnose DNS problems

---

### 7. **Firewall Rules**
View and manage firewall rules directly.

```bash
capybara.py firewall list                # List all rules
capybara.py firewall list --nat          # Show NAT rules
capybara.py firewall list --forward      # Show forward rules
capybara.py firewall allow-port 8080     # Open specific port
capybara.py firewall block-port 8080     # Close specific port
capybara.py firewall reset               # Reset to default
```

---

### 8. **Reports & Analytics**
Generate usage reports.

```bash
capybara.py report daily                 # Daily usage report
capybara.py report weekly                # Weekly summary
capybara.py report user alice            # Specific user report
capybara.py report export --format csv   # Export to CSV
capybara.py report email admin@example.com  # Email report
```

**Report Contents:**
- Total users
- Active users
- Bandwidth per user
- Connection times
- Top bandwidth users
- Failed connections

---

### 9. **Key Management**
Manage encryption keys.

```bash
capybara.py keys rotate                  # Rotate server keys
capybara.py keys backup                  # Backup all keys
capybara.py keys generate-psk            # Generate pre-shared key
capybara.py keys show server             # Show server public key
capybara.py keys show alice              # Show user's public key
```

**Security Benefits:**
- Regular key rotation
- Recover from key compromise
- Enhanced security with PSK

---

### 10. **Maintenance Mode**
Put server in maintenance mode.

```bash
capybara.py maintenance enable           # Enable maintenance mode
capybara.py maintenance disable          # Disable maintenance mode
capybara.py maintenance status           # Check if in maintenance
```

**Features:**
- Disconnect all users
- Block new connections
- Display maintenance message
- Allow admin access only

---

## 🔧 Medium Priority Features

### 11. **System Health**
Monitor server health and resources.

```bash
capybara.py health check                 # Overall health check
capybara.py health cpu                   # CPU usage
capybara.py health memory                # Memory usage
capybara.py health disk                  # Disk space
capybara.py health network               # Network stats
```

---

### 12. **Update Management**
Manage system updates.

```bash
capybara.py update check                 # Check for updates
capybara.py update system                # Update system packages
capybara.py update wireguard             # Update WireGuard
capybara.py update capybara              # Update this tool
```

---

### 13. **Port Management**
Manage VPN ports.

```bash
capybara.py port show                    # Show current ports
capybara.py port change 443 --to 8443    # Change obfuscation port
capybara.py port test 443                # Test if port is accessible
```

---

### 14. **DNS Management**
Manage DNS settings for VPN clients.

```bash
capybara.py dns show                     # Show current DNS servers
capybara.py dns set 1.1.1.1 8.8.8.8      # Set DNS servers
capybara.py dns test                     # Test DNS resolution
```

---

### 15. **User Groups**
Organize users into groups.

```bash
capybara.py group create engineering     # Create group
capybara.py group add alice engineering  # Add user to group
capybara.py group list                   # List all groups
capybara.py group remove alice engineering  # Remove from group
capybara.py group delete engineering     # Delete group
```

---

### 16. **Rate Limiting**
Protect against abuse.

```bash
capybara.py ratelimit enable             # Enable rate limiting
capybara.py ratelimit set --connections 100  # Max connections
capybara.py ratelimit set --bandwidth 100Mbps  # Max bandwidth
```

---

### 17. **Geo-Blocking**
Block connections from specific countries.

```bash
capybara.py geoblock add CN              # Block China
capybara.py geoblock add RU              # Block Russia
capybara.py geoblock list                # List blocked countries
capybara.py geoblock remove CN           # Unblock
```

---

### 18. **IP Whitelist/Blacklist**
Control which IPs can connect.

```bash
capybara.py whitelist add 1.2.3.4        # Allow only this IP
capybara.py whitelist list               # Show whitelist
capybara.py blacklist add 1.2.3.4        # Block specific IP
capybara.py blacklist list               # Show blacklist
```

---

### 19. **Session History**
Track connection history.

```bash
capybara.py history show                 # Show all sessions
capybara.py history show alice           # Show user's sessions
capybara.py history export               # Export to file
capybara.py history clear --older-than 30d  # Clear old history
```

---

### 20. **Configuration Templates**
Save and apply configuration templates.

```bash
capybara.py template save current        # Save current config
capybara.py template list                # List templates
capybara.py template apply strict        # Apply strict template
capybara.py template apply open          # Apply open template
```

---

## 💡 Nice-to-Have Features

### 21. **Multi-Factor Authentication**
Require 2FA for VPN access.

```bash
capybara.py mfa enable alice             # Enable MFA for user
capybara.py mfa disable alice            # Disable MFA
capybara.py mfa reset alice              # Reset MFA codes
```

---

### 22. **Webhook Notifications**
Send notifications on events.

```bash
capybara.py webhook add <url> --event user-connect
capybara.py webhook add <url> --event user-disconnect
capybara.py webhook add <url> --event quota-exceeded
capybara.py webhook list
```

---

### 23. **Load Balancing**
Manage multiple VPN servers.

```bash
capybara.py cluster add server2          # Add server to cluster
capybara.py cluster balance              # Balance users
capybara.py cluster status               # Show cluster status
```

---

### 24. **API Access**
Expose management API.

```bash
capybara.py api enable                   # Enable REST API
capybara.py api token create             # Create API token
capybara.py api docs                     # Show API documentation
```

---

### 25. **Scheduled Tasks**
Automate recurring tasks.

```bash
capybara.py schedule add "backup create" --cron "0 2 * * *"
capybara.py schedule add "report daily" --cron "0 9 * * *"
capybara.py schedule list
```

---

## 📊 Most Requested Features (Priority Order)

Based on typical VPN management needs:

1. **Logs Management** ⭐⭐⭐⭐⭐
   - Essential for troubleshooting
   - Most frequently needed

2. **Connection Management (Kick User)** ⭐⭐⭐⭐⭐
   - Critical for security
   - Immediate action capability

3. **Backup & Restore** ⭐⭐⭐⭐⭐
   - Disaster recovery
   - Peace of mind

4. **Network Diagnostics** ⭐⭐⭐⭐
   - Troubleshooting tool
   - Very useful for support

5. **Service Management** ⭐⭐⭐⭐
   - Restart individual services
   - Less disruptive

6. **User Quotas & Limits** ⭐⭐⭐⭐
   - Prevent abuse
   - Fair usage

7. **Reports & Analytics** ⭐⭐⭐
   - Business intelligence
   - Usage tracking

8. **Firewall Rules** ⭐⭐⭐
   - Security management
   - Advanced users

9. **System Health** ⭐⭐⭐
   - Proactive monitoring
   - Capacity planning

10. **Maintenance Mode** ⭐⭐⭐
    - Controlled downtime
    - Update safety

---

## 🚀 Implementation Roadmap

### Phase 1 (Immediate Value)
- ✅ User management (done)
- ✅ Server start/stop/restart (done)
- ✅ Statistics (done)
- ✅ Resource blocking (done)
- 🔲 **Logs management**
- 🔲 **Connection kick**
- 🔲 **Service management**

### Phase 2 (Enhanced Operations)
- 🔲 Backup & restore
- 🔲 Network diagnostics
- 🔲 User quotas
- 🔲 Reports

### Phase 3 (Advanced Features)
- 🔲 Firewall management
- 🔲 Key rotation
- 🔲 Maintenance mode
- 🔲 System health

### Phase 4 (Enterprise Features)
- 🔲 User groups
- 🔲 Session history
- 🔲 API access
- 🔲 Webhooks

---

## 🎯 Recommended Next Steps

If you want to enhance Capybara, I recommend implementing in this order:

### Top 3 Most Useful
1. **Logs Management** - Essential for troubleshooting
2. **Kick User** - Security and immediate control
3. **Backup/Restore** - Disaster recovery

### Commands to Add First

```bash
# Logs (Most Important)
capybara.py logs show
capybara.py logs wireguard
capybara.py logs udp2raw
capybara.py logs tail

# Connection Control (Critical)
capybara.py connection list
capybara.py connection kick <user>
capybara.py connection kick-all

# Backup (Essential)
capybara.py backup create
capybara.py backup list
capybara.py backup restore <id>

# Diagnostics (Very Useful)
capybara.py diag ping <user>
capybara.py diag ports
capybara.py diag handshake <user>

# Service Management (Practical)
capybara.py service status
capybara.py service restart udp2raw
capybara.py service restart wireguard
```

---

## 💭 Questions to Consider

1. **What's your typical use case?**
   - Personal VPN: Focus on simplicity
   - Small team: Add quotas and reports
   - Business: Need full audit trail

2. **What problems do you face most often?**
   - Connection issues → Add diagnostics
   - Bandwidth abuse → Add quotas
   - Security concerns → Add logging and kick

3. **How many users will you manage?**
   - 1-10: Current features sufficient
   - 10-50: Add quotas and groups
   - 50+: Need automation and API

4. **Do you need compliance/auditing?**
   - Yes: Add session history, audit logs
   - No: Current features fine

---

## 🤔 Which Features Do You Want?

Let me know which features would be most useful for your use case, and I can implement them! The most impactful ones that I'd recommend:

**Tier 1 (Implement First):**
- Logs management
- Kick user/connection control
- Backup & restore

**Tier 2 (High Value):**
- Network diagnostics
- Service management (restart individual services)
- User quotas

**Tier 3 (Advanced):**
- Reports & analytics
- Firewall rules
- System health monitoring

Which direction would you like to go?
