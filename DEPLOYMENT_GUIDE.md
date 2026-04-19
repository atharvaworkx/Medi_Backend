# Deployment Guide - Render

## Current Deployment Status
- **Backend URL**: https://medi-backend-kezm.onrender.com
- **Database**: PostgreSQL on Render
- **Status**: Production Ready

## Environment Variables Required on Render

Add these environment variables in Render dashboard:

```
ENV=prod
DJANGO_SETTINGS_MODULE=src.settings.prod
DB_NAME=ayupilot
DB_USER=ayupilot_user
DB_PASSWORD=J0ONf89tkE82JITlILk8eHdPf53a5L2E
DB_HOST=dpg-d7i8ghgsfn5c73e5ka4g-a.ohio-postgres.render.com
DB_PORT=5432
ALLOWED_HOSTS=medi-backend-kezm.onrender.com,localhost
CORS_ALLOWED_ORIGINS=https://medi-backend-kezm.onrender.com
CSRF_TRUSTED_ORIGINS=https://medi-backend-kezm.onrender.com
```

## How Migrations Work

The system now uses an automatic migration middleware that:

1. **On first request**: Checks if the `users` table exists
2. **If missing**: Runs `python manage.py migrate` automatically
3. **Creates test user**: Automatically creates test@test.com / test123456
4. **Prevents re-running**: Uses a global flag to ensure migrations run only once

This approach works on Render's free tier without needing the Procfile release phase.

## Testing the Backend

### Local Testing
```bash
cd django-boilerplate
python manage.py migrate
python test_backend.py
```

### Remote Testing
The backend is automatically tested on first request. Check:
- Health endpoint: `https://medi-backend-kezm.onrender.com/health/`
- Login endpoint: `POST https://medi-backend-kezm.onrender.com/api/v1/login/`
- Register endpoint: `POST https://medi-backend-kezm.onrender.com/api/v1/register/`

## Test Credentials

**Email**: test@test.com
**Password**: test123456

## Troubleshooting

### 500 Error on Login/Register
1. Check if database tables exist: `SELECT * FROM users;`
2. Verify environment variables are set correctly
3. Check Render logs for migration errors
4. Ensure DB_PASSWORD is correct

### Database Connection Issues
1. Verify DB_HOST, DB_USER, DB_PASSWORD are correct
2. Check if PostgreSQL is running on Render
3. Ensure SSL mode is set to "require"

### Migrations Not Running
1. Check Render logs for middleware errors
2. Verify DJANGO_SETTINGS_MODULE=src.settings.prod
3. Ensure ENV=prod is set

## Deployment Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Fix: Automatic migrations on startup"
   git push origin main
   ```

2. **Render will automatically**:
   - Install dependencies from requirements.txt
   - Collect static files
   - Start the web server

3. **First request will**:
   - Run migrations automatically
   - Create test user
   - Initialize database

4. **Verify deployment**:
   - Check health endpoint
   - Test login with test@test.com
   - Test registration with new user

## Files Modified

- `django-boilerplate/src/middleware.py` - Fixed migration middleware
- `django-boilerplate/src/settings/prod.py` - Removed hardcoded credentials
- `django-boilerplate/Procfile` - Removed release phase
- `django-boilerplate/render.yaml` - Added Render configuration
- `django-boilerplate/test_backend.py` - Added comprehensive test script

## Security Notes

- All database credentials are now in environment variables
- No hardcoded secrets in code
- SSL mode required for database connection
- CORS and CSRF properly configured
- Debug mode disabled in production
