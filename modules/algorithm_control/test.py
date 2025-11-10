import requests
import json

if __name__ =="__main__":
    url = "http://192.168.2.25:6789/get_detail_algo"
    
    print(json.loads(requests.post(url, json={"id_mapAI":4}).content))
