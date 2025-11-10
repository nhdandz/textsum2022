from cmath import log
import json
import requests
from multiprocessing import Process, Manager
import logging
logging.basicConfig(level=logging.INFO)
import base_64 
import init 

def check_valid_input(dataInput):
    # check type
    try:
        if not isinstance(dataInput["raw_text"], list) or len(dataInput["raw_text"]) <1:
            return 404
    except:
        return 404
    
    try:
        if not isinstance(dataInput["topic"], list):
            return 401
    except:
        return 401

    try:
        if not isinstance(dataInput["id_mapAlgTypeAI"], list) or len(dataInput["id_mapAlgTypeAI"]) !=1 :
            return 402
    except:
        return 402
    
    try:
        percent_output = float(dataInput["percent_output"])
        if  not 0 < percent_output <=1:
            return 403
    except:
        return 403
    
    try:
        if not isinstance(dataInput["cluster"], bool) :
            return 405
    except:
        return 405
    
    try:
        if not isinstance(dataInput["file_type"], list) or len(dataInput["file_type"]) != len(dataInput["raw_text"]):
            return 408
        for _type in dataInput["file_type"]:
            try:
                int(_type)
            except:
                return 408
    except:
        return 408
    
    
    # only cluster or topic to summary doc 
    cluster = dataInput["cluster"]
    topic = dataInput["topic"]
    
    
    if cluster:
        if len(topic)>0:
            # also cluster and also topic
            return 406
    else:
        if len(topic)==0:
            return 401
        try:
            for obj in topic:
                topic_keys = obj.keys()
                if len(topic_keys) ==0:
                    return 401
                else:
                    if len(obj["logic"]) !=2:
                        return 401
        except:
            return 401
    
    if cluster == False and len(topic)==0:
        return 407
    return 200

def infer(manger,dataInput, url, key):
    # check if empty input after cluster or topic
    if len(dataInput["list_doc"])==0:
        manger[key] = {"result":None}
    else:
        res=  requests.post(url, json=dataInput)
        code = res.status_code
        if code !=200:
            logging.error(f"{code} status code in {url}")
            manger[key] = {"result":None}
        else:
            res = json.loads(res.content)
            manger[key] = {"result":res["result"]}
    
def mul_infer(inputs, url):
    manager = Manager()
    d = manager.dict()        
    
    for idx, docs in enumerate(inputs):
        p = Process(target=infer, args=(d, inputs[idx],url, idx))
        p.start()
        p.join()
        
    return d

def check_contain(logic, text):
    # assert(logic, list), "must be list logic to check valid"
    result = []
    for express_logic in logic:
        is_valid = True
        keywords = express_logic.split(',')
        for keyword in keywords:
            if not keyword.lower().rstrip() in text.lower():
                is_valid= False
                break
        result.append(is_valid)
    return any(result)

def check_valid_by_topic(logic_topic,text):
    topic_choose = logic_topic[0]
    topic_not = logic_topic[1]
    
    logging.info(f"topic and: {topic_choose}")
        
    logging.info(f"topic not: {topic_not}")
    #check if contain True logic not in text =>False not valid
    if check_contain(topic_not, text):
        return False
    
    # check if contain True in logic And or => True valid
    if check_contain(topic_choose, text):
        return True
    # else False
    return False

def cluster_topics(list_doc, logic):
    elem_arr_valid = []
    list_text_valid = []
    for jdx, doc in enumerate(list_doc):
        text_input = get_raw_text_by_topic(logic, doc)
        if text_input != "": 
            elem_arr_valid.append(jdx)
            list_text_valid.append(text_input)

    return list_text_valid, elem_arr_valid
    
def pre_data_cluster(dataInput, list_cluster):
    percent_output = dataInput["percent_output"]
    raw_data = dataInput["raw_text"]
    inputs =[]
    for cluster in list_cluster:
        list_text_raw = []
        for idx in cluster:
            list_text_raw.append(raw_data[idx])
        inputs.append(
            {
            "list_doc":list_text_raw,
            "percent_output":percent_output
        })
        
    return inputs

def pre_data_topic(dataInput):
    dataInput = cluster_topics(dataInput)
    inputs = []
    topics = dataInput["topic"]
    for top in topics:
        elem_arr = top["elem_arr"]
        list_text_raw = []
        for elem in elem_arr:
            list_text_raw.append(dataInput["raw_text"][elem])
        inputs.append(
            {
            "list_doc":list_text_raw,
            "percent_output":dataInput["percent_output"]
        })
        
    return inputs

def convert_b64_file_to_text(dataInput):
    documents = dataInput["documents"]
    list_doc = []
    list_doc_id = []
    for  doc in documents:
        data_file = doc["raw_text"]
        file_type = int(doc["file_type"])
        doc_id = doc["documents_id"]
        r_text = base_64.get_raw_text(data_file,file_type,0,99999)
        list_doc.append(r_text)
        list_doc_id.append(doc_id)
    
    return list_doc, list_doc_id

def pre_data(dataInput):
    data_format = {
        "user_id":dataInput["user_id"],
        "sumary_id":dataInput["sumary_id"],
        "topic":dataInput["topic"],
        "original_doc_ids":dataInput["original_doc_ids"],
        "is_single":False,
        "is_topic":True,
        "cluster":{},
        "is_cluster":False
    }
    try:
        list_doc, list_doc_id = convert_b64_file_to_text(dataInput)
        id_mapAlgTypeAI = dataInput["id_mapAlgTypeAI"][0]
        algorId = init.topics[str(id_mapAlgTypeAI)]["algo_id"]
        # clustering
        if len(dataInput["topic"])==0:
            data_format.update({"is_cluster": True, "is_topic":False})
            obj = {
                "list_doc":list_doc,
                "list_doc_id":list_doc_id,
                "percent_output":dataInput["percent_output"],
                "algo_id": algorId
            }
            data_format.update({"cluster": obj})
    except:
        print("err read data")
    return data_format

def removeDuplicates(lst):
    return list(set([i for i in lst]))

def get_raw_text_by_topic(topics,raw_text):
    list_pragrab = raw_text.split('\n')
    list_raw = []
    topic_choose = topics[0]
    topic_not = topics[1]
    if len(topic_choose) != 0:
        for key_words in topic_choose:
            key_word = key_words.split(',')
            for pragrab in list_pragrab :
                is_choose = True
                for word in key_word:
                    if word.lower() not in pragrab.lower():
                        is_choose = False
                if is_choose == True:
                    index = list_pragrab.index(pragrab)
                    list_raw.append((index,pragrab))
    else:
        count = 0
        for pragrab in list_pragrab :
            list_raw.append((count,pragrab))
            count +=1
    list_raw = removeDuplicates(list_raw)
    list_raw_process = sorted(list_raw, key=lambda tup: tup[0])
    list_raw_final = []
    if len(topic_not) != 0:
        for key_words in topic_not:
            key_word = key_words.split(',')
            for pragrab in list_raw_process :
                is_choose = True
                for word in key_word:
                    if ' '+word.strip().lower()+' ' in pragrab[1].lower():
                        is_choose = False
                if is_choose == True:
                    list_raw_final.append(pragrab)
    else:
        list_raw_final = list_raw_process
    list_raw_final = removeDuplicates(list_raw_final)
    list_raw_final_process = sorted(list_raw_final, key=lambda tup: tup[0])
    list_text_topic = []
    for text_topic in list_raw_final_process:
        list_text_topic.append(text_topic[1])
    return '\n'.join(list_text_topic)
    

if __name__ == '__main__':
    # data = {
    #     "raw_text":["abc a fg", "bdcd a b dfdanc", "a bc cd"],
    #     "topic": [
    #     {
    #         "logic":[["A","B"],["C"]],
    #         "displayName":"tên topic"
    #     },
    #     {
    #         "logic":[["A","B","C"],["D"]],
    #         "displayName":"tên topic"
    #     }
    #     ],
    #     "id_mapAlgTypeAI" :[1],
    #     "percent_output": 0.3,
    #     "cluster": False
    #     }
    # data = cluster_topics(data)
    # print(data)
    # print(pre_data_topic(data))

    with open("encoded-20220727080043.txt", "r") as r:
        data1 = r.read()
    
    with open("encoded-20220727080145.txt", "r") as r:
        data2 = r.read()
    
    data_input = {
        "user_id":"11212",
        "sumary_id":12,
        "documents":[
            {
            "documents_id":"12122",
            "raw_text":data1,
            "file_type":1,
            "page_from": 0,
            "page_to" :10
            },
            {
            "documents_id":"12345",
            "raw_text":data2,
            "file_type":1,
            "page_from": 0,
            "page_to" :10
            }],
        "topic": [
        # {
        #     "keywords":[["A","B"],["C1"]],
        #     "topic_id":123
        # },
        # {
        #     "keywords":[["A","B","C"],["D2"]],
        #     "topic_id":1232
        # }
        ],
        "id_mapAlgTypeAI" :[1],
        "percent_output": 0.3,
        "is_single": False
    }
    
    print(pre_data(data_input))
    