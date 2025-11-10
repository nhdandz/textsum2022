from kafka import KafkaConsumer
from json import loads
import json
import os
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lấy Kafka bootstrap servers từ environment variable
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-1:9092')
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/result')

consumer = KafkaConsumer(
    "result_ai",
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    max_poll_records=10,
    max_poll_interval_ms=600000,
    group_id="result_ai_consumer",
    value_deserializer=lambda x: loads(x.decode('utf-8')))

logger.info(f"Result consumer started. Listening to topic: result_ai")
logger.info(f"Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
logger.info(f"Backend API URL: {BACKEND_API_URL}")

def send_result_to_backend(message):
    """Gửi kết quả về backend API"""
    try:
        response = requests.post(
            BACKEND_API_URL,
            json=message,
            timeout=30
        )
        if response.status_code == 200:
            logger.info(f"Successfully sent result for summary_id: {message.get('sumary_id', 'unknown')}")
            return True
        else:
            logger.error(f"Failed to send result. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending result to backend: {str(e)}")
        return False

def handle_message(message):
    """Xử lý message từ result_ai"""
    try:
        logger.info(f"Received result message: {json.dumps(message, ensure_ascii=False)[:200]}...")

        # Validate message structure
        if not isinstance(message, dict):
            logger.error("Invalid message format: not a dictionary")
            return False

        # Kiểm tra các field bắt buộc
        required_fields = ['sumary_id', 'user_id']
        for field in required_fields:
            if field not in message:
                logger.warning(f"Missing required field: {field}")

        # Gửi kết quả về backend
        success = send_result_to_backend(message)

        if success:
            logger.info(f"Message processed successfully for summary_id: {message.get('sumary_id', 'unknown')}")
        else:
            logger.error(f"Failed to process message for summary_id: {message.get('sumary_id', 'unknown')}")

        return success

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        return False

# Main loop
logger.info("Starting to consume messages from result_ai...")
for data in consumer:
    message = data.value
    try:
        handle_message(message)
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {str(e)}")
        continue
