import base64
from django.conf import settings
from django.http import HttpResponse


class Basic1CAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/1c/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')

            if not auth_header.startswith('Basic '):
                return HttpResponse('Unauthorized', status=401)

            try:
                auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = auth_decoded.split(':')

                if (username != settings.ONE_C_USERNAME or
                        password != settings.ONE_C_PASSWORD):
                    return HttpResponse('Unauthorized', status=401)

            except Exception:
                return HttpResponse('Unauthorized', status=401)

        return self.get_response(request)