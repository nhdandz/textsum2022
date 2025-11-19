import json
import os
from json import loads
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread
from helper import get_raw_text

def _read_env():
    # Read from environment variables set by docker-compose from root .env file
    kafka_bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-1:19092')

    config = {
        'kafka_config': {
            'bootstrap_servers': [kafka_bootstrap],
            'topic_get_data': 'upload_data',
            'topic_send_results': 'data_content'
        }
    }

    os.environ['kafka_config'] = str(config['kafka_config'])
    print('Loaded config from environment variables')
    return config

def worker(documents):
    arr_results=[]
    for doc in documents:
        try:
            result_doc = {}
            text_input = get_raw_text(doc['encode'],doc['file_type'],doc['page_from'],doc['page_to'])
            result_doc['text'] = text_input
            result_doc['documents_id'] = doc['documents_id']
            arr_results.append(result_doc)
        except:
            result_doc['text'] = ''
            result_doc['documents_id'] = doc['documents_id']
    return arr_results

def get_data_from_kafka():
    print('get_data_from_web') 
    kafka_server=os.getenv('kafka_config')     
    kafka_server=json.loads(kafka_server.replace("'",'"') ) # None
    server_list=kafka_server['bootstrap_servers']
    producer=KafkaProducer(bootstrap_servers=server_list,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    topic=kafka_server['topic_get_data']
    topic_send_results=kafka_server['topic_send_results']
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=server_list,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id=topic+'12',
        max_poll_records=50,
        max_poll_interval_ms=600000,
        value_deserializer=lambda x: loads(x.decode('utf-8'))) 
    i=1   
    for message in consumer:  
        try:
            consumer.commit()
            results_doc=worker( message.value )
            producer.send(topic_send_results,results_doc)            
        except Exception as ex:
            print('fail to get data from') 

if __name__ == "__main__":  
    threads=[]   
    print('get update web')
    _read_env()
    thread_process_data_upload=Thread(target=get_data_from_kafka , )
    thread_process_data_upload.start()
    threads.append(thread_process_data_upload)  
    for thread in threads:      
        thread.join()       