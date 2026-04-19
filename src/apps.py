from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)


def init_db(sender, **kwargs):
    """Initialize database after migrations"""
    try:
        from django.core.management import call_command
        from users.models import Users
        
        logger.info("Checking if migrations are needed...")
        
        # Check if users table exists
        try:
            Users.objects.count()
            logger.info("✓ Database tables exist")
        except Exception as e:
            logger.error(f"Database tables missing: {e}")
            return
        
        # Create test user if doesn't exist
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
            logger.info(f"✓ Created test user: {test_user.email}")
        else:
            logger.info(f"✓ Test user exists: {test_user.email}")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)


class SrcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src'
    
    def ready(self):
        post_migrate.connect(init_db, sender=self)
