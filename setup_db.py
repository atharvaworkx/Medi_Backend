#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.db import connection

print("Setting up database...")

try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
        # Drop and recreate schema
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
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
        
        # Create user_profiles table with correct field names
        cursor.execute("""
            CREATE TABLE user_profiles (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                full_name VARCHAR(200),
                age INTEGER,
                date_of_birth DATE,
                gender VARCHAR(1),
                location VARCHAR(255),
                height_cm INTEGER,
                weight_kg DECIMAL(5,2),
                blood_type VARCHAR(10),
                bio TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create users_devices table
        cursor.execute("""
            CREATE TABLE users_devices (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                device_id VARCHAR(500),
                token VARCHAR(500),
                device_type VARCHAR(500),
                device_info VARCHAR(500),
                language VARCHAR(10),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create health_images table
        cursor.execute("""
            CREATE TABLE health_images (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                image_type VARCHAR(50),
                image_url VARCHAR(512),
                s3_key VARCHAR(255),
                upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                analysis_status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create medical_history table
        cursor.execute("""
            CREATE TABLE medical_history (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                allergies TEXT,
                chronic_conditions TEXT,
                current_medications TEXT,
                family_history TEXT,
                lifestyle_factors TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create ai_reports table
        cursor.execute("""
            CREATE TABLE ai_reports (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                report_data JSONB,
                overall_score INTEGER,
                dominant_prakriti VARCHAR(50),
                dominant_vikriti VARCHAR(50),
                is_critical BOOLEAN DEFAULT FALSE,
                generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create Django content types and auth tables
        cursor.execute("""
            CREATE TABLE django_content_type (
                id SERIAL PRIMARY KEY,
                app_label VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                UNIQUE(app_label, model)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE auth_permission (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                content_type_id INTEGER REFERENCES django_content_type(id),
                codename VARCHAR(100) NOT NULL,
                UNIQUE(content_type_id, codename)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE auth_group (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) UNIQUE NOT NULL
            );
        """)
        
        cursor.execute("""
            CREATE TABLE auth_group_permissions (
                id SERIAL PRIMARY KEY,
                group_id INTEGER REFERENCES auth_group(id),
                permission_id INTEGER REFERENCES auth_permission(id),
                UNIQUE(group_id, permission_id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE users_user_permissions (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES users(id),
                permission_id INTEGER REFERENCES auth_permission(id),
                UNIQUE(user_id, permission_id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE users_groups (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES users(id),
                group_id INTEGER REFERENCES auth_group(id),
                UNIQUE(user_id, group_id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE django_session (
                session_key VARCHAR(40) PRIMARY KEY,
                session_data TEXT NOT NULL,
                expire_date TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        
        # Mark migrations as applied
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('contenttypes', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('auth', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('sessions', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('users', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('profiles', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('medical', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('images', '0001_initial');")
        cursor.execute("INSERT INTO django_migrations (app, name) VALUES ('ai_reports', '0001_initial');")

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
    sys.exit(0)

except Exception as e:
    print(f"✗ Database setup error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)