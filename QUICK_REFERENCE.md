# Capybara v2.0 - Quick Reference Card

## 🚀 New Features Summary

**Version 2.0 adds 7 major feature areas with 15 new commands!**

---

## 📝 Logs
```bash
./capybara.py logs show                    # View all logs
./capybara.py logs show --service udp2raw  # Specific service
./capybara.py logs tail                    # Follow live
```

## 🔌 Connections
```bash
./capybara.py connection list              # Active connections
./capybara.py connection kick alice        # Disconnect user
./capybara.py connection kick-all          # Emergency disconnect
```

## 🔧 Services
```bash
./capybara.py service status               # Check all services
./capybara.py service restart wireguard    # Restart specific
./capybara.py service restart udp2raw      # Target one service
```

## 💾 Backup
```bash
./capybara.py backup create                # Create backup
./capybara.py backup list                  # Show all backups
./capybara.py backup restore <name>        # Restore config
```

## 🔍 Diagnostics
```bash
./capybara.py diag ping alice              # Test connectivity
./capybara.py diag ports                   # Check open ports
./capybara.py diag handshake alice         # Connection status
```

## 🏥 Health
```bash
./capybara.py health check                 # System health
```

## 📊 Reports
```bash
./capybara.py report generate              # Daily report
./capybara.py report generate --format json  # JSON output
./capybara.py report generate --format csv   # CSV export
```

---

## 🎯 Most Useful Commands

```bash
# Daily routine
./capybara.py server status
./capybara.py health check
./capybara.py user list
./capybara.py connection list

# Troubleshooting
./capybara.py logs show --lines 50
./capybara.py diag ping <user>
./capybara.py service status

# Maintenance
./capybara.py backup create
./capybara.py report generate
```

---

## 📚 Documentation

- **[CLIENT_SETUP.md](CLIENT_SETUP.md)** - ⭐ **NEW!** macOS and iOS client setup
- **[FULL_FEATURES_GUIDE.md](FULL_FEATURES_GUIDE.md)** - Complete guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built
- **[README.md](README.md)** - Main overview

## 💡 Getting Help

```bash
./capybara.py --help                # Main help with quick start
./capybara.py <command> --help      # Command-specific help with examples
```

Every command group now includes practical examples in its help text!

---

**All features tested ✅ | Production ready ✅ | Fully documented ✅**
