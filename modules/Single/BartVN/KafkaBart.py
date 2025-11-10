
import json 
from json import loads
from kafka import KafkaProducer,KafkaConsumer
# import nvidia_smi
import time
import requests
# nvidia_smi.nvmlInit()
url_status="http://192.168.210.42:5002/api/multisum/status"
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# load balancing class
from Bart_Helper import *
import logging
logging.basicConfig(level=logging.INFO)
import os 
import time
from kafka.errors import KafkaTimeoutError, CommitFailedError, InvalidSessionTimeoutError
from kafka import TopicPartition,OffsetAndMetadata,ConsumerRebalanceListener
import traceback
import torch
import os 

pid = os.getpid()
print("pid: ", pid)

class TestRebalanceListener(ConsumerRebalanceListener):

    def __init__(self, consumer: KafkaConsumer, error_partition: TopicPartition, error_offset: int):
        self.consumer = consumer
        self.error_partition = error_partition
        self.error_offset = error_offset

    def on_partitions_revoked(self, revoked):
        pass
        
    def on_partitions_assigned(self, assigned):
        
        if len(assigned) > 0 and self.error_partition is not None:
            for partition in assigned:
                # print("chiu")
                if self.error_partition == partition:
                    current_offset = self.error_offset + 1
                else:
                    current_offset = self.consumer.position(partition)
                
                self.consumer.seek(partition, current_offset)

# from helper import summary
import os
with open("log-bart", "w") as f:
    f.write(str(os.getpid()))

SERVER = '192.168.210.42:9092'
TOPIC_SUB = '16_single_memsum'
TOPIC_SUB_RESULT = 'result_ai'
GROUP_ID = '16_single_memsum'
GPU_INFER = 400
TOPIC = '16_single_memsum'
producer= KafkaProducer(bootstrap_servers=SERVER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))
consumer = KafkaConsumer(
    TOPIC_SUB,
    bootstrap_servers=SERVER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    max_poll_records=5,
    max_poll_interval_ms=600000,
    group_id= GROUP_ID,
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)
topic = TOPIC
consumer.subscribe([topic], listener=TestRebalanceListener(consumer, None, 0))

device = "cuda:0" #if torch.cuda.is_available() else "cpu"
import os
pid = None
main_model=None
main_tokenizer=None

def run(status):
    global main_model
    global main_tokenizer
    global main_pipe

    if status == False:
        os.system(f'python kill.py {pid}')
        return

    if status ==True:
        if main_model==None:
            main_tokenizer=AutoTokenizer.from_pretrained("pengold/t5-vietnamese-summarization")
            main_model=AutoModelForSeq2SeqLM.from_pretrained("pengold/t5-vietnamese-summarization")
            main_model = main_model.to(device)

run(True)
def push_recsys_to_kafka(  document_json ,
                            server  ,
                            topic):   
    consumer.commit()
    f = producer.send(topic,document_json)
    f.get(60)

def bart_summary(text):

    text = ' '.join(line.strip() for line in text.strip().splitlines())
    # text =text.replace('\n', ' ')
    encoding = main_tokenizer(text, max_length=1024,truncation=True, return_tensors="pt").to(device)

    input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)

        # Generate Summary
    summary_ids = main_model.generate(input_ids=input_ids, attention_mask=attention_masks, min_length=0, max_length=2048,num_beams=5,length_penalty=1.5)
    summary_txt = main_tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    return summary_txt

def bart_summary_array(text):
    text = ' '.join(line.strip() for line in text.strip().splitlines())
    text =text.replace('\n', '')
    texs = split_doc(text, 500)
    summarys = ""
    for text in texs:
        encoding = main_tokenizer(text, max_length=1024,truncation=True, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)
        # Generate Summary
        summary_ids = main_model.generate(input_ids=input_ids, attention_mask=attention_masks, num_beams=5)
        summary_txt = main_tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        torch.cuda.empty_cache()
        summarys+= ". " + summary_txt
    return summarys.replace(" . ", ". ")


def handle_message(msg):
    tic = time.time()
    text = msg['topic'][0]['raw_text']
    summary_txt = bart_summary_array(text)
    msg['topic'][0]['text'] = summary_txt
    del msg['topic'][0]['raw_text']
    del msg['topic'][0]['percent_output']
    msg['result'] = {}
    msg['result']['topic'] = msg['topic']
    msg['result']['cluster'] = []
    del msg['topic']
    push_recsys_to_kafka(msg,SERVER,TOPIC_SUB_RESULT)
    tac = time.time()
    with open("log-time", "a") as f:
        f.write(str(tac - tic)+"\n")
    print('done')
    # dedupe_news_queue_client.sendMessage(task)



print(consumer)
def process_topic(text):
    return text
for message in consumer:
    msg = message.value
    current_partition = message.partition
    current_offset = message.offset
    print(msg)
    sum_id = msg["sumary_id"]
    try:
        res = requests.get(f"{url_status}/{sum_id}")
        res = json.loads(res.content)
        print(res)
        # thuc hien ko tom tat
        if not res["data"]["status"]:
            consumer.commit()
            continue
    except:
        consumer.commit()
        continue    
    # msg = json.loads(msg)
    if msg is not None:
        txt = msg['topic'][0]['raw_text']    
        if(txt == "" or txt == " " or txt == "\n"):
            requests.post(f"{url_status}", json={
            "inMultiDocSumId" : sum_id,
            "inStatusId" : 3
            })   
            consumer.commit()
            continue
        else:
        # Handle message
            try:
                # handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
                # info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
                # while ((info.used//1024**2) + GPU_INFER)/(info.total//1024**2) > 0.92:
                #     time.sleep(1)
                #     print('sleep')
                #     handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
                #     info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
                # requests.post(f"{url_status}", json={
                #     "inMultiDocSumId" : sum_id,
                #     "inStatusId" : 1
                # })
                try:
                    handle_message(msg)
                except CommitFailedError as ex:
                    requests.post(f"{url_status}", json={
                    "inMultiDocSumId" : sum_id,
                    "inStatusId" : 3
                    })   
                    traceback.print_exc()
                    consumer.subscribe([topic], listener = TestRebalanceListener(consumer, TopicPartition(topic, current_partition), current_offset)) 
            except Exception as e:
                print(e)
                requests.post(f"{url_status}", json={
                    "inMultiDocSumId" : sum_id,
                    "inStatusId" : 3
                })
                consumer.commit()
                pass

