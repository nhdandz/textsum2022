import os
import sys
import json 
from json import loads
import torch
from kafka import KafkaProducer,KafkaConsumer
from helper import batch_process, post_process_document,split_doc
from transformers import (
    AutoTokenizer,
    LEDConfig,
    LEDForConditionalGeneration,
)
from helper import summary


SERVER = '192.168.210.42:9092'
TOPIC_SUB = '16_single_memsum'
TOPIC_SUB_RESULT = 'result_ai'
GROUP_ID = 'summary-11'

producer= KafkaProducer(bootstrap_servers=SERVER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))
# load model
torch_device = torch.device("cuda:0")
PRIMER_path='allenai/PRIMERA-multinews'
TOKENIZER = AutoTokenizer.from_pretrained(PRIMER_path)
MODEL = LEDForConditionalGeneration.from_pretrained(PRIMER_path).to(torch_device)
# MODEL.gradient_checkpointing_enable()
PAD_TOKEN_ID = TOKENIZER.pad_token_id
DOCSEP_TOKEN_ID = TOKENIZER.convert_tokens_to_ids("<doc-sep>")


def push_recsys_to_kafka(  document_json ,
                            server  ,
                            topic):   
    producer.send(topic,document_json)
def handle_message(msg):
    sumary = summary(msg['topic'][0],)
    msg['topic'][0]['text'] = sumary
    del msg['topic'][0]['raw_text']
    del msg['topic'][0]['percent_output']
    msg['result'] = {}
    msg['result']['topic'] = msg['topic']
    msg['result']['cluster'] = []
    del msg['topic']
    push_recsys_to_kafka(msg,SERVER,TOPIC_SUB_RESULT)
    print('done')
    # dedupe_news_queue_client.sendMessage(task)


consumer = KafkaConsumer(
    TOPIC_SUB,
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
        try:
            handle_message(msg)
        except Exception as e:
            print(e)
            pass