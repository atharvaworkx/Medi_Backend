web: python manage.py migrate && python manage.py runserver 0.0.0.0:8000
worker: celery -A src worker -l INFO
beat: celery -A src beat -l INFO
