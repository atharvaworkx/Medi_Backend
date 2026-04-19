from django.utils.deprecation import MiddlewareMixin

class MigrationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        return None
