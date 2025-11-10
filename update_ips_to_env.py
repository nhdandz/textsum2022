"""
Script to update all hardcoded IPs to use environment variables
This script will update both Python and JSON files
"""
import os
import re
import json
from pathlib import Path

# IP mapping - All IPs will be replaced with HOST_IP
IP_REPLACEMENTS = {
    '192.168.210.42': '${HOST_IP}',
    '192.168.2.25': '${HOST_IP}',  # Same machine, just use HOST_IP
}

def update_json_file(file_path):
    """Update JSON files to use environment variable placeholders"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace IPs in JSON content
        for old_ip, new_var in IP_REPLACEMENTS.items():
            content = content.replace(old_ip, new_var)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def update_python_file(file_path):
    """Update Python files to use env_config"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        original_lines = lines.copy()
        updated = False
        has_env_import = False

        # Check if env_config is already imported
        for line in lines:
            if 'from env_config import' in line or 'import env_config' in line:
                has_env_import = True
                break

        # Process each line
        new_lines = []
        for i, line in enumerate(lines):
            new_line = line

            # Replace bootstrap_servers patterns - use single HOST_IP for all
            if 'bootstrap_servers' in line.lower():
                # Replace any Kafka IP with env variable
                if '192.168.210.42:9092' in line or '192.168.2.25:9092' in line:
                    if not has_env_import:
                        # List format
                        new_line = re.sub(r'\["192\.168\.(210\.42|2\.25):9092"\]', '[os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.210.42:9092")]', line)
                        new_line = re.sub(r"\['192\.168\.(210\.42|2\.25):9092'\]", '[os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.210.42:9092")]', new_line)
                        # String format
                        new_line = re.sub(r'"192\.168\.(210\.42|2\.25):9092"', 'os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.210.42:9092")', new_line)
                        new_line = re.sub(r"'192\.168\.(210\.42|2\.25):9092'", 'os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.210.42:9092")', new_line)
                    updated = True

            # Replace SERVER variable
            if 'SERVER = ' in line and ('192.168.210.42:9092' in line or '192.168.2.25:9092' in line):
                new_line = 'SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.210.42:9092")\n'
                updated = True

            # Replace URL patterns - use single HOST_IP for all
            url_patterns = [
                (r'url_status\s*=\s*["\']http://192\.168\.(210\.42|2\.25):5002/api/multisum/status["\']',
                 'url_status = os.getenv("STATUS_WEB_URL", "http://192.168.210.42:5002/api/multisum/status")'),
                (r'url_cluster\s*=\s*["\']http://192\.168\.(210\.42|2\.25):9400/TextClustering["\']',
                 'url_cluster = os.getenv("CLUSTERING_URL", "http://192.168.210.42:9400/TextClustering")'),
                (r'url_get_topic_algo\s*=\s*["\']http://192\.168\.(210\.42|2\.25):6789/get_detail_algo["\']',
                 'url_get_topic_algo = os.getenv("ALGO_CONTROL_URL", "http://192.168.210.42:6789") + "/get_detail_algo"'),
                (r'URL\s*=\s*["\']http://192\.168\.(210\.42|2\.25):8101/change_status_memsum["\']',
                 'URL = os.getenv("MEMSUM_URL", "http://192.168.210.42:8100") + "/change_status_memsum"'),
            ]

            for pattern, replacement in url_patterns:
                if re.search(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    updated = True
                    break

            new_lines.append(new_line)

        # Add import if needed and file was updated
        if updated and not has_env_import:
            # Find where to insert import (after other imports)
            insert_pos = 0
            for i, line in enumerate(new_lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_pos = i + 1
                elif insert_pos > 0 and line.strip() and not line.strip().startswith('#'):
                    break

            if insert_pos == 0:
                insert_pos = 0

            new_lines.insert(insert_pos, 'import os\n')
            if 'from dotenv import load_dotenv' not in ''.join(new_lines):
                new_lines.insert(insert_pos + 1, 'from dotenv import load_dotenv\n')
                new_lines.insert(insert_pos + 2, 'load_dotenv()\n\n')

        if new_lines != original_lines:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✓ Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update 
    all files"""
    root_dir = Path(__file__).parent

    # Files to skip
    skip_files = {
        'update_ips_to_env.py',
        'env_config.py',
        '.env',
    }

    # Directories to skip
    skip_dirs = {
        '.git',
        '__pycache__',
        'venv',
        'node_modules',
        '.pytest_cache',
        'transformers',  # Skip large third-party library
    }

    json_updated = 0
    py_updated = 0

    print("=" * 60)
    print("Updating JSON files...")
    print("=" * 60)

    # Update JSON files
    for json_file in root_dir.rglob('*.json'):
        if any(skip_dir in json_file.parts for skip_dir in skip_dirs):
            continue
        if json_file.name in skip_files:
            continue

        if update_json_file(json_file):
            json_updated += 1

    print("\n" + "=" * 60)
    print("Updating Python files...")
    print("=" * 60)

    # Update Python files
    for py_file in root_dir.rglob('*.py'):
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue
        if py_file.name in skip_files:
            continue

        if update_python_file(py_file):
            py_updated += 1

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"JSON files updated: {json_updated}")
    print(f"Python files updated: {py_updated}")
    print(f"Total files updated: {json_updated + py_updated}")
    print("\nNote: JSON files now contain ${HOST_IP} placeholders.")
    print("You'll need to resolve these at runtime using environment variables.")

if __name__ == '__main__':
    main()
