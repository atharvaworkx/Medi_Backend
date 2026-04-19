from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'https://medi-backend-kezm.onrender.com').split(',')

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://medi-backend-kezm.onrender.com').split(',')

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('DB_NAME', 'ayupilot'),
        "USER": os.getenv('DB_USER', 'ayupilot_user'),
        "PASSWORD": os.getenv('DB_PASSWORD', ''),
        "HOST": os.getenv('DB_HOST', 'dpg-d7i8ghgsfn5c73e5ka4g-a.ohio-postgres.render.com'),
        "PORT": os.getenv('DB_PORT', '5432'),
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "sslmode": "require",
        }
    },
}

EMAIL = os.getenv('EMAIL', '')
PASSWORD = os.getenv('PASSWORD', '')

S3_BUCKET = os.getenv('S3_BUCKET', '')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
REGION = os.getenv('REGION', 'us-east-1')
AWS_URL = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com" if S3_BUCKET else ""

FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'https://medi-backend-kezm.onrender.com')
ADMIN_FRONTEND_BASE_URL = os.getenv('ADMIN_FRONTEND_BASE_URL', 'https://medi-backend-kezm.onrender.com')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_HSTS_SECONDS = 86400
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    
    if 'debug_toolbar' in INSTALLED_APPS:
        INSTALLED_APPS.remove('debug_toolbar')
    if "atomicloops.middleware.QueryCountMiddleware" in MIDDLEWARE:
        MIDDLEWARE.remove("atomicloops.middleware.QueryCountMiddleware")
    if "debug_toolbar.middleware.DebugToolbarMiddleware" in MIDDLEWARE:
        MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")
