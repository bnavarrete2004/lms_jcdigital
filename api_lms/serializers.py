# serializers.py
# Serializers para LMS JC Digital Training
# Basado en models.py real del proyecto

from rest_framework import serializers
from django.contrib.auth.models import User
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


# =====================================================
# SERIALIZERS MÓDULO 1: USUARIOS
# =====================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    rut_completo = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'ultima_actualizacion']
    
    def get_rut_completo(self, obj):
        return obj.get_rut()
    
    def get_nombre_completo(self, obj):
        return obj.nombre_completo()


class PerfilRelatorSerializer(serializers.ModelSerializer):
    usuario_data = UsuarioSerializer(source='usuario', read_only=True)
    
    class Meta:
        model = PerfilRelator
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_cursos_dictados', 
                           'total_estudiantes_capacitados', 'calificacion_promedio']


class ConfiguracionUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionUsuario
        fields = '__all__'
        read_only_fields = ['updated_at']


# =====================================================
# SERIALIZERS MÓDULO 2: CÓDIGOS SENCE
# =====================================================

class CodigoSenceSerializer(serializers.ModelSerializer):
    horas_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = CodigoSence
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_horas_disponibles(self, obj):
        return obj.horas_disponibles


# =====================================================
# SERIALIZERS MÓDULO 3: CURSOS
# =====================================================

class CursoRelatorSerializer(serializers.ModelSerializer):
    relator_nombre = serializers.SerializerMethodField()
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = CursoRelator
        fields = '__all__'
        read_only_fields = ['fecha_asignacion', 'fecha_desasignacion']
    
    def get_relator_nombre(self, obj):
        return obj.relator.nombre_completo()


class ModuloSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = Modulo
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LeccionSerializer(serializers.ModelSerializer):
    modulo_nombre = serializers.CharField(source='modulo.nombre', read_only=True)
    
    class Meta:
        model = Leccion
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CursoSerializer(serializers.ModelSerializer):
    codigo_sence_data = CodigoSenceSerializer(source='codigo_sence', read_only=True)
    modulos = ModuloSerializer(many=True, read_only=True)
    relatores = serializers.SerializerMethodField()
    total_inscritos = serializers.SerializerMethodField()
    cupos_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Curso
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_relatores(self, obj):
        asignaciones = obj.asignaciones_relator.filter(activo=True)
        return CursoRelatorSerializer(asignaciones, many=True).data
    
    def get_total_inscritos(self, obj):
        return obj.total_inscritos
    
    def get_cupos_disponibles(self, obj):
        return obj.cupos_disponibles


# =====================================================
# SERIALIZERS MÓDULO 4: MATERIALES
# =====================================================

class MaterialSerializer(serializers.ModelSerializer):
    #subido_por_nombre = serializers.SerializerMethodField()
    #relator_autor_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_usos']
    
    #def get_subido_por_nombre(self, obj):
        #return obj.subido_por.nombre_completo() if obj.subido_por else None
    
    #def get_relator_autor_nombre(self, obj):
        #return obj.relator_autor.nombre_completo() if obj.relator_autor else None


class LeccionMaterialSerializer(serializers.ModelSerializer):
    leccion_nombre = serializers.CharField(source='leccion.nombre', read_only=True)
    material_data = MaterialSerializer(source='material', read_only=True)
    
    class Meta:
        model = LeccionMaterial
        fields = '__all__'
        read_only_fields = ['asignado_at']


# =====================================================
# SERIALIZERS MÓDULO 5: INSCRIPCIONES
# =====================================================

class InscripcionSerializer(serializers.ModelSerializer):
    estudiante_data = UsuarioSerializer(source='estudiante', read_only=True)
    curso_data = CursoSerializer(source='curso', read_only=True)
    puede_generar_diploma = serializers.SerializerMethodField()
    
    class Meta:
        model = Inscripcion
        fields = '__all__'
        read_only_fields = ['fecha_inscripcion', 'updated_at']
    
    def get_puede_generar_diploma(self, obj):
        return obj.puede_generar_diploma


class ProgresoModuloSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    modulo_data = ModuloSerializer(source='modulo', read_only=True)
    
    class Meta:
        model = ProgresoModulo
        fields = '__all__'
        read_only_fields = ['updated_at']
    
    def get_estudiante_nombre(self, obj):
        return obj.inscripcion.estudiante.nombre_completo()


class ProgresoLeccionSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    leccion_data = LeccionSerializer(source='leccion', read_only=True)
    
    class Meta:
        model = ProgresoLeccion
        fields = '__all__'
        read_only_fields = ['updated_at']
    
    def get_estudiante_nombre(self, obj):
        return obj.inscripcion.estudiante.nombre_completo()


class ActividadEstudianteSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = ActividadEstudiante
        fields = '__all__'
    
    def get_estudiante_nombre(self, obj):
        return obj.inscripcion.estudiante.nombre_completo()


# =====================================================
# SERIALIZERS MÓDULO 6: EVALUACIONES
# =====================================================

class PreguntaSerializer(serializers.ModelSerializer):
    evaluacion_nombre = serializers.CharField(source='evaluacion.nombre', read_only=True)
    
    class Meta:
        model = Pregunta
        fields = '__all__'
        read_only_fields = ['created_at']


class EvaluacionSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)
    curso_nombre = serializers.SerializerMethodField()
    modulo_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluacion
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_curso_nombre(self, obj):
        return obj.curso.nombre if obj.curso else None
    
    def get_modulo_nombre(self, obj):
        return obj.modulo.nombre if obj.modulo else None


class RespuestaEstudianteSerializer(serializers.ModelSerializer):
    pregunta_data = PreguntaSerializer(source='pregunta', read_only=True)
    
    class Meta:
        model = RespuestaEstudiante
        fields = '__all__'
        read_only_fields = ['respondida_at']


class IntentoEvaluacionSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    evaluacion_nombre = serializers.CharField(source='evaluacion.nombre', read_only=True)
    respuestas = RespuestaEstudianteSerializer(many=True, read_only=True)
    
    class Meta:
        model = IntentoEvaluacion
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_fin']
    
    def get_estudiante_nombre(self, obj):
        return obj.estudiante.nombre_completo()


class SolicitudTercerIntentoSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    evaluacion_nombre = serializers.CharField(source='evaluacion.nombre', read_only=True)
    revisado_por_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudTercerIntento
        fields = '__all__'
        read_only_fields = ['solicitado_at', 'fecha_revision']
    
    def get_estudiante_nombre(self, obj):
        return obj.estudiante.nombre_completo()
    
    def get_revisado_por_nombre(self, obj):
        return obj.revisado_por.nombre_completo() if obj.revisado_por else None


# =====================================================
# SERIALIZERS MÓDULO 7: INTEGRACIÓN SENCE
# =====================================================

class SesionSenceSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = SesionSence
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_estudiante_nombre(self, obj):
        return obj.estudiante.nombre_completo()


class LogEnvioSenceSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    enviado_por_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = LogEnvioSence
        fields = '__all__'
        read_only_fields = ['fecha_envio']
    
    def get_enviado_por_nombre(self, obj):
        return obj.enviado_por.nombre_completo() if obj.enviado_por else None


# =====================================================
# SERIALIZERS MÓDULO 8: FORO
# =====================================================

class ForoRespuestaSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = ForoRespuesta
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_autor_nombre(self, obj):
        return obj.autor.nombre_completo()


class ForoConsultaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    leccion_nombre = serializers.CharField(source='leccion.nombre', read_only=True)
    respuestas = ForoRespuestaSerializer(many=True, read_only=True)
    total_respuestas = serializers.SerializerMethodField()
    
    class Meta:
        model = ForoConsulta
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_estudiante_nombre(self, obj):
        return obj.estudiante.nombre_completo()
    
    def get_total_respuestas(self, obj):
        return obj.total_respuestas


# =====================================================
# SERIALIZERS MÓDULO 9: NOTIFICACIONES
# =====================================================

class NotificacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre_completo()


# =====================================================
# SERIALIZERS MÓDULO 10: ENCUESTAS
# =====================================================

class EncuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encuesta
        fields = '__all__'
        read_only_fields = ['created_at']


class RespuestaEncuestaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    encuesta_nombre = serializers.CharField(source='encuesta.nombre', read_only=True)
    
    class Meta:
        model = RespuestaEncuesta
        fields = '__all__'
        read_only_fields = ['completada_at']
    
    def get_estudiante_nombre(self, obj):
        return obj.estudiante.nombre_completo()


# =====================================================
# SERIALIZERS MÓDULO 11: DIPLOMAS
# =====================================================

class PlantillaDiplomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantillaDiploma
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# =====================================================
# SERIALIZERS MÓDULO 12: MÉTRICAS
# =====================================================

class MetricaHistoricaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    curso_nombre = serializers.SerializerMethodField()
    relator_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = MetricaHistorica
        fields = '__all__'
    
    def get_estudiante_nombre(self, obj):
        return obj.estudiante.nombre_completo() if obj.estudiante else None
    
    def get_curso_nombre(self, obj):
        return obj.curso.nombre if obj.curso else None
    
    def get_relator_nombre(self, obj):
        return obj.relator.nombre_completo() if obj.relator else None


# =====================================================
# SERIALIZERS MÓDULO 13: AUDITORÍA
# =====================================================

class AuditLogSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre_completo() if obj.usuario else 'Sistema'
    
# ==========================================
# NOTIFICACIONES Y DIPLOMAS
# ==========================================

from api_lms.models import Notificacion, PlantillaDiploma

class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'url_accion', 'leida', 'fecha_leida', 'prioridad',
            'prioridad_display', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'fecha_leida']


class PlantillaDiplomaSerializer(serializers.ModelSerializer):
    """Serializer para plantillas de diplomas"""
    
    class Meta:
        model = PlantillaDiploma
        fields = [
            'id', 'nombre', 'descripcion', 'plantilla_html',
            'variables_disponibles', 'firma_director_url',
            'firma_relator_incluida', 'activa', 'predeterminada',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']