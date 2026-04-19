import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

accesslog = "-"
errorlog = "-"
loglevel = "info"

capture_output = True
enable_stdio_inheritance = True

preload_app = False
daemon = False

raw_env = [
    f"ENV={os.getenv('ENV', 'prod')}",
]
