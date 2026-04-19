from django.core.management.base import BaseCommand
from users.models import Users
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize database with test user'

    def handle(self, *args, **options):
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
                self.stdout.write(self.style.SUCCESS(f'✓ Created test user: {test_user.email}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Test user exists: {test_user.email}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))
