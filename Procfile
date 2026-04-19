release: python manage.py migrate --noinput
web: gunicorn src.wsgi:application --config gunicorn_config.py
worker: celery -A src worker -l INFO
beat: celery -A src beat -l INFO
