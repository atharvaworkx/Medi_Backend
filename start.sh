#!/bin/bash
echo "Starting Django server..."
export DJANGO_SETTINGS_MODULE=src.settings.prod
export ENV=prod
python -c "import django; print('Django version:', django.get_version())"
python -c "import src.settings.prod; print('Settings loaded successfully')"
python manage.py check --deploy
python manage.py runserver 0.0.0.0:8000 --noreload