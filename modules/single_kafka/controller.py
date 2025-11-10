from helper import get_raw_text_by_topic,get_length
import copy
import queue
import requests
from threading import Thread 
import json

LENGTH_THRESHOLD = 800
SHORT_EXTRACT = 1
LONG_EXTRACT = 4
SHORT_ABSTRACT = 3
LONG_ABSTRACT = 2
api_config = []
with open('db/mapAlgTypeAI.json') as f:
    mapAlgTypeAI = json.load(f)
with open('db/coreAI.json') as f:
    coreAI = json.load(f)
with open('db/TypeAI.json') as f:
    TypeAI = json.load(f)
with open('db/algorithm.json') as f:
    algorithm = json.load(f)
with open('api_config.json') as f:
    for line in f:
        api_config.append(json.loads(line))
load_model_config = {"1":True,"2":True,"3":True,"4":True,"5":True,"6":True,"7":True,"8":True,"9":True,"10":True,"11":True,"12":True,"13":True,"14":True,"15":True,"16":True,"17":True}
# print()
def load_cache(load_model_config):
    for key in load_model_config:
        PARAMS = {"status":load_model_config[key]}
        for config in api_config:
            if config['algorId'] == int(key):
                URL = config['urlStatusAPI']+'/change_status'
        r =  requests.post(url = URL, json = PARAMS)
# load_cache(load_model_config)
def get_input_by_topic(content):
    raw_text = content['raw_text']
    list_topic = content['topic']
    input = []
    if len(list_topic) == 0:
        content['topic'] = 'non_topic'
        input.append(content)
    else:
        for key in list_topic:
            print(key)
            data = copy.deepcopy(content)
            raw_text_topic = get_raw_text_by_topic(list_topic[key],raw_text)
            data['raw_text'] = raw_text_topic
            data['topic'] = key
            input.append(data)
    return input

def get_input_by_len_and_algor(input):
    for data in input:
        data['algor_choose'] = {
                    "type_ai_id": None,
                    "algor_id": None,
                }
                
        # aiID = 
        # typeAIId =
        # id_user_algorithm_short = 
        # id_user_algorithm_long = 
        for item in mapAlgTypeAI:
            if item['id'] == data['id_mapAlgTypeAI'][0]:
               typeAIId =  item['typeAIId']
               id_user_algorithm_short = item['algorId']
        for item in mapAlgTypeAI:
            if item['id'] == data['id_mapAlgTypeAI'][1]:
               typeAIId =  item['typeAIId']
               id_user_algorithm_long = item['algorId']
        if typeAIId == 1:
            len = get_length(data['raw_text'])
            print('len doc :'+str(len))
            if len < LENGTH_THRESHOLD:
                print('short')
                data['algor_choose']['type_ai_id'] = SHORT_EXTRACT
                data['algor_choose']['algor_id'] = id_user_algorithm_short
            else:
                print('long')
                data['algor_choose']['type_ai_id'] = LONG_EXTRACT
                data['algor_choose']['algor_id'] = id_user_algorithm_long
        elif typeAIId == 2:
            len = get_length(data['raw_text'])
            print('len doc :'+str(len))
            if len < LENGTH_THRESHOLD:
                print('short')
                data['algor_choose']['type_ai_id'] = SHORT_ABSTRACT
                data['algor_choose']['algor_id'] = id_user_algorithm_short
            else:
                print('long')
                data['algor_choose']['type_ai_id'] = LONG_ABSTRACT
                data['algor_choose']['algor_id'] = id_user_algorithm_long
            data.pop("percent_output")
        else:
            print('error')
        # data.pop("is_ext")
        # data.pop("is_abs")
        # data.pop("user_algorithm_id")
    return input
def sum(data,out_queue):
    # location given here
    URL = ""
    if data['algor_choose']['type_ai_id'] == 1 or data['algor_choose']['type_ai_id'] == 4:
        PARAMS = {"text":data['raw_text'],"percent_output":data['percent_output']}
    else:
        PARAMS = {"text":data['raw_text']}
    for config in algorithm:
        if config['algorId'] == data['algor_choose']['algor_id']:
            URL = config['urlAPI']
    result_api_sum = {}
    if  (data['algor_choose']['type_ai_id'] == 1 or data['algor_choose']['type_ai_id'] ==4) and data['percent_output'] == 0 :
        result_api_sum['topic'] =data['topic']
        result_api_sum['Summary'] = ""
    else:
        try:
            r =  requests.post(url = URL, json = PARAMS)
            if r.status_code != 500:
                result_api_sum = r.json()
                result_api_sum['topic'] =data['topic']
                result_api_sum['algorithm'] = data['algor_choose']['algor_id']
            else:
                result_api_sum['topic'] =data['topic']
                result_api_sum['Summary'] = ""
                result_api_sum['algorithm'] = data['algor_choose']['algor_id']
        except:
            result_api_sum['topic'] =data['topic']
            result_api_sum['Summary'] = ""
            result_api_sum['algorithm'] = data['algor_choose']['algor_id']
    # defining a params dict for the parameters to be sent to the API
    out_queue.put(result_api_sum)
def run_sum(input):
    threads = []
    out_queue = queue.Queue()
    k = 0
    output_predict = {}
    output_predict['result'] = {}
    output_predict['algorithm'] = {}
    for data in input:
        # result_api_sum = sum(data)
        # output_predict['result'][result_api_sum['topic']] = result_api_sum['Summary']
        # output_predict['topic'] = result_api_sum['topic']
        thread1 = Thread(target=sum, args=(data,out_queue,))
        k+=1
        thread1.start()
        threads.append(thread1)
    for t in threads:
        t.join()    
    
    while not out_queue.empty():
        result = out_queue.get()
        if result !=0:
           output_predict['result'][result['topic']] = result['Summary']
           output_predict['algorithm'][result['topic']] = result['algorithm']
    # sum(data)
    return output_predict