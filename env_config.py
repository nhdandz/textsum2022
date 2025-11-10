"""
Environment Configuration Helper
Load configuration from .env file and provide easy access to environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Network Configuration
HOST_IP = os.getenv('HOST_IP', '192.168.210.42')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', f'{HOST_IP}:9092')

# Core Services
ALGO_CONTROL_URL = os.getenv('ALGO_CONTROL_URL', f'http://{HOST_IP}:6789')
ALGO_CONTROL_PORT = int(os.getenv('ALGO_CONTROL_PORT', '6789'))

APP_PROCESS_URL = os.getenv('APP_PROCESS_URL', f'http://{HOST_IP}:9980')
APP_PROCESS_PORT = int(os.getenv('APP_PROCESS_PORT', '9980'))

STATUS_WEB_URL = os.getenv('STATUS_WEB_URL', f'http://{HOST_IP}:5002/api/multisum/status')
STATUS_WEB_PORT = int(os.getenv('STATUS_WEB_PORT', '5002'))

# Clustering Service
CLUSTERING_URL = os.getenv('CLUSTERING_URL', f'http://{HOST_IP}:9400/TextClustering')
CLUSTERING_PORT = int(os.getenv('CLUSTERING_PORT', '9400'))

# Single Document Summarization Services
TEXTRANK_URL = os.getenv('TEXTRANK_URL', f'http://{HOST_IP}:7300')
TEXTRANK_PORT = int(os.getenv('TEXTRANK_PORT', '7300'))

PRESUM_URL = os.getenv('PRESUM_URL', f'http://{HOST_IP}:7100')
MATCHSUM_URL = os.getenv('MATCHSUM_URL', f'http://{HOST_IP}:7200')
BIGBIRD_ARXIV_URL = os.getenv('BIGBIRD_ARXIV_URL', f'http://{HOST_IP}:5200')
BIGBIRD_PUBMED_URL = os.getenv('BIGBIRD_PUBMED_URL', f'http://{HOST_IP}:5300')

PEGASUS_URL = os.getenv('PEGASUS_URL', f'http://{HOST_IP}:6200')
PEGASUS_PORT = int(os.getenv('PEGASUS_PORT', '6200'))

SIMCLS_URL = os.getenv('SIMCLS_URL', f'http://{HOST_IP}:6300')
SIMCLS_PORT = int(os.getenv('SIMCLS_PORT', '6300'))

BART_URL = os.getenv('BART_URL', f'http://{HOST_IP}:6400')
BART_PORT = int(os.getenv('BART_PORT', '6400'))

BERT_EXT_ABS_URL = os.getenv('BERT_EXT_ABS_URL', f'http://{HOST_IP}:6500')
BERT_EXT_ABS_PORT = int(os.getenv('BERT_EXT_ABS_PORT', '6500'))

MEMSUM_URL = os.getenv('MEMSUM_URL', f'http://{HOST_IP}:8100')
HIMAP_URL = os.getenv('HIMAP_URL', f'http://{HOST_IP}:8898')
HETERSUM_URL = os.getenv('HETERSUM_URL', f'http://{HOST_IP}:8899')
PRIMERA_URL = os.getenv('PRIMERA_URL', f'http://{HOST_IP}:4100')

# Multi Document Summarization Services
MULTI_TEXTRANK_URL = os.getenv('MULTI_TEXTRANK_URL', f'http://{HOST_IP}:7302')
MULTI_TEXTRANK_PORT = int(os.getenv('MULTI_TEXTRANK_PORT', '7302'))

MULTI_BART_URL = os.getenv('MULTI_BART_URL', f'http://{HOST_IP}:6700')
MULTI_BART_PORT = int(os.getenv('MULTI_BART_PORT', '6700'))

MULTI_PEGASUS_URL = os.getenv('MULTI_PEGASUS_URL', f'http://{HOST_IP}:6800')
MULTI_PEGASUS_PORT = int(os.getenv('MULTI_PEGASUS_PORT', '6800'))

# Long Document Services
LSG16X_URL = os.getenv('LSG16X_URL', f'http://{HOST_IP}:6450')
LSG16X_PORT = int(os.getenv('LSG16X_PORT', '6450'))

ARXIV_URL = os.getenv('ARXIV_URL', f'http://{HOST_IP}:6550')
ARXIV_PORT = int(os.getenv('ARXIV_PORT', '6550'))

PRIMERA_ARXIV_URL = os.getenv('PRIMERA_ARXIV_URL', f'http://{HOST_IP}:6350')


def get_service_url(service_name: str, endpoint: str = '') -> str:
    """
    Get full URL for a service

    Args:
        service_name: Name of the service (e.g., 'textrank', 'memsum')
        endpoint: Optional endpoint path

    Returns:
        Full URL string
    """
    service_map = {
        'textrank': f'{TEXTRANK_URL}/TexRank',
        'lexrank': f'{TEXTRANK_URL}/LexRank',
        'lsa': f'{TEXTRANK_URL}/LSA',
        'presum': f'{PRESUM_URL}/presum',
        'matchsum': f'{MATCHSUM_URL}/matchsum',
        'bigbird_arxiv': f'{BIGBIRD_ARXIV_URL}/BigBirdArxiv',
        'bigbird_pubmed': f'{BIGBIRD_PUBMED_URL}/BigBirdPubmed',
        'pegasus': f'{PEGASUS_URL}/PegSum',
        'simcls': f'{SIMCLS_URL}/SimCLS',
        'bart': f'{BART_URL}/BARTD126',
        'bert_ext_abs': f'{BERT_EXT_ABS_URL}/BertExtAbs',
        'memsum': f'{MEMSUM_URL}/MemSum',
        'himap': f'{HIMAP_URL}/HiMap',
        'hetersum': f'{HETERSUM_URL}/HerterSum',
        'primera': f'{PRIMERA_URL}/primera',
        'multi_textrank': f'{MULTI_TEXTRANK_URL}/MultiTexRank',
        'multi_lexrank': f'{MULTI_TEXTRANK_URL}/MultiLexRank',
        'multi_lsa': f'{MULTI_TEXTRANK_URL}/MultiLSA',
        'multi_bart': f'{MULTI_BART_URL}/MultiBart',
        'multi_bart_single': f'{MULTI_BART_URL}/MultiBartSingle',
        'multi_pegasus': f'{MULTI_PEGASUS_URL}/MultiPeg',
        'multi_pegasus_single': f'{MULTI_PEGASUS_URL}/MultiPegSingle',
        'clustering': CLUSTERING_URL,
        'lsg16x': f'{LSG16X_URL}/lsg16x',
        'arxiv': f'{ARXIV_URL}/arxiv',
        'primera_arxiv': f'{PRIMERA_ARXIV_URL}/PrimeraArxiv',
    }

    base_url = service_map.get(service_name.lower(), '')
    if endpoint:
        return f'{base_url}/{endpoint.lstrip("/")}'
    return base_url


if __name__ == '__main__':
    print("Environment Configuration Loaded:")
    print(f"HOST_IP: {HOST_IP}")
    print(f"HOST_IP_ALT: {HOST_IP_ALT}")
    print(f"KAFKA_BOOTSTRAP_SERVERS: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Sample service URL (TextRank): {get_service_url('textrank')}")
