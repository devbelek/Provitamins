from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

API_PREFIX = "api/v1/"

urlpatterns = [
    path(f'{API_PREFIX}schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_PREFIX}schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_PREFIX}schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('api/1c/', include('integration_1c.urls')),
    path(f'{API_PREFIX}marketplace/', include('marketplace.urls')),
    path(f'{API_PREFIX}contents/', include('contents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
