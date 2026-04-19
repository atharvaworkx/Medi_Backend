from django.utils.deprecation import MiddlewareMixin
from django.db import connection
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

_db_setup_done = False


class MigrationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        global _db_setup_done
        
        if not _db_setup_done:
            try:
                logger.info("Running database setup...")
                result = subprocess.run(['python', 'setup_db.py'], capture_output=True, text=True, timeout=60)
                logger.info(f"Setup output: {result.stdout}")
                if result.returncode != 0:
                    logger.error(f"Setup error: {result.stderr}")
                _db_setup_done = True
            except Exception as e:
                logger.error(f"Setup error: {e}", exc_info=True)
                _db_setup_done = True
        
        return None
