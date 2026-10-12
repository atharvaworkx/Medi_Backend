import os
import subprocess

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Run common application lifecycle commands without Docker."

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, required=True)

    def handle(self, *args, **options):
        mode = options["mode"]
        commands = {
            "check-syntax": ["flake8", "."],
            "migrate": ["python", "manage.py", "migrate"],
            "start-deploy": [
                "python",
                "manage.py",
                "collectstatic",
                "--noinput",
            ],
        }
        if mode not in commands:
            raise CommandError(
                "Supported modes are: " + ", ".join(sorted(commands))
            )

        subprocess.run(commands[mode], check=True, env=os.environ.copy())
