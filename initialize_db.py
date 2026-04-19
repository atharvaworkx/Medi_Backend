#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.core.management import call_command

print("Running migrations...")
call_command('migrate', verbosity=1)

print("Creating test user...")
from users.models import Users
from profiles.models import UserProfile

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
    
    profile, _ = UserProfile.objects.get_or_create(userId=test_user)
    profile.fullName = f"{test_user.firstName} {test_user.lastName}"
    profile.save()
else:
    print(f"✓ Test user already exists: {test_user.email}")

print("\nDatabase initialization complete!")
print(f"Test credentials: {test_user.email} / test123456")
