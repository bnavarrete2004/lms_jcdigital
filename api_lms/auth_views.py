# api_lms/auth_views.py
# Views de autenticación JWT para LMS JC Digital Training

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from api_lms.models import Usuario
from api_lms.serializers import UsuarioSerializer


# =====================================================
# SERIALIZER PERSONALIZADO PARA LOGIN
# =====================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado que incluye datos del usuario en la respuesta"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar información personalizada al token JWT
        if hasattr(user, 'perfil'):
            perfil = user.perfil
            token['rol'] = perfil.tipo_usuario  # ← AGREGAR ESTO
            token['usuario_id'] = perfil.id
            token['nombre_completo'] = perfil.nombre_completo()
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información del usuario al response
        if hasattr(self.user, 'perfil'):
            perfil = self.user.perfil
            data['user'] = {
                'id': perfil.id,
                'user_id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'nombre_completo': perfil.nombre_completo(),
                'tipo_usuario': perfil.tipo_usuario,
                'rol': perfil.tipo_usuario,  # ← AGREGAR ESTO
                'rut': perfil.get_rut(),
                'avatar_url': perfil.avatar_url,
            }
        else:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'tipo_usuario': 'sin_perfil',
                'rol': None,  # ← AGREGAR ESTO
            }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para login"""
    serializer_class = CustomTokenObtainPairSerializer


# =====================================================
# ENDPOINT DE REGISTRO
# =====================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registro de nuevos usuarios
    
    Body esperado:
    {
        "username": "usuario123",
        "email": "usuario@example.com",
        "password": "contraseña123",
        "password2": "contraseña123",
        "rut_numero": 12345678,
        "rut_dv": "9",
        "nombres": "Juan",
        "apellido_paterno": "Pérez",
        "apellido_materno": "González",
        "tipo_usuario": "estudiante",  # 'administrador', 'relator', 'estudiante'
        "telefono": "+56912345678",
        "region": "Valparaíso",
        "comuna": "Limache"
    }
    """
    
    # Validar que las contraseñas coincidan
    password = request.data.get('password')
    password2 = request.data.get('password2')
    
    if password != password2:
        return Response(
            {'error': 'Las contraseñas no coinciden'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar fortaleza de contraseña
    try:
        validate_password(password)
    except ValidationError as e:
        return Response(
            {'error': list(e.messages)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar que el username no exista
    if User.objects.filter(username=request.data.get('username')).exists():
        return Response(
            {'error': 'El nombre de usuario ya existe'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar que el email no exista
    if User.objects.filter(email=request.data.get('email')).exists():
        return Response(
            {'error': 'El email ya está registrado'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar que el RUT no exista
    rut_numero = request.data.get('rut_numero')
    rut_dv = request.data.get('rut_dv')
    if Usuario.objects.filter(rut_numero=rut_numero, rut_dv=rut_dv).exists():
        return Response(
            {'error': 'El RUT ya está registrado'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Crear usuario de Django
        user = User.objects.create_user(
            username=request.data.get('username'),
            email=request.data.get('email'),
            password=password,
            first_name=request.data.get('nombres', ''),
            last_name=request.data.get('apellido_paterno', '')
        )
        
        # Crear perfil de Usuario extendido
        usuario = Usuario.objects.create(
            user=user,
            rut_numero=rut_numero,
            rut_dv=rut_dv,
            nombres=request.data.get('nombres'),
            apellido_paterno=request.data.get('apellido_paterno'),
            apellido_materno=request.data.get('apellido_materno'),
            tipo_usuario=request.data.get('tipo_usuario', 'estudiante'),
            telefono=request.data.get('telefono', ''),
            region=request.data.get('region', ''),
            comuna=request.data.get('comuna', ''),
            nivel_educacional=request.data.get('nivel_educacional', ''),
            profesion=request.data.get('profesion', ''),
            activo=True
        )
        
        # Generar tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user': UsuarioSerializer(usuario).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        # Si algo falla, eliminar el usuario si se creó
        if 'user' in locals():
            user.delete()
        
        return Response(
            {'error': f'Error al crear usuario: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =====================================================
# ENDPOINT DE LOGOUT
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout del usuario (blacklist del refresh token)
    
    Body esperado:
    {
        "refresh": "token_de_refresh"
    }
    """
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {'error': 'Se requiere el refresh token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {'message': 'Logout exitoso'}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'Error al hacer logout: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================================
# ENDPOINT PARA VERIFICAR TOKEN
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verifica si el token es válido y retorna info del usuario
    """
    if hasattr(request.user, 'perfil'):
        perfil = request.user.perfil
        return Response({
            'valid': True,
            'user': {
                'id': perfil.id,
                'user_id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'nombre_completo': perfil.nombre_completo(),
                'tipo_usuario': perfil.tipo_usuario,
                'rut': perfil.get_rut(),
                'avatar_url': perfil.avatar_url,
            }
        })
    
    return Response({
        'valid': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        }
    })


# =====================================================
# ENDPOINT PARA CAMBIAR CONTRASEÑA
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Cambiar contraseña del usuario autenticado
    
    Body esperado:
    {
        "old_password": "contraseña_actual",
        "new_password": "nueva_contraseña",
        "new_password2": "nueva_contraseña"
    }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')
    
    # Validar contraseña actual
    if not user.check_password(old_password):
        return Response(
            {'error': 'Contraseña actual incorrecta'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar que las nuevas contraseñas coincidan
    if new_password != new_password2:
        return Response(
            {'error': 'Las nuevas contraseñas no coinciden'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar fortaleza de la nueva contraseña
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response(
            {'error': list(e.messages)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cambiar contraseña
    user.set_password(new_password)
    user.save()
    
    return Response(
        {'message': 'Contraseña cambiada exitosamente'}, 
        status=status.HTTP_200_OK
    )