#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.db import connection
from users.models import Users

print("\n" + "="*60)
print("DATABASE INSERT TEST")
print("="*60)

try:
    print("\n1. Testing database connection...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connected")
    
    print("\n2. Checking if users table exists...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        exists = cursor.fetchone()[0]
    
    if not exists:
        print("✗ Users table does not exist - running migrations...")
        from django.core.management import call_command
        call_command('migrate', verbosity=0, interactive=False)
        print("✓ Migrations completed")
    else:
        print("✓ Users table exists")
    
    print("\n3. Inserting test user...")
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
    
    print("\n4. Verifying user in database...")
    user = Users.objects.get(email='test@test.com')
    print(f"✓ User found: {user.firstName} {user.lastName}")
    print(f"  Email: {user.email}")
    print(f"  Phone: {user.phone}")
    print(f"  Verified: {user.isVerified}")
    print(f"  Active: {user.is_active}")
    
    print("\n5. Testing password verification...")
    if user.check_password('test123456'):
        print("✓ Password verification works")
    else:
        print("✗ Password verification failed")
    
    print("\n6. Counting total users...")
    count = Users.objects.count()
    print(f"✓ Total users in database: {count}")
    
    print("\n7. Listing all users...")
    all_users = Users.objects.all().values('email', 'firstName', 'lastName', 'isVerified')
    for u in all_users:
        print(f"  - {u['email']} ({u['firstName']} {u['lastName']}) - Verified: {u['isVerified']}")
    
    print("\n" + "="*60)
    print("✓✓✓ DATABASE INSERT TEST PASSED ✓✓✓")
    print("="*60)
    print("\nDatabase is working correctly!")
    print("Users table exists and can store data.")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
