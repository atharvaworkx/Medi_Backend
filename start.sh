#!/bin/bash
echo "Starting Django server..."
export DJANGO_SETTINGS_MODULE=src.settings.prod
python manage.py runserver 0.0.0.0:8000 --noreload