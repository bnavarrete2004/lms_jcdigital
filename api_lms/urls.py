# urls.py
# URLs Django REST Framework para LMS JC Digital Training
# Compatible con Django 5.0+ y DRF 3.14+

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework_nested import routers  # Instalar: pip install drf-nested-routers
from . import views

# =====================================================
# CONFIGURACIÓN DE ROUTERS
# =====================================================

# Router principal
router = DefaultRouter()

# =====================================================
# MÓDULO 1: USUARIOS Y AUTENTICACIÓN
# =====================================================

router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'perfiles-relator', views.PerfilRelatorViewSet, basename='perfil-relator')
router.register(r'configuracion-usuario', views.ConfiguracionUsuarioViewSet, basename='configuracion-usuario')

# =====================================================
# MÓDULO 2: CÓDIGOS SENCE
# =====================================================

router.register(r'codigos-sence', views.CodigoSenceViewSet, basename='codigo-sence')

# =====================================================
# MÓDULO 3: MATERIALES
# =====================================================

router.register(r'materiales', views.MaterialViewSet, basename='material')

# =====================================================
# MÓDULO 4: CURSOS Y ESTRUCTURA
# =====================================================

router.register(r'cursos', views.CursoViewSet, basename='curso')
router.register(r'modulos', views.ModuloCursoViewSet, basename='modulo')
router.register(r'lecciones', views.LeccionViewSet, basename='leccion')
router.register(r'actividades', views.ActividadLeccionViewSet, basename='actividad')

# Rutas anidadas para cursos (requiere drf-nested-routers)
# Instalar con: pip install drf-nested-routers
# cursos_router = routers.NestedDefaultRouter(router, r'cursos', lookup='curso')
# cursos_router.register(r'modulos', views.ModuloCursoViewSet, basename='curso-modulos')
# cursos_router.register(r'inscripciones', views.InscripcionViewSet, basename='curso-inscripciones')
# cursos_router.register(r'sesiones', views.SesionCursoViewSet, basename='curso-sesiones')
# cursos_router.register(r'evaluaciones', views.EvaluacionViewSet, basename='curso-evaluaciones')
# cursos_router.register(r'foros', views.ForoViewSet, basename='curso-foros')

# Rutas anidadas para módulos
# modulos_router = routers.NestedDefaultRouter(cursos_router, r'modulos', lookup='modulo')
# modulos_router.register(r'lecciones', views.LeccionViewSet, basename='modulo-lecciones')

# Rutas anidadas para lecciones
# lecciones_router = routers.NestedDefaultRouter(modulos_router, r'lecciones', lookup='leccion')
# lecciones_router.register(r'actividades', views.ActividadLeccionViewSet, basename='leccion-actividades')

# =====================================================
# MÓDULO 5: INSCRIPCIONES Y MATRÍCULAS
# =====================================================

router.register(r'inscripciones', views.InscripcionViewSet, basename='inscripcion')

# =====================================================
# MÓDULO 6: PROGRESO Y SEGUIMIENTO
# =====================================================

router.register(r'progreso-modulos', views.ProgresoModuloViewSet, basename='progreso-modulo')
router.register(r'progreso-lecciones', views.ProgresoLeccionViewSet, basename='progreso-leccion')
router.register(r'progreso-actividades', views.ProgresoActividadViewSet, basename='progreso-actividad')

# =====================================================
# MÓDULO 7: EVALUACIONES Y CALIFICACIONES
# =====================================================

router.register(r'evaluaciones', views.EvaluacionViewSet, basename='evaluacion')
router.register(r'preguntas-evaluacion', views.PreguntaEvaluacionViewSet, basename='pregunta-evaluacion')
router.register(r'intentos-evaluacion', views.IntentoEvaluacionViewSet, basename='intento-evaluacion')

# Rutas anidadas para evaluaciones (requiere drf-nested-routers)
# evaluaciones_router = routers.NestedDefaultRouter(router, r'evaluaciones', lookup='evaluacion')
# evaluaciones_router.register(r'preguntas', views.PreguntaEvaluacionViewSet, basename='evaluacion-preguntas')
# evaluaciones_router.register(r'intentos', views.IntentoEvaluacionViewSet, basename='evaluacion-intentos')

# =====================================================
# MÓDULO 8: ASISTENCIA Y SESIONES
# =====================================================

router.register(r'sesiones', views.SesionCursoViewSet, basename='sesion')
router.register(r'asistencias', views.RegistroAsistenciaViewSet, basename='asistencia')

# =====================================================
# MÓDULO 9: FOROS Y COMUNICACIÓN
# =====================================================

router.register(r'foros', views.ForoViewSet, basename='foro')
router.register(r'temas-foro', views.TemaForoViewSet, basename='tema-foro')
router.register(r'respuestas-foro', views.RespuestaForoViewSet, basename='respuesta-foro')

# Rutas anidadas para foros (requiere drf-nested-routers)
# foros_router = routers.NestedDefaultRouter(router, r'foros', lookup='foro')
# foros_router.register(r'temas', views.TemaForoViewSet, basename='foro-temas')

# Rutas anidadas para temas
# temas_router = routers.NestedDefaultRouter(foros_router, r'temas', lookup='tema')
# temas_router.register(r'respuestas', views.RespuestaForoViewSet, basename='tema-respuestas')

# =====================================================
# MÓDULO 10: NOTIFICACIONES Y MENSAJERÍA
# =====================================================

router.register(r'notificaciones', views.NotificacionViewSet, basename='notificacion')
router.register(r'mensajes', views.MensajePrivadoViewSet, basename='mensaje')

# =====================================================
# MÓDULO 11: ENCUESTAS Y DIPLOMAS
# =====================================================

router.register(r'preguntas-encuesta', views.PreguntaEncuestaViewSet, basename='pregunta-encuesta')
router.register(r'respuestas-encuesta', views.RespuestaEncuestaViewSet, basename='respuesta-encuesta')
router.register(r'plantillas-diploma', views.PlantillaDiplomaViewSet, basename='plantilla-diploma')
router.register(r'diplomas', views.DiplomaViewSet, basename='diploma')

# =====================================================
# MÓDULO 12: REPORTES Y MÉTRICAS
# =====================================================

router.register(r'metricas-historicas', views.MetricaHistoricaViewSet, basename='metrica-historica')

# =====================================================
# MÓDULO 13: AUDITORÍA
# =====================================================

router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')

# =====================================================
# URLS PRINCIPALES
# =====================================================

urlpatterns = [
    # Incluir todas las rutas del router principal
    path('api/v1/', include(router.urls)),
    
    # Rutas anidadas comentadas - descomentar después de instalar drf-nested-routers
    # path('api/v1/', include(cursos_router.urls)),
    # path('api/v1/', include(modulos_router.urls)),
    # path('api/v1/', include(lecciones_router.urls)),
    # path('api/v1/', include(evaluaciones_router.urls)),
    # path('api/v1/', include(foros_router.urls)),
    # path('api/v1/', include(temas_router.urls)),
    
    # =====================================================
    # AUTENTICACIÓN Y AUTORIZACIÓN
    # =====================================================
    
    path('api/v1/auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('api/v1/auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('api/v1/auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('api/v1/auth/password/change/', views.ChangePasswordView.as_view(), name='auth-password-change'),
    path('api/v1/auth/password/reset/', views.PasswordResetView.as_view(), name='auth-password-reset'),
    path('api/v1/auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('api/v1/auth/verify-email/', views.VerifyEmailView.as_view(), name='auth-verify-email'),
    path('api/v1/auth/refresh-token/', views.RefreshTokenView.as_view(), name='auth-refresh-token'),
    
    # =====================================================
    # PERFIL DE USUARIO
    # =====================================================
    
    path('api/v1/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('api/v1/me/profile/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('api/v1/me/avatar/', views.UpdateAvatarView.as_view(), name='update-avatar'),
    path('api/v1/me/configuracion/', views.UpdateConfiguracionView.as_view(), name='update-configuracion'),
    
    # =====================================================
    # DASHBOARDS
    # =====================================================
    
    path('api/v1/dashboard/estudiante/', views.DashboardEstudianteView.as_view(), name='dashboard-estudiante'),
    path('api/v1/dashboard/relator/', views.DashboardRelatorView.as_view(), name='dashboard-relator'),
    path('api/v1/dashboard/administrador/', views.DashboardAdministradorView.as_view(), name='dashboard-administrador'),
    
    # =====================================================
    # MATERIALES - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/materiales/<int:pk>/aprobar/', views.AprobarMaterialView.as_view(), name='material-aprobar'),
    path('api/v1/materiales/<int:pk>/rechazar/', views.RechazarMaterialView.as_view(), name='material-rechazar'),
    path('api/v1/materiales/<int:pk>/solicitar-cambios/', views.SolicitarCambiosMaterialView.as_view(), name='material-solicitar-cambios'),
    path('api/v1/materiales/<int:pk>/incrementar-vistas/', views.IncrementarVistasMaterialView.as_view(), name='material-incrementar-vistas'),
    path('api/v1/materiales/pendientes-revision/', views.MaterialesPendientesRevisionView.as_view(), name='materiales-pendientes-revision'),
    
    # =====================================================
    # CURSOS - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/cursos/<int:pk>/publicar/', views.PublicarCursoView.as_view(), name='curso-publicar'),
    path('api/v1/cursos/<int:pk>/despublicar/', views.DespublicarCursoView.as_view(), name='curso-despublicar'),
    path('api/v1/cursos/<int:pk>/duplicar/', views.DuplicarCursoView.as_view(), name='curso-duplicar'),
    path('api/v1/cursos/<int:pk>/estadisticas/', views.EstadisticasCursoView.as_view(), name='curso-estadisticas'),
    path('api/v1/cursos/destacados/', views.CursosDestacadosView.as_view(), name='cursos-destacados'),
    path('api/v1/cursos/proximos/', views.CursosProximosView.as_view(), name='cursos-proximos'),
    path('api/v1/cursos/categoria/<str:categoria>/', views.CursosPorCategoriaView.as_view(), name='cursos-por-categoria'),
    
    # =====================================================
    # INSCRIPCIONES - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/inscripciones/<int:pk>/cancelar/', views.CancelarInscripcionView.as_view(), name='inscripcion-cancelar'),
    path('api/v1/inscripciones/<int:pk>/reactivar/', views.ReactivarInscripcionView.as_view(), name='inscripcion-reactivar'),
    path('api/v1/inscripciones/<int:pk>/generar-diploma/', views.GenerarDiplomaView.as_view(), name='inscripcion-generar-diploma'),
    path('api/v1/inscripciones/<int:pk>/reporte-progreso/', views.ReporteProgresoView.as_view(), name='inscripcion-reporte-progreso'),
    
    # =====================================================
    # PROGRESO - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/progreso/marcar-leccion-completada/', views.MarcarLeccionCompletadaView.as_view(), name='marcar-leccion-completada'),
    path('api/v1/progreso/actualizar-posicion-video/', views.ActualizarPosicionVideoView.as_view(), name='actualizar-posicion-video'),
    path('api/v1/progreso/registrar-tiempo/', views.RegistrarTiempoView.as_view(), name='registrar-tiempo'),
    
    # =====================================================
    # EVALUACIONES - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/evaluaciones/<int:pk>/iniciar/', views.IniciarEvaluacionView.as_view(), name='evaluacion-iniciar'),
    path('api/v1/evaluaciones/<int:pk>/enviar-respuestas/', views.EnviarRespuestasEvaluacionView.as_view(), name='evaluacion-enviar-respuestas'),
    path('api/v1/evaluaciones/<int:pk>/resultados/', views.ResultadosEvaluacionView.as_view(), name='evaluacion-resultados'),
    path('api/v1/evaluaciones/<int:pk>/estadisticas/', views.EstadisticasEvaluacionView.as_view(), name='evaluacion-estadisticas'),
    
    # =====================================================
    # ASISTENCIA - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/asistencias/registrar/', views.RegistrarAsistenciaView.as_view(), name='asistencia-registrar'),
    path('api/v1/asistencias/registrar-biometrica/', views.RegistrarAsistenciaBiometricaView.as_view(), name='asistencia-registrar-biometrica'),
    path('api/v1/asistencias/sesion/<int:sesion_id>/reporte/', views.ReporteAsistenciaSesionView.as_view(), name='asistencia-reporte-sesion'),
    path('api/v1/asistencias/curso/<int:curso_id>/reporte/', views.ReporteAsistenciaCursoView.as_view(), name='asistencia-reporte-curso'),
    
    # =====================================================
    # FOROS - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/temas-foro/<int:pk>/marcar-resuelto/', views.MarcarTemaResueltoView.as_view(), name='tema-marcar-resuelto'),
    path('api/v1/temas-foro/<int:pk>/fijar/', views.FijarTemaView.as_view(), name='tema-fijar'),
    path('api/v1/temas-foro/<int:pk>/cerrar/', views.CerrarTemaView.as_view(), name='tema-cerrar'),
    path('api/v1/respuestas-foro/<int:pk>/like/', views.LikeRespuestaView.as_view(), name='respuesta-like'),
    path('api/v1/respuestas-foro/<int:pk>/marcar-correcta/', views.MarcarRespuestaCorrectaView.as_view(), name='respuesta-marcar-correcta'),
    
    # =====================================================
    # NOTIFICACIONES - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/notificaciones/marcar-leida/<int:pk>/', views.MarcarNotificacionLeidaView.as_view(), name='notificacion-marcar-leida'),
    path('api/v1/notificaciones/marcar-todas-leidas/', views.MarcarTodasNotificacionesLeidasView.as_view(), name='notificaciones-marcar-todas-leidas'),
    path('api/v1/notificaciones/no-leidas/', views.NotificacionesNoLeidasView.as_view(), name='notificaciones-no-leidas'),
    path('api/v1/notificaciones/recientes/', views.NotificacionesRecientesView.as_view(), name='notificaciones-recientes'),
    
    # =====================================================
    # MENSAJERÍA - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/mensajes/enviados/', views.MensajesEnviadosView.as_view(), name='mensajes-enviados'),
    path('api/v1/mensajes/recibidos/', views.MensajesRecibidosView.as_view(), name='mensajes-recibidos'),
    path('api/v1/mensajes/<int:pk>/marcar-leido/', views.MarcarMensajeLeidoView.as_view(), name='mensaje-marcar-leido'),
    path('api/v1/mensajes/no-leidos/', views.MensajesNoLeidosView.as_view(), name='mensajes-no-leidos'),
    
    # =====================================================
    # DIPLOMAS - ACCIONES ESPECIALES
    # =====================================================
    
    path('api/v1/diplomas/<str:codigo>/verificar/', views.VerificarDiplomaView.as_view(), name='diploma-verificar'),
    path('api/v1/diplomas/<int:pk>/descargar/', views.DescargarDiplomaView.as_view(), name='diploma-descargar'),
    path('api/v1/diplomas/<int:pk>/regenerar/', views.RegenerarDiplomaView.as_view(), name='diploma-regenerar'),
    
    # =====================================================
    # REPORTES Y ESTADÍSTICAS
    # =====================================================
    
    path('api/v1/reportes/estudiante/<int:estudiante_id>/', views.ReporteEstudianteView.as_view(), name='reporte-estudiante'),
    path('api/v1/reportes/curso/<int:curso_id>/', views.ReporteCursoView.as_view(), name='reporte-curso'),
    path('api/v1/reportes/relator/<int:relator_id>/', views.ReporteRelatorView.as_view(), name='reporte-relator'),
    path('api/v1/reportes/plataforma/', views.ReportePlataformaView.as_view(), name='reporte-plataforma'),
    path('api/v1/reportes/asistencias/', views.ReporteAsistenciasView.as_view(), name='reporte-asistencias'),
    path('api/v1/reportes/evaluaciones/', views.ReporteEvaluacionesView.as_view(), name='reporte-evaluaciones'),
    path('api/v1/reportes/exportar/excel/', views.ExportarReporteExcelView.as_view(), name='exportar-reporte-excel'),
    path('api/v1/reportes/exportar/pdf/', views.ExportarReportePDFView.as_view(), name='exportar-reporte-pdf'),
    
    # =====================================================
    # ESTADÍSTICAS Y MÉTRICAS
    # =====================================================
    
    path('api/v1/estadisticas/general/', views.EstadisticasGeneralesView.as_view(), name='estadisticas-generales'),
    path('api/v1/estadisticas/inscripciones/', views.EstadisticasInscripcionesView.as_view(), name='estadisticas-inscripciones'),
    path('api/v1/estadisticas/cursos-populares/', views.CursosPopularesView.as_view(), name='estadisticas-cursos-populares'),
    path('api/v1/estadisticas/relatores-destacados/', views.RelatoresDestacadosView.as_view(), name='estadisticas-relatores-destacados'),
    
    # =====================================================
    # INTEGRACIÓN SENCE
    # =====================================================
    
    path('api/v1/sence/sincronizar-inscripcion/', views.SincronizarInscripcionSenceView.as_view(), name='sence-sincronizar-inscripcion'),
    path('api/v1/sence/sincronizar-asistencia/', views.SincronizarAsistenciaSenceView.as_view(), name='sence-sincronizar-asistencia'),
    path('api/v1/sence/sincronizar-certificacion/', views.SincronizarCertificacionSenceView.as_view(), name='sence-sincronizar-certificacion'),
    path('api/v1/sence/verificar-codigo/', views.VerificarCodigoSenceView.as_view(), name='sence-verificar-codigo'),
    path('api/v1/sence/estado-sincronizacion/', views.EstadoSincronizacionSenceView.as_view(), name='sence-estado-sincronizacion'),
    
    # =====================================================
    # BÚSQUEDA Y FILTRADO
    # =====================================================
    
    path('api/v1/buscar/cursos/', views.BuscarCursosView.as_view(), name='buscar-cursos'),
    path('api/v1/buscar/materiales/', views.BuscarMaterialesView.as_view(), name='buscar-materiales'),
    path('api/v1/buscar/usuarios/', views.BuscarUsuariosView.as_view(), name='buscar-usuarios'),
    path('api/v1/buscar/global/', views.BusquedaGlobalView.as_view(), name='busqueda-global'),
    
    # =====================================================
    # ADMINISTRACIÓN
    # =====================================================
    
    path('api/v1/admin/usuarios/bulk-create/', views.BulkCreateUsuariosView.as_view(), name='admin-bulk-create-usuarios'),
    path('api/v1/admin/usuarios/bulk-update/', views.BulkUpdateUsuariosView.as_view(), name='admin-bulk-update-usuarios'),
    path('api/v1/admin/inscripciones/bulk-create/', views.BulkCreateInscripcionesView.as_view(), name='admin-bulk-create-inscripciones'),
    path('api/v1/admin/sistema/configuracion/', views.ConfiguracionSistemaView.as_view(), name='admin-configuracion-sistema'),
    path('api/v1/admin/sistema/logs/', views.LogsSistemaView.as_view(), name='admin-logs-sistema'),
    path('api/v1/admin/sistema/backup/', views.BackupSistemaView.as_view(), name='admin-backup-sistema'),
    path('api/v1/admin/sistema/mantenimiento/', views.MantenimientoSistemaView.as_view(), name='admin-mantenimiento-sistema'),
    
    # =====================================================
    # ARCHIVOS Y UPLOADS
    # =====================================================
    
    path('api/v1/uploads/material/', views.UploadMaterialView.as_view(), name='upload-material'),
    path('api/v1/uploads/avatar/', views.UploadAvatarView.as_view(), name='upload-avatar'),
    path('api/v1/uploads/imagen-curso/', views.UploadImagenCursoView.as_view(), name='upload-imagen-curso'),
    path('api/v1/uploads/documento/', views.UploadDocumentoView.as_view(), name='upload-documento'),
    path('api/v1/uploads/validar/', views.ValidarArchivoView.as_view(), name='validar-archivo'),
    
    # =====================================================
    # WEBHOOKS Y CALLBACKS
    # =====================================================
    
    path('api/v1/webhooks/sence/', views.WebhookSenceView.as_view(), name='webhook-sence'),
    path('api/v1/webhooks/pago/', views.WebhookPagoView.as_view(), name='webhook-pago'),
    path('api/v1/callbacks/video-procesado/', views.CallbackVideoProcesadoView.as_view(), name='callback-video-procesado'),
    
    # =====================================================
    # UTILIDADES Y SALUD DEL SISTEMA
    # =====================================================
    
    path('api/v1/health/', views.HealthCheckView.as_view(), name='health-check'),
    path('api/v1/version/', views.VersionView.as_view(), name='version'),
    path('api/v1/regiones/', views.RegionesView.as_view(), name='regiones'),
    path('api/v1/comunas/', views.ComunasView.as_view(), name='comunas'),
    path('api/v1/comunas/<str:region>/', views.ComunasPorRegionView.as_view(), name='comunas-por-region'),
    
    # =====================================================
    # DOCUMENTACIÓN API
    # =====================================================
    
    # Schema OpenAPI
    path('api/v1/schema/', views.SchemaView.as_view(), name='api-schema'),
    
    # Swagger UI
    path('api/v1/docs/', views.SwaggerUIView.as_view(), name='api-docs'),
    
    # ReDoc
    path('api/v1/redoc/', views.ReDocView.as_view(), name='api-redoc'),
]

# =====================================================
# CONFIGURACIÓN ADICIONAL PARA DESARROLLO
# =====================================================

# Solo en desarrollo: agregar rutas para servir archivos media
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# =====================================================
# PATRONES DE URL PERSONALIZADOS
# =====================================================

# Handler personalizado para errores 404
handler404 = 'api_lms.views.custom_404'

# Handler personalizado para errores 500
handler500 = 'api_lms.views.custom_500'

# =====================================================
# NOTAS DE IMPLEMENTACIÓN
# =====================================================

"""
ESTRUCTURA DE URLS:

1. API VERSIONING:
   - Todas las URLs están bajo /api/v1/
   - Facilita versionado futuro (v2, v3, etc.)

2. ROUTERS:
   - DefaultRouter: Para endpoints CRUD estándar
   - NestedRouter: Para relaciones anidadas (cursos/1/modulos/2/lecciones)

3. ENDPOINTS PERSONALIZADOS:
   - Acciones especiales como aprobar, rechazar, publicar
   - Dashboards específicos por rol
   - Reportes y estadísticas
   - Integración SENCE

4. AUTENTICACIÓN:
   - JWT tokens recomendado
   - Session authentication para navegador
   - Token authentication para API mobile

5. PERMISOS:
   - IsAuthenticated: Usuario autenticado
   - IsAdminUser: Solo administradores
   - IsRelator: Solo relatores
   - IsOwnerOrReadOnly: Propietario o solo lectura

6. PAGINACIÓN:
   - PageNumberPagination por defecto
   - LimitOffsetPagination para casos específicos
   - CursorPagination para grandes datasets

7. FILTRADO:
   - django-filter para filtrado avanzado
   - SearchFilter para búsqueda de texto
   - OrderingFilter para ordenamiento

8. THROTTLING:
   - AnonRateThrottle: Limitar usuarios anónimos
   - UserRateThrottle: Limitar usuarios autenticados
   - Custom rates para endpoints específicos

EJEMPLOS DE USO:

# Listar todos los cursos
GET /api/v1/cursos/

# Obtener un curso específico
GET /api/v1/cursos/123/

# Crear un curso
POST /api/v1/cursos/

# Actualizar un curso
PUT /api/v1/cursos/123/
PATCH /api/v1/cursos/123/

# Eliminar un curso
DELETE /api/v1/cursos/123/

# Listar módulos de un curso
GET /api/v1/cursos/123/modulos/

# Listar lecciones de un módulo
GET /api/v1/cursos/123/modulos/456/lecciones/

# Publicar un curso
POST /api/v1/cursos/123/publicar/

# Dashboard de estudiante
GET /api/v1/dashboard/estudiante/

# Registrar asistencia biométrica
POST /api/v1/asistencias/registrar-biometrica/

# Sincronizar con SENCE
POST /api/v1/sence/sincronizar-inscripcion/

CONSIDERACIONES DE SEGURIDAD:

1. CSRF Protection habilitado para session auth
2. CORS configurado apropiadamente
3. Rate limiting en endpoints sensibles
4. Validación de permisos en cada endpoint
5. Sanitización de inputs
6. Logs de auditoría para acciones críticas
7. HTTPS obligatorio en producción

OPTIMIZACIONES:

1. select_related() para relaciones ForeignKey
2. prefetch_related() para relaciones ManyToMany
3. Caché de Redis para endpoints frecuentes
4. Compresión gzip habilitada
5. CDN para archivos estáticos
6. Database indexing apropiado
"""

# =====================================================
# FIN DE URLS
# =====================================================