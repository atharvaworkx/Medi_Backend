#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.core.management import call_command
from users.models import Users

print("Running migrations...")
try:
    call_command('migrate', verbosity=2, interactive=False)
    print("✓ Migrations completed")
except Exception as e:
    print(f"Migration error: {e}")

print("Creating test user...")
try:
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
        print(f"✓ Test user already exists: {test_user.email}")
except Exception as e:
    print(f"User creation error: {e}")

print("✓ Database setup complete")