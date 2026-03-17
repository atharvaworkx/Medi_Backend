from .base import *
from src.vault import credentials

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend", "*"]
CSRF_TRUSTED_ORIGINS = [
    "https://paragenetic-nonclamorously-dominica.ngrok-free.dev",
    "http://localhost:8000"
]

DATABASES = {
    "default": {
        "ENGINE": credentials['dev']['DB_ENGINE'],
        "NAME": "postgres2",  # Matching POSTGRES_DB in docker-compose
        "USER": credentials['dev']['DB_USER'],
        "PASSWORD": credentials['dev']['DB_PASSWORD'],
        "HOST": "db",  # Service name in docker-compose
        "PORT": credentials['dev']['DB_PORT'],
    },
}

EMAIL = credentials['dev']["EMAIL"]
PASSWORD = credentials['dev']["PASSWORD"]

# AWS credentials
# DEV SECRET KEYS
S3_BUCKET = credentials['dev']['S3_BUCKET']
AWS_ACCESS_KEY_ID = credentials['dev']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = credentials['dev']['AWS_SECRET_ACCESS_KEY']
REGION = credentials['dev']['REGION']
AWS_URL = "https://%s.s3.%s.amazonaws.com" % (S3_BUCKET, REGION)

# Frontend Urls
FRONTEND_BASE_URL = credentials['dev']['FRONTEND_BASE_URL']
ADMIN_FRONTEND_BASE_URL = credentials['dev']['ADMIN_FRONTEND_BASE_URL']
