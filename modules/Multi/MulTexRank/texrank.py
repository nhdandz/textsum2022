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
import time

# write txt
# init.textrank_pid = os.getpid()

def main():
    consumer = KafkaConsumer(
        "2_single_textrank",
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=600000,

        group_id="2_single_textrank",
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    producer = KafkaProducer(bootstrap_servers=init.configs["bootstrap_servers"],
                    max_request_size=100000000,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'))
                    
       
    for data in consumer:
        try:
            # call api web cai nay co tom nua hay
            message = data.value
            time.sleep(1)
            # tinh toan gpu 
            output_format = {
                "user_id":message["user_id"],
                "sumary_id":message["sumary_id"],
                "original_doc_ids": message["original_doc_ids"],
                "is_single":True,
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
            # topic
            for top in message["topic"]:
                obj = {
                        "text": "textsummary",
                        "topic_id":top["topic_id"],
                        "documents_id": top["documents_id"],
                        "algo_id":top["algo_id"]
                }

            
                summary = luhn_text_sum(top["raw_text"], short_count_sentences(top["raw_text"], per))
                obj.update({"text": summary})
                output_format["result"]["topic"].append(obj)
            producer.send("result_ai", output_format)
            # send api t thanhf cong
            consumer.commit()
        except Exception as e:
            logging.info(e)
            # end api t ko thanh cong
            consumer.commit()

if __name__ =="__main__":
    main()