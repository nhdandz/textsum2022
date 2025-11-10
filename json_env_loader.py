"""
JSON Environment Variable Loader
Use this to load JSON files that contain ${HOST_IP} placeholders
"""
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

def expand_env_vars(text):
    """
    Replace ${VAR_NAME} placeholders with environment variables

    Args:
        text: String containing ${VAR} placeholders

    Returns:
        String with all placeholders replaced
    """
    # Get HOST_IP from env or use default
    host_ip = os.getenv('HOST_IP', '${HOST_IP}')

    # Replace ${HOST_IP} with actual value
    text = text.replace('${HOST_IP}', host_ip)

    # Also support $HOST_IP (without braces)
    text = re.sub(r'\$HOST_IP\b', host_ip, text)

    return text

def load_json_with_env(file_path):
    """
    Load JSON file and expand environment variables

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON with environment variables expanded
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Expand environment variables
    content = expand_env_vars(content)

    # Parse JSON
    return json.loads(content)

def load_json_list_with_env(file_path):
    """
    Load JSON file containing one JSON object per line (JSONL format)

    Args:
        file_path: Path to JSONL file

    Returns:
        List of parsed JSON objects with environment variables expanded
    """
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Expand environment variables
            line = expand_env_vars(line)
            # Parse JSON
            results.append(json.loads(line))
    return results


# Example usage
if __name__ == '__main__':
    # Test with algo.json if it exists
    test_file = Path(__file__).parent / 'modules' / 'root_kafka' / 'algo.json'

    if test_file.exists():
        print(f"Testing with: {test_file}")
        print(f"HOST_IP: {os.getenv('HOST_IP', '${HOST_IP}')}")
        print("=" * 60)

        try:
            data = load_json_list_with_env(test_file)
            print(f"Loaded {len(data)} entries")

            # Show first entry
            if data:
                print("\nFirst entry:")
                print(json.dumps(data[0], indent=2))
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Test file not found")
        print("\nUsage example:")
        print("  from json_env_loader import load_json_with_env")
        print("  data = load_json_with_env('config.json')")
