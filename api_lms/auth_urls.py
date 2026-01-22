# api_lms/auth_urls.py
# URLs de autenticación JWT

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .auth_views import (
    CustomTokenObtainPairView,
    register,
    logout,
    verify_token,
    change_password,
)

urlpatterns = [
    # Login (obtener tokens)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Refresh token (obtener nuevo access token)
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registro de nuevos usuarios
    path('register/', register, name='register'),
    
    # Logout (blacklist del refresh token)
    path('logout/', logout, name='logout'),
    
    # Verificar si el token es válido
    path('verify/', verify_token, name='verify_token'),
    
    # Cambiar contraseña
    path('change-password/', change_password, name='change_password'),
]