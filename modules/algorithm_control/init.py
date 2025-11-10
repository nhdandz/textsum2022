
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
logging.basicConfig(level=logging.INFO)


my_conn, my_db, env_configs, configs =None, None, None, None
with open("configs.json", "r") as r:
    CONFIG_TO_WEB = json.load(r)


def Initialize():
    global my_conn, my_db, env_configs,configs
    with open("configs.json", "r") as r:
        configs = json.load(r)
        
    with open(".env", "r") as r:
        env_configs = json.load(r)
    
    username_rh = urllib.parse.quote_plus(env_configs['username'].strip())
    password_rh = urllib.parse.quote_plus(env_configs['password'].strip())
    if username_rh!="" and password_rh!="":
        connection_string='mongodb://%s:%s@%s:%s/%s?authSource=admin' % (username_rh, password_rh,
                env_configs['host'],env_configs['port'],
                env_configs['auth_database'])
    else:
            connection_string='mongodb://%s:%s/%s' % (env_configs['host'],
                            env_configs['port'], env_configs['auth_database'])
    try:
        my_conn=MongoClient(connection_string, maxPoolSize=5000)
        my_db=my_conn[env_configs['database']]
        my_conn.admin.command('ismaster')
    except:
        print("Mongo Connection Error")
        exit(1)

def update_status_algo(id_algo, status):
    
    # update change status mapAlgTypeAI
    try:
        mapAl_algo = list(my_db[env_configs["mapAlgTypeAI_collection"]].find({"algorId":id_algo}))
        mapAl_algo_id = mapAl_algo[0]["_id"]
        latest_mapAI_status = mapAl_algo[0]["enable"]
        my_db[env_configs["mapAlgTypeAI_collection"]].update({"_id" :ObjectId(mapAl_algo_id) },{'$set' : {"enable":status}})
        logging.INFO("Successfull change status mapAlgTypeAI")
    except:
        return 0
    
    # update change status algorithm

    try:
        algorithm = list(my_db[env_configs["algorithm_collection"]].find({"algorId":id_algo}))
        latest_algo_status = algorithm["enable"]
        
        ulr_change_status = algorithm[0]["urlChangeStatus"]
        
        r = requests.post(ulr_change_status, json={"status":status})
        if r.status_code !=200:
            logging.INFO(f"Can not change status algorithm {id_algo}")
            my_db[env_configs["mapAlgTypeAI_collection"]].update({"_id" :ObjectId(mapAl_algo_id) },{'$set' : {"enable":latest_mapAI_status}})
            return 0

        my_db[env_configs["algorithm_collection"]].update({"_id" :ObjectId(algorithm["_id"]) },{'$set' : {"enable":status}})
        logging.INFO("Successfull change status algorithm")
        
        data_to_web ={
            "id":mapAl_algo["id"],
            "aiId":mapAl_algo["aiId"],
            "typeAIId":mapAl_algo["typeAIId"] ,
            "algorId":mapAl_algo["algorId"] ,
            "enable":status
        }
        
        try:
            URL_TO_WEB = CONFIG_TO_WEB["url_update_web"]
            r = requests.post(URL_TO_WEB, json=data_to_web)
            if r.status_code !=200:
                # if not change status in web, update latest status mapAI, algorithm
                logging.INFO("Can not async to WEB change status")
                my_db[env_configs["mapAlgTypeAI_collection"]].update({"_id" :ObjectId(mapAl_algo_id) },{'$set' : {"enable":latest_mapAI_status}})
                my_db[env_configs["algorithm_collection"]].update({"_id" :ObjectId(algorithm["_id"]) },{'$set' : {"enable":latest_algo_status}})
                return 0
        except:
            logging.INFO("Can not async to WEB change status")
            my_db[env_configs["mapAlgTypeAI_collection"]].update({"_id" :ObjectId(mapAl_algo_id) },{'$set' : {"enable":latest_mapAI_status}})
            my_db[env_configs["algorithm_collection"]].update({"_id" :ObjectId(algorithm["_id"]) },{'$set' : {"enable":latest_algo_status}})
            return 0
        
        return 1
    except:
        return 0
    
def insert_new_algo():
    new_algo = {
        "algorId" : 30,# ?? update new id
        "displayName" : "LongPegasus ???",
        "description" : "LongPegasus ???",
        "urlAPI" : "http://192.168.210.42:6800/MultiPegSingle ????",
        "needPercentLong" : False,
        "enable" : 0,
        "urlChangeStatus" : "url ???"
    }
    new_map_ai = {
        "id" : "??",
        "aiId" : "??",
        "typeAIId" : "??",
        "algorId" : "??",
        "enable" : 0
    }
    
    data_to_web ={
        "id":new_map_ai["id"],
        "aiId":new_map_ai["aiId"],
        "typeAIId":new_map_ai["typeAIId"] ,
        "algorId":new_map_ai["algorId"]  ,
        "displayName":new_algo["displayName"],
        "description":new_algo["description"],
        "needPercentLong": new_algo["needPercentLong"],
        "needKeywords": False
    }
    try:
        my_db[env_configs["algorithm_collection"]].insert(new_algo)
    except:
        logging.INFO("Can not insert new algoritm to algorithm collection")
        return 0
    
    try:
        my_db[env_configs["mapAlgTypeAI_collection"]].insert(new_map_ai)
    except:
        logging.INFO("Can not insert new map ai to mapAlgTypeAI collection")
        return 0 
    
    # async to web
    try:
        URL_INSERT_WEB = CONFIG_TO_WEB["url_insert_algo_web"]
        r = requests.post(URL_INSERT_WEB, json=data_to_web)
        if r.status_code !=200:
            logging.INFO("Can not insert async new algorithm to web")
            return 0
    except:
        return 0
    
    return 1



# def get_detail_algo(mapAlgTypeAI_id):
#     try:
#         mapAl_algo = list(my_db[env_configs["mapAlgTypeAI_collection"]].find({"id":mapAlgTypeAI_id}))
#         id_algo = mapAl_algo[0]["algorId"]
#     except:
#         return None
#     try:
#         algorithm = list(my_db[env_configs["algorithm_collection"]].find({"algorId":id_algo}))
#         return algorithm[0]["topic"], id_algo
#     except:
#         return None, None

def get_detail_algo(mapAlgTypeAI_id):
    with open("maptype.json", "r") as r:
        maptype = json.load(r)
    with open("algo.json", "r") as r:
        algo = json.load(r)

    id_algo = None
    for obj in maptype:
        if mapAlgTypeAI_id == obj["id"]:
            id_algo = obj["algorId"]
            break

    if id_algo is None:
        return None, None

    for obj in algo:
        if obj["algorId"] == id_algo:
            return obj["topic"], id_algo
    return None, None


if __name__ =="__main__":
    # Initialize()
    print(get_detail_algo(10))