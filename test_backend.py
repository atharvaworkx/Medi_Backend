#!/usr/bin/env python
import os
import sys
import django
import requests
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
django.setup()

from django.db import connection
from users.models import Users

BASE_URL = "https://medi-backend-kezm.onrender.com/api/v1"

def test_database_connection():
    print("\n" + "="*50)
    print("Testing Database Connection...")
    print("="*50)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_database_tables():
    print("\n" + "="*50)
    print("Testing Database Tables...")
    print("="*50)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """)
            users_table_exists = cursor.fetchone()[0]
        
        if users_table_exists:
            print("✓ Users table exists")
            user_count = Users.objects.count()
            print(f"✓ Total users in database: {user_count}")
            return True
        else:
            print("✗ Users table does not exist")
            return False
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        return False

def test_test_user():
    print("\n" + "="*50)
    print("Testing Test User...")
    print("="*50)
    try:
        test_user = Users.objects.get(email='test@test.com')
        print(f"✓ Test user exists: {test_user.email}")
        print(f"  - Name: {test_user.firstName} {test_user.lastName}")
        print(f"  - Verified: {test_user.isVerified}")
        print(f"  - Active: {test_user.is_active}")
        return True
    except Users.DoesNotExist:
        print("✗ Test user does not exist")
        return False
    except Exception as e:
        print(f"✗ Error checking test user: {e}")
        return False

def test_health_endpoint():
    print("\n" + "="*50)
    print("Testing Health Endpoint...")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health/", timeout=10)
        if response.status_code == 200:
            print(f"✓ Health endpoint returned 200")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing health endpoint: {e}")
        return False

def test_login_endpoint():
    print("\n" + "="*50)
    print("Testing Login Endpoint...")
    print("="*50)
    try:
        payload = {
            "email": "test@test.com",
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/login/", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful")
            print(f"  - User: {data.get('firstName')} {data.get('lastName')}")
            print(f"  - Email: {data.get('email')}")
            print(f"  - Token: {data.get('access', '')[:40]}...")
            return True
        else:
            print(f"✗ Login failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error testing login endpoint: {e}")
        return False

def test_register_endpoint():
    print("\n" + "="*50)
    print("Testing Register Endpoint...")
    print("="*50)
    try:
        import uuid
        unique_email = f"testuser_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "firstName": "Test",
            "lastName": "User",
            "phone": f"98765{uuid.uuid4().hex[:5]}",
            "password": "TestPass123",
            "passwordConfirm": "TestPass123"
        }
        response = requests.post(f"{BASE_URL}/register/", json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Registration successful")
            print(f"  - User: {data.get('firstName')} {data.get('lastName')}")
            print(f"  - Email: {data.get('email')}")
            print(f"  - Token: {data.get('access', '')[:40]}...")
            return True
        else:
            print(f"✗ Registration failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error testing register endpoint: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "╔" + "="*48 + "╗")
    print("║" + " "*10 + "BACKEND VERIFICATION TEST" + " "*13 + "║")
    print("╚" + "="*48 + "╝")
    
    results = []
    results.append(("Database Connection", test_database_connection()))
    results.append(("Database Tables", test_database_tables()))
    results.append(("Test User", test_test_user()))
    results.append(("Health Endpoint", test_health_endpoint()))
    results.append(("Login Endpoint", test_login_endpoint()))
    results.append(("Register Endpoint", test_register_endpoint()))
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED - BACKEND IS 100% WORKING ✓✓✓")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        sys.exit(1)
