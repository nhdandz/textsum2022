
import json
import urllib
import json
import urllib.parse
from sys import exit
import requests
import logging
logging.basicConfig(level=logging.INFO)



multi_textrank_pid = None
textrank_pid = None
multi_lexrank_pid = None
lexrank_pid = None
multi_lsa_pid = None
lsa_pid = None

with open("configs.json", "r") as r:
    configs = json.load(r)