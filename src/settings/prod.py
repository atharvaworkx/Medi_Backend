from .base import *
import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'https://medi-backend-kezm.onrender.com').split(',')

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://medi-backend-kezm.onrender.com').split(',')

# Use DATABASE_URL if available (Render provides this)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ayupilot_user:J0ONf89tkE82JITlILk8eHdPf53a5L2E@dpg-d7i8ghgsfn5c73e5ka4g-a.ohio-postgres.render.com/ayupilot')

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
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
