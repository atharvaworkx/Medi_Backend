web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.wsgi:application
worker: celery -A src worker -l INFO
beat: celery -A src beat -l INFO
