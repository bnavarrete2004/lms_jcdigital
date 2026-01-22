# admin.py
# Admin básico para LMS JC Digital Training

from django.contrib import admin
from .models import (
    Usuario, PerfilRelator, ConfiguracionUsuario,
    CodigoSence,
    Curso, CursoRelator, Modulo, Leccion,
    Material, LeccionMaterial,
    Inscripcion, ProgresoModulo, ProgresoLeccion, ActividadEstudiante,
    Evaluacion, Pregunta, IntentoEvaluacion, RespuestaEstudiante, SolicitudTercerIntento,
    SesionSence, LogEnvioSence,
    ForoConsulta, ForoRespuesta,
    Notificacion,
    Encuesta, RespuestaEncuesta,
    PlantillaDiploma,
    MetricaHistorica,
    AuditLog
)

# Configuración del sitio
admin.site.site_header = "LMS J&C Digital Training - Administración"
admin.site.site_title = "LMS J&C Digital"
admin.site.index_title = "Panel de Administración"

# Registros básicos
admin.site.register(Usuario)
admin.site.register(PerfilRelator)
admin.site.register(ConfiguracionUsuario)
admin.site.register(CodigoSence)
admin.site.register(Curso)
admin.site.register(CursoRelator)
admin.site.register(Modulo)
admin.site.register(Leccion)
admin.site.register(Material)
admin.site.register(LeccionMaterial)
admin.site.register(Inscripcion)
admin.site.register(ProgresoModulo)
admin.site.register(ProgresoLeccion)
admin.site.register(ActividadEstudiante)
admin.site.register(Evaluacion)
admin.site.register(Pregunta)
admin.site.register(IntentoEvaluacion)
admin.site.register(RespuestaEstudiante)
admin.site.register(SolicitudTercerIntento)
admin.site.register(SesionSence)
admin.site.register(LogEnvioSence)
admin.site.register(ForoConsulta)
admin.site.register(ForoRespuesta)
admin.site.register(Notificacion)
admin.site.register(Encuesta)
admin.site.register(RespuestaEncuesta)
admin.site.register(PlantillaDiploma)
admin.site.register(MetricaHistorica)
admin.site.register(AuditLog)