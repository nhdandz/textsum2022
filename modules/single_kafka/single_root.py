import os
import sys
import json
from json import loads
from kafka import KafkaProducer,KafkaConsumer
from controller import get_input_by_topic,get_input_by_len_and_algor,run_sum
from helper import get_length,check_add_optional_value_document,check_percent_output,get_raw_text_by_topic,get_raw_text,check_add_optional_value_msg
import init
import requests

SERVER = init.bootstrap_servers
TOPIC_ROOT_SINGLE = 'single_root'
TOPIC_SUB_BASE = 'algor_'
TOPIC_SUB_SHORT = 'topic_single_short_tupk'
GROUP_ID = 'summary-22'
producer= KafkaProducer(bootstrap_servers=SERVER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def push_recsys_to_kafka(  document_json ,
                            server  ,
                            topic):   
    producer.send(topic,document_json)
def handle_message(msg):
    print(msg['sumary_id'])
    inputs_by_topic = []
    # process file 
    check_add_optional_value_msg(msg)
    check_add_optional_value_document(msg['documents'][0])
    text_input = get_raw_text(msg['documents'][0]['raw_text'],msg['documents'][0]['file_type'],msg['documents'][0]['page_from'],msg['documents'][0]['page_to'])
    list_id_mapAlgTypeAI = msg['id_mapAlgTypeAI']
    #process by topic
    if len(msg['topic']) !=0:
        for topic in msg['topic']:
            input = {
                "user_id":msg['user_id'],
                "sumary_id":msg['sumary_id'],
                "original_doc_ids" : msg.get('original_doc_ids', [msg['documents'][0]['documents_id']]),
                "topic":[
                            {
                            "topic_id":None,
                            "raw_text":None,
                            "documents_id":[msg['documents'][0]['documents_id']],
                            "algo_id":None,
                            "percent_output" : msg['percent_output'],
                            "id_mapAlgTypeAI" : None
                            },
                        ],
                "is_single":True,
                "is_topic":True
            }
            # Get keywords with default empty list if not exists
            keywords = topic.get('keywords', [])
            text = get_raw_text_by_topic(keywords, text_input)

            # Set topic_id and id_mapAlgTypeAI with default None if not exists
            input['topic'][0]['topic_id'] = topic.get('topic_id', None)
            input['topic'][0]['id_mapAlgTypeAI'] = topic.get('id_mapAlgTypeAI', None)
            input['topic'][0]['raw_text'] = text
            inputs_by_topic.append(input)
    else:
        input = {
            "user_id":msg['user_id'],
            "sumary_id":msg['sumary_id'],
            "original_doc_ids" : msg.get('original_doc_ids', [msg['documents'][0]['documents_id']]),
            "topic":[
                        {
                        "topic_id":None,
                        "raw_text": text_input,
                        "documents_id":[msg['documents'][0]['documents_id']],
                        "algo_id":None,
                        "percent_output" : msg['percent_output'],
                        "id_mapAlgTypeAI" : None
                        },
                    ],
            "is_single":True,
            "is_topic":False
        }
        inputs_by_topic.append(input)
    for i in range(len(inputs_by_topic)):
        len_word = get_length(inputs_by_topic[i]['topic'][0]['raw_text'])
        if inputs_by_topic[i]['topic'][0]['id_mapAlgTypeAI'] == None:
            id_mapAlgTypeAI = list_id_mapAlgTypeAI[0]
            if id_mapAlgTypeAI not in init.topics.keys():
                print(id_mapAlgTypeAI)
                res = requests.post(url=init.url_get_topic_algo, json={"id_mapAI": id_mapAlgTypeAI})
                res = json.loads(res.content)
                topic_name, algo_id = res["topic"], res["algo_id"]
                if topic_name != None:
                    init.topics.update({str(id_mapAlgTypeAI):{"topic_name":topic_name, "algo_id": algo_id}})
                # else:
                #     logging.info(f"Can not get topic name from {init.url_get_topic_algo}")
                #     consumer.commit()
            else:
                topic_name = init.topics[str(id_mapAlgTypeAI)]["topic_name"]
                algo_id = init.topics[str(id_mapAlgTypeAI)]["algo_id"]
            inputs_by_topic[i]['topic'][0]['algo_id'] = algo_id
            # TOPIC_SUB = TOPIC_SUB_BASE + str(algo_id[1])
            push_recsys_to_kafka(inputs_by_topic[i],SERVER,topic_name)
        else:
            id_mapAlgTypeAI = inputs_by_topic[i]['topic'][0]['id_mapAlgTypeAI']
            if id_mapAlgTypeAI not in init.topics.keys():
                res = requests.post(url=init.url_get_topic_algo, json={"id_mapAI": id_mapAlgTypeAI})
                res = json.loads(res.content)
                topic_name, algo_id = res["topic"], res["algo_id"]
                if topic_name != None:
                    init.topics.update({str(id_mapAlgTypeAI):{"topic_name":topic_name, "algo_id": algo_id}})
                # else:
                #     logging.info(f"Can not get topic name from {init.url_get_topic_algo}")
                #     consumer.commit()
            else:
                topic_name = init.topics[str(id_mapAlgTypeAI)]["topic_name"]
                algo_id = init.topics[str(id_mapAlgTypeAI)]["algo_id"]
            inputs_by_topic[i]['topic'][0]['algo_id'] = algo_id
            # TOPIC_SUB = TOPIC_SUB_BASE + str(algo_id[1])
            push_recsys_to_kafka(inputs_by_topic[i],SERVER,topic_name)
    print('Done')
    # dedupe_news_queue_client.sendMessage(task)


consumer = KafkaConsumer(
    TOPIC_ROOT_SINGLE,
    bootstrap_servers=SERVER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id= GROUP_ID,
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)
def process_topic(text):
    return text
for message in consumer:
    msg = message.value
    # msg = json.loads(msg)
    if msg is not None:
        # Handle message
        # try:
        handle_message(msg)
        # except Exception as e:
        #     print(e)
        #     pass