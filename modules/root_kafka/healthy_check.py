from kafka import KafkaConsumer
from kafka import KafkaAdminClient
import schedule
import time
import os

algo_dict ={
    "31_single_brio",,
    "29_single_longbart",,
    "25_multi_lsa",,
    "24_multi_lexrank",,
    "23_multi_textrank",,
    "21_multi_primera",,
    "19": ["19_multi_bart",],
    "18": ["18_multi_hertersum",],
    
    "16": ["16_single_memsum",16],
    "11": ["11_single_bart",11],
    "10": ["10_single_simcls",10],
    
    "4": ["4_single_bertext",4],
    
    "6": ["3_single_lsa",25],
    "5": ["2_single_textrank",23],
    "4": ["1_single_lexrank",24]
    
    "3": ["3_single_lsa",3],
    "2": ["2_single_textrank",2],
    "1": ["1_single_lexrank",1],
}

def check_lag(topic_name="18_multi_hetersum"):
    consumer = KafkaConsumer(bootstrap_servers=["192.168.2.25:9092"],
                            group_id=topic_name)
    consumer.subscribe(topic_name)

    admin_client = KafkaAdminClient(bootstrap_servers=["192.168.2.25:9092"])

    metadata_dict = admin_client.list_consumer_group_offsets(topic_name)

    topic_partition_latest_offsets = dict()
    for topic_partition in metadata_dict.keys():
        offset_metadata = metadata_dict[topic_partition]
        latest_offset = offset_metadata.offset

        topic_partition_latest_offsets[topic_partition] = latest_offset

    topic_partition_list = []
    for topic_partition in metadata_dict.keys():
        topic_partition_list.append(topic_partition)

    topic_partition_end_offsets = consumer.end_offsets(topic_partition_list)


    topic_partition_lags = dict()
    for topic_partition in topic_partition_latest_offsets:
        lag = abs(topic_partition_latest_offsets[topic_partition] - topic_partition_end_offsets[topic_partition])

        topic_partition_lags[topic_partition] = lag

    lag_sum = 0
    for topic_partition in topic_partition_lags:
        lag_sum += topic_partition_lags[topic_partition]

    return lag_sum

def check_healthy():
    keys = algo_dict.keys()
    for topic_name in keys:
        lags = check_lag(topic_name)
    if lags >500: # thuc hien kill thuat toan va khoi tao lai
        os.system("bash ./kill.bash")
        os.system("bash ./start.bash")

schedule.every().hour.do(check_healthy)
while True:
    schedule.run_pending()
    time.sleep(1)
