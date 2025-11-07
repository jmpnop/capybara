# CLI Redesign Proposal: Clear and Consistent Commands

## Current Problems

### 1. Inconsistent "server" commands
```bash
./capybara.py server status      # Shows ALL protocols ✓
./capybara.py server start       # Only starts WireGuard ✗ CONFUSING!
./capybara.py server stop        # Only stops WireGuard ✗ CONFUSING!
./capybara.py server restart     # Only restarts WireGuard ✗ CONFUSING!
```

**Problem**: User expects `server start` to start the entire VPN server (all protocols), but it only starts WireGuard.

### 2. Overlapping commands
```bash
./capybara.py server restart           # Restarts only WireGuard
./capybara.py service restart wireguard # Also restarts WireGuard
```

**Problem**: Two ways to do the same thing, confusing!

---

## Proposed Solution

### Option A: "server" Controls ALL Protocols (RECOMMENDED)

**Principle**: `server` = entire VPN server (all protocols)

```bash
# Server-level commands (ALL protocols)
./capybara.py server status      # Show all protocols (ALREADY WORKS)
./capybara.py server start       # Start ALL protocols
./capybara.py server stop        # Stop ALL protocols
./capybara.py server restart     # Restart ALL protocols

# Individual protocol control
./capybara.py service start wireguard
./capybara.py service start shadowsocks
./capybara.py service start v2ray
./capybara.py service restart shadowsocks
./capybara.py service stop v2ray
```

**Benefits**:
- ✅ Consistent: `server` always means "all protocols"
- ✅ Clear: Two distinct command groups
- ✅ Practical: Common operations (restart all) are simple

**Changes Required**:
- Update `start_server()` to start all 3 protocols
- Update `stop_server()` to stop all 3 protocols
- Update `restart_server()` to restart all 3 protocols
- Add individual `service start/stop` commands

---

### Option B: Remove "server" Commands (SIMPLER)

**Principle**: Only use `service` commands, remove `server start/stop/restart`

```bash
# Only status at server level
./capybara.py server status            # Overview of all protocols

# Individual protocol control (ONLY way)
./capybara.py service start wireguard
./capybara.py service start shadowsocks
./capybara.py service start v2ray
./capybara.py service start all        # Start all protocols

./capybara.py service restart all      # Restart all
./capybara.py service stop all         # Stop all
```

**Benefits**:
- ✅ Simpler: Only one command group
- ✅ Explicit: Always specify what you're controlling
- ✅ Flexible: Can use "all" for bulk operations

**Changes Required**:
- Remove `server start/stop/restart` CLI commands
- Add `all` option to `service start/stop/restart`
- Add `service start` and `service stop` (currently only have `restart`)

---

## Detailed Comparison

| Operation | Current (Confusing) | Option A (Recommended) | Option B (Simpler) |
|-----------|---------------------|------------------------|---------------------|
| **Check status** | `server status` | `server status` | `server status` |
| **Start all** | ❌ No command | `server start` | `service start all` |
| **Stop all** | ❌ No command | `server stop` | `service stop all` |
| **Restart all** | ❌ No command | `server restart` | `service restart all` |
| **Start WireGuard** | `server start` ✗ | `service start wireguard` | `service start wireguard` |
| **Restart WireGuard** | `server restart` or `service restart wireguard` ✗ | `service restart wireguard` | `service restart wireguard` |
| **Restart Shadowsocks** | `service restart shadowsocks` | `service restart shadowsocks` | `service restart shadowsocks` |

---

## Recommended Structure (Option A)

### Server Commands (Bulk Operations)
```bash
server status         # Show all protocol status and configs
server start          # Start WireGuard + Shadowsocks + V2Ray
server stop           # Stop all protocols
server restart        # Restart all protocols
```

### Service Commands (Individual Protocol Control)
```bash
service status                      # Show status of all services
service start <protocol>            # Start one protocol
service stop <protocol>             # Stop one protocol
service restart <protocol>          # Restart one protocol

Where <protocol> is:
  - wireguard
  - shadowsocks
  - v2ray
  - udp2raw
  - firewall
```

---

## Implementation Plan

### Phase 1: Update "server" commands to control ALL protocols

**File**: `capybara.py`

**Methods to update**:
1. `start_server()` - Start all 3 protocols
2. `stop_server()` - Stop all 3 protocols
3. `restart_server()` - Restart all 3 protocols

**New implementation**:
```python
def start_server(self):
    """Start ALL VPN protocols (WireGuard, Shadowsocks, V2Ray)"""
    with SSHConnection(self.config) as ssh:
        click.echo(f"{Fore.YELLOW}Starting VPN server (all protocols)...")

        # Start WireGuard (includes udp2raw via PreUp)
        ssh.execute(f"wg-quick up {self.config['vpn']['interface']}")
        click.echo(f"{Fore.GREEN}  ✓ WireGuard started")

        # Start Shadowsocks
        ssh.execute("rc-service shadowsocks-rust start", check_error=False)
        click.echo(f"{Fore.GREEN}  ✓ Shadowsocks started")

        # Start V2Ray
        ssh.execute("rc-service v2ray start", check_error=False)
        click.echo(f"{Fore.GREEN}  ✓ V2Ray started")

        click.echo(f"{Fore.GREEN}✓ VPN server started successfully")
```

### Phase 2: Add service start/stop commands

**New CLI commands**:
```python
@service.command('start')
@click.argument('service_name', type=click.Choice([
    'wireguard', 'udp2raw', 'shadowsocks', 'v2ray', 'firewall'
]))
def service_start_cmd(service_name):
    """Start a specific service"""
    # Implementation similar to restart

@service.command('stop')
@click.argument('service_name', type=click.Choice([
    'wireguard', 'udp2raw', 'shadowsocks', 'v2ray', 'firewall'
]))
def service_stop_cmd(service_name):
    """Stop a specific service"""
    # Implementation similar to restart
```

### Phase 3: Update help text and documentation

Update all docstrings and help text to make the distinction clear:
- `server` = all protocols (bulk operations)
- `service` = individual protocol control

---

## Migration Guide for Users

### Old Command → New Command

| What you want | Old (Confusing) | New (Clear) |
|---------------|-----------------|-------------|
| Start everything | ❌ No single command | `server start` |
| Stop everything | ❌ No single command | `server stop` |
| Restart everything | ❌ No single command | `server restart` |
| Check status | `server status` | `server status` (unchanged) |
| Start WireGuard only | `server start` | `service start wireguard` |
| Restart Shadowsocks | `service restart shadowsocks` | `service restart shadowsocks` (unchanged) |

---

## Questions for User

1. **Which option do you prefer?**
   - Option A: `server` = all protocols, `service` = individual
   - Option B: Remove `server start/stop/restart`, only use `service`

2. **Additional considerations:**
   - Should `server restart` restart protocols in sequence or parallel?
   - Should there be a `--force` flag to ignore errors?
   - Should there be a `--protocol` filter for `server` commands?

---

## My Recommendation

**Use Option A** because:
1. It's intuitive: "server" = entire server
2. Consistent with `server status` (already shows all)
3. Provides both convenience (server-level) and control (service-level)
4. Matches common VPS management patterns

The distinction becomes:
- **server**: High-level operations (status, start/stop/restart entire VPN)
- **service**: Low-level operations (individual protocol control)
