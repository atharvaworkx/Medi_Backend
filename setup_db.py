#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.core.management import call_command
from django.db import connection

print("Setting up database...")

# Create all tables manually to avoid migration issues
with connection.cursor() as cursor:
    cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    
    # Drop all tables
    cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS user_profiles CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE;")
    
    # Create django_migrations table
    cursor.execute("""
        CREATE TABLE django_migrations (
            id SERIAL PRIMARY KEY,
            app VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            applied TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    
    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    
    # Create user_profiles table
    cursor.execute("""
        CREATE TABLE user_profiles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            "userId_id" UUID REFERENCES users(id) ON DELETE CASCADE,
            "fullName" VARCHAR(200),
            age INTEGER,
            gender VARCHAR(1),
            height DECIMAL(5,2),
            weight DECIMAL(5,2),
            blood_type VARCHAR(3),
            bio TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    
    # Mark migrations as applied
    cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('users', '0001_initial');")
    cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('profiles', '0001_initial');")
    cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('contenttypes', '0001_initial');")
    cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('auth', '0001_initial');")
    cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('sessions', '0001_initial');")

print("✓ Database tables created")

# Create test user
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
    print(f"✓ Test user already exists: {test_user.email}")

print("✓ Database setup complete")