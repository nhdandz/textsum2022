# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:9980"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 600  # 10 phút timeout cho mỗi request
keepalive = 5

# Process naming
proc_name = 'app_process'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
