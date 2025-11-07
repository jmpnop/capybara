# 🔍 Capybara VPN - Debugging Guide

Complete guide for debugging issues with all three protocols: WireGuard, Shadowsocks, and V2Ray.

---

## 🎯 Quick Debugging Checklist

When a user reports connection issues, check in this order:

1. **Server Status:** `./capybara.py server status`
2. **Service Health:** `./capybara.py health check`
3. **Active Connections:** `./capybara.py connection list`
4. **Protocol-Specific Logs:** `./capybara.py logs show --service <protocol>`

---

## 📊 Viewing Logs for All Protocols

### View All Logs at Once

```bash
./capybara.py logs show
```

Shows logs from all services: WireGuard, udp2raw, Shadowsocks, V2Ray, and system.

### Protocol-Specific Logs

**WireGuard Logs:**
```bash
./capybara.py logs show --service wireguard
```

**Shadowsocks Logs:**
```bash
./capybara.py logs show --service shadowsocks
```

**V2Ray Logs:**
```bash
./capybara.py logs show --service v2ray
```

**udp2raw Logs (WireGuard obfuscation):**
```bash
./capybara.py logs show --service udp2raw
```

**System Logs:**
```bash
./capybara.py logs show --service system
```

### Follow Logs in Real-Time

**Follow WireGuard logs:**
```bash
./capybara.py logs tail --service wireguard
```

**Follow Shadowsocks logs:**
```bash
./capybara.py logs tail --service shadowsocks
```

**Follow V2Ray logs:**
```bash
./capybara.py logs tail --service v2ray
```

**Follow udp2raw logs:**
```bash
./capybara.py logs tail --service udp2raw
```

Press `Ctrl+C` to stop following logs.

### Show More Log Lines

```bash
./capybara.py logs show --service shadowsocks --lines 200
```

---

## 🔧 Protocol-Specific Debugging

### WireGuard Debugging

**Check WireGuard Interface:**
```bash
ssh root@YOUR_SERVER_IP "wg show"
```

**Check WireGuard Service:**
```bash
ssh root@YOUR_SERVER_IP "rc-service wg-quick status"
```

**View WireGuard Config:**
```bash
ssh root@YOUR_SERVER_IP "cat /etc/wireguard/wg0.conf"
```

**Common Issues:**

| Problem | Solution |
|---------|----------|
| No handshake | Check client's allowed IPs and server's peer config |
| udp2raw not working | Check udp2raw logs: `./capybara.py logs show --service udp2raw` |
| Connection drops | Check MTU settings (default 1280) |
| Port 443 blocked | Check firewall: `ssh root@SERVER "awall list"` |

**Key Log Messages:**

```
✅ Good: "peer xxx has a handshake"
❌ Bad: "no recent handshake"
❌ Bad: "invalid packet"
```

---

### Shadowsocks Debugging

**Check Shadowsocks Service:**
```bash
ssh root@YOUR_SERVER_IP "rc-service shadowsocks-rust status"
```

**View Shadowsocks Config:**
```bash
ssh root@YOUR_SERVER_IP "cat /etc/shadowsocks-rust/config.json"
```

**Test Shadowsocks Server:**
```bash
ssh root@YOUR_SERVER_IP "ss-server --version"
```

**Check Active Connections:**
```bash
ssh root@YOUR_SERVER_IP "netstat -tulpn | grep :8388"
```

**Common Issues:**

| Problem | Solution |
|---------|----------|
| "Invalid password" | Verify password in config matches user's password |
| Port 8388 not listening | Check if service is running: `rc-service shadowsocks-rust status` |
| Connection timeout | Check firewall allows port 8388 |
| AEAD encryption error | Ensure client uses `chacha20-ietf-poly1305` |

**Key Log Messages:**

```
✅ Good: "accepted connection from xxx"
❌ Bad: "authentication failed"
❌ Bad: "invalid method"
❌ Bad: "connection closed"
```

**Manual Log Access:**
```bash
# Try these locations in order:
ssh root@SERVER "tail -f /var/log/shadowsocks.log"
ssh root@SERVER "journalctl -u shadowsocks-rust -f"
ssh root@SERVER "grep shadowsocks /var/log/messages"
```

---

### V2Ray Debugging

**Check V2Ray Service:**
```bash
ssh root@YOUR_SERVER_IP "rc-service v2ray status"
```

**View V2Ray Config:**
```bash
ssh root@YOUR_SERVER_IP "cat /etc/v2ray/config.json"
```

**Test V2Ray Binary:**
```bash
ssh root@YOUR_SERVER_IP "v2ray version"
```

**Check Active Connections:**
```bash
ssh root@YOUR_SERVER_IP "netstat -tulpn | grep :8443"
```

**View Both V2Ray Logs:**
```bash
# Access logs (successful connections)
ssh root@SERVER "tail -f /var/log/v2ray/access.log"

# Error logs (failures and issues)
ssh root@SERVER "tail -f /var/log/v2ray/error.log"
```

**Common Issues:**

| Problem | Solution |
|---------|----------|
| "invalid UUID" | Verify UUID matches between server and client |
| Port 8443 not listening | Check if service is running: `rc-service v2ray status` |
| "connection rejected" | Check user is in /etc/v2ray/config.json clients list |
| VMess handshake failed | Ensure AlterID is 0 on both client and server |

**Key Log Messages:**

```
✅ Good: "accepted vmess connection"
✅ Good: "from xxx to xxx"
❌ Bad: "invalid user"
❌ Bad: "connection timeout"
❌ Bad: "failed to read request"
```

---

## 🚨 Common Multi-Protocol Issues

### Issue: User Can't Connect with Any Protocol

**Debugging Steps:**

1. **Check server is accessible:**
   ```bash
   ping YOUR_SERVER_IP
   ```

2. **Check all services are running:**
   ```bash
   ./capybara.py server status
   ```

3. **Check firewall rules:**
   ```bash
   ssh root@SERVER "awall list"
   ssh root@SERVER "iptables -L -n"
   ```

4. **Verify user exists:**
   ```bash
   ./capybara.py user list
   ```

5. **Check all protocol logs:**
   ```bash
   ./capybara.py logs show
   ```

---

### Issue: One Protocol Works, Others Don't

**Scenario: WireGuard works, Shadowsocks doesn't**

```bash
# Check if Shadowsocks service is running
ssh root@SERVER "rc-service shadowsocks-rust status"

# Check if port 8388 is open
ssh root@SERVER "netstat -tulpn | grep 8388"

# View Shadowsocks logs
./capybara.py logs show --service shadowsocks

# Check firewall allows port 8388
ssh root@SERVER "awall list | grep 8388"
```

**Scenario: Shadowsocks works, V2Ray doesn't**

```bash
# Check if V2Ray service is running
ssh root@SERVER "rc-service v2ray status"

# Check if port 8443 is open
ssh root@SERVER "netstat -tulpn | grep 8443"

# View V2Ray error logs
./capybara.py logs show --service v2ray

# Restart V2Ray service
ssh root@SERVER "rc-service v2ray restart"
```

---

## 📱 Mobile Client Debugging

### iOS (Shadowrocket) Issues

**Problem: QR code won't scan**
- Ensure good lighting
- Try manual entry instead
- Verify QR code PNG is not corrupted

**Problem: "Connection timeout"**
```bash
# Check which protocol user is trying
# Then check that service's logs
./capybara.py logs show --service shadowsocks  # if using Shadowsocks
./capybara.py logs show --service v2ray       # if using V2Ray
```

**Problem: Connected but no internet**
- Check Shadowrocket routing: Settings → Global Routing → Proxy
- Verify in server logs that user is actually connecting

### Android Issues

**Problem: v2rayNG "connection failed"**
```bash
# View V2Ray logs for authentication errors
./capybara.py logs show --service v2ray --lines 100

# Check user's UUID is in server config
ssh root@SERVER "grep UUID_HERE /etc/v2ray/config.json"
```

**Problem: Shadowsocks "invalid server"**
```bash
# Check Shadowsocks is running
ssh root@SERVER "rc-service shadowsocks-rust status"

# View connection attempts
./capybara.py logs tail --service shadowsocks
```

---

## 🔍 Advanced Debugging

### Enable Verbose Logging

**V2Ray Verbose Logging:**
```bash
ssh root@SERVER "cat >> /etc/v2ray/config.json" << 'EOF'
{
  "log": {
    "loglevel": "debug"
  }
}
EOF

ssh root@SERVER "rc-service v2ray restart"
```

**Shadowsocks Verbose Logging:**
```bash
ssh root@SERVER "ss-server -c /etc/shadowsocks-rust/config.json -v"
```

### Network Packet Analysis

**Capture traffic for debugging:**
```bash
# WireGuard traffic
ssh root@SERVER "tcpdump -i any port 51820 -n"

# Shadowsocks traffic
ssh root@SERVER "tcpdump -i any port 8388 -n"

# V2Ray traffic
ssh root@SERVER "tcpdump -i any port 8443 -n"

# udp2raw obfuscated traffic
ssh root@SERVER "tcpdump -i any port 443 -n"
```

### Check for Port Conflicts

```bash
ssh root@SERVER "netstat -tulpn | grep -E '443|8388|8443|51820'"
```

Expected output:
```
tcp    0.0.0.0:443    LISTEN    12345/udp2raw
tcp    0.0.0.0:8388   LISTEN    12346/ss-server
tcp    0.0.0.0:8443   LISTEN    12347/v2ray
udp    0.0.0.0:51820  LISTEN    12348/wg-quick
```

---

## 📊 Log Interpretation Guide

### WireGuard Log Levels

```
INFO:  Normal operations
WARN:  Potential issues (expired handshakes)
ERROR: Connection failures
```

### Shadowsocks Log Patterns

```
[server] accepted connection from x.x.x.x:port  ← User connected
[server] connection established                 ← Successful
authentication failed                           ← Wrong password
invalid method                                  ← Wrong encryption
```

### V2Ray Log Levels

```
[Info]    Normal operations
[Warning] Potential issues
[Error]   Connection failures
[Debug]   Detailed debugging info
```

**V2Ray Access Log Format:**
```
2025/11/06 13:45:23 accepted connection from x.x.x.x:port
```

**V2Ray Error Log Format:**
```
2025/11/06 13:45:23 [Error] failed to handle connection
```

---

## 🛠️ Quick Fixes

### Restart All Services

```bash
ssh root@SERVER << 'EOF'
rc-service wg-quick restart
rc-service shadowsocks-rust restart
rc-service v2ray restart
pkill -HUP udp2raw
EOF
```

### Regenerate User Config

```bash
./capybara.py user remove alice
./capybara.py user add alice --description "Regenerated config"
```

### Check Firewall Rules

```bash
ssh root@SERVER "awall list"
ssh root@SERVER "awall activate"
```

### Clear Old Connections

```bash
./capybara.py connection list
./capybara.py connection kick alice  # if specific user has issues
```

---

## 📞 Getting Additional Help

### Collect Debug Information

When reporting an issue, collect:

```bash
# 1. Server status
./capybara.py server status > debug_info.txt

# 2. System health
./capybara.py health check >> debug_info.txt

# 3. All logs
./capybara.py logs show --lines 200 >> debug_info.txt

# 4. Active connections
./capybara.py connection list >> debug_info.txt

# 5. User list
./capybara.py user list --detailed >> debug_info.txt
```

### Log Locations Reference

| Service | Log Location | Access Method |
|---------|--------------|---------------|
| **WireGuard** | journalctl | `./capybara.py logs show --service wireguard` |
| **udp2raw** | /var/log/udp2raw.log | `./capybara.py logs show --service udp2raw` |
| **Shadowsocks** | Multiple locations | `./capybara.py logs show --service shadowsocks` |
| **V2Ray** | /var/log/v2ray/*.log | `./capybara.py logs show --service v2ray` |
| **System** | dmesg | `./capybara.py logs show --service system` |

---

## ✅ Debugging Checklist

Use this checklist when troubleshooting:

- [ ] Server is reachable (ping)
- [ ] All services are running (`server status`)
- [ ] System resources are healthy (`health check`)
- [ ] User exists in system (`user list`)
- [ ] Relevant ports are open (firewall check)
- [ ] Service logs show no errors (`logs show`)
- [ ] Client using correct protocol/port
- [ ] Client configuration matches server
- [ ] No port conflicts on server
- [ ] Firewall allows relevant traffic

---

**Made with 🦫 by the Capybara Team**

**Version:** 3.0.0
**Last Updated:** November 6, 2025

🔍 For more help, run `./capybara.py --help` or check the main README.md
