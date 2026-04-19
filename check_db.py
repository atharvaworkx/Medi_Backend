#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.db import connection
from django.core.management import call_command

print("=" * 50)
print("DATABASE CHECK")
print("=" * 50)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    exit(1)

try:
    from users.models import Users
    count = Users.objects.count()
    print(f"✓ Users table exists. Count: {count}")
except Exception as e:
    print(f"✗ Users table error: {e}")
    print("\nRunning migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migrations completed")
    except Exception as me:
        print(f"✗ Migration failed: {me}")
        exit(1)

try:
    from users.models import Users
    test_user, created = Users.objects.get_or_create(
        email='test@test.com',
        defaults={
            'firstName': 'Test',
            'lastName': 'User',
            'phone': '9876543210',
            'is_active': True,
            'isVerified': True,
            'level': 1,
        }
    )
    if created:
        test_user.set_password('test123456')
        test_user.save()
        print(f"✓ Created test user: {test_user.email}")
    else:
        print(f"✓ Test user exists: {test_user.email}")
except Exception as e:
    print(f"✗ User creation failed: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✓ DATABASE IS READY")
print("=" * 50)
