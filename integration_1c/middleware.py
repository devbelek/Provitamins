import base64
from django.conf import settings
from django.http import HttpResponse


class Basic1CAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("DEBUG: Request path:", request.path)  # Для отладки
        if request.path.startswith('/api/1c/'):
            return self.get_response(request)  # Временно пропускаем все запросы
        return self.get_response(request)