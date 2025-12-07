#!/usr/bin/env python3
"""
Capybara VPN - macOS Installer Builder
Generates user-specific .pkg installers with pre-configured VPN settings
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

class InstallerBuilder:
    def __init__(self, username, arch="arm64", output_dir=None):
        self.username = username
        self.arch = arch  # "intel" or "arm64"
        self.project_root = Path(__file__).parent.parent
        self.installer_root = Path(__file__).parent

        # Default to project_root/installers if not specified
        if output_dir is None:
            self.output_dir = self.project_root / "installers"
        else:
            # If output_dir is provided, resolve it as absolute or relative to CWD
            self.output_dir = Path(output_dir).resolve()

        self.output_dir.mkdir(exist_ok=True)

        # Paths
        self.vpn_clients_dir = self.project_root / "vpn_clients"
        self.payload_dir = self.installer_root / "payload"
        self.scripts_dir = self.installer_root / "scripts"
        self.resources_dir = self.installer_root / "resources" / "binaries"
        self.build_dir = self.installer_root / "build" / f"{username}_{arch}"

    def validate_user(self):
        """Check if user configs exist"""
        wg_config = self.vpn_clients_dir / f"{self.username}_wireguard.conf"

        if not wg_config.exists():
            print(f"❌ Error: WireGuard config not found for user '{self.username}'")
            print(f"   Expected: {wg_config}")
            print(f"\nRun this first:")
            print(f"   python3 capybara.py user add {self.username}")
            return False

        return True

    def prepare_build_directory(self):
        """Prepare temporary build directory"""
        print(f"📁 Preparing build directory...")

        # Clean and create build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True)

        # Copy payload (app bundle)
        print(f"   Copying application bundle...")
        payload_dest = self.build_dir / "payload"
        shutil.copytree(self.payload_dir, payload_dest)

        # Copy scripts
        print(f"   Copying installer scripts...")
        scripts_dest = self.build_dir / "scripts"
        shutil.copytree(self.scripts_dir, scripts_dest)

        # Make scripts executable
        for script in scripts_dest.glob("*"):
            os.chmod(script, 0o755)

        # Generate proper configs with obfuscation
        print(f"   Generating configs with obfuscation for '{self.username}'...")
        generate_cmd = [
            "python3",
            str(self.installer_root / "generate_configs.py"),
            self.username
        ]
        result = subprocess.run(generate_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ ERROR: Config generation failed!")
            print(result.stderr)
            raise RuntimeError("Config generation failed")

        # Create temp directory for configs
        temp_config_dir = self.build_dir / "payload" / "tmp" / "capybara-vpn-install"
        temp_config_dir.mkdir(parents=True)

        # Copy generated configs
        generated_dir = self.installer_root / "generated_configs"

        # Copy WireGuard config (with obfuscation hooks)
        wg_config = generated_dir / f"{self.username}_wireguard.conf"
        if not wg_config.exists():
            raise RuntimeError(f"Generated config not found: {wg_config}")
        shutil.copy(wg_config, temp_config_dir)
        print(f"   ✓ WireGuard config (with obfuscation)")

        # Copy LaunchDaemon plist
        launchdaemon = generated_dir / "com.capybara.udp2raw.plist"
        if not launchdaemon.exists():
            raise RuntimeError(f"Generated LaunchDaemon not found: {launchdaemon}")
        shutil.copy(launchdaemon, temp_config_dir)
        print(f"   ✓ LaunchDaemon (for auto-starting udp2raw)")

        # Create config.txt with username
        config_file = temp_config_dir / "config.txt"
        config_file.write_text(self.username)

        print(f"✅ Build directory prepared with validated configs")

    def download_udp2raw(self):
        """Embed architecture-specific udp2raw binary"""
        print(f"📥 Embedding udp2raw binary for {self.arch}...")

        # Determine which binary to use
        if self.arch == "intel":
            binary_name = "udp2raw_amd64"
            arch_display = "Intel (x86_64)"
        elif self.arch == "arm64":
            binary_name = "udp2raw_arm64"
            arch_display = "Apple Silicon (ARM64)"
        else:
            print(f"   ❌ Error: Unknown architecture '{self.arch}'")
            return False

        # Check resources directory for pre-downloaded binary
        source_binary = self.resources_dir / binary_name

        if not source_binary.exists():
            print(f"   ❌ Error: {binary_name} not found in {self.resources_dir}")
            print(f"   Expected: {source_binary}")
            return False

        # Copy to both possible names for compatibility
        udp2raw_mp_dest = self.build_dir / "payload" / "tmp" / "udp2raw_mp"
        udp2raw_dest = self.build_dir / "payload" / "tmp" / "udp2raw"

        shutil.copy(source_binary, udp2raw_mp_dest)
        shutil.copy(source_binary, udp2raw_dest)
        os.chmod(udp2raw_mp_dest, 0o755)
        os.chmod(udp2raw_dest, 0o755)

        binary_size = source_binary.stat().st_size / 1024 / 1024
        print(f"   ✅ Embedded {binary_name} ({binary_size:.1f} MB)")
        print(f"   Architecture: {arch_display}")
        return True

    def embed_wireguard(self):
        """Embed architecture-specific WireGuard binaries"""
        print(f"📥 Embedding WireGuard tools for {self.arch}...")

        # Determine which wg binary to use
        if self.arch == "intel":
            wg_binary_name = "wg_amd64"
            arch_display = "Intel (x86_64)"
        elif self.arch == "arm64":
            wg_binary_name = "wg_arm64"
            arch_display = "Apple Silicon (ARM64)"
        else:
            print(f"   ❌ Error: Unknown architecture '{self.arch}'")
            return False

        # Source binaries
        wg_source = self.resources_dir / wg_binary_name
        wg_quick_source = self.resources_dir / "wg-quick_universal"

        if not wg_source.exists():
            print(f"   ❌ Error: {wg_binary_name} not found in {self.resources_dir}")
            return False

        if not wg_quick_source.exists():
            print(f"   ❌ Error: wg-quick_universal not found in {self.resources_dir}")
            return False

        # Destination in payload
        wg_dest = self.build_dir / "payload" / "tmp" / "wg"
        wg_quick_dest = self.build_dir / "payload" / "tmp" / "wg-quick"

        # Copy binaries
        shutil.copy(wg_source, wg_dest)
        shutil.copy(wg_quick_source, wg_quick_dest)
        os.chmod(wg_dest, 0o755)
        os.chmod(wg_quick_dest, 0o755)

        wg_size = wg_source.stat().st_size / 1024
        print(f"   ✅ Embedded wg ({wg_size:.0f} KB)")
        print(f"   ✅ Embedded wg-quick (bash script)")
        print(f"   Architecture: {arch_display}")
        return True

    def create_icon(self):
        """Create a simple app icon (optional)"""
        # For now, skip icon creation - can be added later
        pass

    def build_package(self):
        """Build the .pkg installer"""
        arch_suffix = "Intel" if self.arch == "intel" else "AppleSilicon"
        pkg_name = f"CapybaraVPN-{self.username}-{arch_suffix}.pkg"
        pkg_path = self.output_dir / pkg_name

        print(f"📦 Building installer package...")
        print(f"   Architecture: {arch_suffix}")
        print(f"   Package: {pkg_path}")

        # Build component package
        component_pkg = self.build_dir / "component.pkg"

        cmd = [
            "pkgbuild",
            "--root", str(self.build_dir / "payload"),
            "--scripts", str(self.build_dir / "scripts"),
            "--identifier", f"com.capybara.vpn.{self.username}",
            "--version", "1.0",
            "--install-location", "/",
            str(component_pkg)
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Component package built")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building component package:")
            print(e.stderr)
            return False

        # Create distribution XML
        distribution_xml = self.build_dir / "distribution.xml"
        distribution_xml.write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
    <title>Capybara VPN - {self.username}</title>
    <organization>com.capybara</organization>
    <domains enable_localSystem="true"/>
    <options customize="never" require-scripts="true" hostArchitectures="x86_64,arm64"/>

    <welcome file="welcome.html" mime-type="text/html"/>
    <conclusion file="conclusion.html" mime-type="text/html"/>

    <pkg-ref id="com.capybara.vpn.{self.username}">
        <bundle-version/>
    </pkg-ref>

    <choices-outline>
        <line choice="default">
            <line choice="com.capybara.vpn.{self.username}"/>
        </line>
    </choices-outline>

    <choice id="default"/>
    <choice id="com.capybara.vpn.{self.username}" visible="false">
        <pkg-ref id="com.capybara.vpn.{self.username}"/>
    </choice>

    <pkg-ref id="com.capybara.vpn.{self.username}" version="1.0" onConclusion="none">component.pkg</pkg-ref>
</installer-gui-script>
""")

        # Create welcome/conclusion HTML
        resources_dir = self.build_dir / "resources"
        resources_dir.mkdir(exist_ok=True)

        welcome_html = resources_dir / "welcome.html"
        welcome_html.write_text(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #333; }}
        .user {{ color: #007AFF; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Welcome to Capybara VPN</h1>
    <p>This installer will set up Capybara VPN for user: <span class="user">{self.username}</span></p>

    <h2>What will be installed:</h2>
    <ul>
        <li><strong>CapybaraWG.app</strong> - GUI VPN application (macOS 10.14+)</li>
        <li><strong>Capybara VPN.app</strong> - CLI VPN launcher (macOS 10.13+)</li>
        <li><strong>Uninstall Capybara VPN.app</strong> - GUI uninstaller</li>
        <li><strong>WireGuard tools</strong> (wg, wg-quick) - Bundled VPN client</li>
        <li><strong>udp2raw</strong> - Bundled traffic obfuscation tool</li>
        <li><strong>VPN configurations</strong> - Pre-configured for your account</li>
        <li><strong>Desktop config file</strong> - CapybaraWG-{self.username}.conf (for easy import into GUI app)</li>
    </ul>

    <h2>System Requirements:</h2>
    <ul>
        <li>macOS 10.13 (High Sierra) or later</li>
        <li>Administrator access (for VPN connections)</li>
    </ul>

    <h2>⚠️ IMPORTANT: Bypassing Gatekeeper Security</h2>
    <p><strong style="color: #d9534f;">The apps are self-signed and will be blocked by macOS Gatekeeper.</strong></p>
    <p>After installation, you MUST bypass Gatekeeper to launch the apps:</p>
    <ol>
        <li><strong>Option 1 (Recommended):</strong> Open Terminal and run:
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">xattr -cr "/Applications/CapybaraWG.app"
xattr -cr "/Applications/Capybara VPN.app"
xattr -cr "/Applications/Uninstall Capybara VPN.app"</pre>
        </li>
        <li><strong>Option 2:</strong> Right-click each app → select "Open" → click "Open" in the warning dialog</li>
    </ol>

    <h2>Everything Included:</h2>
    <p><strong>This is a self-contained installer.</strong> All dependencies are bundled - no additional software installation required!</p>
    <ul>
        <li>✅ WireGuard GUI app (CapybaraWG) for macOS 10.14+</li>
        <li>✅ CLI launcher for macOS 10.13 compatibility</li>
        <li>✅ WireGuard tools included (architecture-specific)</li>
        <li>✅ udp2raw binary included (architecture-specific)</li>
        <li>✅ VPN configurations included</li>
    </ul>
</body>
</html>
""")

        conclusion_html = resources_dir / "conclusion.html"
        conclusion_html.write_text(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #28a745; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>✅ Installation Complete!</h1>

    <h2>What Was Installed:</h2>
    <ul>
        <li><strong>CapybaraWG.app</strong> - GUI VPN application (macOS 10.14+)</li>
        <li><strong>Capybara VPN.app</strong> - CLI VPN launcher (macOS 10.13+)</li>
        <li><strong>Uninstall Capybara VPN.app</strong> - GUI uninstaller</li>
        <li><strong>WireGuard tools</strong> - VPN client (wg, wg-quick)</li>
        <li><strong>udp2raw</strong> - Traffic obfuscation tool</li>
        <li><strong>VPN configurations</strong> - Pre-configured for your account</li>
    </ul>

    <h2>⚠️ CRITICAL FIRST STEP: Bypass Gatekeeper</h2>
    <p><strong style="color: #d9534f;">Before using the apps, you MUST bypass Gatekeeper security:</strong></p>
    <ol style="background: #fff3cd; padding: 15px; border-left: 5px solid #ffc107; margin: 10px 0;">
        <li><strong>Open Terminal</strong> (Applications → Utilities → Terminal)</li>
        <li><strong>Copy and paste this command:</strong>
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; margin: 10px 0;">xattr -cr "/Applications/CapybaraWG.app"
xattr -cr "/Applications/Capybara VPN.app"
xattr -cr "/Applications/Uninstall Capybara VPN.app"</pre>
        </li>
        <li><strong>Press Enter</strong></li>
    </ol>
    <p><em>Alternative: Right-click each app → "Open" → "Open" in warning dialog</em></p>

    <h2>Next Steps:</h2>

    <h3>For CapybaraWG (GUI App - macOS 10.14+):</h3>
    <ol>
        <li><strong>Launch CapybaraWG.app</strong> from Applications folder</li>
        <li><div style="background: #d4edda; padding: 10px; border-left: 4px solid #28a745; margin: 10px 0;">
            ✨ <strong>Your tunnel is automatically imported on first launch!</strong><br>
            No manual configuration needed - CapybaraWG will find and import your settings automatically.
        </div></li>
        <li>Toggle the switch to <strong>"Activate"</strong> the tunnel</li>
        <li>Enter your administrator password when prompted</li>
        <li>✅ You're connected! All your traffic is now encrypted and obfuscated.</li>
    </ol>

    <div style="background: #f8f9fa; padding: 10px; border-left: 4px solid #6c757d; margin: 10px 0;">
        <strong>Note:</strong> A backup config file <strong>CapybaraWG-{self.username}.conf</strong> is also on your Desktop if you need to manually import later.
    </div>

    <h3>For Capybara VPN (CLI App - macOS 10.13+):</h3>
    <ol>
        <li><strong>Launch Capybara VPN.app</strong> from Applications folder</li>
        <li>The VPN configuration is pre-installed - just click <strong>"Connect"</strong></li>
        <li>Enter your administrator password when prompted</li>
    </ol>

    <h2>All Dependencies Included:</h2>
    <p><strong>No additional software needed!</strong> This installer includes everything:</p>
    <ul>
        <li>✅ WireGuard GUI app (CapybaraWG) for modern macOS</li>
        <li>✅ CLI launcher for High Sierra compatibility</li>
        <li>✅ WireGuard CLI tools (bundled for your Mac architecture)</li>
        <li>✅ udp2raw binary (bundled for your Mac architecture)</li>
        <li>✅ Pre-configured VPN settings</li>
    </ul>

    <h2>Troubleshooting:</h2>
    <p>If you have connection issues, check the log file:</p>
    <p><code>~/Library/Application Support/CapybaraVPN/vpn.log</code></p>
    <p>You can also view connection status in the app.</p>

    <h2>To Uninstall:</h2>
    <p>Open <strong>"Uninstall Capybara VPN"</strong> from your Applications folder.</p>
    <p>The uninstaller will guide you through removing components with options to keep or remove:</p>
    <ul>
        <li>udp2raw binary</li>
        <li>WireGuard tools (only if installed by this installer)</li>
        <li>VPN configurations</li>
    </ul>
</body>
</html>
""")

        # Build final product
        cmd = [
            "productbuild",
            "--distribution", str(distribution_xml),
            "--resources", str(resources_dir),
            "--package-path", str(self.build_dir),
            str(pkg_path)
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Installer package created successfully!")
            print(f"\n📦 Installer: {pkg_path}")
            print(f"   Size: {pkg_path.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building product:")
            print(e.stderr)
            return False

    def cleanup(self):
        """Clean up build directory"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)

    def build(self):
        """Main build process"""
        arch_display = "Intel (x86_64)" if self.arch == "intel" else "Apple Silicon (ARM64)"
        print(f"\n🚀 Building Capybara VPN Installer")
        print(f"   User: {self.username}")
        print(f"   Architecture: {arch_display}")
        print(f"=" * 60)

        if not self.validate_user():
            return False

        try:
            self.prepare_build_directory()
            if not self.download_udp2raw():
                return False
            if not self.embed_wireguard():
                return False
            self.create_icon()

            if self.build_package():
                arch_suffix = "Intel" if self.arch == "intel" else "AppleSilicon"
                pkg_name = f"CapybaraVPN-{self.username}-{arch_suffix}.pkg"
                print(f"\n" + "=" * 60)
                print(f"✅ SUCCESS! Installer ready for distribution")
                print(f"=" * 60)
                print(f"\nShare this file with {self.username}:")
                print(f"   {self.output_dir / pkg_name}")
                print(f"\nThey can double-click to install on {arch_display} Macs.")
                return True
            else:
                return False

        finally:
            # Optional: keep build dir for debugging
            # self.cleanup()
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Build macOS installer for Capybara VPN users"
    )
    parser.add_argument("username", help="VPN username to build installer for")
    parser.add_argument("-a", "--arch", choices=["intel", "arm64", "both"], default="both",
                       help="Target architecture: intel, arm64, or both (default: both)")
    parser.add_argument("-o", "--output", default=None,
                       help="Output directory for .pkg files (default: project_root/installers)")
    parser.add_argument("--keep-build", action="store_true",
                       help="Keep build directory after completion")

    args = parser.parse_args()

    # Build for specified architecture(s)
    if args.arch == "both":
        architectures = ["intel", "arm64"]
    else:
        architectures = [args.arch]

    all_success = True
    for arch in architectures:
        builder = InstallerBuilder(args.username, arch, args.output)
        success = builder.build()

        if not args.keep_build:
            builder.cleanup()

        all_success = all_success and success

    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
