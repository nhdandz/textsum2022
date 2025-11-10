import os
from dotenv import load_dotenv

load_dotenv()

global topics
topics = {}

# Use environment variables from docker-compose
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-1:9092')
ALGO_CONTROL_URL = os.getenv('ALGO_CONTROL_URL', 'http://algo-control:6789')

url_get_topic_algo = f"{ALGO_CONTROL_URL}/get_detail_algo"
bootstrap_servers = [KAFKA_BOOTSTRAP_SERVERS]