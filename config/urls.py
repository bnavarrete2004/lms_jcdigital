"""
URL Configuration for LMS JC Digital Training
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_lms.urls')),
]

# Admin customization
admin.site.site_header = "LMS JC Digital Training"
admin.site.site_title = "LMS Admin"
admin.site.index_title = "Panel de Administración"

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
