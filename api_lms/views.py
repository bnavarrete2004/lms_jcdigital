# views.py
# Views para LMS JC Digital Training
# Basado en models.py real del proyecto

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    # Módulo 1: Usuarios
    Usuario, PerfilRelator, ConfiguracionUsuario,
    
    # Módulo 2: Códigos SENCE
    CodigoSence,
    
    # Módulo 3: Cursos
    Curso, CursoRelator, Modulo, Leccion,
    
    # Módulo 4: Materiales
    Material, LeccionMaterial,
    
    # Módulo 5: Inscripciones
    Inscripcion, ProgresoModulo, ProgresoLeccion, ActividadEstudiante,
    
    # Módulo 6: Evaluaciones
    Evaluacion, Pregunta, IntentoEvaluacion, RespuestaEstudiante, SolicitudTercerIntento,
    
    # Módulo 7: Integración SENCE
    SesionSence, LogEnvioSence,
    
    # Módulo 8: Foro
    ForoConsulta, ForoRespuesta,
    
    # Módulo 9: Notificaciones
    Notificacion,
    
    # Módulo 10: Encuestas
    Encuesta, RespuestaEncuesta,
    
    # Módulo 11: Diplomas
    PlantillaDiploma,
    
    # Módulo 12: Métricas
    MetricaHistorica,
    
    # Módulo 13: Auditoría
    AuditLog
)

from .serializers import (
    UserSerializer, UsuarioSerializer, PerfilRelatorSerializer, ConfiguracionUsuarioSerializer,
    CodigoSenceSerializer,
    CursoSerializer, CursoRelatorSerializer, ModuloSerializer, LeccionSerializer,
    MaterialSerializer, LeccionMaterialSerializer,
    InscripcionSerializer, ProgresoModuloSerializer, ProgresoLeccionSerializer, ActividadEstudianteSerializer,
    EvaluacionSerializer, PreguntaSerializer, IntentoEvaluacionSerializer, 
    RespuestaEstudianteSerializer, SolicitudTercerIntentoSerializer,
    SesionSenceSerializer, LogEnvioSenceSerializer,
    ForoConsultaSerializer, ForoRespuestaSerializer,
    NotificacionSerializer,
    EncuestaSerializer, RespuestaEncuestaSerializer,
    PlantillaDiplomaSerializer,
    MetricaHistoricaSerializer,
    AuditLogSerializer
)


# =====================================================
# PERMISOS PERSONALIZADOS
# =====================================================

class IsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and hasattr(request.user, 'perfil') and 
                request.user.perfil.tipo_usuario == 'administrador')


class IsRelator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and hasattr(request.user, 'perfil') and 
                request.user.perfil.tipo_usuario == 'relator')


class IsEstudiante(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and hasattr(request.user, 'perfil') and 
                request.user.perfil.tipo_usuario == 'estudiante')


class IsAdminOrRelator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and hasattr(request.user, 'perfil') and 
                request.user.perfil.tipo_usuario in ['administrador', 'relator'])


class ReadOnlyOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (request.user.is_authenticated and hasattr(request.user, 'perfil') and 
                request.user.perfil.tipo_usuario == 'administrador')


# =====================================================
# VIEWSETS
# =====================================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministrador]


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return Usuario.objects.all()
            return Usuario.objects.filter(user=user)
        return Usuario.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        if hasattr(request.user, 'perfil'):
            serializer = self.get_serializer(request.user.perfil)
            return Response(serializer.data)
        return Response({'error': 'Usuario sin perfil'}, status=status.HTTP_404_NOT_FOUND)


class PerfilRelatorViewSet(viewsets.ModelViewSet):
    queryset = PerfilRelator.objects.all()
    serializer_class = PerfilRelatorSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [IsAdminOrRelator()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return PerfilRelator.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return PerfilRelator.objects.filter(usuario=user.perfil)
        return PerfilRelator.objects.none()


class ConfiguracionUsuarioViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionUsuario.objects.all()
    serializer_class = ConfiguracionUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'perfil'):
            return ConfiguracionUsuario.objects.filter(usuario=self.request.user.perfil)
        return ConfiguracionUsuario.objects.none()


class CodigoSenceViewSet(viewsets.ModelViewSet):
    queryset = CodigoSence.objects.all()
    serializer_class = CodigoSenceSerializer
    permission_classes = [ReadOnlyOrAdmin]


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return Curso.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return Curso.objects.filter(asignaciones_relator__relator=user.perfil, asignaciones_relator__activo=True)
            else:
                return Curso.objects.filter(inscripciones__estudiante=user.perfil)
        return Curso.objects.none()


class CursoRelatorViewSet(viewsets.ModelViewSet):
    queryset = CursoRelator.objects.all()
    serializer_class = CursoRelatorSerializer
    permission_classes = [IsAdministrador]


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
    permission_classes = [ReadOnlyOrAdmin]


class LeccionViewSet(viewsets.ModelViewSet):
    queryset = Leccion.objects.all()
    serializer_class = LeccionSerializer
    permission_classes = [ReadOnlyOrAdmin]


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrRelator()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return Material.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return Material.objects.filter(relator_autor=user.perfil)
            else:
                return Material.objects.filter(estado='aprobado')
        return Material.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'relator':
            serializer.save(estado='pendiente', subido_por=user.perfil, relator_autor=user.perfil)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def aprobar(self, request, pk=None):
        material = self.get_object()
        material.estado = 'aprobado'
        material.revisado_por = request.user.perfil
        material.fecha_revision = timezone.now()
        material.save()
        return Response({'status': 'Material aprobado'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def rechazar(self, request, pk=None):
        material = self.get_object()
        material.estado = 'rechazado'
        material.revisado_por = request.user.perfil
        material.fecha_revision = timezone.now()
        material.comentarios_revision = request.data.get('comentarios', '')
        material.save()
        return Response({'status': 'Material rechazado'})


class LeccionMaterialViewSet(viewsets.ModelViewSet):
    queryset = LeccionMaterial.objects.all()
    serializer_class = LeccionMaterialSerializer
    permission_classes = [ReadOnlyOrAdmin]


class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return Inscripcion.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return Inscripcion.objects.filter(curso__asignaciones_relator__relator=user.perfil)
            else:
                return Inscripcion.objects.filter(estudiante=user.perfil)
        return Inscripcion.objects.none()


class ProgresoModuloViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgresoModulo.objects.all()
    serializer_class = ProgresoModuloSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return ProgresoModulo.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return ProgresoModulo.objects.filter(inscripcion__curso__asignaciones_relator__relator=user.perfil)
            else:
                return ProgresoModulo.objects.filter(inscripcion__estudiante=user.perfil)
        return ProgresoModulo.objects.none()


class ProgresoLeccionViewSet(viewsets.ModelViewSet):
    queryset = ProgresoLeccion.objects.all()
    serializer_class = ProgresoLeccionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return ProgresoLeccion.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return ProgresoLeccion.objects.filter(inscripcion__curso__asignaciones_relator__relator=user.perfil)
            else:
                return ProgresoLeccion.objects.filter(inscripcion__estudiante=user.perfil)
        return ProgresoLeccion.objects.none()
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        progreso = self.get_object()
        if request.user.perfil != progreso.inscripcion.estudiante:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        progreso.completada = True
        progreso.fecha_completado = timezone.now()
        progreso.save()
        return Response({'status': 'Lección completada'})


class ActividadEstudianteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActividadEstudiante.objects.all()
    serializer_class = ActividadEstudianteSerializer
    permission_classes = [IsAdminOrRelator]


class EvaluacionViewSet(viewsets.ModelViewSet):
    queryset = Evaluacion.objects.all()
    serializer_class = EvaluacionSerializer
    permission_classes = [ReadOnlyOrAdmin]


class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer
    permission_classes = [ReadOnlyOrAdmin]


class IntentoEvaluacionViewSet(viewsets.ModelViewSet):
    queryset = IntentoEvaluacion.objects.all()
    serializer_class = IntentoEvaluacionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return IntentoEvaluacion.objects.all()
            elif user.perfil.tipo_usuario == 'relator':
                return IntentoEvaluacion.objects.filter(evaluacion__curso__asignaciones_relator__relator=user.perfil)
            else:
                return IntentoEvaluacion.objects.filter(estudiante=user.perfil)
        return IntentoEvaluacion.objects.none()


class RespuestaEstudianteViewSet(viewsets.ModelViewSet):
    queryset = RespuestaEstudiante.objects.all()
    serializer_class = RespuestaEstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]


class SolicitudTercerIntentoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudTercerIntento.objects.all()
    serializer_class = SolicitudTercerIntentoSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsEstudiante()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'administrador':
                return SolicitudTercerIntento.objects.all()
            else:
                return SolicitudTercerIntento.objects.filter(estudiante=user.perfil)
        return SolicitudTercerIntento.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        solicitud.estado = 'aprobada'
        solicitud.revisado_por = request.user.perfil
        solicitud.fecha_revision = timezone.now()
        solicitud.comentarios_revision = request.data.get('comentarios', '')
        solicitud.save()
        return Response({'status': 'Solicitud aprobada'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def rechazar(self, request, pk=None):
        solicitud = self.get_object()
        solicitud.estado = 'rechazada'
        solicitud.revisado_por = request.user.perfil
        solicitud.fecha_revision = timezone.now()
        solicitud.comentarios_revision = request.data.get('comentarios', '')
        solicitud.save()
        return Response({'status': 'Solicitud rechazada'})


class SesionSenceViewSet(viewsets.ModelViewSet):
    queryset = SesionSence.objects.all()
    serializer_class = SesionSenceSerializer
    permission_classes = [IsAdministrador]


class LogEnvioSenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogEnvioSence.objects.all()
    serializer_class = LogEnvioSenceSerializer
    permission_classes = [IsAdministrador]


class ForoConsultaViewSet(viewsets.ModelViewSet):
    queryset = ForoConsulta.objects.all()
    serializer_class = ForoConsultaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario in ['administrador', 'relator']:
                return ForoConsulta.objects.all()
            else:
                return ForoConsulta.objects.filter(estudiante=user.perfil)
        return ForoConsulta.objects.none()


class ForoRespuestaViewSet(viewsets.ModelViewSet):
    queryset = ForoRespuesta.objects.all()
    serializer_class = ForoRespuestaSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'perfil'):
            return Notificacion.objects.filter(usuario=self.request.user.perfil)
        return Notificacion.objects.none()
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.marcar_como_leida()
        return Response({'status': 'Notificación marcada como leída'})


class EncuestaViewSet(viewsets.ModelViewSet):
    queryset = Encuesta.objects.all()
    serializer_class = EncuestaSerializer
    permission_classes = [ReadOnlyOrAdmin]


class RespuestaEncuestaViewSet(viewsets.ModelViewSet):
    queryset = RespuestaEncuesta.objects.all()
    serializer_class = RespuestaEncuestaSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsEstudiante()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario in ['administrador', 'relator']:
                return RespuestaEncuesta.objects.all()
            else:
                return RespuestaEncuesta.objects.filter(estudiante=user.perfil)
        return RespuestaEncuesta.objects.none()


class PlantillaDiplomaViewSet(viewsets.ModelViewSet):
    queryset = PlantillaDiploma.objects.all()
    serializer_class = PlantillaDiplomaSerializer
    permission_classes = [IsAdministrador]


class MetricaHistoricaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetricaHistorica.objects.all()
    serializer_class = MetricaHistoricaSerializer
    permission_classes = [IsAdminOrRelator]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdministrador]