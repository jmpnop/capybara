# Capybara VPN Functionality Analysis: WireGuard vs Shadowsocks vs V2Ray

## Overview
This document analyzes the current functionality available for each protocol in Capybara and identifies gaps where WireGuard has features that Shadowsocks and V2Ray lack.

---

## Feature Comparison Matrix

| Feature | WireGuard | Shadowsocks | V2Ray | Status |
|---------|-----------|-------------|-------|--------|
| **User Management** |
| Add user | ✅ Full | ✅ Full | ✅ Full | **COMPLETE** |
| Remove user | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| List users | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| Block user | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| **Connection Management** |
| List active connections | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| Kick user | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| Kick all users | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| Connection statistics | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| **Service Management** |
| Status check | ✅ Full | ✅ Full | ✅ Full | **COMPLETE** |
| Start/Stop | ✅ Full | ❌ Manual | ❌ Manual | **GAP** |
| Restart | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| **Monitoring** |
| View logs | ✅ Full | ✅ Full | ✅ Full | **COMPLETE** |
| Tail logs | ✅ Full | ✅ Full | ✅ Full | **COMPLETE** |
| Server statistics | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| **Diagnostics** |
| Ping user | ✅ Full | ❌ N/A | ❌ N/A | **ARCHITECTURE** |
| Check handshake | ✅ Full | ❌ N/A | ❌ N/A | **ARCHITECTURE** |
| Check ports | ✅ Full | ✅ Full | ✅ Full | **COMPLETE** |
| **Backup & Restore** |
| Backup config | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| Restore config | ✅ Full | ❌ Missing | ❌ Missing | **GAP** |
| List backups | ✅ Full | ✅ Full | ✅ Full | **PARTIAL** |

---

## Detailed Analysis by Feature Category

### 1. User Management

#### ✅ **Add User** - COMPLETE
- **WireGuard**: Creates peer config, assigns IP, generates QR code
- **Shadowsocks**: Generates config with shared password, creates QR code
- **V2Ray**: Creates UUID, adds to clients array, generates QR code
- **Status**: All three protocols fully supported

#### ❌ **Remove User** - MISSING for SS/V2Ray
**Current Implementation (WireGuard only):**
```python
def remove_user(self, identifier):
    # Parses WireGuard config
    # Finds peer section by username or IP
    # Removes peer from config
    # Reloads WireGuard with wg syncconf
```

**Why Missing:**
- **Shadowsocks**: Uses shared password model - no per-user configuration to remove
- **V2Ray**: User UUIDs are in `/etc/v2ray/config.json` clients array, but removal not implemented

**Impact**: Cannot remove compromised users from Shadowsocks/V2Ray without manual editing

#### ❌ **List Users** - MISSING for SS/V2Ray
**Current Implementation (WireGuard only):**
```python
def list_users(self):
    # Reads /etc/wireguard/wg0.conf
    # Parses peer sections with metadata
    # Enriches with wg show data (connections, transfer stats)
    # Returns list with: username, IP, endpoint, last_handshake, transfer
```

**Why Missing:**
- **Shadowsocks**: No user tracking - all connections share same credentials
- **V2Ray**: Users exist in config.json but no connection stats available via simple CLI

**Impact**: Cannot see who is using Shadowsocks/V2Ray or their usage statistics

#### ❌ **Block User** - MISSING for SS/V2Ray
**Current Implementation (WireGuard only):**
```python
def block_user(self, identifier):
    # Comments out peer section in config
    # Reloads WireGuard to disconnect user
```

**Why Missing:**
- **Shadowsocks**: No per-user identification
- **V2Ray**: Could remove from clients array but not implemented

**Impact**: Cannot temporarily block misbehaving users

---

### 2. Connection Management

#### ❌ **List Active Connections** - MISSING for SS/V2Ray
**Current Implementation (WireGuard only):**
```python
connection_list():
    # Uses list_users() to get all peers
    # Filters by endpoint != 'Never connected'
    # Shows username, IP, endpoint, last handshake
```

**Why Missing:**
- **Shadowsocks**: No built-in connection tracking API
- **V2Ray**: Has API but requires additional setup and parsing

**Impact**: Cannot monitor who is currently connected via SS/V2Ray

#### ❌ **Kick User** - MISSING for SS/V2Ray
**Current Implementation (WireGuard only):**
```python
def kick_user(self, identifier):
    # Removes peer with: wg set wg0 peer <pubkey> remove
    # Temporarily blocks IP with iptables
    # Auto-unblocks after 5 seconds
```

**Why Missing:**
- **Shadowsocks**: No per-connection control
- **V2Ray**: No simple disconnect mechanism

**Impact**: Cannot immediately disconnect users in emergency situations

---

### 3. Service Management

#### ❌ **Service Restart** - MISSING for SS/V2Ray
**Current Implementation:**
```python
@click.argument('service_name', type=click.Choice(['wireguard', 'udp2raw', 'firewall']))
def service_restart_cmd(service_name):
    # Only allows: wireguard, udp2raw, firewall
    # Missing: shadowsocks, v2ray
```

**Code location:** capybara.py:1917

**Why Missing:**
- Oversight - should be easy to add
- `rc-service shadowsocks-rust restart` exists
- `rc-service v2ray restart` exists

**Impact**: Must manually SSH to restart Shadowsocks/V2Ray

**Fix difficulty**: ⭐ EASY - just add to choices and if/elif branches

---

### 4. Backup & Restore

#### ❌ **Backup Config** - MISSING for SS/V2Ray
**Current Implementation:**
```python
def create_backup(self, name=None):
    # Backs up:
    # - /etc/wireguard/wg0.conf
    # - /etc/wireguard/*.key
    # - /etc/wireguard/clients
    # - iptables rules
    # - awall config

    # Missing:
    # - /etc/shadowsocks-rust/config.json
    # - /etc/v2ray/config.json
```

**Code location:** capybara.py:1056-1095

**Why Missing:**
- Focused on WireGuard initially
- Shadowsocks/V2Ray support added later

**Impact**: Shadowsocks/V2Ray configs not included in disaster recovery

**Fix difficulty**: ⭐⭐ MODERATE - add backup commands for both configs

---

## Architectural Limitations (Cannot Be Fixed)

### Why Some Features Cannot Work for Shadowsocks/V2Ray

#### 1. **Shadowsocks Architecture**
Shadowsocks is a **simple SOCKS5 proxy**, not a VPN:
- All users share the same server password and port
- No concept of "users" or "peers"
- No connection tracking built into the protocol
- No handshake or session management
- Think of it as a shared tunnel, not individual connections

**Analogy**: Like a public door with one key vs. WireGuard's personalized keycards

#### 2. **V2Ray Architecture**
V2Ray VMess is more sophisticated but still different:
- Has user UUIDs in configuration
- Can track connections via API (not simple CLI)
- No equivalent to WireGuard's `wg show` command
- Statistics require enabling API endpoint and querying it
- More complex than simple command-line tools

**Possible but Complex**: V2Ray monitoring would require:
- Enabling V2Ray API in config
- Installing V2Ray API tools (v2ctl)
- Parsing API responses
- Much more complex than `wg show`

#### 3. **No VPN IP Addresses**
- WireGuard: Each peer has a VPN IP (10.7.0.x)
- Shadowsocks: No VPN network - just proxies traffic
- V2Ray: No VPN network - just proxies traffic

**Impact**: Cannot ping users or do network diagnostics on SS/V2Ray

---

## Recommendations

### Priority 1: Easy Fixes (Immediate Implementation)

1. **Add Shadowsocks/V2Ray to service restart**
   - Difficulty: ⭐ Easy (5 minutes)
   - Impact: High
   - Files: capybara.py:1007, 1917
   ```python
   # Add to restart_service():
   elif service == 'shadowsocks':
       ssh.execute("rc-service shadowsocks-rust restart")
   elif service == 'v2ray':
       ssh.execute("rc-service v2ray restart")

   # Update CLI choices:
   @click.argument('service_name', type=click.Choice([
       'wireguard', 'udp2raw', 'shadowsocks', 'v2ray', 'firewall'
   ]))
   ```

2. **Add SS/V2Ray configs to backup**
   - Difficulty: ⭐⭐ Moderate (15 minutes)
   - Impact: High (disaster recovery)
   - File: capybara.py:1056
   ```python
   # Add to create_backup():
   ssh.execute(f"cp /etc/shadowsocks-rust/config.json {backup_dir}/ 2>/dev/null || true")
   ssh.execute(f"cp /etc/v2ray/config.json {backup_dir}/ 2>/dev/null || true")
   ```

### Priority 2: Moderate Effort (Recommended)

3. **Implement V2Ray user removal**
   - Difficulty: ⭐⭐⭐ Moderate (30 minutes)
   - Impact: Medium
   - Implementation:
     - Read `/etc/v2ray/config.json`
     - Remove user from clients array by UUID or email
     - Write updated config
     - Restart V2Ray service

4. **Add V2Ray user listing**
   - Difficulty: ⭐⭐ Moderate (20 minutes)
   - Impact: Medium
   - Implementation:
     - Parse `/etc/v2ray/config.json`
     - Extract clients array
     - Display UUID, email, alterId
     - Note: No connection stats without API

### Priority 3: Complex (Optional)

5. **V2Ray statistics via API**
   - Difficulty: ⭐⭐⭐⭐ Hard (2-3 hours)
   - Impact: Low (nice to have)
   - Requirements:
     - Enable V2Ray API in config
     - Install v2ctl or use API directly
     - Parse JSON responses
     - May not be worth the complexity

6. **Shadowsocks connection monitoring**
   - Difficulty: ⭐⭐⭐⭐⭐ Very Hard
   - Impact: Low
   - Challenges:
     - No built-in monitoring in SS protocol
     - Would need to parse netstat or use ss-manager
     - Still can't identify individual users (shared password)
     - Probably not feasible

---

## Summary

### What Works Well
✅ User creation (all 3 protocols)
✅ Service status (all 3 protocols)
✅ Logs viewing (all 3 protocols)
✅ QR code generation (all 3 protocols)

### Quick Wins (Should Fix)
🔧 Service restart missing for SS/V2Ray
🔧 Backup missing SS/V2Ray configs
🔧 V2Ray user removal not implemented
🔧 V2Ray user listing not implemented

### Architectural Limitations (Accept)
🚫 Shadowsocks has no per-user tracking (by design)
🚫 V2Ray stats require complex API integration
🚫 No VPN IPs for SS/V2Ray (not a VPN, just proxy)
🚫 Cannot ping SS/V2Ray "users" (no network layer)

### Recommended Action Plan
1. Add SS/V2Ray to service restart (5 min)
2. Add SS/V2Ray to backups (15 min)
3. Implement V2Ray user removal (30 min)
4. Implement V2Ray user listing (20 min)
5. Document limitations in README

**Total effort for priorities 1-2**: ~70 minutes
**Impact**: Closes most important gaps while respecting architectural limitations
