from algtm import *
from counter import *
from prep import *
from kafka import KafkaConsumer, KafkaProducer
from json import loads
import init
import json
import init
import requests
import logging
logging.basicConfig(level=logging.INFO)
import os 

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
                

init.lexrank_pid = os.getpid()

def main():
    consumer = KafkaConsumer(
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=600000,

        group_id="1_single_lexrank",
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    topic = "1_single_lexrank"
    consumer.subscribe([topic], listener=TestRebalanceListener(consumer, None, 0))

    producer = KafkaProducer(bootstrap_servers=init.configs["bootstrap_servers"],
                    max_request_size=100000000,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'))



    for data in consumer:
        message = data.value

        current_partition = data.partition
        current_offset = data.offset

        url_status = init.configs["url_status_Web"]
        sum_id = message["sumary_id"]
        try:
            res = requests.get(f"{url_status}/{sum_id}")
            res =json.loads(res.content)
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
                "is_single":True,
                "is_topic":message["is_topic"],
                "result":
                    {
                    "cluster": [],
                    "topic": []
                    }
                }
        
            # topic
            requests.post(f"{url_status}", json={
                    "inMultiDocSumId" : sum_id,
                    "inStatusId" : 1
                })
            try:
                for top in message["topic"]:
                    obj = {
                            "text": "textsummary",
                            "topic_id":top["topic_id"],
                            "documents_id": top["documents_id"],
                            "algo_id":top["algo_id"]
                    }
                    try:
                        per = top["percent_output"]
                        if per is  None:
                            per = 0.1
                    except:
                        per = 0.1
                
                    summary = lexrank_extract_sum(top["raw_text"], short_count_sentences(top['raw_text'], per))
                    obj.update({"text": summary})
                    output_format["result"]["topic"].append(obj)
                
                consumer.commit()
                f = producer.send("result_ai", output_format)
                f.get(60)
                print("Successfull send result")

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


if __name__ =="__main__":
    main()