import os
from django.core.wsgi import get_wsgi_application

ENV = os.getenv('ENV', 'dev')
if ENV == "prod":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.dev')

application = get_wsgi_application()
