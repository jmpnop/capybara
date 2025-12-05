#!/usr/bin/env python3
"""
Batch Installer Builder for Capybara VPN
Builds macOS .pkg installers for all configured users
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class BatchInstallerBuilder:
    def __init__(self, output_dir=None):
        self.project_root = Path(__file__).parent.parent
        self.installer_root = Path(__file__).parent
        self.vpn_clients_dir = self.project_root / "vpn_clients"

        # Default to project_root/installers if not specified
        if output_dir is None:
            self.output_dir = self.project_root / "installers"
        else:
            # If output_dir is provided, resolve it as absolute or relative to CWD
            self.output_dir = Path(output_dir).resolve()

        self.builder_script = Path(__file__).parent / "build_installer.py"

        self.output_dir.mkdir(exist_ok=True)

    def get_all_users(self):
        """Get list of all users with VPN configs"""
        if not self.vpn_clients_dir.exists():
            print(f"❌ Error: VPN clients directory not found: {self.vpn_clients_dir}")
            return []

        # Find all WireGuard config files
        wg_configs = list(self.vpn_clients_dir.glob("*_wireguard.conf"))

        if not wg_configs:
            print(f"❌ Error: No WireGuard configs found in {self.vpn_clients_dir}")
            return []

        # Extract usernames from config filenames
        users = []
        for config in wg_configs:
            # Extract username from filename like "alice_wireguard.conf"
            username = config.stem.replace("_wireguard", "")
            users.append(username)

        return sorted(set(users))  # Remove duplicates and sort

    def build_installer_for_user(self, username):
        """Build installers for a single user (both architectures)"""
        print(f"\n{'=' * 70}")
        print(f"Building installers for: {username}")
        print(f"{'=' * 70}")

        # Build for both Intel and ARM64
        cmd = [
            sys.executable,  # Use same Python interpreter
            str(self.builder_script),
            username,
            "--arch", "both",  # Build both architectures
            "-o", str(self.output_dir)
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            # Print the output
            print(result.stdout)

            if result.returncode == 0:
                # Check for both package files
                intel_pkg = self.output_dir / f"CapybaraVPN-{username}-Intel.pkg"
                arm64_pkg = self.output_dir / f"CapybaraVPN-{username}-AppleSilicon.pkg"

                packages = []
                if intel_pkg.exists():
                    packages.append({
                        "arch": "Intel",
                        "path": str(intel_pkg),
                        "size_mb": f"{intel_pkg.stat().st_size / 1024 / 1024:.2f}"
                    })
                if arm64_pkg.exists():
                    packages.append({
                        "arch": "AppleSilicon",
                        "path": str(arm64_pkg),
                        "size_mb": f"{arm64_pkg.stat().st_size / 1024 / 1024:.2f}"
                    })

                if packages:
                    return {
                        "username": username,
                        "status": "success",
                        "packages": packages
                    }
                else:
                    return {
                        "username": username,
                        "status": "error",
                        "error": "No package files found after build"
                    }
            else:
                return {
                    "username": username,
                    "status": "error",
                    "error": result.stderr
                }

        except subprocess.CalledProcessError as e:
            return {
                "username": username,
                "status": "error",
                "error": e.stderr
            }
        except Exception as e:
            return {
                "username": username,
                "status": "error",
                "error": str(e)
            }

    def build_all(self, users=None):
        """Build installers for all users or specified list"""
        if users is None:
            users = self.get_all_users()

        if not users:
            print("No users found!")
            return []

        print(f"\n🚀 Batch Building Capybara VPN Installers")
        print(f"   Total users: {len(users)}")
        print(f"   Output directory: {self.output_dir}")
        print(f"=" * 70)

        results = []
        for i, username in enumerate(users, 1):
            print(f"\n[{i}/{len(users)}]")
            result = self.build_installer_for_user(username)
            results.append(result)

        return results

    def print_summary(self, results):
        """Print build summary"""
        print(f"\n\n{'=' * 70}")
        print(f"📊 BUILD SUMMARY")
        print(f"{'=' * 70}\n")

        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "error"]

        if successful:
            total_packages = sum(len(r["packages"]) for r in successful)
            print(f"✅ Successfully built installers for {len(successful)} user(s) ({total_packages} packages):\n")
            total_size = 0
            for result in successful:
                print(f"   • {result['username']}")
                for pkg in result["packages"]:
                    size_mb = float(pkg["size_mb"])
                    total_size += size_mb
                    arch_label = f"[{pkg['arch']}]"
                    print(f"     {arch_label:<20} → {pkg['path']}")
                    print(f"     {'':20}    Size: {pkg['size_mb']} MB")

            print(f"\n   Total size: {total_size:.2f} MB")
            print(f"   Total packages: {total_packages}")

        if failed:
            print(f"\n❌ Failed to build {len(failed)} user(s):\n")
            for result in failed:
                print(f"   • {result['username']:<20}")
                error_lines = result["error"].split("\n")
                for line in error_lines[:3]:  # Show first 3 lines of error
                    if line.strip():
                        print(f"     {'':20}    {line}")

        print(f"\n{'=' * 70}")
        print(f"Summary: {len(successful)} users succeeded, {len(failed)} failed")
        print(f"Output: {self.output_dir}")
        print(f"{'=' * 70}\n")

        return len(successful), len(failed)

    def create_distribution_manifest(self, results):
        """Create a manifest file listing all built installers"""
        successful = [r for r in results if r["status"] == "success"]

        if not successful:
            return

        total_packages = sum(len(r["packages"]) for r in successful)

        manifest = {
            "build_date": datetime.now().isoformat(),
            "total_users": len(successful),
            "total_packages": total_packages,
            "users": []
        }

        for result in successful:
            user_entry = {
                "username": result["username"],
                "packages": []
            }
            for pkg in result["packages"]:
                user_entry["packages"].append({
                    "architecture": pkg["arch"],
                    "filename": Path(pkg["path"]).name,
                    "size_mb": pkg["size_mb"],
                    "path": pkg["path"]
                })
            manifest["users"].append(user_entry)

        manifest_file = self.output_dir / "BUILD_MANIFEST.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"📄 Build manifest created: {manifest_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch build macOS installers for all Capybara VPN users"
    )
    parser.add_argument("users", nargs="*",
                       help="Specific users to build for (default: all users)")
    parser.add_argument("-o", "--output", default=None,
                       help="Output directory for .pkg files (default: project_root/installers)")
    parser.add_argument("--list", action="store_true",
                       help="List all available users and exit")
    parser.add_argument("--manifest", action="store_true",
                       help="Create BUILD_MANIFEST.json file")

    args = parser.parse_args()

    builder = BatchInstallerBuilder(args.output)

    # List users and exit
    if args.list:
        users = builder.get_all_users()
        if users:
            print(f"Found {len(users)} user(s):\n")
            for user in users:
                wg_config = builder.vpn_clients_dir / f"{user}_wireguard.conf"
                if wg_config.exists():
                    print(f"  ✅ {user}")
                else:
                    print(f"  ⚠️  {user} (config missing)")
        else:
            print("No users found")
        return

    # Build installers
    users = args.users if args.users else None
    results = builder.build_all(users)

    if not results:
        print("No installers built")
        sys.exit(1)

    # Print summary
    succeeded, failed = builder.print_summary(results)

    # Create manifest if requested
    if args.manifest:
        builder.create_distribution_manifest(results)

    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
