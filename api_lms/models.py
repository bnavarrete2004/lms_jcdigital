# models.py
# Modelos Django para LMS JC Digital Training
# Compatible con Django 5.0+ y PostgreSQL 14+

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


# =====================================================
# MÓDULO 1: USUARIOS Y AUTENTICACIÓN
# =====================================================

class Usuario(models.Model):
    """Información extendida de usuarios del sistema"""
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no especificar'),
    ]
    
    TIPO_USUARIO_CHOICES = [
        ('administrador', 'Administrador'),
        ('relator', 'Relator'),
        ('estudiante', 'Estudiante'),
    ]
    
    # Relación con User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Datos personales
    rut_numero = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99999999)]
    )
    rut_dv = models.CharField(max_length=1)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True)
    
    # Contacto
    telefono = models.CharField(max_length=20, blank=True)
    telefono_emergencia = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Académico/Profesional
    nivel_educacional = models.CharField(max_length=50, blank=True)
    profesion = models.CharField(max_length=100, blank=True)
    empresa_actual = models.CharField(max_length=200, blank=True)
    cargo_actual = models.CharField(max_length=100, blank=True)
    
    # Tipo de usuario
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)
    
    # Avatar
    avatar_url = models.URLField(max_length=500, blank=True)
    
    # Metadata
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuarios'
        unique_together = [('rut_numero', 'rut_dv')]
        indexes = [
            models.Index(fields=['tipo_usuario']),
            models.Index(fields=['rut_numero', 'rut_dv']),
            models.Index(fields=['activo']),
        ]
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} ({self.get_rut()})"
    
    def get_rut(self):
        """Retorna RUT formateado"""
        return f"{self.rut_numero}-{self.rut_dv}"
    
    def nombre_completo(self):
        """Retorna nombre completo"""
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"


class PerfilRelator(models.Model):
    """Información adicional para usuarios tipo relator"""
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_relator')
    
    # Especialización
    especialidad = models.CharField(max_length=100, blank=True)
    areas_experiencia = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    
    # Certificaciones (almacenadas como JSON)
    certificaciones = models.JSONField(default=dict, blank=True)
    
    # Experiencia
    anos_experiencia = models.IntegerField(null=True, blank=True)
    cv_url = models.URLField(max_length=500, blank=True)
    
    # Calificación y estadísticas
    calificacion_promedio = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(7)]
    )
    total_cursos_dictados = models.IntegerField(default=0)
    total_estudiantes_capacitados = models.IntegerField(default=0)
    
    # Estado
    verificado = models.BooleanField(default=False)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'perfil_relator'
        verbose_name = 'Perfil de Relator'
        verbose_name_plural = 'Perfiles de Relatores'
    
    def __str__(self):
        return f"Perfil Relator: {self.usuario.nombre_completo()}"


class ConfiguracionUsuario(models.Model):
    """Preferencias y configuración personalizada de cada usuario"""
    
    TEMA_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
        ('auto', 'Automático'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='configuracion')
    
    # Preferencias de notificaciones
    notif_email = models.BooleanField(default=True)
    notif_push = models.BooleanField(default=True)
    notif_sms = models.BooleanField(default=False)
    
    # Preferencias de interfaz
    tema = models.CharField(max_length=20, choices=TEMA_CHOICES, default='light')
    idioma = models.CharField(max_length=5, default='es')
    zona_horaria = models.CharField(max_length=50, default='America/Santiago')
    
    # Preferencias de privacidad
    perfil_publico = models.BooleanField(default=False)
    mostrar_progreso = models.BooleanField(default=True)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'configuracion_usuario'
        verbose_name = 'Configuración de Usuario'
        verbose_name_plural = 'Configuraciones de Usuarios'
    
    def __str__(self):
        return f"Config: {self.usuario.nombre_completo()}"


# =====================================================
# MÓDULO 2: CÓDIGOS Y CATÁLOGOS SENCE
# =====================================================

class CodigoSence(models.Model):
    """Catálogo de códigos SENCE válidos y sus características"""
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('caducado', 'Caducado'),
        ('suspendido', 'Suspendido'),
    ]
    
    LINEA_CHOICES = [
        (1, 'Programas Sociales'),
        (3, 'Franquicia Tributaria'),
    ]
    
    # Código SENCE
    codigo = models.CharField(max_length=10, unique=True)
    nombre_curso = models.CharField(max_length=300)
    
    # Horas y duración
    horas_totales = models.IntegerField(validators=[MinValueValidator(1)])
    horas_asignadas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Vigencia
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    # Clasificación
    area_tematica = models.CharField(max_length=100, blank=True)
    nivel = models.CharField(max_length=50, blank=True)
    modalidad = models.CharField(max_length=50, blank=True)
    
    # Línea de capacitación
    linea_capacitacion = models.IntegerField(choices=LINEA_CHOICES, default=3)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'codigos_sence'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['estado']),
            models.Index(fields=['area_tematica']),
        ]
        verbose_name = 'Código SENCE'
        verbose_name_plural = 'Códigos SENCE'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre_curso}"
    
    @property
    def horas_disponibles(self):
        """Calcula horas disponibles"""
        return self.horas_totales - self.horas_asignadas
    
    def puede_asignar_horas(self, horas):
        """Verifica si se pueden asignar las horas solicitadas"""
        return self.horas_disponibles >= horas


# =====================================================
# MÓDULO 3: CURSOS Y ESTRUCTURA ACADÉMICA
# =====================================================

class Curso(models.Model):
    """Cursos de capacitación ofrecidos por JC Digital Training"""
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('archivado', 'Archivado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    objetivos = models.TextField(blank=True)
    requisitos = models.TextField(blank=True)
    
    # Código SENCE
    codigo_sence = models.ForeignKey(
        CodigoSence, 
        on_delete=models.RESTRICT, 
        related_name='cursos',
        null=True,
        blank=True
    )
    codigo_sence_curso = models.CharField(max_length=50, unique=True)
    
    # Duración y horas
    horas_totales = models.IntegerField(validators=[MinValueValidator(1)])
    duracion_semanas = models.IntegerField(null=True, blank=True)
    
    # Fechas
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    publicado = models.BooleanField(default=False)
    
    # Configuración académica
    nota_aprobacion = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=4.00,
        validators=[MinValueValidator(1.0), MaxValueValidator(7.0)]
    )
    porcentaje_asistencia_minimo = models.IntegerField(
        default=75,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Cupos
    cupo_maximo = models.IntegerField(null=True, blank=True)
    cupo_minimo = models.IntegerField(null=True, blank=True)
    
    # Imagen y multimedia
    imagen_portada = models.URLField(max_length=500, blank=True)
    video_presentacion = models.URLField(max_length=500, blank=True)
    
    # Metadata
    creado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='cursos_creados'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cursos'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['codigo_sence']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
            models.Index(fields=['publicado']),
        ]
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_inscritos(self):
        """Retorna total de estudiantes inscritos"""
        return self.inscripciones.count()
    
    @property
    def cupos_disponibles(self):
        """Retorna cupos disponibles"""
        if self.cupo_maximo:
            return self.cupo_maximo - self.total_inscritos
        return None


# MODELO SIMPLIFICADO - CursoRelator
# Reemplazar en models.py

class CursoRelator(models.Model):
    """Asignación de relatores a cursos (relación muchos a muchos)"""
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='asignaciones_relator')
    relator = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cursos_asignados')
    
    # Información adicional de la asignación
    especialidad = models.CharField(max_length=100, blank=True, help_text="Área de especialidad del relator en este curso")
    
    # Estado
    activo = models.BooleanField(default=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_desasignacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'curso_relator'
        unique_together = [('curso', 'relator')]
        indexes = [
            models.Index(fields=['curso']),
            models.Index(fields=['relator']),
            models.Index(fields=['activo']),
        ]
        verbose_name = 'Asignación Curso-Relator'
        verbose_name_plural = 'Asignaciones Curso-Relator'
    
    def __str__(self):
        return f"{self.relator.nombre_completo()} - {self.curso.nombre}"


class Modulo(models.Model):
    """Módulos que componen un curso"""
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    
    # Información básica
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    objetivos = models.TextField(blank=True)
    
    # Orden y estructura
    orden = models.IntegerField()
    codigo_modulo = models.CharField(max_length=50, blank=True)
    
    # Duración
    horas_estimadas = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Estado
    publicado = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modulos'
        unique_together = [('curso', 'orden')]
        ordering = ['orden']
        indexes = [
            models.Index(fields=['curso']),
            models.Index(fields=['curso', 'orden']),
        ]
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
    
    def __str__(self):
        return f"{self.curso.nombre} - Módulo {self.orden}: {self.nombre}"


class Leccion(models.Model):
    """Lecciones individuales dentro de cada módulo"""
    
    TIPO_CHOICES = [
        ('teorica', 'Teórica'),
        ('practica', 'Práctica'),
        ('evaluacion', 'Evaluación'),
        ('mixta', 'Mixta'),
    ]
    
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='lecciones')
    
    # Información básica
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    objetivos = models.TextField(blank=True)
    
    # Orden
    orden = models.IntegerField()
    
    # Duración estimada
    duracion_minutos = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Tipo de lección
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='teorica')
    
    # Estado
    publicado = models.BooleanField(default=False)
    obligatoria = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lecciones'
        unique_together = [('modulo', 'orden')]
        ordering = ['orden']
        indexes = [
            models.Index(fields=['modulo']),
            models.Index(fields=['modulo', 'orden']),
        ]
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
    
    def __str__(self):
        return f"{self.modulo.nombre} - Lección {self.orden}: {self.nombre}"


# =====================================================
# MÓDULO 4: MATERIALES Y CONTENIDO
# =====================================================

class Material(models.Model):
    """Repositorio de materiales educativos"""
    
    TIPO_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('presentacion', 'Presentación'),
        ('documento', 'Documento'),
        ('imagen', 'Imagen'),
        ('enlace', 'Enlace'),
        ('scorm', 'SCORM'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cambios_solicitados', 'Cambios Solicitados'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Archivo
    archivo_url = models.URLField(max_length=500, blank=True)
    archivo_size = models.BigIntegerField(null=True, blank=True)
    archivo_hash = models.CharField(max_length=64, blank=True)
    
    # Metadata del archivo
    duracion_segundos = models.IntegerField(null=True, blank=True)
    total_paginas = models.IntegerField(null=True, blank=True)
    
    # Autoría
    subido_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='materiales_subidos'
    )
    relator_autor = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='materiales_creados'
    )
    
    # Estado de revisión
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    revisado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='materiales_revisados'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    comentarios_revision = models.TextField(blank=True)
    
    # Categorización
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    
    # Reutilización
    reutilizable = models.BooleanField(default=True)
    total_usos = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'materiales'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['estado']),
            models.Index(fields=['relator_autor']),
            models.Index(fields=['archivo_hash']),
        ]
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class LeccionMaterial(models.Model):
    """Asignación de materiales a lecciones"""
    
    PROPOSITO_CHOICES = [
        ('video_intro', 'Video de Introducción'),
        ('contenido_principal', 'Contenido Principal'),
        ('material_apoyo', 'Material de Apoyo'),
        ('evaluacion', 'Evaluación'),
    ]
    
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='materiales_asignados')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='lecciones_asignadas')
    
    # Orden de presentación en la lección
    orden = models.IntegerField()
    
    # Tipo de uso en la lección
    proposito = models.CharField(max_length=50, choices=PROPOSITO_CHOICES, blank=True)
    
    # Obligatoriedad
    obligatorio = models.BooleanField(default=True)
    
    # Metadata
    asignado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'leccion_material'
        unique_together = [('leccion', 'orden')]
        ordering = ['orden']
        indexes = [
            models.Index(fields=['leccion']),
            models.Index(fields=['material']),
        ]
        verbose_name = 'Material de Lección'
        verbose_name_plural = 'Materiales de Lecciones'
    
    def __str__(self):
        return f"{self.leccion.nombre} - {self.material.nombre}"


# =====================================================
# CONTINÚA EN PARTE 2...
# =====================================================

# =====================================================
# MÓDULO 5: INSCRIPCIONES Y PROGRESO
# =====================================================

class Inscripcion(models.Model):
    """Registro de estudiantes inscritos en cursos"""
    
    ESTADO_CHOICES = [
        ('inscrito', 'Inscrito'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('pendiente_revision', 'Pendiente de Revisión'),  # ← Solo debe aparecer UNA vez
        ('aprobado', 'Aprobado'),
        ('reprobado', 'Reprobado'),
        ('retirado', 'Retirado'),
        ('suspendido', 'Suspendido'),
    ]
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mis_inscripciones')
    
    # Fechas
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    fecha_inicio_real = models.DateTimeField(null=True, blank=True)
    fecha_fin_real = models.DateTimeField(null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='inscrito')
    
    # Notas y progreso
    nota_final = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(7.0)],
        help_text="Nota final oficial del curso (asignada por admin)"
    )

    # ========== NUEVOS CAMPOS - SISTEMA DE CALIFICACIÓN AUTOMÁTICA ==========
    nota_final_calculada = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(7.0)],
        help_text="Nota calculada automáticamente por el sistema (promedio ponderado)"
    )
    
    cumple_requisitos_aprobacion = models.BooleanField(
        default=False,
        help_text="True si cumple: nota >= 4.0 Y asistencia >= 75%"
    )
    # ========================================================================

    porcentaje_avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    porcentaje_asistencia = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Tiempo total de estudio (en minutos)
    tiempo_total_minutos = models.IntegerField(default=0)

    # ========== NUEVOS CAMPOS - APROBACIÓN MANUAL ==========
    aprobacion_manual = models.BooleanField(
        default=False,
        help_text="True si el admin aprobó/reprobó manualmente (decisión excepcional)"
    )
    
    justificacion_aprobacion = models.TextField(
        blank=True,
        help_text="Justificación del admin para aprobar/reprobar (obligatoria en decisiones excepcionales)"
    )
    
    revisado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscripciones_revisadas',
        help_text="Administrador que revisó y aprobó/reprobó la inscripción"
    )
    
    fecha_revision = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que el admin revisó la inscripción"
    )
    # ========================================================
    
    # Encuesta de satisfacción
    encuesta_completada = models.BooleanField(default=False)
    fecha_encuesta_completada = models.DateTimeField(null=True, blank=True)
    
    # Diploma
    diploma_generado = models.BooleanField(default=False)
    diploma_url = models.URLField(max_length=500, blank=True)
    diploma_codigo_validacion = models.CharField(max_length=20, blank=True)
    fecha_diploma = models.DateTimeField(null=True, blank=True)
    
    # ← ❌ BORRAR ESTAS LÍNEAS (duplicados sin help_text)
    # nota_final_calculada = models.DecimalField(...)
    # cumple_requisitos_aprobacion = models.BooleanField(...)
    # aprobacion_manual = models.BooleanField(...)
    # justificacion_aprobacion = models.TextField(...)
    # revisado_por = models.ForeignKey(...)
    # fecha_revision = models.DateTimeField(...)
        
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inscripciones'
        unique_together = [('curso', 'estudiante')]
        indexes = [
            models.Index(fields=['curso']),
            models.Index(fields=['estudiante']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_inscripcion']),
            models.Index(fields=['diploma_codigo_validacion']),
            models.Index(fields=['cumple_requisitos_aprobacion']),  # ← AGREGAR
            models.Index(fields=['revisado_por']),  # ← AGREGAR
        ]
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
    
    def __str__(self):
        return f"{self.estudiante.nombre_completo()} - {self.curso.nombre}"
    
    @property
    def puede_generar_diploma(self):
        """Verifica si el estudiante puede obtener su diploma"""
        return (
            self.estado == 'aprobado' and 
            self.encuesta_completada and 
            not self.diploma_generado
        )

class ProgresoModulo(models.Model):
    """Progreso de estudiantes por módulo"""
    
    ESTADO_SENCE_CHOICES = [
        (1, 'En curso'),
        (2, 'Completado'),
    ]
    
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='progreso_modulos')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='progresos')
    
    # Progreso
    porcentaje_avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completado = models.BooleanField(default=False)
    
    # Tiempo
    tiempo_total_minutos = models.IntegerField(default=0)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    # Calificación
    nota_modulo = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Estado SENCE
    estado_sence = models.IntegerField(choices=ESTADO_SENCE_CHOICES, default=1)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'progreso_modulo'
        unique_together = [('inscripcion', 'modulo')]
        indexes = [
            models.Index(fields=['inscripcion']),
            models.Index(fields=['modulo']),
        ]
        verbose_name = 'Progreso de Módulo'
        verbose_name_plural = 'Progresos de Módulos'
    
    def __str__(self):
        return f"{self.inscripcion.estudiante.nombre_completo()} - {self.modulo.nombre}: {self.porcentaje_avance}%"


class ProgresoLeccion(models.Model):
    """Progreso detallado de estudiantes por lección"""
    
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='progreso_lecciones')
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='progresos')
    
    # Progreso
    completada = models.BooleanField(default=False)
    porcentaje_avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Tiempo
    tiempo_total_minutos = models.IntegerField(default=0)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    # Actividad
    ultima_actividad = models.DateTimeField(null=True, blank=True)
    total_visitas = models.IntegerField(default=0)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'progreso_leccion'
        unique_together = [('inscripcion', 'leccion')]
        indexes = [
            models.Index(fields=['inscripcion']),
            models.Index(fields=['leccion']),
        ]
        verbose_name = 'Progreso de Lección'
        verbose_name_plural = 'Progresos de Lecciones'
    
    def __str__(self):
        return f"{self.inscripcion.estudiante.nombre_completo()} - {self.leccion.nombre}"


class ActividadEstudiante(models.Model):
    """Log detallado de actividad de estudiantes"""
    
    TIPO_ACTIVIDAD_CHOICES = [
        ('inicio_leccion', 'Inicio de Lección'),
        ('fin_leccion', 'Fin de Lección'),
        ('reproduccion_video', 'Reproducción de Video'),
        ('descarga_material', 'Descarga de Material'),
        ('participacion_foro', 'Participación en Foro'),
        ('inicio_evaluacion', 'Inicio de Evaluación'),
        ('fin_evaluacion', 'Fin de Evaluación'),
    ]
    
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='actividades')
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Tipo de actividad
    tipo_actividad = models.CharField(max_length=50, choices=TIPO_ACTIVIDAD_CHOICES)
    
    # Tiempo
    timestamp_inicio = models.DateTimeField(default=timezone.now)
    timestamp_fin = models.DateTimeField(null=True, blank=True)
    duracion_segundos = models.IntegerField(null=True, blank=True)
    
    # Metadata adicional
    metadata = models.JSONField(default=dict, blank=True)
    
    # IP y dispositivo
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'actividad_estudiante'
        indexes = [
            models.Index(fields=['inscripcion']),
            models.Index(fields=['timestamp_inicio']),
            models.Index(fields=['tipo_actividad']),
        ]
        verbose_name = 'Actividad de Estudiante'
        verbose_name_plural = 'Actividades de Estudiantes'
    
    def __str__(self):
        return f"{self.inscripcion.estudiante.nombre_completo()} - {self.get_tipo_actividad_display()}"


# =====================================================
# MÓDULO 6: EVALUACIONES
# =====================================================

class Evaluacion(models.Model):
    """Evaluaciones diagnósticas, formativas y sumativas"""
    
    TIPO_CHOICES = [
        ('diagnostica', 'Diagnóstica'),
        ('formativa', 'Formativa'),
        ('sumativa', 'Sumativa'),
        ('final', 'Final'),
    ]
    
    # Asociación (puede ser a curso O a módulo)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True, related_name='evaluaciones')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, null=True, blank=True, related_name='evaluaciones')
    
    # Información básica
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    instrucciones = models.TextField(blank=True)
    
    # Tipo de evaluación
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Configuración
    tiempo_limite_minutos = models.IntegerField(default=80)
    intentos_permitidos = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )
    
    # Sistema de notas chileno
    nota_aprobacion = models.DecimalField(max_digits=3, decimal_places=2, default=4.00)
    porcentaje_aprobacion = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Porcentaje de exigencia para aprobar (típicamente 60%)"
    )
    nota_minima = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=1.0,
        help_text="Nota mínima de la escala (típicamente 1.0)"
    )
    nota_maxima = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=7.0,
        help_text="Nota máxima de la escala (típicamente 7.0)"
    )
    
    # Peso en nota final
    peso_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Peso de esta evaluación en la nota final del curso (%)"
    )
    
    # Requisitos
    requiere_seb = models.BooleanField(default=False)  # Safe Exam Browser
    orden = models.IntegerField(null=True, blank=True)
    
    # Fechas de disponibilidad
    disponible_desde = models.DateTimeField(null=True, blank=True)
    disponible_hasta = models.DateTimeField(null=True, blank=True)
    
    # Estado
    publicada = models.BooleanField(default=False)
    
    # Corrección
    correccion_automatica = models.BooleanField(default=True)
    requiere_validacion_relator = models.BooleanField(default=True)
    
    # Metadata
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluaciones'
        indexes = [
            models.Index(fields=['curso']),
            models.Index(fields=['modulo']),
            models.Index(fields=['tipo']),
        ]
        verbose_name = 'Evaluación'
        verbose_name_plural = 'Evaluaciones'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not (self.curso or self.modulo) or (self.curso and self.modulo):
            raise ValidationError('La evaluación debe estar asociada a un curso O a un módulo, no a ambos.')
    
    @property
    def puntaje_maximo(self):
        """Calcula el puntaje máximo sumando todas las preguntas"""
        return self.preguntas.aggregate(
            total=models.Sum('puntaje')
        )['total'] or 0


class Pregunta(models.Model):
    """Preguntas que componen cada evaluación"""
    
    TIPO_CHOICES = [
        ('seleccion_multiple', 'Selección Múltiple'),
        ('verdadero_falso', 'Verdadero/Falso'),
        ('completar', 'Completar'),
        ('desarrollo', 'Desarrollo'),
        ('matching', 'Emparejamiento'),
    ]
    
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='preguntas')
    
    # Contenido
    enunciado = models.TextField()
    imagen_url = models.URLField(max_length=500, blank=True)
    
    # Tipo de pregunta
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Opciones (para selección múltiple)
    opciones = models.JSONField(default=dict, blank=True)
    
    # Respuesta correcta (para otros tipos)
    respuesta_correcta = models.TextField(blank=True)
    
    # Puntaje
    puntaje = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    
    # Orden
    orden = models.IntegerField()
    
    # Feedback
    feedback_correcto = models.TextField(blank=True)
    feedback_incorrecto = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'preguntas'
        unique_together = [('evaluacion', 'orden')]
        ordering = ['orden']
        indexes = [
            models.Index(fields=['evaluacion']),
        ]
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
    
    def __str__(self):
        return f"Pregunta {self.orden}: {self.enunciado[:50]}..."


class IntentoEvaluacion(models.Model):
    """Registro de cada intento de evaluación por estudiante"""
    
    ESTADO_CHOICES = [
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('abandonado', 'Abandonado'),
        ('tiempo_excedido', 'Tiempo Excedido'),
    ]
    
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='intentos')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mis_intentos')
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='intentos_evaluacion')
    
    # Número de intento
    numero_intento = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Timestamps
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    # Duración
    duracion_minutos = models.IntegerField(null=True, blank=True)
    
    # Calificación
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    puntaje_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nota_obtenida = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    aprobado = models.BooleanField(null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_progreso')
    
    # Validación
    validado_automaticamente = models.BooleanField(default=False)
    validado_por_relator = models.BooleanField(default=False)
    validado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='intentos_validados')
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    comentarios_relator = models.TextField(blank=True)
    
    # Safe Exam Browser
    seb_detectado = models.BooleanField(default=False)
    seb_config_hash = models.CharField(max_length=64, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'intentos_evaluacion'
        unique_together = [('evaluacion', 'estudiante', 'numero_intento')]
        indexes = [
            models.Index(fields=['evaluacion']),
            models.Index(fields=['estudiante']),
            models.Index(fields=['inscripcion']),
            models.Index(fields=['estado']),
        ]
        verbose_name = 'Intento de Evaluación'
        verbose_name_plural = 'Intentos de Evaluaciones'
    
    def __str__(self):
        return f"{self.estudiante.nombre_completo()} - {self.evaluacion.nombre} (Intento {self.numero_intento})"


class RespuestaEstudiante(models.Model):
    """Respuestas dadas por estudiantes en cada intento"""
    
    intento = models.ForeignKey(IntentoEvaluacion, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas_dadas')
    
    # Respuesta
    respuesta_texto = models.TextField(blank=True)
    respuesta_seleccionada = models.IntegerField(null=True, blank=True)
    respuestas_multiples = ArrayField(models.IntegerField(), default=list, blank=True)
    
    # Evaluación
    correcta = models.BooleanField(null=True, blank=True)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Timestamp
    respondida_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuestas_estudiante'
        unique_together = [('intento', 'pregunta')]
        indexes = [
            models.Index(fields=['intento']),
            models.Index(fields=['pregunta']),
        ]
        verbose_name = 'Respuesta de Estudiante'
        verbose_name_plural = 'Respuestas de Estudiantes'
    
    def __str__(self):
        return f"Respuesta a: {self.pregunta.enunciado[:50]}..."


class SolicitudTercerIntento(models.Model):
    """Solicitudes de estudiantes para obtener un tercer intento en evaluaciones"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='solicitudes_tercer_intento')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_tercer_intento')
    
    # Justificación
    justificacion = models.TextField()
    documentos_adjuntos = ArrayField(models.URLField(), default=list, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Revisión
    revisado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_revisadas')
    fecha_revision = models.DateTimeField(null=True, blank=True)
    comentarios_revision = models.TextField(blank=True)
    
    # Metadata
    solicitado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'solicitudes_tercer_intento'
        indexes = [
            models.Index(fields=['evaluacion']),
            models.Index(fields=['estudiante']),
            models.Index(fields=['estado']),
        ]
        verbose_name = 'Solicitud de Tercer Intento'
        verbose_name_plural = 'Solicitudes de Tercer Intento'
    
    def __str__(self):
        return f"{self.estudiante.nombre_completo()} - {self.evaluacion.nombre}"


# =====================================================
# MÓDULO 7: INTEGRACIÓN SENCE
# =====================================================

class SesionSence(models.Model):
    """Registro de sesiones de estudio validadas por SENCE con ClaveÚnica"""
    
    ESTADO_CHOICES = [
        ('iniciando', 'Iniciando'),
        ('activa', 'Activa'),
        ('cerrando', 'Cerrando'),
        ('cerrada', 'Cerrada'),
        ('error', 'Error'),
    ]
    
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='sesiones_sence')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones_sence')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='sesiones_sence')
    
    # Identificadores de sesión
    id_sesion_otec = models.CharField(max_length=149, unique=True)
    id_sesion_sence = models.CharField(max_length=149, blank=True)
    
    # Timestamps
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    # Duración calculada
    duracion_minutos = models.IntegerField(null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='iniciando')
    
    # Zonas horarias
    zona_horaria_inicio = models.CharField(max_length=100, blank=True)
    zona_horaria_cierre = models.CharField(max_length=100, blank=True)
    
    # Manejo de errores
    codigo_error = models.IntegerField(null=True, blank=True)
    mensaje_error = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sesiones_sence'
        indexes = [
            models.Index(fields=['inscripcion']),
            models.Index(fields=['estudiante']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_inicio']),
        ]
        verbose_name = 'Sesión SENCE'
        verbose_name_plural = 'Sesiones SENCE'
    
    def __str__(self):
        return f"{self.estudiante.nombre_completo()} - {self.curso.nombre} ({self.estado})"
    
    def calcular_duracion(self):
        """Calcula y guarda la duración en minutos"""
        if self.fecha_inicio and self.fecha_cierre:
            delta = self.fecha_cierre - self.fecha_inicio
            self.duracion_minutos = int(delta.total_seconds() / 60)
            self.save(update_fields=['duracion_minutos'])


class LogEnvioSence(models.Model):
    """Registro de envíos de progreso académico a API Gestor Intermedio de SENCE"""
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='logs_envio_sence')
    
    # Información del envío
    fecha_envio = models.DateTimeField(auto_now_add=True)
    id_proceso = models.IntegerField(null=True, blank=True)
    
    # Resultado
    exitoso = models.BooleanField(default=False)
    total_alumnos_enviados = models.IntegerField(default=0)
    total_errores = models.IntegerField(default=0)
    
    # Respuesta completa de SENCE
    respuesta_completa = models.JSONField(default=dict)
    errores_detalle = models.JSONField(default=dict, blank=True)
    
    # Metadata
    enviado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'logs_envio_sence'
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['curso']),
            models.Index(fields=['fecha_envio']),
            models.Index(fields=['exitoso']),
        ]
        verbose_name = 'Log de Envío SENCE'
        verbose_name_plural = 'Logs de Envíos SENCE'
    
    def __str__(self):
        estado = "✓" if self.exitoso else "✗"
        return f"{estado} {self.curso.nombre} - {self.fecha_envio.strftime('%Y-%m-%d %H:%M')}"


# =====================================================
# CONTINÚA EN PARTE 3...
# =====================================================
# models_parte3.py
# Parte final de modelos Django para LMS JC Digital Training

# =====================================================
# MÓDULO 8: COMUNICACIÓN - FORO
# =====================================================

class ForoConsulta(models.Model):
    """Consultas/preguntas de estudiantes en el foro privado"""
    
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('resuelta', 'Resuelta'),
        ('cerrada', 'Cerrada'),
    ]
    
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='consultas_foro')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='consultas_foro')
    
    # Contenido
    titulo = models.CharField(max_length=300)
    pregunta = models.TextField()
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierta')
    
    # Privacidad (para futura funcionalidad de foro público)
    es_publica = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'foro_consultas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['leccion']),
            models.Index(fields=['estudiante']),
            models.Index(fields=['estado']),
        ]
        verbose_name = 'Consulta de Foro'
        verbose_name_plural = 'Consultas de Foro'
    
    def __str__(self):
        return f"{self.titulo} - {self.estudiante.nombre_completo()}"
    
    @property
    def total_respuestas(self):
        """Retorna número de respuestas"""
        return self.respuestas.count()


class ForoRespuesta(models.Model):
    """Respuestas a consultas del foro (de relatores u otros estudiantes)"""
    
    consulta = models.ForeignKey(ForoConsulta, on_delete=models.CASCADE, related_name='respuestas')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respuestas_foro')
    
    # Contenido
    respuesta = models.TextField()
    
    # Marcado como solución
    es_solucion = models.BooleanField(default=False)
    
    # Archivos adjuntos
    archivos_adjuntos = ArrayField(models.URLField(), default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'foro_respuestas'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['consulta']),
            models.Index(fields=['autor']),
        ]
        verbose_name = 'Respuesta de Foro'
        verbose_name_plural = 'Respuestas de Foro'
    
    def __str__(self):
        return f"Respuesta de {self.autor.nombre_completo()} a: {self.consulta.titulo}"
    
    def save(self, *args, **kwargs):
        """Si se marca como solución, actualiza estado de consulta"""
        super().save(*args, **kwargs)
        if self.es_solucion:
            self.consulta.estado = 'resuelta'
            self.consulta.save(update_fields=['estado'])


# =====================================================
# MÓDULO 9: NOTIFICACIONES
# =====================================================

class Notificacion(models.Model):
    """Notificaciones del sistema para usuarios"""
    
    TIPO_CHOICES = [
        ('material_aprobado', 'Material Aprobado'),
        ('material_rechazado', 'Material Rechazado'),
        ('nueva_evaluacion', 'Nueva Evaluación Disponible'),
        ('evaluacion_validada', 'Evaluación Validada'),
        ('mensaje_foro', 'Nuevo Mensaje en Foro'),
        ('curso_proximo', 'Curso Próximo a Iniciar'),
        ('diploma_listo', 'Diploma Listo'),
        ('sesion_sence_error', 'Error en Sesión SENCE'),
        ('general', 'General'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    
    # Contenido
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    
    # Link de acción
    url_accion = models.URLField(max_length=500, blank=True)
    
    # Estado
    leida = models.BooleanField(default=False)
    fecha_leida = models.DateTimeField(null=True, blank=True)
    
    # Prioridad
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='normal')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['leida']),
            models.Index(fields=['tipo']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.nombre_completo()}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_leida = timezone.now()
            self.save(update_fields=['leida', 'fecha_leida'])


# =====================================================
# MÓDULO 10: ENCUESTAS DE SATISFACCIÓN
# =====================================================

class Encuesta(models.Model):
    """Plantillas de encuestas de satisfacción"""
    
    TIPO_CHOICES = [
        ('satisfaccion_curso', 'Satisfacción del Curso'),
        ('evaluacion_relator', 'Evaluación del Relator'),
        ('experiencia_plataforma', 'Experiencia en la Plataforma'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Tipo
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    
    # Preguntas (almacenadas como JSON)
    preguntas = models.JSONField()
    """
    Estructura ejemplo:
    [
        {
            "id": 1,
            "pregunta": "¿Cómo califica el curso?",
            "tipo": "escala",
            "escala_min": 1,
            "escala_max": 7,
            "requerida": true
        },
        {
            "id": 2,
            "pregunta": "Comentarios adicionales",
            "tipo": "texto_largo",
            "requerida": false
        }
    ]
    """
    
    # Estado
    activa = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'encuestas'
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class RespuestaEncuesta(models.Model):
    """Respuestas de estudiantes a encuestas de satisfacción"""
    
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='respuestas')
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='respuestas_encuesta')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respuestas_encuesta')
    
    # Respuestas (almacenadas como JSON)
    respuestas = models.JSONField()
    """
    Estructura ejemplo:
    {
        "1": 6,
        "2": "El curso fue excelente, aprendí mucho",
        "3": 7
    }
    """
    
    # Metadata
    completada_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuestas_encuesta'
        unique_together = [('encuesta', 'inscripcion')]
        indexes = [
            models.Index(fields=['encuesta']),
            models.Index(fields=['inscripcion']),
        ]
        verbose_name = 'Respuesta de Encuesta'
        verbose_name_plural = 'Respuestas de Encuestas'
    
    def __str__(self):
        return f"{self.estudiante.nombre_completo()} - {self.encuesta.nombre}"


# =====================================================
# MÓDULO 11: DIPLOMAS
# =====================================================

class PlantillaDiploma(models.Model):
    """Plantillas HTML para generación de diplomas"""
    
    # Información básica
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Archivo de plantilla
    plantilla_html = models.TextField()  # HTML con placeholders
    
    # Configuración
    variables_disponibles = ArrayField(
        models.CharField(max_length=100), 
        default=list, 
        blank=True
    )
    
    # Firmas
    firma_director_url = models.URLField(max_length=500, blank=True)
    firma_relator_incluida = models.BooleanField(default=True)
    
    # Estado
    activa = models.BooleanField(default=True)
    predeterminada = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plantillas_diploma'
        verbose_name = 'Plantilla de Diploma'
        verbose_name_plural = 'Plantillas de Diplomas'
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        """Si se marca como predeterminada, desmarcar las demás"""
        if self.predeterminada:
            PlantillaDiploma.objects.filter(predeterminada=True).update(predeterminada=False)
        super().save(*args, **kwargs)


# =====================================================
# MÓDULO 12: REPORTES Y MÉTRICAS HISTÓRICAS
# =====================================================

class MetricaHistorica(models.Model):
    """Snapshots históricos de métricas para gráficos y análisis temporal"""
    
    TIPO_CHOICES = [
        ('progreso_estudiante', 'Progreso de Estudiante'),
        ('estadisticas_curso', 'Estadísticas de Curso'),
        ('actividad_plataforma', 'Actividad de Plataforma'),
        ('desempeño_relator', 'Desempeño de Relator'),
    ]
    
    PERIODO_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    ]
    
    # Tipo de métrica
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    
    # Asociación
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='metricas_historicas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True, related_name='metricas_historicas')
    relator = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='metricas_relator')
    
    # Datos de la métrica (JSON flexible)
    datos = models.JSONField()
    
    # Timestamp del snapshot
    snapshot_fecha = models.DateTimeField(default=timezone.now)
    
    # Período al que corresponde
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, blank=True)
    
    class Meta:
        db_table = 'metricas_historicas'
        ordering = ['-snapshot_fecha']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['snapshot_fecha']),
            models.Index(fields=['estudiante']),
            models.Index(fields=['curso']),
        ]
        verbose_name = 'Métrica Histórica'
        verbose_name_plural = 'Métricas Históricas'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.snapshot_fecha.strftime('%Y-%m-%d')}"


# =====================================================
# MÓDULO 13: LOGS Y AUDITORÍA
# =====================================================

class AuditLog(models.Model):
    """Log de auditoría de todas las acciones importantes del sistema"""
    
    # Usuario que realizó la acción
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='acciones_auditoria')
    
    # Acción realizada
    accion = models.CharField(max_length=100)
    entidad_tipo = models.CharField(max_length=50, blank=True)  # 'curso', 'usuario', 'evaluacion', etc.
    entidad_id = models.BigIntegerField(null=True, blank=True)
    
    # Descripción
    descripcion = models.TextField(blank=True)
    
    # Datos antes/después (para cambios)
    datos_anteriores = models.JSONField(default=dict, blank=True)
    datos_nuevos = models.JSONField(default=dict, blank=True)
    
    # Contexto
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['entidad_tipo', 'entidad_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['accion']),
        ]
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
    
    def __str__(self):
        usuario_str = self.usuario.nombre_completo() if self.usuario else 'Sistema'
        return f"{usuario_str} - {self.accion} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# =====================================================
# SIGNALS PARA AUTOMATIZACIÓN
# =====================================================

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(post_save, sender=Usuario)
def crear_configuracion_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente configuración para nuevos usuarios"""
    if created:
        ConfiguracionUsuario.objects.create(usuario=instance)
        
        # Si es relator, crear perfil de relator
        if instance.tipo_usuario == 'relator':
            PerfilRelator.objects.create(usuario=instance)


@receiver(post_save, sender=Inscripcion)
def crear_progreso_inicial(sender, instance, created, **kwargs):
    """Crea registros de progreso inicial al inscribir estudiante"""
    if created:
        # Crear progreso para cada módulo
        for modulo in instance.curso.modulos.all():
            ProgresoModulo.objects.get_or_create(
                inscripcion=instance,
                modulo=modulo
            )
            
            # Crear progreso para cada lección del módulo
            for leccion in modulo.lecciones.all():
                ProgresoLeccion.objects.get_or_create(
                    inscripcion=instance,
                    leccion=leccion
                )


@receiver(post_save, sender=RespuestaEncuesta)
def marcar_encuesta_completada(sender, instance, created, **kwargs):
    """Marca la encuesta como completada en la inscripción"""
    if created:
        instance.inscripcion.encuesta_completada = True
        instance.inscripcion.fecha_encuesta_completada = timezone.now()
        instance.inscripcion.save(update_fields=['encuesta_completada', 'fecha_encuesta_completada'])


@receiver(pre_save, sender=PlantillaDiploma)
def validar_plantilla_predeterminada(sender, instance, **kwargs):
    """Asegura que solo haya una plantilla predeterminada"""
    if instance.predeterminada:
        PlantillaDiploma.objects.filter(predeterminada=True).exclude(pk=instance.pk).update(predeterminada=False)


# =====================================================
# MANAGERS PERSONALIZADOS
# =====================================================

class InscripcionActivaManager(models.Manager):
    """Manager para obtener solo inscripciones activas"""
    def get_queryset(self):
        return super().get_queryset().filter(estado__in=['inscrito', 'en_curso'])


class MaterialAprobadoManager(models.Manager):
    """Manager para obtener solo materiales aprobados"""
    def get_queryset(self):
        return super().get_queryset().filter(estado='aprobado')


# Agregar managers a los modelos correspondientes
Inscripcion.activas = InscripcionActivaManager()
Material.aprobados = MaterialAprobadoManager()


# =====================================================
# MÉTODOS DE UTILIDAD
# =====================================================

def generar_codigo_diploma():
    """Genera código único para diplomas"""
    import hashlib
    import time
    
    timestamp = str(time.time()).encode()
    hash_obj = hashlib.sha256(timestamp)
    return hash_obj.hexdigest()[:12].upper()


def calcular_nota_evaluacion(intento):
    """Calcula la nota de una evaluación basada en puntaje"""
    if intento.puntaje_total and intento.puntaje_total > 0:
        porcentaje = (intento.puntaje_obtenido / intento.puntaje_total) * 100
        # Escala chilena: 1.0 - 7.0
        # 60% = 4.0 (nota mínima aprobación)
        if porcentaje < 60:
            nota = 1.0 + (porcentaje / 60) * 3.0
        else:
            nota = 4.0 + ((porcentaje - 60) / 40) * 3.0
        
        return round(nota, 2)
    return None


# =====================================================
# FIN DE MODELOS
# =====================================================