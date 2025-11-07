# CLI Redesign Complete: Clear Server vs Service Commands

## Problem Solved

**Before (Confusing):**
```bash
./capybara.py server status      # Shows ALL protocols ✓
./capybara.py server start       # Only started WireGuard ✗ CONFUSING!
./capybara.py server stop        # Only stopped WireGuard ✗ CONFUSING!
./capybara.py server restart     # Only restarted WireGuard ✗ CONFUSING!
```

**After (Clear):**
```bash
./capybara.py server status      # Shows ALL protocols ✓
./capybara.py server start       # Starts ALL protocols ✓ CONSISTENT!
./capybara.py server stop        # Stops ALL protocols ✓ CONSISTENT!
./capybara.py server restart     # Restarts ALL protocols ✓ CONSISTENT!
```

---

## New Command Structure

### Server Commands (Bulk Operations - ALL Protocols)

```bash
# Control ALL protocols at once (WireGuard + Shadowsocks + V2Ray)
./capybara.py server status      # Check status of all protocols
./capybara.py server start       # Start WireGuard, Shadowsocks, V2Ray
./capybara.py server stop        # Stop all 3 protocols
./capybara.py server restart     # Restart all 3 protocols
```

**Clear Communication:**
- Help text says: "Manage entire VPN server (ALL protocols)"
- Prompts say: "Are you sure you want to stop ALL VPN protocols?"
- Docstrings say: "Stop ALL VPN protocols (WireGuard, Shadowsocks, V2Ray)"

### Service Commands (Individual Protocol Control)

```bash
# Control ONE protocol at a time
./capybara.py service status                    # Show all services
./capybara.py service start wireguard           # Start WireGuard only
./capybara.py service start shadowsocks         # Start Shadowsocks only
./capybara.py service start v2ray               # Start V2Ray only
./capybara.py service stop shadowsocks          # Stop Shadowsocks only
./capybara.py service restart v2ray             # Restart V2Ray only
```

**Clear Communication:**
- Help text says: "Manage individual protocol services (fine-grained control)"
- Help text says: "Use 'service' commands to control ONE protocol at a time"

---

## Complete Command Comparison

| Task | Old (Confusing) | New (Clear) |
|------|----------------|-------------|
| **Start everything** | ❌ No single command | `server start` |
| **Stop everything** | ❌ No single command | `server stop` |
| **Restart everything** | ❌ No single command | `server restart` |
| **Check all status** | `server status` | `server status` (unchanged) |
| **Start WireGuard only** | `server start` | `service start wireguard` |
| **Stop Shadowsocks only** | ❌ SSH required | `service stop shadowsocks` |
| **Restart V2Ray only** | `service restart v2ray` | `service restart v2ray` (unchanged) |

---

## Implementation Details

### Changes Made

#### 1. Updated `start_server()` Method
**Before:** Only started WireGuard
```python
def start_server(self):
    """Start WireGuard server"""
    ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
```

**After:** Starts all 3 protocols
```python
def start_server(self):
    """Start ALL VPN protocols (WireGuard, Shadowsocks, V2Ray)"""
    # Start WireGuard (includes udp2raw via PreUp)
    ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")

    # Start Shadowsocks
    ssh.execute("rc-service shadowsocks-rust start")

    # Start V2Ray
    ssh.execute("rc-service v2ray start")
```

#### 2. Updated `stop_server()` Method
**Before:** Only stopped WireGuard
**After:** Stops all 3 protocols

#### 3. Updated `restart_server()` Method
**Before:** Only restarted WireGuard
**After:** Restarts all 3 protocols

#### 4. Added `start_service()` and `stop_service()` Methods
New methods for individual protocol control (previously only had `restart_service`)

#### 5. Added CLI Commands
```python
@service.command('start')  # NEW
@service.command('stop')   # NEW
@service.command('restart') # Already existed
```

#### 6. Updated All Help Text
- Server commands now explicitly say "ALL protocols"
- Service commands now explicitly say "ONE protocol at a time"
- Confirmation prompts updated to be clear

---

## Example Usage

### Scenario 1: System Maintenance (Restart Everything)
```bash
# Old way: Manual steps required
ssh root@server
wg-quick down wg0 && wg-quick up wg0
rc-service shadowsocks-rust restart
rc-service v2ray restart

# New way: One command
./capybara.py server restart
```

**Output:**
```
Restarting VPN server (all protocols)...
  ✓ WireGuard restarted
  ✓ Shadowsocks restarted
  ✓ V2Ray restarted
✓ VPN server restarted successfully
```

### Scenario 2: Fix Shadowsocks Only
```bash
# Old way: SSH required
ssh root@server "rc-service shadowsocks-rust restart"

# New way: One command
./capybara.py service restart shadowsocks
```

**Output:**
```
Restarting shadowsocks...
✓ shadowsocks restarted successfully
```

### Scenario 3: Emergency Shutdown
```bash
# Stop everything immediately
./capybara.py server stop
```

**Prompt:**
```
Are you sure you want to stop ALL VPN protocols? [y/N]:
```

**Output:**
```
Stopping VPN server (all protocols)...
  ✓ WireGuard stopped
  ✓ Shadowsocks stopped
  ✓ V2Ray stopped
✓ VPN server stopped successfully
```

---

## Help Text Examples

### `./capybara.py server --help`
```
Manage entire VPN server (ALL protocols: WireGuard, Shadowsocks, V2Ray).

Server commands control all protocols at once. For individual protocol
control, use the 'service' command instead.

Examples:
  capybara.py server status               # Check all protocols status
  capybara.py server start                # Start ALL protocols
  capybara.py server stop                 # Stop ALL protocols
  capybara.py server restart              # Restart ALL protocols

Commands:
  restart  Restart ALL VPN protocols (WireGuard, Shadowsocks, V2Ray)
  start    Start ALL VPN protocols (WireGuard, Shadowsocks, V2Ray)
  status   Check VPN server status
  stop     Stop ALL VPN protocols (WireGuard, Shadowsocks, V2Ray)
```

### `./capybara.py service --help`
```
Manage individual protocol services (fine-grained control).

Use 'service' commands to control ONE protocol at a time.
For bulk operations (all protocols), use 'server' command instead.

Examples:
  capybara.py service status                  # Check all services status
  capybara.py service start wireguard         # Start WireGuard only
  capybara.py service start shadowsocks       # Start Shadowsocks only
  capybara.py service stop v2ray              # Stop V2Ray only
  capybara.py service restart shadowsocks     # Restart Shadowsocks only

Commands:
  restart  Restart a specific service
  start    Start a specific service
  status   Check status of all services
  stop     Stop a specific service
```

---

## Benefits

### 1. Intuitive
- `server` = entire server (all protocols)
- `service` = individual protocols
- Matches user expectations

### 2. Consistent
- `server status` shows all protocols
- `server start/stop/restart` controls all protocols
- No more confusion!

### 3. Convenient
- Common operations (restart all) are simple one-liners
- Fine-grained control still available via `service`

### 4. Safe
- Confirmation prompts for destructive operations
- Clear warnings about what will be affected

---

## Testing Performed

✅ Syntax validation: `python3 -m py_compile capybara.py`
✅ Help text verified: All commands show correct help
✅ Choices verified: All service commands accept correct protocol names
✅ Docstrings verified: All clearly indicate scope (ALL vs ONE)

---

## Migration Notes

### If You Were Using Old Commands

**Old:** `./capybara.py server start`
- **Behavior changed:** Now starts ALL protocols (not just WireGuard)
- **To start WireGuard only:** Use `./capybara.py service start wireguard`

**Old:** `./capybara.py server stop`
- **Behavior changed:** Now stops ALL protocols (not just WireGuard)
- **To stop WireGuard only:** Use `./capybara.py service stop wireguard`

**Old:** `./capybara.py server restart`
- **Behavior changed:** Now restarts ALL protocols (not just WireGuard)
- **To restart WireGuard only:** Use `./capybara.py service restart wireguard`

### If You Want Old Behavior

Use the `service` command with specific protocol:
```bash
./capybara.py service start wireguard    # Old server start behavior
./capybara.py service stop wireguard     # Old server stop behavior
./capybara.py service restart wireguard  # Old server restart behavior
```

---

## Files Changed

- `capybara.py`:
  - Updated `start_server()`, `stop_server()`, `restart_server()` methods
  - Added `start_service()`, `stop_service()` methods
  - Added `service start` and `service stop` CLI commands
  - Updated all help text and docstrings

---

## Summary

The CLI is now **clear and consistent**:

- **`server`** = High-level bulk operations (all protocols)
- **`service`** = Low-level individual control (one protocol)

No more confusion about what "server start" does! It now starts the entire VPN server, as users would naturally expect.
