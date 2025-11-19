import logging
from kafka import KafkaConsumer, KafkaProducer
from json import loads
import json
import time
import random
import init

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test():
    logging.info("="*80)
    logging.info("Starting root-kafka consumer (DEBUG VERSION)")
    logging.info(f"Bootstrap servers: {init.bootstrap_servers}")
    logging.info("="*80)

    try:
        logging.info("Creating consumer for 'topic_input_ai'...")
        consumer = KafkaConsumer(
            'topic_input_ai',
            bootstrap_servers=init.bootstrap_servers,
            auto_offset_reset='earliest',
            max_poll_records=5,
            max_poll_interval_ms=600000,
            group_id='root-input1',
            value_deserializer=lambda x: loads(x.decode('utf-8')) if x is not None else None)
        logging.info("✅ Consumer created successfully")

        logging.info("Creating producer...")
        producer = KafkaProducer(bootstrap_servers=init.bootstrap_servers,
                    max_request_size=100000000,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        logging.info("✅ Producer created successfully")

        logging.info("\n" + "="*80)
        logging.info("Waiting for messages...")
        logging.info("="*80 + "\n")

        message_count = 0
        for data in consumer:
            message = data.value

            # Skip tombstone records (None values)
            if message is None:
                logging.warning("Skipping tombstone record")
                consumer.commit()
                continue

            message_count += 1
            logging.info(f"\n{'='*80}")
            logging.info(f"📨 MESSAGE #{message_count} RECEIVED")
            logging.info(f"{'='*80}")
            logging.info(f"Offset: {data.offset}")
            logging.info(f"Partition: {data.partition}")
            logging.info(f"Sumary ID: {message.get('sumary_id', 'N/A')}")
            logging.info(f"User ID: {message.get('user_id', 'N/A')}")
            logging.info(f"is_single: {message.get('is_single', 'N/A')}")

            if message.get("is_single"):
                target_topic = "single_root"
                logging.info(f"📤 Sending to: {target_topic}")
                try:
                    producer.send(target_topic, message)
                    producer.flush()
                    logging.info(f"✅ Successfully sent to {target_topic}")
                except Exception as e:
                    logging.error(f"❌ Failed to send to {target_topic}: {str(e)}")
            else:
                target_topic = "multi_root"
                logging.info(f"📤 Sending to: {target_topic}")
                try:
                    producer.send(target_topic, message)
                    producer.flush()
                    logging.info(f"✅ Successfully sent to {target_topic}")
                except Exception as e:
                    logging.error(f"❌ Failed to send to {target_topic}: {str(e)}")

            logging.info("*"*80)
            consumer.commit()
            logging.info("Committed offset\n")

    except Exception as e:
        logging.error(f"❌ Fatal error: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

if __name__ =="__main__":
    test()
