# views_notificaciones.py
# ViewSet para notificaciones con acciones personalizadas
# LMS JC Digital Training

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from api_lms.models import Notificacion
from api_lms.serializers import NotificacionSerializer
from .notificaciones_utils import marcar_todas_leidas


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para notificaciones del usuario
    
    Endpoints:
    - GET /notificaciones/ - Listar notificaciones del usuario
    - GET /notificaciones/{id}/ - Detalle de notificación
    - GET /notificaciones/no_leidas/ - Solo notificaciones no leídas
    - POST /notificaciones/{id}/marcar_leida/ - Marcar como leída
    - POST /notificaciones/marcar_todas_leidas/ - Marcar todas como leídas
    - GET /notificaciones/contador/ - Contador de no leídas
    """
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo notificaciones del usuario actual"""
        user = self.request.user
        
        # Obtener perfil de usuario
        try:
            usuario = user.perfil
        except:
            return Notificacion.objects.none()
        
        queryset = Notificacion.objects.filter(usuario=usuario)
        
        # Filtros opcionales
        tipo = self.request.query_params.get('tipo', None)
        prioridad = self.request.query_params.get('prioridad', None)
        leida = self.request.query_params.get('leida', None)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)
        
        if leida is not None:
            leida_bool = leida.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(leida=leida_bool)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """
        Obtiene solo las notificaciones no leídas
        GET /notificaciones/no_leidas/
        """
        queryset = self.get_queryset().filter(leida=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'notificaciones': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """
        Marca una notificación como leída
        POST /notificaciones/{id}/marcar_leida/
        """
        notificacion = self.get_object()
        
        if notificacion.leida:
            return Response({
                'mensaje': 'La notificación ya estaba marcada como leída'
            }, status=status.HTTP_200_OK)
        
        notificacion.marcar_como_leida()
        
        return Response({
            'mensaje': 'Notificación marcada como leída',
            'notificacion': self.get_serializer(notificacion).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """
        Marca todas las notificaciones del usuario como leídas
        POST /notificaciones/marcar_todas_leidas/
        """
        user = request.user
        
        try:
            usuario = user.perfil
        except:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        count = marcar_todas_leidas(usuario)
        
        return Response({
            'mensaje': f'{count} notificaciones marcadas como leídas'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def contador(self, request):
        """
        Obtiene contador de notificaciones por estado y tipo
        GET /notificaciones/contador/
        """
        user = request.user
        
        try:
            usuario = user.perfil
        except:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Contadores generales
        total = Notificacion.objects.filter(usuario=usuario).count()
        no_leidas = Notificacion.objects.filter(usuario=usuario, leida=False).count()
        
        # Contadores por prioridad (solo no leídas)
        por_prioridad = {
            'urgente': Notificacion.objects.filter(
                usuario=usuario, leida=False, prioridad='urgente'
            ).count(),
            'alta': Notificacion.objects.filter(
                usuario=usuario, leida=False, prioridad='alta'
            ).count(),
            'normal': Notificacion.objects.filter(
                usuario=usuario, leida=False, prioridad='normal'
            ).count(),
            'baja': Notificacion.objects.filter(
                usuario=usuario, leida=False, prioridad='baja'
            ).count(),
        }
        
        # Contadores por tipo (solo no leídas)
        por_tipo = {}
        for tipo, _ in Notificacion.TIPO_CHOICES:
            count = Notificacion.objects.filter(
                usuario=usuario, leida=False, tipo=tipo
            ).count()
            if count > 0:
                por_tipo[tipo] = count
        
        return Response({
            'total': total,
            'no_leidas': no_leidas,
            'leidas': total - no_leidas,
            'por_prioridad': por_prioridad,
            'por_tipo': por_tipo
        })
    
    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """
        Obtiene las 10 notificaciones más recientes
        GET /notificaciones/recientes/
        """
        queryset = self.get_queryset()[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)