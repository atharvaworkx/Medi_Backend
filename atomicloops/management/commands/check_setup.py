import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check required application configuration."

    def handle(self, *args, **kwargs):
        required = []
        if os.getenv("ENV") == "prod":
            required.extend(["DJANGO_SECRET_KEY", "DATABASE_URL", "ALLOWED_HOSTS"])

        missing = [name for name in required if not os.getenv(name)]
        if missing:
            self.stdout.write(
                self.style.ERROR(
                    "Missing required environment variables: " + ", ".join(missing)
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Configuration loaded for {settings.PROJECT_NAME} ({os.getenv('ENV', 'dev')})."
            )
        )
