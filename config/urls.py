"""
URL Configuration for LMS JC Digital Training
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api_lms.views_calificacion import (
    calcular_nota_intento,
    calcular_nota_final_inscripcion,
    aprobar_inscripcion,
    reprobar_inscripcion,
    detalle_calificaciones_inscripcion,
    validar_configuracion_evaluaciones
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_lms.urls')),
    path('api/auth/', include('api_lms.auth_urls')),
    path('api/intentos-evaluacion/<int:intento_id>/calcular-nota/', calcular_nota_intento),
    path('api/inscripciones/<int:inscripcion_id>/calcular-nota-final/', calcular_nota_final_inscripcion),
    path('api/inscripciones/<int:inscripcion_id>/aprobar/', aprobar_inscripcion),
    path('api/inscripciones/<int:inscripcion_id>/reprobar/', reprobar_inscripcion),
    path('api/inscripciones/<int:inscripcion_id>/calificaciones/', detalle_calificaciones_inscripcion),
    path('api/cursos/<int:curso_id>/validar-evaluaciones/', validar_configuracion_evaluaciones),

]

# Admin customization
admin.site.site_header = "LMS JC Digital Training"
admin.site.site_title = "LMS Admin"
admin.site.index_title = "Panel de Administración"

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
