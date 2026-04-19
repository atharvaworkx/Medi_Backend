web: gunicorn src.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 120 --access-logfile - --error-logfile -
worker: celery -A src worker -l INFO
beat: celery -A src beat -l INFO
