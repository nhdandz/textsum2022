import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

with open("configs.json", "r") as r:
    configs = json.load(r)

def expand_env_vars(config_dict):
    """Recursively expand ${VAR} patterns in config values"""
    if isinstance(config_dict, dict):
        return {k: expand_env_vars(v) for k, v in config_dict.items()}
    elif isinstance(config_dict, list):
        return [expand_env_vars(item) for item in config_dict]
    elif isinstance(config_dict, str):
        pattern = r'\$\{([^}]+)\}'
        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        return re.sub(pattern, replacer, config_dict)
    return config_dict

configs = expand_env_vars(configs)
