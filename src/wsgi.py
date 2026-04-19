import os
from django.core.wsgi import get_wsgi_application

# Force production settings on Render
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')

application = get_wsgi_application()
