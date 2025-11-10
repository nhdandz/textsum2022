from kafka import KafkaConsumer, KafkaProducer
from json import loads
import json
import requests
import logging
logging.basicConfig(level=logging.INFO)
import os 
import init
from transformers import (
    AutoTokenizer,
    LEDConfig,
    LEDForConditionalGeneration,
)
from helper import summary_func
import torch
import time
from kafka.errors import KafkaTimeoutError, CommitFailedError, InvalidSessionTimeoutError
from kafka import TopicPartition,OffsetAndMetadata,ConsumerRebalanceListener
import traceback
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
                

GPU_INFER = 3700

torch_device = torch.device("cuda:0")
PRIMER_path='allenai/PRIMERA-multinews'
TOKENIZER = AutoTokenizer.from_pretrained(PRIMER_path)
MODEL = LEDForConditionalGeneration.from_pretrained(PRIMER_path).to(torch_device)
# MODEL.gradient_checkpointing_enable()
PAD_TOKEN_ID = TOKENIZER.pad_token_id
DOCSEP_TOKEN_ID = TOKENIZER.convert_tokens_to_ids("<doc-sep>")
TOPIC_SUB = '19_multi_bart'
print('done load')
def main():
    GROUP_ID = '19_multi_bart'
    consumer = KafkaConsumer(
        TOPIC_SUB,
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=1200000,

        group_id=GROUP_ID,
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    producer = KafkaProducer(bootstrap_servers=init.configs["bootstrap_servers"],
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    consumer.subscribe([TOPIC_SUB], listener=TestRebalanceListener(consumer, None, 0))
	
    for data in consumer:
        message = data.value
        current_partition = data.partition
        current_offset = data.offset
        # handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        # info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        # while ((info.used//1024**2) + GPU_INFER)/(info.total//1024**2) > 0.92:
        #     time.sleep(1)
        #     print('sleep')
        #     handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        #     info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        # # print(message)
        url_status = init.configs["url_status_Web"]
        sum_id = message["sumary_id"]
        try:
            res = requests.get(f"{url_status}/{sum_id}")
            res = json.loads(res.content)
            # thuc hien ko tom tat
            if not res["data"]["status"]:
                consumer.commit()
                continue
        except:
            consumer.commit()
            continue
        try:
            output_format = {
            "user_id":message["user_id"],
            "sumary_id":message["sumary_id"],
            "original_doc_ids": message["original_doc_ids"],
            "is_single":False,
            "is_topic":message["is_topic"],
            "result":
                {
                "cluster": [   ],
                "topic": []
                }
            }
            try:
                per = message["cluster"]["percent_output"]
                if per is  None:
                    per = 0.1
            except:
                per = 0.1
            # call api cluster:
            if message["is_cluster"]:
                try:
                    res = requests.post(init.configs["url_cluster"], json={"list_doc":message["cluster"]["list_doc"]})
                except:
                    continue
                code = res.status_code
                list_cluster = json.loads(res.content)["clusters"]
                # list_cluster, code =[[0,1],[2,3]],200
                if code!=200:
                    # error return topic luon
                    logging.info("err call api cluster")
                    producer.send("result_ai", output_format)
                    consumer.commit()

                # cap nhat traing thai bat dau tom tat
                requests.post(f"{url_status}", json={
                    "inMultiDocSumId" : sum_id,
                    "inStatusId" : 1
                })
                try:
                    for idx, cluster in enumerate(list_cluster):
                        obj = {
                                "text": "textsummary",
                                "displayName": f"Cụm {int(idx) + 1}",
                                "documents_id": [message["cluster"]["list_doc_id"][x] for x in cluster],
                                "algo_id": message["cluster"]["algo_id"]
                        }

                    
                        summary = summary_func([message["cluster"]["list_doc"][x] for x in cluster],MODEL,TOKENIZER,DOCSEP_TOKEN_ID)
                        torch.cuda.empty_cache()
                        obj.update({"text": summary})
                        output_format["result"]["cluster"].append(obj)
                    consumer.commit()
                    f = producer.send("result_ai", output_format)
                    f.get(60)
                    print('done')
                    
                except CommitFailedError as ex:
                    requests.post(f"{url_status}", json={
                                    "inMultiDocSumId" : sum_id,
                                    "inStatusId" : 3
                                })
                    traceback.print_exc()
                    consumer.subscribe([topic], listener = TestRebalanceListener(consumer, TopicPartition(topic, current_partition), current_offset))

            else:
                # topic
                try:
                    requests.post(f"{url_status}", json={
                            "inMultiDocSumId" : sum_id,
                            "inStatusId" : 1
                        })
                    for top in message["topic"]:
                        obj = {
                                "text": "textsummary",
                                "topic_id":top["topic_id"],
                                "documents_id": top["list_doc_id"],
                                "algo_id":top["algo_id"]
                        }

                    
                        summary = summary_func(top["list_doc"],MODEL,TOKENIZER,DOCSEP_TOKEN_ID)
                        torch.cuda.empty_cache()
                        obj.update({"text": summary})
                        output_format["result"]["topic"].append(obj)

                    f = producer.send("result_ai", output_format)
                    f.get(60)
                    print('done')
                    consumer.commit()
                except CommitFailedError as ex:
                    requests.post(f"{url_status}", json={
                                    "inMultiDocSumId" : sum_id,
                                    "inStatusId" : 3
                                })
                    traceback.print_exc()
                    consumer.subscribe([topic], listener = TestRebalanceListener(consumer, TopicPartition(topic, current_partition), current_offset))

        except Exception as e:
            logging.error(e)
            consumer.commit()

if __name__ =="__main__":
    main()