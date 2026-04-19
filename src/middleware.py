from django.utils.deprecation import MiddlewareMixin
from django.core.management import call_command
import logging
import os

logger = logging.getLogger(__name__)

_migrations_run = False


class MigrationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        global _migrations_run
        
        if not _migrations_run and os.getenv('ENV') == 'prod':
            try:
                logger.info("Running migrations on first request...")
                call_command('migrate', verbosity=0, interactive=False)
                
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
                    logger.info(f"Created test user: {test_user.email}")
                
                _migrations_run = True
                logger.info("✓ Database initialized successfully")
            except Exception as e:
                logger.error(f"Migration error: {e}", exc_info=True)
        
        return None
