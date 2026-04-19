web: python setup_db.py && exec gunicorn src.wsgi:application --config gunicorn_config.py --log-level debug --access-logfile - --error-logfile -
worker: celery -A src worker -l INFO
beat: celery -A src beat -l INFO
