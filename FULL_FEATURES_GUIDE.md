# Capybara - Full Features Guide

Complete guide for all Capybara VPN management features (Option C - Full Featured Implementation).

## 🎉 New Features Added

### ✅ **Logs Management**
View and monitor server logs in real-time

### ✅ **Connection Control**
Disconnect users immediately for security or troubleshooting

### ✅ **Service Management**
Restart individual services without full server restart

### ✅ **Backup & Restore**
Complete backup and disaster recovery system

### ✅ **Network Diagnostics**
Test connectivity and troubleshoot issues

### ✅ **System Health**
Monitor CPU, memory, disk, and network

### ✅ **Reports & Analytics**
Generate usage reports in multiple formats

---

## 📋 Complete Command Reference

### 1. Logs Management

#### View Recent Logs
```bash
# Show all logs (default 50 lines)
./capybara.py logs show

# Show specific service logs
./capybara.py logs show --service wireguard
./capybara.py logs show --service udp2raw
./capybara.py logs show --service system

# Show more lines
./capybara.py logs show --lines 100
./capybara.py logs show -n 200

# Combine options
./capybara.py logs show --service udp2raw --lines 20
```

#### Follow Logs in Real-Time
```bash
# Follow udp2raw logs (default)
./capybara.py logs tail

# Follow specific service
./capybara.py logs tail --service wireguard
./capybara.py logs tail --service udp2raw
./capybara.py logs tail --service system

# Press Ctrl+C to stop
```

**Use Cases:**
- Debug connection problems
- Monitor for errors
- Track security events
- Investigate performance issues

**Example Output:**
```
=== udp2raw Logs ===
[2025-11-06 07:30:50][INFO] received syn, sent syn ack back
[2025-11-06 07:30:54][INFO] connection established
[2025-11-06 07:31:10][INFO] data transfer active

=== WireGuard Logs ===
Nov 06 08:30:15 wg-quick[1234]: [#] wg0 up
Nov 06 08:30:15 wg-quick[1234]: Interface configured successfully
```

---

### 2. Connection Management

#### List Active Connections
```bash
./capybara.py connection list
```

**Example Output:**
```
Active Connections:
+----------+------------+-------------------------+-------------------+
| Username | IP         | Endpoint                | Last Handshake    |
+==========+============+=========================+===================+
| alice    | 10.7.0.2   | 192.168.1.100:54321     | 2 minutes ago     |
| bob      | 10.7.0.3   | 203.0.113.45:41234      | 5 minutes ago     |
+----------+------------+-------------------------+-------------------+

Total: 2
```

#### Disconnect a User
```bash
# By username
./capybara.py connection kick alice

# By IP
./capybara.py connection kick 10.7.0.2

# Confirmation required
```

**What Happens:**
1. User is immediately disconnected
2. Temporarily blocked for 5 seconds
3. Can reconnect after block expires

**Use Cases:**
- Security incident response
- Force user to get new config
- Clear stuck connections
- Immediate policy enforcement

#### Disconnect All Users
```bash
./capybara.py connection kick-all
```

**Use Cases:**
- Emergency shutdown
- Server maintenance
- Configuration changes
- Security breach response

---

### 3. Service Management

#### Check All Services
```bash
./capybara.py service status
```

**Example Output:**
```
============================================================
Service Status
============================================================

Wireguard       RUNNING
Udp2raw         RUNNING
Firewall        STOPPED
```

#### Restart Individual Service
```bash
# Restart just WireGuard
./capybara.py service restart wireguard

# Restart just udp2raw
./capybara.py service restart udp2raw

# Restart firewall
./capybara.py service restart firewall
```

**Advantages:**
- Less disruptive than full server restart
- Faster recovery
- Target specific issues
- Keep other services running

**When to Use:**
- udp2raw crashes but WireGuard is fine
- WireGuard config changes
- Firewall rule updates
- Troubleshooting specific service

---

### 4. Backup & Restore

#### Create Backup
```bash
# Auto-named backup (backup_TIMESTAMP)
./capybara.py backup create

# Custom name
./capybara.py backup create --name before-upgrade
./capybara.py backup create -n friday-backup
```

**What Gets Backed Up:**
- WireGuard configuration (/etc/wireguard/wg0.conf)
- All encryption keys (server and clients)
- Client keys directory
- iptables firewall rules
- Awall configuration
- Metadata (timestamp, server info)

**Example Output:**
```
Creating backup 'before-upgrade'...
✓ Backup created: before-upgrade.tar.gz

Backup saved to: /root/vpn_backups/before-upgrade.tar.gz
```

#### List All Backups
```bash
./capybara.py backup list
```

**Example Output:**
```
Available Backups:
+------------------+--------+-------------+
| Name             | Size   | Date        |
+==================+========+=============+
| before-upgrade   | 2.2K   | Nov 6 08:30 |
| friday-backup    | 2.1K   | Nov 5 18:00 |
| test_backup      | 2.2K   | Nov 6 08:44 |
+------------------+--------+-------------+

Total: 3
```

#### Restore from Backup
```bash
./capybara.py backup restore before-upgrade
```

**Process:**
1. Stops VPN services
2. Extracts backup
3. Restores all files
4. Restarts services
5. Verifies restoration

**Use Cases:**
- Disaster recovery
- Undo bad configuration
- Migrate to new server
- Regular backup schedule

**Important:**
- Always backup before major changes
- Test restore procedure regularly
- Keep backups offsite (download them)
- Old backups should be cleaned periodically

---

### 5. Network Diagnostics

#### Ping User's VPN IP
```bash
# By username
./capybara.py diag ping alice

# By IP
./capybara.py diag ping 10.7.0.2
```

**Example Output:**
```
Pinging 10.7.0.2...
PING 10.7.0.2 (10.7.0.2) 56(84) bytes of data.
64 bytes from 10.7.0.2: icmp_seq=1 ttl=64 time=0.123 ms
64 bytes from 10.7.0.2: icmp_seq=2 ttl=64 time=0.098 ms
64 bytes from 10.7.0.2: icmp_seq=3 ttl=64 time=0.105 ms
64 bytes from 10.7.0.2: icmp_seq=4 ttl=64 time=0.091 ms

--- 10.7.0.2 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3003ms
rtt min/avg/max/mdev = 0.091/0.104/0.123/0.012 ms
```

**Use Cases:**
- Verify user is connected
- Test network connectivity
- Measure latency
- Troubleshoot routing

#### Check Listening Ports
```bash
./capybara.py diag ports
```

**Example Output:**
```
Listening Ports:
tcp    0.0.0.0:443     LISTEN    3161/udp2raw
tcp    0.0.0.0:22      LISTEN    2950/sshd
udp    0.0.0.0:51820   -         (WireGuard)
udp    :::51820        -         (WireGuard)
```

**What to Check:**
- Port 443 (udp2raw obfuscation)
- Port 51820 (WireGuard)
- Port 22 (SSH management)

#### Check User Handshake
```bash
./capybara.py diag handshake alice
```

**Example Output:**
```
Handshake Info for alice:
Last Handshake: 2 minutes ago
Endpoint: 192.168.1.100:54321
Transfer RX: 15.2 MiB
Transfer TX: 8.5 MiB
```

**Use Cases:**
- Verify user is actively connected
- Check when user last communicated
- See data transfer amounts
- Troubleshoot connection issues

---

### 6. System Health Monitoring

#### Check System Health
```bash
./capybara.py health check
```

**Example Output:**
```
============================================================
System Health
============================================================

Uptime:
  08:44:23 up 2:12, 0 users, load average: 0.00, 0.00, 0.00

CPU:
  %Cpu(s):  0.3 us,  0.1 sy,  0.0 ni, 99.6 id,  0.0 wa

Memory:
  Mem:  960.1M total, 56.2M used, 828.3M free, 75.5M buff/cache

Disk:
  /dev/vda2  24G  3.0G  20G  14%  /

Network Interface (wg0):
  RX: bytes 0, packets 0, errors 0
  TX: bytes 0, packets 0, errors 0
```

**Monitoring Checklist:**
- **CPU**: Should be low (< 50% normally)
- **Memory**: Watch for high usage (> 80%)
- **Disk**: Keep free space > 20%
- **Load Average**: Should be < number of CPUs
- **Network Errors**: Should be zero

**When to Act:**
- High CPU: Investigate processes
- High Memory: Check for leaks
- Low Disk: Clean old logs/backups
- Network Errors: Check hardware/config

---

### 7. Reports & Analytics

#### Generate Report
```bash
# Daily report (default)
./capybara.py report generate

# Weekly report
./capybara.py report generate --type weekly

# Monthly report
./capybara.py report generate --type monthly
```

**Example Output (Text Format):**
```
============================================================
Daily Report
============================================================

Generated: 2025-11-06 03:44:49
Report Type: daily

Summary:
  Total Users: 5
  Active Users: 3
  Server Uptime: 08:44:48 up 2:12

User Details:
+----------+----------+----------+-------------+--------+--------+
| Username | IP       | Status   | Last Seen   | RX     | TX     |
+==========+==========+==========+=============+========+========+
| alice    | 10.7.0.2 | Active   | 2 mins ago  | 15 MiB | 8 MiB  |
| bob      | 10.7.0.3 | Active   | 5 mins ago  | 102 MB | 45 MB  |
| charlie  | 10.7.0.4 | Inactive | Never       | 0 B    | 0 B    |
+----------+----------+----------+-------------+--------+--------+
```

#### Export in JSON Format
```bash
./capybara.py report generate --format json
```

**Example Output:**
```json
{
  "type": "daily",
  "generated": "2025-11-06 03:44:49",
  "summary": {
    "total_users": 5,
    "active_users": 3,
    "server_uptime": "08:44:48 up 2:12"
  },
  "users": [
    {
      "username": "alice",
      "ip": "10.7.0.2",
      "status": "Active",
      "last_seen": "2 minutes ago",
      "data_received": "15 MiB",
      "data_sent": "8 MiB"
    }
  ]
}
```

#### Export in CSV Format
```bash
./capybara.py report generate --format csv
```

**Example Output:**
```csv
Username,IP,Status,Last Seen,Data RX,Data TX
alice,10.7.0.2,Active,2 minutes ago,15 MiB,8 MiB
bob,10.7.0.3,Active,5 minutes ago,102 MiB,45 MiB
charlie,10.7.0.4,Inactive,Never,0 B,0 B
```

**Use Cases:**
- Daily usage tracking
- Billing/accounting
- Capacity planning
- Security audits
- Trend analysis
- Email reports

**Save to File:**
```bash
# Save text report
./capybara.py report generate > report_$(date +%Y%m%d).txt

# Save JSON
./capybara.py report generate --format json > report.json

# Save CSV for Excel
./capybara.py report generate --format csv > report.csv
```

---

## 🔥 Common Workflows

### Daily Operations
```bash
# Morning routine
./capybara.py server status          # Check if everything is running
./capybara.py user list               # See active users
./capybara.py health check            # Check system resources
./capybara.py logs show --lines 20    # Check for any errors
```

### Troubleshooting User Connection
```bash
# 1. Check if user exists
./capybara.py user list --detailed

# 2. Check handshake status
./capybara.py diag handshake alice

# 3. Ping user
./capybara.py diag ping alice

# 4. Check logs
./capybara.py logs show --service wireguard

# 5. If needed, disconnect and reconnect
./capybara.py connection kick alice
```

### Before Server Upgrade
```bash
# 1. Create backup
./capybara.py backup create --name before-upgrade-$(date +%Y%m%d)

# 2. Generate report
./capybara.py report generate > pre-upgrade-status.txt

# 3. Verify backup created
./capybara.py backup list

# 4. Proceed with upgrade
```

### After Configuration Changes
```bash
# 1. Restart specific service
./capybara.py service restart wireguard

# 2. Check service status
./capybara.py service status

# 3. Verify users can connect
./capybara.py connection list

# 4. Check logs for errors
./capybara.py logs show --lines 50
```

### Security Incident Response
```bash
# 1. Disconnect all users immediately
./capybara.py connection kick-all

# 2. Check who was connected
./capybara.py user list --detailed

# 3. Review logs
./capybara.py logs show --service all --lines 200

# 4. Create backup of current state
./capybara.py backup create --name incident-$(date +%Y%m%d-%H%M)

# 5. Generate report
./capybara.py report generate --format json > incident-report.json
```

### Weekly Maintenance
```bash
# 1. Health check
./capybara.py health check

# 2. Create weekly backup
./capybara.py backup create --name weekly-$(date +%Y%m%d)

# 3. Generate weekly report
./capybara.py report generate --type weekly > weekly-report.txt

# 4. Check for inactive users
./capybara.py user list | grep "Never connected"

# 5. Review logs
./capybara.py logs show --lines 100
```

---

## 📊 Monitoring Best Practices

### Daily Checks
- [ ] Server status
- [ ] Active connections
- [ ] System health
- [ ] Recent logs

### Weekly Tasks
- [ ] Generate usage report
- [ ] Create backup
- [ ] Review inactive users
- [ ] Check disk space
- [ ] Clean old logs

### Monthly Tasks
- [ ] Rotate encryption keys
- [ ] Archive old backups
- [ ] Generate monthly report
- [ ] Review security logs
- [ ] Update server packages

---

## 🛠️ Automation Examples

### Automated Daily Backup
Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to && ./capybara.py backup create --name daily-$(date +\%Y\%m\%d)
```

### Daily Email Report
```bash
# Daily report at 9 AM
0 9 * * * cd /path/to && ./capybara.py report generate > /tmp/vpn-report.txt && mail -s "VPN Daily Report" admin@example.com < /tmp/vpn-report.txt
```

### Health Monitoring
```bash
# Check health every hour
0 * * * * cd /path/to && ./capybara.py health check >> /var/log/vpn-health.log
```

### Log Rotation
```bash
# Archive logs weekly
0 0 * * 0 cd /path/to && ./capybara.py logs show --lines 1000 > vpn-logs-$(date +\%Y\%m\%d).txt
```

---

## 🚨 Troubleshooting Guide

### Issue: Service Not Running

**Symptoms:**
```bash
./capybara.py service status
# Shows: Wireguard STOPPED
```

**Solution:**
```bash
# 1. Check logs
./capybara.py logs show --service wireguard

# 2. Restart service
./capybara.py service restart wireguard

# 3. Verify
./capybara.py service status
```

### Issue: User Can't Connect

**Diagnosis:**
```bash
# 1. Check user exists
./capybara.py user list | grep username

# 2. Check handshake
./capybara.py diag handshake username

# 3. Try ping
./capybara.py diag ping username

# 4. Check ports
./capybara.py diag ports
```

### Issue: High System Load

**Diagnosis:**
```bash
# Check health
./capybara.py health check

# Check active connections
./capybara.py connection list

# Check logs for issues
./capybara.py logs show --lines 100
```

### Issue: Backup Failed

**Solution:**
```bash
# 1. Check disk space
./capybara.py health check

# 2. List existing backups
./capybara.py backup list

# 3. Try again with different name
./capybara.py backup create --name manual-backup
```

---

## 📈 Performance Tuning

### Monitor Performance
```bash
# Real-time monitoring
watch -n 5 './capybara.py health check'

# Live connections
watch -n 10 './capybara.py connection list'

# Service status
watch -n 30 './capybara.py service status'
```

### Optimize Based on Reports
```bash
# Generate report
./capybara.py report generate

# Analyze:
# - High bandwidth users
# - Connection patterns
# - Resource usage trends
```

---

## 🎯 Quick Command Reference

```bash
# === LOGS ===
./capybara.py logs show
./capybara.py logs show --service udp2raw --lines 50
./capybara.py logs tail

# === CONNECTIONS ===
./capybara.py connection list
./capybara.py connection kick alice
./capybara.py connection kick-all

# === SERVICES ===
./capybara.py service status
./capybara.py service restart wireguard
./capybara.py service restart udp2raw

# === BACKUP ===
./capybara.py backup create
./capybara.py backup create --name my-backup
./capybara.py backup list
./capybara.py backup restore my-backup

# === DIAGNOSTICS ===
./capybara.py diag ping alice
./capybara.py diag ports
./capybara.py diag handshake alice

# === HEALTH ===
./capybara.py health check

# === REPORTS ===
./capybara.py report generate
./capybara.py report generate --type weekly
./capybara.py report generate --format json
./capybara.py report generate --format csv
```

---

**Version:** 2.0.0 (Full Featured)
**Last Updated:** 2025-11-06
**Documentation:** Full Features Guide
