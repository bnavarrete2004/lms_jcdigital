# urls.py
# URLs para LMS J&C Digital Training
# Basado en models.py real del proyecto

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, UsuarioViewSet, PerfilRelatorViewSet, ConfiguracionUsuarioViewSet,
    CodigoSenceViewSet,
    CursoViewSet, CursoRelatorViewSet, ModuloViewSet, LeccionViewSet,
    MaterialViewSet, LeccionMaterialViewSet,
    InscripcionViewSet, ProgresoModuloViewSet, ProgresoLeccionViewSet, ActividadEstudianteViewSet,
    EvaluacionViewSet, PreguntaViewSet, IntentoEvaluacionViewSet, 
    RespuestaEstudianteViewSet, SolicitudTercerIntentoViewSet,
    SesionSenceViewSet, LogEnvioSenceViewSet,
    ForoConsultaViewSet, ForoRespuestaViewSet,
    NotificacionViewSet,
    EncuestaViewSet, RespuestaEncuestaViewSet,
    PlantillaDiplomaViewSet,
    MetricaHistoricaViewSet,
    AuditLogViewSet
)

# Importar views de upload
from .views_upload import upload_material, upload_avatar, delete_avatar

router = DefaultRouter()

# Módulo 1: Usuarios
router.register(r'users', UserViewSet, basename='user')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'perfiles-relator', PerfilRelatorViewSet, basename='perfil-relator')
router.register(r'configuraciones-usuario', ConfiguracionUsuarioViewSet, basename='configuracion-usuario')

# Módulo 2: Códigos SENCE
router.register(r'codigos-sence', CodigoSenceViewSet, basename='codigo-sence')

# Módulo 3: Cursos
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'curso-relator', CursoRelatorViewSet, basename='curso-relator')
router.register(r'modulos', ModuloViewSet, basename='modulo')
router.register(r'lecciones', LeccionViewSet, basename='leccion')

# Módulo 4: Materiales
router.register(r'materiales', MaterialViewSet, basename='material')
router.register(r'leccion-material', LeccionMaterialViewSet, basename='leccion-material')

# Módulo 5: Inscripciones
router.register(r'inscripciones', InscripcionViewSet, basename='inscripcion')
router.register(r'progreso-modulos', ProgresoModuloViewSet, basename='progreso-modulo')
router.register(r'progreso-lecciones', ProgresoLeccionViewSet, basename='progreso-leccion')
router.register(r'actividades-estudiante', ActividadEstudianteViewSet, basename='actividad-estudiante')

# Módulo 6: Evaluaciones
router.register(r'evaluaciones', EvaluacionViewSet, basename='evaluacion')
router.register(r'preguntas', PreguntaViewSet, basename='pregunta')
router.register(r'intentos-evaluacion', IntentoEvaluacionViewSet, basename='intento-evaluacion')
router.register(r'respuestas-estudiante', RespuestaEstudianteViewSet, basename='respuesta-estudiante')
router.register(r'solicitudes-tercer-intento', SolicitudTercerIntentoViewSet, basename='solicitud-tercer-intento')

# Módulo 7: Integración SENCE
router.register(r'sesiones-sence', SesionSenceViewSet, basename='sesion-sence')
router.register(r'logs-envio-sence', LogEnvioSenceViewSet, basename='log-envio-sence')

# Módulo 8: Foro
router.register(r'foro-consultas', ForoConsultaViewSet, basename='foro-consulta')
router.register(r'foro-respuestas', ForoRespuestaViewSet, basename='foro-respuesta')

# Módulo 9: Notificaciones
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

# Módulo 10: Encuestas
router.register(r'encuestas', EncuestaViewSet, basename='encuesta')
router.register(r'respuestas-encuesta', RespuestaEncuestaViewSet, basename='respuesta-encuesta')

# Módulo 11: Diplomas
router.register(r'plantillas-diploma', PlantillaDiplomaViewSet, basename='plantilla-diploma')

# Módulo 12: Métricas
router.register(r'metricas-historicas', MetricaHistoricaViewSet, basename='metrica-historica')

# Módulo 13: Auditoría
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
    
    # Módulo 14: Upload de archivos
    path('upload/material/', upload_material, name='upload-material'),
    path('upload/avatar/', upload_avatar, name='upload-avatar'),
    path('upload/avatar/', delete_avatar, name='delete-avatar'),  # DELETE method
]