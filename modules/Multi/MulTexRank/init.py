
import json
from bson import ObjectId
from pymongo import MongoClient
import urllib
import json
import urllib.parse
from pymongo import MongoClient
from sys import exit
import requests
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

multi_textrank_pid = None
textrank_pid = None
multi_lexrank_pid = None
lexrank_pid = None
multi_lsa_pid = None
lsa_pid = None

with open("configs.json", "r") as r:
    configs = json.load(r)

# Expand environment variables in configs
def expand_env_vars(config_dict):
    """Recursively expand ${VAR} patterns in config values"""
    if isinstance(config_dict, dict):
        return {k: expand_env_vars(v) for k, v in config_dict.items()}
    elif isinstance(config_dict, list):
        return [expand_env_vars(item) for item in config_dict]
    elif isinstance(config_dict, str):
        # Replace ${VAR} with environment variable value
        import re
        pattern = r'\$\{([^}]+)\}'
        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        return re.sub(pattern, replacer, config_dict)
    return config_dict

configs = expand_env_vars(configs)