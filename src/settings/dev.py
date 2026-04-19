from .base import *
import os

try:
    from src.vault import credentials
    vault_available = True
except ImportError:
    vault_available = False
    credentials = {}

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend", "*"]
CSRF_TRUSTED_ORIGINS = [
    "https://paragenetic-nonclamorously-dominica.ngrok-free.dev",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]

if vault_available:
    DATABASES = {
        "default": {
            "ENGINE": credentials['dev']['DB_ENGINE'],
            "NAME": "postgres2",
            "USER": credentials['dev']['DB_USER'],
            "PASSWORD": credentials['dev']['DB_PASSWORD'],
            "HOST": "db",
            "PORT": credentials['dev']['DB_PORT'],
        },
    }
    EMAIL = credentials['dev']["EMAIL"]
    PASSWORD = credentials['dev']["PASSWORD"]
    S3_BUCKET = credentials['dev']['S3_BUCKET']
    AWS_ACCESS_KEY_ID = credentials['dev']['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = credentials['dev']['AWS_SECRET_ACCESS_KEY']
    REGION = credentials['dev']['REGION']
    AWS_URL = "https://%s.s3.%s.amazonaws.com" % (S3_BUCKET, REGION)
    FRONTEND_BASE_URL = credentials['dev']['FRONTEND_BASE_URL']
    ADMIN_FRONTEND_BASE_URL = credentials['dev']['ADMIN_FRONTEND_BASE_URL']
else:
    DATABASES = {
        "default": {
            "ENGINE": os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            "NAME": os.getenv('DB_NAME', 'postgres2'),
            "USER": os.getenv('DB_USER', 'postgres'),
            "PASSWORD": os.getenv('DB_PASSWORD', 'postgres'),
            "HOST": os.getenv('DB_HOST', 'db'),
            "PORT": os.getenv('DB_PORT', '5432'),
        },
    }
    EMAIL = os.getenv('EMAIL', '')
    PASSWORD = os.getenv('PASSWORD', '')
    S3_BUCKET = os.getenv('S3_BUCKET', '')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    REGION = os.getenv('REGION', 'us-east-1')
    AWS_URL = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com" if S3_BUCKET else ""
    FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')
    ADMIN_FRONTEND_BASE_URL = os.getenv('ADMIN_FRONTEND_BASE_URL', 'http://localhost:3000')
