from pathlib import Path
import os
from datetime import timedelta
import sys

try:
    from celery.schedules import crontab
except ImportError:
    crontab = None


# Project Name
PROJECT_NAME = "medipilot"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Check if vault file is present
if not os.path.exists('src/vault.py'):
    print('vault file not found! \nPlease download the it.\nRefer the README for more information.')
    sys.exit(1)

# Create log directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
API_LOG_DIR = os.path.join(LOGS_DIR, "api")
GUNICORN_LOG_DIR = os.path.join(LOGS_DIR, 'gunicorn')
CELERY_LOG_DIR = os.path.join(LOGS_DIR, 'celery')
EXCEPTION_LOG_DIR = os.path.join(LOGS_DIR, "exceptions")

if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)
    os.mkdir(API_LOG_DIR)
    os.mkdir(GUNICORN_LOG_DIR)
    os.mkdir(CELERY_LOG_DIR)
    os.mkdir(EXCEPTION_LOG_DIR)
    # os.mkdir(exception_error_file)

# Create backup directory
BACKUP_DIR = os.path.join(BASE_DIR, 'db_backup')

if not os.path.exists(BACKUP_DIR):
    os.mkdir(BACKUP_DIR,)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-y*z$q8($bqrrpz6^f0g$dfg*=d23p3eq+ciig46x69^ia=dvyk'

# SECURITY WARNING: don't run with debug turned on in production!


# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "debug_toolbar",
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    "rest_framework",
    "corsheaders",
    "django_filters",
    "django_extensions",
    "atomicloops",
    "drf_api_logger",
    "django_rest_passwordreset",
    "drf_yasg",
    "import_export",
    "rest_framework_simplejwt.token_blacklist",
    "users",
    "profiles",
    "medical",
    "images",
    "quiz",
    "ai_reports",
    "doctors",
    "appointments",
    "consultations",
    "chatbot",
    "prescriptions",
    "medicines",
    "orders",
    "progress",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    "atomicloops.middleware.AtomicSQLInjectionMiddleware",
    "atomicloops.middleware.QueryCountMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # Debugger Middleware
    'drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware',  # Add here
]

CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Logger Configuration
DRF_API_LOGGER_DATABASE = True
DRF_API_LOGGER_DEFAULT_DATABASE = 'default'
DRF_API_LOGGER_EXCLUDE_KEYS = ['password', 'token', 'access', 'refresh', 'AUTHORIZATION']

WSGI_APPLICATION = 'src.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Change Timezone
# TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CUSTOM MODEL
AUTH_USER_MODEL = 'users.Users'

# JWT Configuration is defined at the bottom of this file (do not duplicate)


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587


# Debugger Tool
INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', 'backend')


def show_toolbar(*args, **kwargs):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

# Django Reset Passwod Configuration
DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomNumberTokenGenerator",
    "OPTIONS": {
        "min_number": 100000,
        "max_number": 999999
    }
}

# REST Framework configuration is defined at the bottom of this file (old atomicloops config removed)

# Swagger/OpenAPI Configuration
SWAGGER_USE_COMPAT_RENDERERS = False

# RabbitMQ configuration
CELERY_BROKER_URL = 'amqp://admin:admin@rabbit-mq'

# periodic tasks
if crontab:
    CELERY_BEAT_SCHEDULE = {
        'demo-task': {
            'task': 'src.celery.debug_task',
            'schedule': crontab(hour="*/12")  # 12 hours
        },
    }
else:
    CELERY_BEAT_SCHEDULE = {}

# REDIS Server
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "example"
    }
}

# TIMEOUT for REDIS 5 minutes
CACHE_TTL = 60 * 5

# Fix for put/patch api
APPEND_SLASH = False

# Allowed CORS Headers
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    'x-timezone-region'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'django_errors.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# AWS S3 Configuration (Optional - for image uploads)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'medipilot-images')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

# Image Upload limits
MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10485760))  # 10MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']