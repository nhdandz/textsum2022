#!/usr/bin/env python3
"""
Simple script to replace all hardcoded IPs with ${HOST_IP} placeholder
Run this to update all JSON, Python, and config files
"""
import os
import sys
from pathlib import Path

def replace_ips_in_file(file_path):
    """Replace all IP addresses with ${HOST_IP} placeholder"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Replace both IPs with ${HOST_IP}
        content = content.replace('192.168.210.42', '${HOST_IP}')
        content = content.replace('192.168.2.25', '${HOST_IP}')

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    root = Path(__file__).parent

    # Directories to skip
    skip_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules',
                 '.pytest_cache', 'transformers'}

    # Files to skip
    skip_files = {'replace_ips_simple.py', 'update_ips_to_env.py',
                  'env_config.py', '.env'}

    # File extensions to process
    extensions = {'.py', '.json', '.yaml', '.yml', '.txt', '.conf'}

    updated_files = []

    print("🔍 Scanning for files with hardcoded IPs...")
    print("=" * 60)

    for file_path in root.rglob('*'):
        # Skip directories
        if file_path.is_dir():
            continue

        # Skip if in skip_dirs
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue

        # Skip specific files
        if file_path.name in skip_files:
            continue

        # Only process specific extensions
        if file_path.suffix not in extensions:
            continue

        # Try to replace
        if replace_ips_in_file(file_path):
            rel_path = file_path.relative_to(root)
            print(f"✓ {rel_path}")
            updated_files.append(rel_path)

    print("\n" + "=" * 60)
    print(f"✅ Updated {len(updated_files)} files")
    print("=" * 60)

    if updated_files:
        print("\n📝 Updated files:")
        for f in updated_files[:20]:  # Show first 20
            print(f"   - {f}")
        if len(updated_files) > 20:
            print(f"   ... and {len(updated_files) - 20} more files")

    print("\n⚠️  Note: JSON files now contain ${HOST_IP} placeholders.")
    print("   You'll need to handle these at runtime.")
    print("\n💡 Next steps:")
    print("   1. Check the .env file and set your HOST_IP")
    print("   2. Make sure docker-compose.yml loads the .env file")
    print("   3. For JSON files, create a loader that replaces ${HOST_IP}")

if __name__ == '__main__':
    main()
