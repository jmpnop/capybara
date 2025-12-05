# Building CapybaraWG from Source

CapybaraWG is a rebranded build of WireGuard that is completely isolated from the official WireGuard app.

## Prerequisites

- macOS 10.14+ (for running the app) or macOS 10.13+ (for CLI version)
- Xcode 14.0+
- Go 1.19+ (for building wireguard-go)

## Build Steps

### 1. Clone WireGuard Source

```bash
cd macos-installer
git clone https://github.com/WireGuard/wireguard-apple.git wireguard-src
cd wireguard-src
git checkout 1.0.16-27
```

### 2. Apply Patches

**File: `Sources/WireGuardKitC/WireGuardKitC.h`**

Add `#include <sys/types.h>` at the top (after copyright header):

```c
// SPDX-License-Identifier: MIT
// Copyright © 2018-2023 WireGuard LLC. All Rights Reserved.

#include <sys/types.h>
#include "key.h"
#include "x25519.h"
```

**File: `Sources/WireGuardApp/UI/macOS/Info.plist`**

Add after `CFBundleName`:

```xml
<key>CFBundleDisplayName</key>
<string>CapybaraWG</string>
```

Change the app group key from `com.wireguard.macos.app_group_id` to:

```xml
<key>com.capybara.capybarawg.app_group_id</key>
<string>$(DEVELOPMENT_TEAM).group.$(APP_ID_MACOS)</string>
```

Change `NSPrincipalClass` from `WireGuard.Application` to:

```xml
<key>NSPrincipalClass</key>
<string>CapybaraWG.Application</string>
```

**File: `Sources/Shared/FileManager+Extension.swift`**

Change the app group dictionary keys:

```swift
static var appGroupId: String? {
    #if os(iOS)
    let appGroupIdInfoDictionaryKey = "com.capybara.capybarawg.app_group_id"
    #elseif os(macOS)
    let appGroupIdInfoDictionaryKey = "com.capybara.capybarawg.app_group_id"
    #else
    #error("Unimplemented")
    #endif
    return Bundle.main.object(forInfoDictionaryKey: appGroupIdInfoDictionaryKey) as? String
}
```

### 3. Create Developer.xcconfig

**File: `Sources/WireGuardApp/Config/Developer.xcconfig`**

```
// Developer.xcconfig - Self-signed build for CapybaraWG

// Self-signed (no Apple Developer account needed)
CODE_SIGN_IDENTITY = -
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM =

// The bundle identifier of the apps - completely separate from official WireGuard
APP_ID_IOS = com.capybara.capybarawg
APP_ID_MACOS = com.capybara.capybarawg
```

### 4. Filter Tunnels by Bundle Identifier

**File: `Sources/WireGuardApp/Tunnel/TunnelsManager.swift`**

Add filtering after loading tunnels to prevent showing other apps' tunnels.

In the `create()` function, after `var tunnelManagers = managers ?? []` add:

```swift
// Filter to only CapybaraWG tunnels (not official WireGuard or other apps)
if let ourBundleId = Bundle.main.bundleIdentifier {
    let ourExtensionBundleId = "\(ourBundleId).network-extension"
    tunnelManagers = tunnelManagers.filter { manager in
        guard let proto = manager.protocolConfiguration as? NETunnelProviderProtocol else { return false }
        return proto.providerBundleIdentifier == ourExtensionBundleId
    }
}
```

In the `reload()` function, after `let loadedTunnelProviders = managers ?? []` add the same filtering code (change `let` to `var`):

```swift
var loadedTunnelProviders = managers ?? []

// Filter to only CapybaraWG tunnels (not official WireGuard or other apps)
if let ourBundleId = Bundle.main.bundleIdentifier {
    let ourExtensionBundleId = "\(ourBundleId).network-extension"
    loadedTunnelProviders = loadedTunnelProviders.filter { manager in
        guard let proto = manager.protocolConfiguration as? NETunnelProviderProtocol else { return false }
        return proto.providerBundleIdentifier == ourExtensionBundleId
    }
}
```

### 5. Update UI Strings

**File: `Sources/WireGuardApp/Base.lproj/Localizable.strings`**

Replace WireGuard branding with CapybaraWG:

```bash
sed -i.bak 's/"About WireGuard"/"About CapybaraWG"/g; s/"Quit WireGuard"/"Quit CapybaraWG"/g; s/"Manage WireGuard Tunnels"/"Manage CapybaraWG Tunnels"/g' Sources/WireGuardApp/Base.lproj/Localizable.strings
```

This changes:
- Menu: "About WireGuard" → "About CapybaraWG"
- Menu: "Quit WireGuard" → "Quit CapybaraWG"
- Window: "Manage WireGuard Tunnels" → "Manage CapybaraWG Tunnels"

### 6. Rename Product in Xcode Project

Edit `WireGuard.xcodeproj/project.pbxproj`:

```bash
sed -i.bak 's/PRODUCT_NAME = WireGuard;/PRODUCT_NAME = CapybaraWG;/g' WireGuard.xcodeproj/project.pbxproj
```

### 7. Build

```bash
xcodebuild -target WireGuardmacOS \
  -configuration Release \
  -sdk macosx \
  CODE_SIGN_STYLE=Manual \
  CODE_SIGN_IDENTITY= \
  DEVELOPMENT_TEAM= \
  build
```

The built app will be at: `build/Release/CapybaraWG.app`

### 8. Bypass Gatekeeper

Since the app is self-signed:

```bash
xattr -cr build/Release/CapybaraWG.app
```

## Key Differences from Official WireGuard

- **Bundle ID**: `com.capybara.capybarawg` (vs `com.wireguard.macos`)
- **Display Name**: `CapybaraWG` (vs `WireGuard`)
- **App Group**: Separate container (won't share tunnels with official WireGuard)
- **Configuration**: Completely isolated settings and tunnels

## Automatic Tunnel Configuration Import

**CapybaraWG automatically imports your VPN configuration on first launch!**

### How Auto-Import Works

When you install the Capybara VPN package:

1. **Installer copies config** to `~/Library/Application Support/CapybaraVPN/<username>_wireguard.conf`
2. **Backup copy placed on Desktop** as `CapybaraWG-<username>.conf` (for manual use if needed)
3. **On first launch**, CapybaraWG checks if there are zero tunnels
4. **If no tunnels found**, it automatically looks for and imports the config from Application Support
5. **Tunnel appears** ready to use - just toggle the switch to activate!

### Manual Import (If Needed)

If you need to manually import the config later (e.g., after resetting CapybaraWG):

**Method 1: Import via Menu**
1. Launch CapybaraWG.app
2. Click "Import Tunnel(s) from File..." (bottom left)
3. Select `CapybaraWG-<username>.conf` from Desktop
4. Click "Open"

**Method 2: Drag and Drop**
1. Launch CapybaraWG.app
2. Drag `CapybaraWG-<username>.conf` into the CapybaraWG window

### Implementation Details

The auto-import feature is implemented in `Sources/WireGuardApp/UI/macOS/AppDelegate.swift`:

- **Trigger**: `applicationDidFinishLaunching` after `TunnelsManager.create()` succeeds
- **Condition**: Only runs if `tunnelsManager.numberOfTunnels() == 0`
- **Location**: Looks for any `.conf` file in `~/Library/Application Support/CapybaraVPN/`
- **Name extraction**: Strips `_wireguard` suffix from filename (e.g., `pasha_wireguard.conf` → tunnel named `pasha`)
- **Error handling**: Fails silently if no config found or parse error occurs

## Troubleshooting

### Build fails with Swift/C errors

Make sure you added `#include <sys/types.h>` to `WireGuardKitC.h`

### App crashes on launch

Check that you updated `NSPrincipalClass` from `WireGuard.Application` to `CapybaraWG.Application`

### Shows official WireGuard tunnels

Make sure you updated both:
1. Info.plist app group key
2. FileManager+Extension.swift app group dictionary key

Both must reference `com.capybara.capybarawg.app_group_id`

### Sees official WireGuard tunnels

If CapybaraWG shows tunnels from the official WireGuard app, check that you added the filtering code to `TunnelsManager.swift` in both the `create()` and `reload()` functions to filter by `providerBundleIdentifier`
