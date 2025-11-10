import json
# from json import ObjectId 
# from pymongo import MongoClient
# import urllib
import json
# import urllib.parse
# from pymongo import MongoClient
# from sys import exit
# import requests
import logging
logging.basicConfig(level=logging.INFO)


bart_pid = None

with open("configs.json", "r") as r:
    configs = json.load(r)
