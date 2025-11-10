import logging
from kafka import KafkaConsumer, KafkaProducer
from json import loads
import json
import time 
import random
# from pynvml import *
# nvmlInit()
import init

def test():
    consumer = KafkaConsumer(
        'topic_input_ai',
        bootstrap_servers=init.bootstrap_servers,
        auto_offset_reset='earliest',
        # enable_auto_commit=True,
        max_poll_records=5,
        max_poll_interval_ms=600000,

        group_id='root-input1',
        value_deserializer=lambda x: loads(x.decode('utf-8')) if x is not None else None)

    producer = KafkaProducer(bootstrap_servers=init.bootstrap_servers,
                max_request_size=100000000,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'))



    for data in consumer: #  # for message in consumer:
        message = data.value

        # Skip tombstone records (None values)
        if message is None:
            print("Skipping tombstone record")
            consumer.commit()
            continue

        # print(message)
        # h = nvmlDeviceGetHandleByIndex(0)
        # info = nvmlDeviceGetMemoryInfo(h)
        # print(f'total    : {info.total // 1024 ** 2}')
        # print(f'free     : {info.free // 1024 ** 2}')
        # print(f'used     : {info.used // 1024 ** 2}')
        # print(message)

        if message["is_single"]:
            print("send to single root")
            # logging.info("send to single root")
            producer.send("single_root", message)
        else:
            print("send to multi root")
            logging.info("send to multi root")
            producer.send("multi_root", message)
        print("*"*50)
        consumer.commit()


if __name__ =="__main__":
    # init.Initialize()
    test()