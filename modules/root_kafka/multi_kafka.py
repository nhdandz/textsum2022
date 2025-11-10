from kafka import KafkaConsumer, KafkaProducer
from json import loads
import init
import json
import helper_multi
import os 
import requests
import logging
logging.basicConfig(level=logging.INFO)
import helper_multi
import init
import requests
from kafka.errors import KafkaTimeoutError, CommitFailedError, InvalidSessionTimeoutError
from kafka import TopicPartition,OffsetAndMetadata,ConsumerRebalanceListener
import traceback
import time 

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


consumer = KafkaConsumer(
    bootstrap_servers=init.bootstrap_servers,
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    max_poll_records=5,
    session_timeout_ms=300000,
    max_poll_interval_ms=600000,
    group_id='multi_root',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

topic = 'multi_root'
consumer.subscribe([topic], listener=TestRebalanceListener(consumer, None, 0))

producer = KafkaProducer(bootstrap_servers=init.bootstrap_servers,
                max_request_size=100000000,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'))

url_status="http://192.168.210.42:5002/api/multisum/status"
for data in consumer:
    message = data.value
    current_partition = data.partition
    current_offset = data.offset
    sum_id = message["sumary_id"]
    try:
        try:
            try:
                id_mapAlgTypeAI = message["id_mapAlgTypeAI"]
            except:
                logging.info("Can not get id_mapAlgTypeAI")
                consumer.commit()

            if len(id_mapAlgTypeAI) >0:
                id_mapAlgTypeAI = id_mapAlgTypeAI[0]
                if str(id_mapAlgTypeAI) not in init.topics.keys():
                    res = requests.post(url=init.url_get_topic_algo, json={"id_mapAI": id_mapAlgTypeAI})
                    res = json.loads(res.content)
                    topic_name, algo_id = res["topic"], res["algo_id"]
                    if topic_name != None and topic_name!= '':
                        init.topics.update({str(id_mapAlgTypeAI):{"topic_name":topic_name, "algo_id": algo_id}})
                    else:
                        logging.info(f"Can not get topic name from {init.url_get_topic_algo}")
                        consumer.commit()
                topic_name = init.topics[str(id_mapAlgTypeAI)]["topic_name"]
                logging.info("Topic Name: "+ topic_name)
                try:
                    predata =  helper_multi.pre_data(message)
                    # print(predata)
                except Exception as e:
                    logging.info("Err predata: {e}")
                    consumer.commit()
                logging.info("send message")
                consumer.commit()
                f = producer.send(topic_name, predata)
                f.get(60)
                
            else: # topic
                list_doc, list_doc_id = helper_multi.convert_b64_file_to_text(message)
                topics = message["topic"]
                for idx, top in enumerate(topics):
                    list_text_valid, elem_arr_valid = helper_multi.cluster_topics(list_doc, top["keywords"])
                    id_mapAlgTypeAI = top["id_mapAlgTypeAI"]
                    if id_mapAlgTypeAI not in init.topics.keys():
                        res = requests.post(url=init.url_get_topic_algo, json={"id_mapAI": id_mapAlgTypeAI})
                        res = json.loads(res.content)
                        topic_name, algo_id = res["topic"], res["algo_id"]
                        if topic_name != None and topic_name!= '':
                            init.topics.update({str(id_mapAlgTypeAI):{"topic_name":topic_name, "algo_id": algo_id}})
                        else:
                            logging.info(f"Can not get topic name from {init.url_get_topic_algo}")
                            consumer.commit()
                    topic_name = init.topics[str(id_mapAlgTypeAI)]["topic_name"]
                    algo_id = init.topics[str(id_mapAlgTypeAI)]["algo_id"]

                    logging.info("Topic Name: "+ topic_name)

                    data_format = {
                        "user_id":message["user_id"],
                        "sumary_id":message["sumary_id"],
                        "topic":[{
                                "list_doc": list_text_valid,
                                "list_doc_id": [list_doc_id[x] for x in elem_arr_valid],
                                "topic_id": top["topic_id"],
                                "algo_id": algo_id,
                                "percent_output": message["percent_output"]
                                }],
                        "original_doc_ids":message["original_doc_ids"],
                        "is_single":False,
                        "is_topic":True,
                        "cluster":{},
                        "is_cluster":False
                    }
                    logging.info(data_format)
                    logging.info(f"send message to {topic_name}")
                    consumer.commit()
                    f = producer.send(topic_name, data_format)
                    f.get(60)

        except CommitFailedError as ex:
                requests.post(f"{url_status}", json={
                                "inMultiDocSumId" : sum_id,
                                "inStatusId" : 3
                            })
                traceback.print_exc()
                consumer.subscribe([topic], listener = TestRebalanceListener(consumer, TopicPartition(topic, current_partition), current_offset))     
    except Exception as e:
        print(e)
        consumer.commit()

