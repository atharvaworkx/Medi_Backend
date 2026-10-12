#!/bin/bash
modes="  start-dev\n  start-prod\n  check-syntax\n  start-deploy\n  migrate\n  sync-vault\n  check-setup\n  db-backup"
mode=$1

if [ "$mode" == "" ]; then
    echo -e $"Invalid mode \nPlease enter one of the following mode:\n${modes}"
elif [ "$mode" == "start-dev" ]; then
    export DJANGO_SETTINGS_MODULE=src.settings.dev
    export ENV=dev
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
elif [ "$mode" == "start-prod" ]; then
    export DJANGO_SETTINGS_MODULE=src.settings.prod
    export ENV=prod
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 src.wsgi:application
elif [ "$mode" == "check-syntax" ]; then
    flake8 .
elif [ "$mode" == "start-deploy" ]; then
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
elif [ "$mode" == "sync-vault" ]; then
    python manage.py sync-vault
elif [ "$mode" == "check-setup" ]; then
    python manage.py check_setup
elif [ "$mode" == "db-backup" ]; then
    python manage.py db-backup
elif [ "$mode" == "migrate" ]; then
    python manage.py migrate
else
    echo -e $"Invalid mode \nPlease enter one of the following mode:\n${modes}"
fi