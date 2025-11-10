from algtm import *
from counter import *
from prep import *
from kafka import KafkaConsumer, KafkaProducer
from json import loads
# import init
import json
import init
import requests
import logging
logging.basicConfig(level=logging.INFO)
import os 

init.multi_textrank_pid = os.getpid()

def main():
    consumer = KafkaConsumer(
        "23_multi_textrank",
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=600000,

        group_id="23_multi_textrank",
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    producer = KafkaProducer(bootstrap_servers=init.configs["bootstrap_servers"],
                    max_request_size=100000000,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'))



    for data in consumer:
        message = data.value
        print("*"*50)
        print(message)
        print("*"*50)
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
            # commit
            try:
                res = requests.post(init.configs["url_cluster"], json={"list_doc":message["cluster"]["list_doc"]}, timeout=30)
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

        

            for idx, cluster in enumerate(list_cluster):
                obj = {
                        "text": "textsummary",
                        "displayName": f"Cụm {int(idx) + 1}",
                        "documents_id": [message["cluster"]["list_doc_id"][x] for x in cluster],
                        "algo_id":1
                }

            
                summary = TexRankSummary([message["cluster"]["list_doc"][x] for x in cluster], per)
                obj.update({"text": summary})
                output_format["result"]["cluster"].append(obj)

            print(output_format)
            producer.send("result_ai", output_format)
            consumer.commit()
        else:
            # topic
            for top in message["topic"]:
                obj = {
                        "text": "textsummary",
                        "topic_id":top["topic_id"],
                        "documents_id": top["list_doc_id"],
                        "algo_id":top["algo_id"]
                }

            
                summary = TexRankSummary(top["list_doc"], per)
                obj.update({"text": summary})
                output_format["result"]["topic"].append(obj)
            print("send successfully to result ouput")
            producer.send("result_ai", output_format)
            consumer.commit()
        
if __name__ =="__main__":
    main()
