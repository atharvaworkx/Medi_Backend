#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")

try:
    from users.models import Users
    count = Users.objects.count()
    print(f"✓ Users table exists. Count: {count}")
except Exception as e:
    print(f"✗ Users table error: {e}")
