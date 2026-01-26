# views_diplomas.py
# ViewSet para generación y validación de diplomas
# LMS JC Digital Training

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api_lms.models import PlantillaDiploma, Inscripcion
from api_lms.serializers import PlantillaDiplomaSerializer
from .diplomas_utils import (
    generar_diploma_completo,
    validar_codigo_diploma
)


class PlantillaDiplomaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de plantillas de diplomas
    Solo accesible por administradores
    """
    serializer_class = PlantillaDiplomaSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PlantillaDiploma.objects.all()
    
    def get_permissions(self):
        """Solo administradores pueden crear/editar/eliminar plantillas"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def marcar_predeterminada(self, request, pk=None):
        """
        Marca una plantilla como predeterminada
        POST /plantillas-diploma/{id}/marcar_predeterminada/
        """
        plantilla = self.get_object()
        
        # Desmarcar todas las demás
        PlantillaDiploma.objects.update(predeterminada=False)
        
        # Marcar esta como predeterminada
        plantilla.predeterminada = True
        plantilla.save(update_fields=['predeterminada'])
        
        return Response({
            'mensaje': f'Plantilla "{plantilla.nombre}" marcada como predeterminada',
            'plantilla': self.get_serializer(plantilla).data
        })


class DiplomaViewSet(viewsets.ViewSet):
    """
    ViewSet para operaciones relacionadas con diplomas de estudiantes
    
    Endpoints:
    - POST /diplomas/generar/ - Generar diploma para inscripción
    - GET /diplomas/validar/{codigo}/ - Validar código de diploma
    - GET /diplomas/mis-diplomas/ - Diplomas del usuario actual
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generar(self, request):
        """
        Genera el diploma para una inscripción completada
        POST /diplomas/generar/
        Body: { "inscripcion_id": 123 }
        
        Solo administradores o el propio estudiante pueden generar su diploma
        """
        inscripcion_id = request.data.get('inscripcion_id')
        
        if not inscripcion_id:
            return Response({
                'error': 'Se requiere el ID de la inscripción'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que la inscripción existe
        try:
            inscripcion = Inscripcion.objects.get(id=inscripcion_id)
        except Inscripcion.DoesNotExist:
            return Response({
                'error': 'Inscripción no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar permisos
        user = request.user
        try:
            usuario = user.perfil
        except:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Solo admin o el propio estudiante
        es_admin = usuario.tipo_usuario == 'administrador'
        es_el_estudiante = inscripcion.estudiante == usuario
        
        if not (es_admin or es_el_estudiante):
            return Response({
                'error': 'No tienes permiso para generar este diploma'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generar diploma
        resultado = generar_diploma_completo(inscripcion_id)
        
        if not resultado.get('success'):
            return Response({
                'error': resultado.get('error', 'Error al generar diploma')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Diploma generado exitosamente',
            'diploma': {
                'url': resultado['diploma_url'],
                'codigo_validacion': resultado['codigo_validacion'],
                'estudiante': resultado['estudiante'],
                'curso': resultado['curso']
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='validar/(?P<codigo>[^/.]+)')
    def validar(self, request, codigo=None):
        """
        Valida un código de diploma
        GET /diplomas/validar/{codigo}/
        
        Endpoint público (no requiere autenticación)
        """
        if not codigo:
            return Response({
                'error': 'Se requiere un código de validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = validar_codigo_diploma(codigo)
        
        if not resultado.get('valido'):
            return Response({
                'valido': False,
                'mensaje': 'Código de diploma no válido'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'valido': True,
            'diploma': {
                'estudiante': resultado['estudiante'],
                'rut': resultado['rut'],
                'curso': resultado['curso'],
                'fecha_termino': resultado['fecha_termino'],
                'nota_final': resultado['nota_final'],
                'url': resultado['diploma_url']
            }
        })
    
    @action(detail=False, methods=['get'])
    def mis_diplomas(self, request):
        """
        Obtiene todos los diplomas del usuario actual
        GET /diplomas/mis-diplomas/
        """
        user = request.user
        
        try:
            usuario = user.perfil
        except:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener inscripciones completadas con diploma
        inscripciones = Inscripcion.objects.filter(
            estudiante=usuario,
            estado='completado',
            diploma_url__isnull=False
        ).select_related('curso')
        
        diplomas = []
        for inscripcion in inscripciones:
            diplomas.append({
                'id': inscripcion.id,
                'curso': {
                    'id': inscripcion.curso.id,
                    'nombre': inscripcion.curso.nombre,
                    'codigo_sence': inscripcion.curso.codigo_sence.codigo if inscripcion.curso.codigo_sence else None
                },
                'fecha_termino': inscripcion.fecha_termino,
                'nota_final': inscripcion.nota_final,
                'diploma_url': inscripcion.diploma_url,
                'codigo_validacion': inscripcion.diploma_codigo_validacion
            })
        
        return Response({
            'count': len(diplomas),
            'diplomas': diplomas
        })
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Obtiene inscripciones completadas sin diploma generado
        GET /diplomas/pendientes/
        
        Solo para administradores
        """
        user = request.user
        
        try:
            usuario = user.perfil
        except:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if usuario.tipo_usuario != 'administrador':
            return Response({
                'error': 'Solo administradores pueden ver diplomas pendientes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Inscripciones completadas sin diploma
        inscripciones = Inscripcion.objects.filter(
            estado='completado',
            diploma_url__isnull=True
        ).select_related('estudiante', 'curso')
        
        pendientes = []
        for inscripcion in inscripciones:
            pendientes.append({
                'inscripcion_id': inscripcion.id,
                'estudiante': {
                    'nombre': inscripcion.estudiante.nombre_completo(),
                    'rut': inscripcion.estudiante.get_rut()
                },
                'curso': {
                    'nombre': inscripcion.curso.nombre,
                    'codigo_sence': inscripcion.curso.codigo_sence.codigo if inscripcion.curso.codigo_sence else None
                },
                'fecha_termino': inscripcion.fecha_termino,
                'nota_final': inscripcion.nota_final
            })
        
        return Response({
            'count': len(pendientes),
            'pendientes': pendientes
        })


# Hacer públicamente accesible la validación de diplomas
validar_diploma_permission_classes = []