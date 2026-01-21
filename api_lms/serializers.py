# serializers.py
# Serializers Django REST Framework para LMS JC Digital Training
# Compatible con Django 5.0+ y DRF 3.14+

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


# =====================================================
# SERIALIZERS BASE Y UTILIDAD
# =====================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User de Django"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


# =====================================================
# MÓDULO 1: USUARIOS Y AUTENTICACIÓN
# =====================================================

class ConfiguracionUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para preferencias y configuración de usuario"""
    
    class Meta:
        model = 'ConfiguracionUsuario'  # Referencia al modelo
        fields = [
            'id', 'notif_email', 'notif_push', 'notif_sms',
            'tema', 'idioma', 'zona_horaria',
            'perfil_publico', 'mostrar_progreso', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class PerfilRelatorSerializer(serializers.ModelSerializer):
    """Serializer para perfil de relator"""
    
    class Meta:
        model = 'PerfilRelator'
        fields = [
            'id', 'especialidad', 'areas_experiencia', 'certificaciones',
            'anos_experiencia', 'cv_url', 'calificacion_promedio',
            'total_cursos_dictados', 'total_estudiantes_capacitados',
            'verificado', 'fecha_verificacion', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'calificacion_promedio', 'total_cursos_dictados',
            'total_estudiantes_capacitados', 'fecha_verificacion',
            'created_at', 'updated_at'
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer principal para Usuario con información completa"""
    
    user = UserSerializer(read_only=True)
    perfil_relator = PerfilRelatorSerializer(read_only=True)
    configuracion = ConfiguracionUsuarioSerializer(read_only=True)
    rut_completo = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Usuario'
        fields = [
            'id', 'user', 'rut_numero', 'rut_dv', 'rut_completo',
            'nombres', 'apellido_paterno', 'apellido_materno', 'nombre_completo',
            'fecha_nacimiento', 'genero', 'telefono', 'telefono_emergencia',
            'direccion', 'comuna', 'region', 'nivel_educacional', 'profesion',
            'empresa_actual', 'cargo_actual', 'tipo_usuario', 'avatar_url',
            'activo', 'fecha_registro', 'ultima_actualizacion',
            'perfil_relator', 'configuracion'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultima_actualizacion', 'rut_completo', 'nombre_completo']
    
    def get_rut_completo(self, obj):
        return f"{obj.rut_numero}-{obj.rut_dv}"
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno}"


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de usuarios"""
    
    rut_completo = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Usuario'
        fields = [
            'id', 'rut_completo', 'nombre_completo', 'tipo_usuario',
            'email', 'activo', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def get_rut_completo(self, obj):
        return f"{obj.rut_numero}-{obj.rut_dv}"
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellido_paterno}"


# =====================================================
# MÓDULO 2: CÓDIGOS Y CATÁLOGOS SENCE
# =====================================================

class CodigoSenceSerializer(serializers.ModelSerializer):
    """Serializer para códigos SENCE"""
    
    horas_disponibles = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()
    
    class Meta:
        model = 'CodigoSence'
        fields = [
            'id', 'codigo', 'nombre_curso', 'horas_totales', 'horas_asignadas',
            'horas_disponibles', 'fecha_inicio_vigencia', 'fecha_fin_vigencia',
            'estado', 'vigente', 'area_tematica', 'nivel', 'modalidad',
            'linea_capacitacion', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'horas_disponibles', 'vigente']
    
    def get_horas_disponibles(self, obj):
        return obj.horas_totales - obj.horas_asignadas
    
    def get_vigente(self, obj):
        hoy = timezone.now().date()
        return (obj.fecha_inicio_vigencia <= hoy <= obj.fecha_fin_vigencia and 
                obj.estado == 'activo')


# =====================================================
# MÓDULO 3: MATERIALES
# =====================================================

class MaterialSerializer(serializers.ModelSerializer):
    """Serializer para materiales educativos"""
    
    relator_nombre = serializers.CharField(source='relator.nombre_completo', read_only=True)
    revisor_nombre = serializers.CharField(source='revisor.nombre_completo', read_only=True)
    archivo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Material'
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_material', 'categoria',
            'relator', 'relator_nombre', 'archivo_url', 'archivo_tipo',
            'archivo_size_mb', 'duracion_minutos', 'nivel_dificultad',
            'tags', 'estado', 'fecha_creacion', 'fecha_ultima_modificacion',
            'fecha_revision', 'revisor', 'revisor_nombre',
            'comentarios_revision', 'version', 'vistas_totales',
            'calificacion_promedio', 'publico', 'destacado'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_ultima_modificacion',
            'vistas_totales', 'calificacion_promedio', 'version'
        ]
    
    def get_archivo_url(self, obj):
        # Aquí se debe implementar la lógica de generación de URL firmada
        # Para desarrollo, retornar la URL directa
        return obj.archivo_url


class MaterialListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de materiales"""
    
    relator_nombre = serializers.CharField(source='relator.nombre_completo', read_only=True)
    
    class Meta:
        model = 'Material'
        fields = [
            'id', 'titulo', 'tipo_material', 'categoria', 'relator_nombre',
            'estado', 'fecha_creacion', 'duracion_minutos', 'nivel_dificultad'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class RevisionMaterialSerializer(serializers.ModelSerializer):
    """Serializer para revisión de materiales"""
    
    class Meta:
        model = 'Material'
        fields = [
            'id', 'estado', 'fecha_revision', 'revisor',
            'comentarios_revision'
        ]
        read_only_fields = ['id', 'fecha_revision']
    
    def validate_estado(self, value):
        if value not in ['aprobado', 'rechazado', 'requiere_cambios']:
            raise serializers.ValidationError(
                "Estado debe ser 'aprobado', 'rechazado' o 'requiere_cambios'"
            )
        return value


# =====================================================
# MÓDULO 4: CURSOS Y ESTRUCTURA
# =====================================================

class CursoSerializer(serializers.ModelSerializer):
    """Serializer completo para cursos"""
    
    codigo_sence_info = CodigoSenceSerializer(source='codigo_sence', read_only=True)
    relatores_info = UsuarioListSerializer(source='relatores', many=True, read_only=True)
    total_modulos = serializers.SerializerMethodField()
    total_lecciones = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Curso'
        fields = [
            'id', 'nombre', 'descripcion', 'descripcion_corta', 'objetivos',
            'requisitos', 'codigo_sence', 'codigo_sence_info',
            'horas_totales', 'nivel', 'modalidad', 'categoria',
            'imagen_portada_url', 'video_presentacion_url',
            'relatores', 'relatores_info', 'estado', 'fecha_inicio', 'fecha_fin',
            'precio', 'cupos_totales', 'cupos_disponibles', 'activo',
            'destacado', 'certificacion_disponible', 'total_modulos',
            'total_lecciones', 'fecha_creacion', 'fecha_publicacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_publicacion', 'total_modulos', 'total_lecciones']
    
    def get_total_modulos(self, obj):
        return obj.modulos.count()
    
    def get_total_lecciones(self, obj):
        return sum(modulo.lecciones.count() for modulo in obj.modulos.all())


class CursoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de cursos"""
    
    codigo_sence_nombre = serializers.CharField(source='codigo_sence.nombre_curso', read_only=True)
    
    class Meta:
        model = 'Curso'
        fields = [
            'id', 'nombre', 'descripcion_corta', 'codigo_sence_nombre',
            'horas_totales', 'nivel', 'modalidad', 'imagen_portada_url',
            'estado', 'fecha_inicio', 'fecha_fin', 'precio', 'cupos_disponibles',
            'activo', 'destacado'
        ]
        read_only_fields = ['id']


class ModuloCursoSerializer(serializers.ModelSerializer):
    """Serializer para módulos de curso"""
    
    total_lecciones = serializers.SerializerMethodField()
    duracion_total = serializers.SerializerMethodField()
    
    class Meta:
        model = 'ModuloCurso'
        fields = [
            'id', 'curso', 'titulo', 'descripcion', 'orden', 'objetivos',
            'duracion_estimada_horas', 'total_lecciones', 'duracion_total',
            'activo'
        ]
        read_only_fields = ['id', 'total_lecciones', 'duracion_total']
    
    def get_total_lecciones(self, obj):
        return obj.lecciones.count()
    
    def get_duracion_total(self, obj):
        return sum(leccion.duracion_minutos or 0 for leccion in obj.lecciones.all())


class LeccionSerializer(serializers.ModelSerializer):
    """Serializer para lecciones"""
    
    material_info = MaterialListSerializer(source='material', read_only=True)
    
    class Meta:
        model = 'Leccion'
        fields = [
            'id', 'modulo', 'titulo', 'descripcion', 'orden', 'tipo_leccion',
            'contenido_texto', 'material', 'material_info', 'video_url',
            'duracion_minutos', 'recursos_adicionales', 'preguntas_frecuentes',
            'activa'
        ]
        read_only_fields = ['id']


class ActividadLeccionSerializer(serializers.ModelSerializer):
    """Serializer para actividades de lección"""
    
    material_info = MaterialListSerializer(source='material', read_only=True)
    
    class Meta:
        model = 'ActividadLeccion'
        fields = [
            'id', 'leccion', 'titulo', 'descripcion', 'tipo_actividad',
            'orden', 'material', 'material_info', 'contenido_interactivo',
            'duracion_estimada_minutos', 'obligatoria', 'calificable',
            'puntaje_maximo', 'activa'
        ]
        read_only_fields = ['id']


# =====================================================
# MÓDULO 5: INSCRIPCIONES Y MATRÍCULAS
# =====================================================

class InscripcionSerializer(serializers.ModelSerializer):
    """Serializer para inscripciones de estudiantes"""
    
    estudiante_info = UsuarioListSerializer(source='estudiante', read_only=True)
    curso_info = CursoListSerializer(source='curso', read_only=True)
    progreso_porcentaje = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Inscripcion'
        fields = [
            'id', 'estudiante', 'estudiante_info', 'curso', 'curso_info',
            'fecha_inscripcion', 'fecha_inicio_efectiva', 'fecha_fin_efectiva',
            'estado', 'progreso_porcentaje', 'nota_final', 'asistencia_porcentaje',
            'encuesta_completada', 'fecha_encuesta_completada',
            'diploma_emitido', 'fecha_emision_diploma', 'codigo_diploma',
            'metodo_pago', 'monto_pagado', 'estado_pago', 'notas'
        ]
        read_only_fields = [
            'id', 'fecha_inscripcion', 'progreso_porcentaje', 'nota_final',
            'asistencia_porcentaje', 'fecha_emision_diploma', 'codigo_diploma'
        ]
    
    def get_progreso_porcentaje(self, obj):
        # Calcular progreso basado en lecciones completadas
        total_lecciones = sum(modulo.lecciones.count() for modulo in obj.curso.modulos.all())
        if total_lecciones == 0:
            return 0
        lecciones_completadas = obj.progreso_lecciones.filter(completada=True).count()
        return round((lecciones_completadas / total_lecciones) * 100, 2)


class InscripcionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de inscripciones"""
    
    estudiante_nombre = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = 'Inscripcion'
        fields = [
            'id', 'estudiante_nombre', 'curso_nombre', 'fecha_inscripcion',
            'estado', 'progreso_porcentaje', 'nota_final'
        ]
        read_only_fields = ['id', 'fecha_inscripcion']


# =====================================================
# MÓDULO 6: PROGRESO Y SEGUIMIENTO
# =====================================================

class ProgresoModuloSerializer(serializers.ModelSerializer):
    """Serializer para progreso en módulos"""
    
    modulo_titulo = serializers.CharField(source='modulo.titulo', read_only=True)
    porcentaje_completado = serializers.SerializerMethodField()
    
    class Meta:
        model = 'ProgresoModulo'
        fields = [
            'id', 'inscripcion', 'modulo', 'modulo_titulo',
            'fecha_inicio', 'fecha_completado', 'completado',
            'tiempo_dedicado_minutos', 'porcentaje_completado'
        ]
        read_only_fields = ['id', 'fecha_inicio', 'fecha_completado', 'porcentaje_completado']
    
    def get_porcentaje_completado(self, obj):
        total_lecciones = obj.modulo.lecciones.count()
        if total_lecciones == 0:
            return 0
        lecciones_completadas = obj.inscripcion.progreso_lecciones.filter(
            leccion__modulo=obj.modulo,
            completada=True
        ).count()
        return round((lecciones_completadas / total_lecciones) * 100, 2)


class ProgresoLeccionSerializer(serializers.ModelSerializer):
    """Serializer para progreso en lecciones"""
    
    leccion_titulo = serializers.CharField(source='leccion.titulo', read_only=True)
    
    class Meta:
        model = 'ProgresoLeccion'
        fields = [
            'id', 'inscripcion', 'leccion', 'leccion_titulo',
            'fecha_inicio', 'fecha_completado', 'completada',
            'tiempo_dedicado_minutos', 'veces_vista', 'ultima_posicion_video'
        ]
        read_only_fields = ['id', 'fecha_inicio', 'fecha_completado']


class ProgresoActividadSerializer(serializers.ModelSerializer):
    """Serializer para progreso en actividades"""
    
    actividad_titulo = serializers.CharField(source='actividad.titulo', read_only=True)
    
    class Meta:
        model = 'ProgresoActividad'
        fields = [
            'id', 'inscripcion', 'actividad', 'actividad_titulo',
            'fecha_inicio', 'fecha_completado', 'completada',
            'puntaje_obtenido', 'intentos', 'respuesta_usuario', 'retroalimentacion'
        ]
        read_only_fields = ['id', 'fecha_inicio', 'fecha_completado']


# =====================================================
# MÓDULO 7: EVALUACIONES Y CALIFICACIONES
# =====================================================

class EvaluacionSerializer(serializers.ModelSerializer):
    """Serializer para evaluaciones"""
    
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    modulo_titulo = serializers.CharField(source='modulo.titulo', read_only=True)
    total_preguntas = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Evaluacion'
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_evaluacion', 'curso',
            'curso_nombre', 'modulo', 'modulo_titulo', 'duracion_minutos',
            'puntaje_total', 'puntaje_aprobacion', 'total_preguntas',
            'numero_intentos_permitidos', 'orden_aleatorio', 'mostrar_resultados',
            'activa', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'total_preguntas']
    
    def get_total_preguntas(self, obj):
        return obj.preguntas.count()


class PreguntaEvaluacionSerializer(serializers.ModelSerializer):
    """Serializer para preguntas de evaluación"""
    
    class Meta:
        model = 'PreguntaEvaluacion'
        fields = [
            'id', 'evaluacion', 'texto_pregunta', 'tipo_pregunta',
            'opciones', 'respuesta_correcta', 'explicacion', 'puntaje',
            'orden', 'activa'
        ]
        read_only_fields = ['id']


class IntentoEvaluacionSerializer(serializers.ModelSerializer):
    """Serializer para intentos de evaluación"""
    
    estudiante_nombre = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    evaluacion_titulo = serializers.CharField(source='evaluacion.titulo', read_only=True)
    nota_calculada = serializers.SerializerMethodField()
    
    class Meta:
        model = 'IntentoEvaluacion'
        fields = [
            'id', 'evaluacion', 'evaluacion_titulo', 'estudiante',
            'estudiante_nombre', 'inscripcion', 'numero_intento',
            'fecha_inicio', 'fecha_finalizacion', 'puntaje_obtenido',
            'puntaje_total', 'nota_calculada', 'aprobado', 'respuestas',
            'tiempo_empleado_minutos', 'completado'
        ]
        read_only_fields = [
            'id', 'fecha_inicio', 'fecha_finalizacion', 'nota_calculada',
            'tiempo_empleado_minutos'
        ]
    
    def get_nota_calculada(self, obj):
        if obj.puntaje_total and obj.puntaje_total > 0:
            porcentaje = (obj.puntaje_obtenido / obj.puntaje_total) * 100
            if porcentaje < 60:
                nota = 1.0 + (porcentaje / 60) * 3.0
            else:
                nota = 4.0 + ((porcentaje - 60) / 40) * 3.0
            return round(nota, 2)
        return None


# =====================================================
# MÓDULO 8: ASISTENCIA Y SESIONES
# =====================================================

class SesionCursoSerializer(serializers.ModelSerializer):
    """Serializer para sesiones de curso"""
    
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    relator_nombre = serializers.CharField(source='relator.nombre_completo', read_only=True)
    total_asistentes = serializers.SerializerMethodField()
    porcentaje_asistencia = serializers.SerializerMethodField()
    
    class Meta:
        model = 'SesionCurso'
        fields = [
            'id', 'curso', 'curso_nombre', 'relator', 'relator_nombre',
            'numero_sesion', 'titulo', 'descripcion', 'fecha_programada',
            'hora_inicio', 'hora_fin', 'duracion_minutos', 'tipo_sesion',
            'ubicacion', 'link_videoconferencia', 'estado', 'material_sesion',
            'total_asistentes', 'porcentaje_asistencia', 'notas_sesion'
        ]
        read_only_fields = ['id', 'total_asistentes', 'porcentaje_asistencia']
    
    def get_total_asistentes(self, obj):
        return obj.asistencias.filter(presente=True).count()
    
    def get_porcentaje_asistencia(self, obj):
        total_inscritos = obj.curso.inscripciones.filter(estado__in=['inscrito', 'en_curso']).count()
        if total_inscritos == 0:
            return 0
        asistentes = obj.asistencias.filter(presente=True).count()
        return round((asistentes / total_inscritos) * 100, 2)


class RegistroAsistenciaSerializer(serializers.ModelSerializer):
    """Serializer para registro de asistencia"""
    
    estudiante_nombre = serializers.CharField(source='inscripcion.estudiante.nombre_completo', read_only=True)
    sesion_titulo = serializers.CharField(source='sesion.titulo', read_only=True)
    
    class Meta:
        model = 'RegistroAsistencia'
        fields = [
            'id', 'sesion', 'sesion_titulo', 'inscripcion', 'estudiante_nombre',
            'presente', 'fecha_hora_registro', 'metodo_registro',
            'datos_biometricos', 'ip_registro', 'observaciones'
        ]
        read_only_fields = ['id', 'fecha_hora_registro']


# =====================================================
# MÓDULO 9: FOROS Y COMUNICACIÓN
# =====================================================

class ForoSerializer(serializers.ModelSerializer):
    """Serializer para foros de discusión"""
    
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    leccion_titulo = serializers.CharField(source='leccion.titulo', read_only=True)
    total_temas = serializers.SerializerMethodField()
    
    class Meta:
        model = 'Foro'
        fields = [
            'id', 'titulo', 'descripcion', 'curso', 'curso_nombre',
            'leccion', 'leccion_titulo', 'tipo_foro', 'moderado',
            'activo', 'total_temas', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'total_temas']
    
    def get_total_temas(self, obj):
        return obj.temas.count()


class TemaForoSerializer(serializers.ModelSerializer):
    """Serializer para temas de foro"""
    
    autor_nombre = serializers.CharField(source='autor.nombre_completo', read_only=True)
    foro_titulo = serializers.CharField(source='foro.titulo', read_only=True)
    total_respuestas = serializers.SerializerMethodField()
    
    class Meta:
        model = 'TemaForo'
        fields = [
            'id', 'foro', 'foro_titulo', 'titulo', 'autor', 'autor_nombre',
            'contenido', 'tipo_tema', 'etiquetas', 'fijado', 'cerrado',
            'total_respuestas', 'vistas', 'fecha_creacion', 'fecha_ultima_actividad'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_ultima_actividad', 'vistas', 'total_respuestas']
    
    def get_total_respuestas(self, obj):
        return obj.respuestas.count()


class RespuestaForoSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de foro"""
    
    autor_nombre = serializers.CharField(source='autor.nombre_completo', read_only=True)
    
    class Meta:
        model = 'RespuestaForo'
        fields = [
            'id', 'tema', 'autor', 'autor_nombre', 'contenido',
            'respuesta_a', 'marcada_correcta', 'likes', 'fecha_creacion',
            'fecha_edicion', 'editado'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_edicion', 'likes']


# =====================================================
# MÓDULO 10: NOTIFICACIONES Y MENSAJERÍA
# =====================================================

class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = 'Notificacion'
        fields = [
            'id', 'usuario', 'usuario_nombre', 'tipo', 'titulo', 'mensaje',
            'leida', 'fecha_lectura', 'link_accion', 'metadata',
            'fecha_creacion', 'fecha_expiracion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_lectura']


class MensajePrivadoSerializer(serializers.ModelSerializer):
    """Serializer para mensajes privados"""
    
    remitente_nombre = serializers.CharField(source='remitente.nombre_completo', read_only=True)
    destinatario_nombre = serializers.CharField(source='destinatario.nombre_completo', read_only=True)
    
    class Meta:
        model = 'MensajePrivado'
        fields = [
            'id', 'remitente', 'remitente_nombre', 'destinatario',
            'destinatario_nombre', 'asunto', 'contenido', 'leido',
            'fecha_lectura', 'fecha_envio', 'archivos_adjuntos'
        ]
        read_only_fields = ['id', 'fecha_envio', 'fecha_lectura']


# =====================================================
# MÓDULO 11: ENCUESTAS Y DIPLOMAS
# =====================================================

class PreguntaEncuestaSerializer(serializers.ModelSerializer):
    """Serializer para preguntas de encuesta"""
    
    class Meta:
        model = 'PreguntaEncuesta'
        fields = [
            'id', 'texto_pregunta', 'tipo_pregunta', 'opciones',
            'categoria', 'orden', 'obligatoria', 'activa'
        ]
        read_only_fields = ['id']


class RespuestaEncuestaSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de encuesta"""
    
    estudiante_nombre = serializers.CharField(source='inscripcion.estudiante.nombre_completo', read_only=True)
    curso_nombre = serializers.CharField(source='inscripcion.curso.nombre', read_only=True)
    
    class Meta:
        model = 'RespuestaEncuesta'
        fields = [
            'id', 'inscripcion', 'estudiante_nombre', 'curso_nombre',
            'respuestas', 'calificacion_general', 'comentarios_adicionales',
            'fecha_completada'
        ]
        read_only_fields = ['id', 'fecha_completada']


class PlantillaDiplomaSerializer(serializers.ModelSerializer):
    """Serializer para plantillas de diploma"""
    
    class Meta:
        model = 'PlantillaDiploma'
        fields = [
            'id', 'nombre', 'descripcion', 'archivo_plantilla_url',
            'variables_disponibles', 'estilo_css', 'predeterminada',
            'activa', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DiplomaSerializer(serializers.ModelSerializer):
    """Serializer para diplomas"""
    
    estudiante_nombre = serializers.CharField(source='inscripcion.estudiante.nombre_completo', read_only=True)
    curso_nombre = serializers.CharField(source='inscripcion.curso.nombre', read_only=True)
    plantilla_nombre = serializers.CharField(source='plantilla.nombre', read_only=True)
    
    class Meta:
        model = 'Diploma'
        fields = [
            'id', 'inscripcion', 'estudiante_nombre', 'curso_nombre',
            'codigo_unico', 'plantilla', 'plantilla_nombre',
            'datos_diploma', 'archivo_generado_url', 'fecha_emision',
            'emitido_por', 'verificado', 'fecha_verificacion'
        ]
        read_only_fields = [
            'id', 'codigo_unico', 'fecha_emision', 'fecha_verificacion'
        ]


# =====================================================
# MÓDULO 12: REPORTES Y MÉTRICAS
# =====================================================

class MetricaHistoricaSerializer(serializers.ModelSerializer):
    """Serializer para métricas históricas"""
    
    estudiante_nombre = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = 'MetricaHistorica'
        fields = [
            'id', 'tipo', 'estudiante', 'estudiante_nombre',
            'curso', 'curso_nombre', 'relator', 'datos',
            'snapshot_fecha', 'periodo'
        ]
        read_only_fields = ['id', 'snapshot_fecha']


# =====================================================
# MÓDULO 13: AUDITORÍA
# =====================================================

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoría"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = 'AuditLog'
        fields = [
            'id', 'usuario', 'usuario_nombre', 'accion', 'entidad_tipo',
            'entidad_id', 'descripcion', 'datos_anteriores', 'datos_nuevos',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =====================================================
# SERIALIZERS ESPECIALIZADOS
# =====================================================

class DashboardEstudianteSerializer(serializers.Serializer):
    """Serializer para dashboard del estudiante"""
    
    cursos_activos = InscripcionListSerializer(many=True)
    progreso_general = serializers.DecimalField(max_digits=5, decimal_places=2)
    proximas_sesiones = SesionCursoSerializer(many=True)
    evaluaciones_pendientes = EvaluacionSerializer(many=True)
    notificaciones_recientes = NotificacionSerializer(many=True)
    logros = serializers.JSONField()


class DashboardRelatorSerializer(serializers.Serializer):
    """Serializer para dashboard del relator"""
    
    cursos_activos = CursoListSerializer(many=True)
    materiales_pendientes = MaterialListSerializer(many=True)
    proximas_sesiones = SesionCursoSerializer(many=True)
    estadisticas = serializers.JSONField()
    calificacion_promedio = serializers.DecimalField(max_digits=3, decimal_places=2)


class DashboardAdministradorSerializer(serializers.Serializer):
    """Serializer para dashboard del administrador"""
    
    total_estudiantes_activos = serializers.IntegerField()
    total_cursos_activos = serializers.IntegerField()
    total_relatores = serializers.IntegerField()
    materiales_pendientes_revision = serializers.IntegerField()
    inscripciones_recientes = InscripcionListSerializer(many=True)
    metricas_plataforma = serializers.JSONField()
    alertas_sistema = serializers.JSONField()


class ReporteProgresoEstudianteSerializer(serializers.Serializer):
    """Serializer para reporte de progreso de estudiante"""
    
    estudiante = UsuarioListSerializer()
    curso = CursoListSerializer()
    inscripcion = InscripcionSerializer()
    progreso_modulos = ProgresoModuloSerializer(many=True)
    evaluaciones_realizadas = IntentoEvaluacionSerializer(many=True)
    asistencias = RegistroAsistenciaSerializer(many=True)
    tiempo_total_dedicado = serializers.IntegerField()
    nota_promedio = serializers.DecimalField(max_digits=3, decimal_places=2)


class EstadisticasCursoSerializer(serializers.Serializer):
    """Serializer para estadísticas de curso"""
    
    curso = CursoSerializer()
    total_inscritos = serializers.IntegerField()
    total_activos = serializers.IntegerField()
    total_completados = serializers.IntegerField()
    total_abandonos = serializers.IntegerField()
    tasa_aprobacion = serializers.DecimalField(max_digits=5, decimal_places=2)
    nota_promedio = serializers.DecimalField(max_digits=3, decimal_places=2)
    asistencia_promedio = serializers.DecimalField(max_digits=5, decimal_places=2)
    tiempo_promedio_completacion = serializers.IntegerField()
    satisfaccion_promedio = serializers.DecimalField(max_digits=3, decimal_places=2)


# =====================================================
# SERIALIZERS PARA INTEGRACIÓN SENCE
# =====================================================

class InscripcionSenceSerializer(serializers.Serializer):
    """Serializer para sincronización de inscripción con SENCE"""
    
    run_alumno = serializers.CharField(max_length=12)
    codigo_sence = serializers.CharField(max_length=10)
    fecha_inicio = serializers.DateField()
    fecha_termino = serializers.DateField()
    tipo_modalidad = serializers.CharField(max_length=50)
    estado_capacitacion = serializers.CharField(max_length=50)


class AsistenciaSenceSerializer(serializers.Serializer):
    """Serializer para sincronización de asistencia con SENCE"""
    
    run_alumno = serializers.CharField(max_length=12)
    codigo_sence = serializers.CharField(max_length=10)
    fecha_sesion = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_termino = serializers.TimeField()
    asistio = serializers.BooleanField()
    tipo_registro = serializers.CharField(max_length=50)


class CertificacionSenceSerializer(serializers.Serializer):
    """Serializer para sincronización de certificación con SENCE"""
    
    run_alumno = serializers.CharField(max_length=12)
    codigo_sence = serializers.CharField(max_length=10)
    fecha_certificacion = serializers.DateField()
    nota_final = serializers.DecimalField(max_digits=3, decimal_places=2)
    asistencia_porcentaje = serializers.DecimalField(max_digits=5, decimal_places=2)
    aprobado = serializers.BooleanField()
    observaciones = serializers.CharField(max_length=500, required=False)


# =====================================================
# FIN DE SERIALIZERS
# =====================================================