"""
API URLs for LMS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Registrar ViewSets aquí cuando estén listos
# router.register(r'cursos', CursoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
