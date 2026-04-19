import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

accesslog = "/opt/logs/gunicorn/access.log"
errorlog = "/opt/logs/gunicorn/error.log"
loglevel = "info"

capture_output = True
enable_stdio_inheritance = True

preload_app = True
daemon = False

raw_env = [
    f"ENV={os.getenv('ENV', 'prod')}",
]
