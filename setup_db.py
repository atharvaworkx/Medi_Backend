#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.core.management import call_command
from django.db import connection
from users.models import Users

print("Creating database tables...")
try:
    # Create tables without migrations first
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                password VARCHAR(128),
                last_login TIMESTAMP WITH TIME ZONE,
                is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20) UNIQUE,
                "firstName" VARCHAR(100),
                "lastName" VARCHAR(100),
                level INTEGER NOT NULL DEFAULT 1,
                phone_number VARCHAR(20),
                profile_picture VARCHAR(512),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
    
    print("✓ Tables created")
    
    # Now run migrations
    call_command('migrate', verbosity=0, interactive=False, fake_initial=True)
    print("✓ Migrations completed")
    
except Exception as e:
    print(f"Migration error (continuing anyway): {e}")

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