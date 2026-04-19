#!/bin/bash

set -e

echo "Starting deployment..."

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating log directories..."
mkdir -p logs/api logs/gunicorn logs/celery logs/exceptions

echo "Deployment complete!"
