#!/usr/bin/env python3
"""
Add env_file to all services in docker-compose.yml
"""
import re
from pathlib import Path

def add_env_file_to_services(file_path):
    """Add env_file section to all services that don't have it"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    modified = False

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is a service definition (starts with 2 spaces and a name)
        if re.match(r'^  \w+:', line) and not line.strip().startswith('#'):
            service_name = line.strip().rstrip(':')

            # Skip infrastructure services
            if service_name in ['version', 'services', 'networks', 'volumes']:
                i += 1
                continue

            # Look ahead to see if env_file already exists
            has_env_file = False
            has_environment = False
            env_start_idx = None
            indent_level = None

            for j in range(i + 1, min(i + 50, len(lines))):
                if lines[j].strip().startswith('env_file:'):
                    has_env_file = True
                    break
                if lines[j].strip().startswith('environment:'):
                    has_environment = True
                    env_start_idx = j
                    # Get indent level of environment:
                    indent_level = len(lines[j]) - len(lines[j].lstrip())
                    break
                # If we hit another service, stop looking
                if re.match(r'^  \w+:', lines[j]):
                    break

            # Add env_file before environment section if it doesn't exist
            if not has_env_file and has_environment and env_start_idx:
                # Find where to insert (before environment)
                insert_pos = env_start_idx - i + len(new_lines) - 1
                indent = ' ' * indent_level
                new_lines.insert(insert_pos, f'{indent}env_file:\n')
                new_lines.insert(insert_pos + 1, f'{indent}  - .env\n')
                modified = True
                print(f"✓ Added env_file to: {service_name}")

        i += 1

    if modified:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)

    return modified

def main():
    compose_files = [
        Path('docker-compose.yml'),
        Path('docker-compose.hub.yml'),
    ]

    for compose_file in compose_files:
        if compose_file.exists():
            print(f"\n📝 Processing: {compose_file}")
            print("=" * 60)
            if add_env_file_to_services(compose_file):
                print(f"✅ Modified: {compose_file}")
            else:
                print(f"ℹ️  No changes needed: {compose_file}")

if __name__ == '__main__':
    main()
