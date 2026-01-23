#!/usr/bin/env python
"""
Script para crear datos de prueba en LMS JC Digital Training
Ejecutar: python manage.py shell < create_test_data.py
"""

from django.contrib.auth.models import User
from api_lms.models import (
    Usuario, PerfilRelator, ConfiguracionUsuario,
    CodigoSence,
    Curso, CursoRelator, Modulo, Leccion,
    Material, LeccionMaterial,
    Inscripcion, ProgresoModulo, ProgresoLeccion,
    Evaluacion, Pregunta,
)
from datetime import date, timedelta
from django.utils import timezone

print("=" * 60)
print("CREANDO DATOS DE PRUEBA - LMS JC Digital Training")
print("=" * 60)

# =====================================================
# 1. USUARIOS
# =====================================================

print("\n📝 Creando usuarios...")

# Usuario 1: Administrador
user_admin = User.objects.create_user(
    username='admin_jc',
    email='admin@jcdigital.cl',
    password='Admin123!',
    first_name='María',
    last_name='González'
)

usuario_admin = Usuario.objects.create(
    user=user_admin,
    rut_numero=12345678,
    rut_dv='5',
    nombres='María',
    apellido_paterno='González',
    apellido_materno='Pérez',
    fecha_nacimiento=date(1985, 5, 15),
    genero='F',
    telefono='+56912345678',
    region='Valparaíso',
    comuna='Valparaíso',
    tipo_usuario='administrador',
    activo=True
)
print(f"✅ Administrador: {usuario_admin.nombre_completo()} - {usuario_admin.get_rut()}")

# Usuario 2: Relator
user_relator = User.objects.create_user(
    username='relator_juan',
    email='juan.silva@jcdigital.cl',
    password='Relator123!',
    first_name='Juan',
    last_name='Silva'
)

usuario_relator = Usuario.objects.create(
    user=user_relator,
    rut_numero=23456789,
    rut_dv='0',
    nombres='Juan',
    apellido_paterno='Silva',
    apellido_materno='Martínez',
    fecha_nacimiento=date(1980, 8, 20),
    genero='M',
    telefono='+56987654321',
    region='Araucanía',
    comuna='Temuco',
    nivel_educacional='Universitaria Completa',
    profesion='Ingeniero en Acuicultura',
    tipo_usuario='relator',
    activo=True
)

# Actualizar perfil de relator (ya fue creado automáticamente por el signal)
perfil_relator = usuario_relator.perfil_relator
perfil_relator.especialidad = 'Acuicultura y Seguridad Alimentaria'
perfil_relator.areas_experiencia = ['Acuicultura', 'Inocuidad Alimentaria', 'BPM']
perfil_relator.anos_experiencia = 10
perfil_relator.calificacion_promedio = 6.5
perfil_relator.verificado = True
perfil_relator.fecha_verificacion = timezone.now()
perfil_relator.save()
print(f"✅ Relator: {usuario_relator.nombre_completo()} - {usuario_relator.get_rut()}")

# Usuario 3: Estudiante
user_estudiante = User.objects.create_user(
    username='estudiante_pedro',
    email='pedro.ramirez@gmail.com',
    password='Estudiante123!',
    first_name='Pedro',
    last_name='Ramírez'
)

usuario_estudiante = Usuario.objects.create(
    user=user_estudiante,
    rut_numero=34567890,
    rut_dv='1',
    nombres='Pedro',
    apellido_paterno='Ramírez',
    apellido_materno='Torres',
    fecha_nacimiento=date(1995, 3, 10),
    genero='M',
    telefono='+56945678901',
    region='Los Lagos',
    comuna='Puerto Montt',
    nivel_educacional='Media Completa',
    profesion='Operario',
    empresa_actual='Salmonera del Sur',
    cargo_actual='Operario de Planta',
    tipo_usuario='estudiante',
    activo=True
)
print(f"✅ Estudiante: {usuario_estudiante.nombre_completo()} - {usuario_estudiante.get_rut()}")

# =====================================================
# 2. CÓDIGOS SENCE
# =====================================================

print("\n📋 Creando códigos SENCE...")

codigo_sence_1 = CodigoSence.objects.create(
    codigo='1237890123',
    nombre_curso='Buenas Prácticas de Manufactura en Industria Alimentaria',
    horas_totales=40,
    horas_asignadas=0,
    fecha_inicio_vigencia=date(2024, 1, 1),
    fecha_fin_vigencia=date(2025, 12, 31),
    estado='activo',
    area_tematica='Inocuidad Alimentaria',
    nivel='Intermedio',
    modalidad='E-learning',
    linea_capacitacion=3
)
print(f"✅ Código SENCE: {codigo_sence_1.codigo} - {codigo_sence_1.nombre_curso}")

codigo_sence_2 = CodigoSence.objects.create(
    codigo='1237890124',
    nombre_curso='Acuicultura Sustentable y Manejo de Cultivos',
    horas_totales=60,
    horas_asignadas=0,
    fecha_inicio_vigencia=date(2024, 1, 1),
    fecha_fin_vigencia=date(2025, 12, 31),
    estado='activo',
    area_tematica='Acuicultura',
    nivel='Avanzado',
    modalidad='E-learning',
    linea_capacitacion=3
)
print(f"✅ Código SENCE: {codigo_sence_2.codigo} - {codigo_sence_2.nombre_curso}")

# =====================================================
# 3. CURSOS
# =====================================================

print("\n📚 Creando cursos...")

curso_1 = Curso.objects.create(
    nombre='Buenas Prácticas de Manufactura (BPM) en Industria Alimentaria',
    descripcion='Curso práctico sobre implementación de BPM en plantas procesadoras de alimentos',
    objetivos='Conocer y aplicar los principios de BPM para garantizar la inocuidad alimentaria',
    requisitos='Trabajar o tener interés en la industria alimentaria',
    codigo_sence=codigo_sence_1,
    codigo_sence_curso='BPM-2024-001',
    horas_totales=40,
    duracion_semanas=4,
    fecha_inicio=date.today() + timedelta(days=7),
    fecha_fin=date.today() + timedelta(days=35),
    estado='activo',
    publicado=True,
    nota_aprobacion=4.0,
    porcentaje_asistencia_minimo=75,
    cupo_maximo=30,
    cupo_minimo=10,
    creado_por=usuario_admin
)
print(f"✅ Curso: {curso_1.nombre}")

# Asignar relator al curso
curso_relator_1 = CursoRelator.objects.create(
    curso=curso_1,
    relator=usuario_relator,
    especialidad='BPM e Inocuidad',
    activo=True
)
print(f"   → Relator asignado: {usuario_relator.nombre_completo()}")

curso_2 = Curso.objects.create(
    nombre='Acuicultura Sustentable - Fundamentos y Prácticas',
    descripcion='Curso integral sobre acuicultura moderna y sustentable',
    objetivos='Dominar los conceptos y técnicas de acuicultura sustentable',
    requisitos='Educación media completa',
    codigo_sence=codigo_sence_2,
    codigo_sence_curso='ACU-2024-001',
    horas_totales=60,
    duracion_semanas=6,
    fecha_inicio=date.today() + timedelta(days=14),
    fecha_fin=date.today() + timedelta(days=56),
    estado='activo',
    publicado=True,
    nota_aprobacion=4.0,
    porcentaje_asistencia_minimo=75,
    cupo_maximo=25,
    cupo_minimo=8,
    creado_por=usuario_admin
)
print(f"✅ Curso: {curso_2.nombre}")

curso_relator_2 = CursoRelator.objects.create(
    curso=curso_2,
    relator=usuario_relator,
    especialidad='Acuicultura',
    activo=True
)
print(f"   → Relator asignado: {usuario_relator.nombre_completo()}")

# =====================================================
# 4. MÓDULOS Y LECCIONES
# =====================================================

print("\n📖 Creando módulos y lecciones...")

# Módulo 1 del Curso 1
modulo_1_1 = Modulo.objects.create(
    curso=curso_1,
    nombre='Introducción a las Buenas Prácticas de Manufactura',
    descripcion='Conceptos básicos y marco regulatorio de BPM',
    objetivos='Comprender qué son las BPM y su importancia',
    orden=1,
    codigo_modulo='BPM-M1',
    horas_estimadas=10,
    publicado=True
)
print(f"✅ Módulo: {modulo_1_1.nombre}")

# Lecciones del Módulo 1
leccion_1_1_1 = Leccion.objects.create(
    modulo=modulo_1_1,
    nombre='¿Qué son las BPM?',
    descripcion='Definición y alcance de las Buenas Prácticas de Manufactura',
    objetivos='Conocer la definición y alcance de BPM',
    orden=1,
    duracion_minutos=60,
    tipo='teorica',
    publicado=True,
    obligatoria=True
)
print(f"   → Lección: {leccion_1_1_1.nombre}")

leccion_1_1_2 = Leccion.objects.create(
    modulo=modulo_1_1,
    nombre='Marco Legal y Normativo',
    descripcion='Legislación chilena e internacional sobre BPM',
    objetivos='Identificar las principales normativas de BPM',
    orden=2,
    duracion_minutos=90,
    tipo='teorica',
    publicado=True,
    obligatoria=True
)
print(f"   → Lección: {leccion_1_1_2.nombre}")

# Módulo 2 del Curso 1
modulo_1_2 = Modulo.objects.create(
    curso=curso_1,
    nombre='Higiene y Saneamiento',
    descripcion='Principios de higiene personal y limpieza de instalaciones',
    objetivos='Aplicar protocolos de higiene en la industria alimentaria',
    orden=2,
    codigo_modulo='BPM-M2',
    horas_estimadas=15,
    publicado=True
)
print(f"✅ Módulo: {modulo_1_2.nombre}")

leccion_1_2_1 = Leccion.objects.create(
    modulo=modulo_1_2,
    nombre='Higiene del Personal',
    descripcion='Prácticas de higiene personal en planta',
    objetivos='Conocer y aplicar normas de higiene personal',
    orden=1,
    duracion_minutos=120,
    tipo='practica',
    publicado=True,
    obligatoria=True
)
print(f"   → Lección: {leccion_1_2_1.nombre}")

# Módulo 1 del Curso 2
modulo_2_1 = Modulo.objects.create(
    curso=curso_2,
    nombre='Fundamentos de Acuicultura',
    descripcion='Conceptos básicos de acuicultura y especies cultivadas',
    objetivos='Conocer los fundamentos de la acuicultura moderna',
    orden=1,
    codigo_modulo='ACU-M1',
    horas_estimadas=20,
    publicado=True
)
print(f"✅ Módulo: {modulo_2_1.nombre}")

leccion_2_1_1 = Leccion.objects.create(
    modulo=modulo_2_1,
    nombre='Introducción a la Acuicultura',
    descripcion='Historia y desarrollo de la acuicultura',
    objetivos='Comprender el desarrollo histórico de la acuicultura',
    orden=1,
    duracion_minutos=90,
    tipo='teorica',
    publicado=True,
    obligatoria=True
)
print(f"   → Lección: {leccion_2_1_1.nombre}")

# =====================================================
# 5. MATERIALES
# =====================================================

print("\n📄 Creando materiales...")

material_1 = Material.objects.create(
    nombre='Manual de BPM - Introducción',
    descripcion='Manual completo sobre los conceptos básicos de BPM',
    tipo='pdf',
    archivo_url='https://ejemplo.com/manuales/bpm_intro.pdf',
    archivo_size=2048000,
    subido_por=usuario_relator,
    relator_autor=usuario_relator,
    estado='aprobado',
    revisado_por=usuario_admin,
    fecha_revision=timezone.now(),
    tags=['BPM', 'Manual', 'Introducción'],
    categoria='Material Teórico',
    reutilizable=True
)
print(f"✅ Material: {material_1.nombre} - Estado: {material_1.estado}")

material_2 = Material.objects.create(
    nombre='Video: Principios de BPM',
    descripcion='Video educativo sobre los principios fundamentales de BPM',
    tipo='video',
    archivo_url='https://youtube.com/watch?v=ejemplo123',
    duracion_segundos=1200,
    subido_por=usuario_relator,
    relator_autor=usuario_relator,
    estado='aprobado',
    revisado_por=usuario_admin,
    fecha_revision=timezone.now(),
    tags=['BPM', 'Video', 'Principios'],
    categoria='Material Audiovisual',
    reutilizable=True
)
print(f"✅ Material: {material_2.nombre} - Estado: {material_2.estado}")

# Asignar materiales a lecciones
leccion_material_1 = LeccionMaterial.objects.create(
    leccion=leccion_1_1_1,
    material=material_1,
    orden=1,
    proposito='contenido_principal',
    obligatorio=True
)
print(f"   → Material asignado a lección: {leccion_1_1_1.nombre}")

leccion_material_2 = LeccionMaterial.objects.create(
    leccion=leccion_1_1_1,
    material=material_2,
    orden=2,
    proposito='video_intro',
    obligatorio=True
)
print(f"   → Material asignado a lección: {leccion_1_1_1.nombre}")

# =====================================================
# 6. INSCRIPCIONES
# =====================================================

print("\n✍️ Creando inscripciones...")

inscripcion_1 = Inscripcion.objects.create(
    curso=curso_1,
    estudiante=usuario_estudiante,
    estado='en_curso',
    porcentaje_avance=25,
    porcentaje_asistencia=100
)
print(f"✅ Inscripción: {usuario_estudiante.nombre_completo()} → {curso_1.nombre}")

# =====================================================
# 7. EVALUACIONES
# =====================================================

print("\n📝 Creando evaluaciones...")

evaluacion_1 = Evaluacion.objects.create(
    curso=curso_1,
    nombre='Evaluación Diagnóstica - BPM',
    descripcion='Evaluación inicial para medir conocimientos previos',
    instrucciones='Responda todas las preguntas al mejor de su conocimiento',
    tipo='diagnostica',
    tiempo_limite_minutos=30,
    intentos_permitidos=2,
    nota_aprobacion=4.0,
    peso_porcentaje=10.0,
    orden=1,
    publicada=True,
    correccion_automatica=True,
    requiere_validacion_relator=False,
    creado_por=usuario_admin
)
print(f"✅ Evaluación: {evaluacion_1.nombre}")

# Preguntas de la evaluación
pregunta_1 = Pregunta.objects.create(
    evaluacion=evaluacion_1,
    enunciado='¿Qué significa BPM en la industria alimentaria?',
    tipo='seleccion_multiple',
    opciones={
        '1': 'Buenas Prácticas de Manufactura',
        '2': 'Beneficios para la Producción y el Mercado',
        '3': 'Búsqueda de Procesos Mejorados',
        '4': 'Base de Programación y Mantenimiento'
    },
    respuesta_correcta='1',
    puntaje=1.0,
    orden=1,
    feedback_correcto='¡Correcto! BPM significa Buenas Prácticas de Manufactura',
    feedback_incorrecto='Incorrecto. BPM significa Buenas Prácticas de Manufactura'
)
print(f"   → Pregunta: {pregunta_1.enunciado[:50]}...")

pregunta_2 = Pregunta.objects.create(
    evaluacion=evaluacion_1,
    enunciado='Las BPM son obligatorias en Chile para la industria alimentaria',
    tipo='verdadero_falso',
    respuesta_correcta='Verdadero',
    puntaje=1.0,
    orden=2,
    feedback_correcto='¡Correcto! Las BPM son obligatorias según la normativa chilena',
    feedback_incorrecto='Incorrecto. Las BPM son obligatorias en Chile'
)
print(f"   → Pregunta: {pregunta_2.enunciado[:50]}...")

# =====================================================
# RESUMEN
# =====================================================

print("\n" + "=" * 60)
print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("=" * 60)
print(f"\n👥 USUARIOS CREADOS:")
print(f"   • Administrador: admin_jc / Admin123!")
print(f"   • Relator: relator_juan / Relator123!")
print(f"   • Estudiante: estudiante_pedro / Estudiante123!")
print(f"\n📚 CURSOS: {Curso.objects.count()}")
print(f"📖 MÓDULOS: {Modulo.objects.count()}")
print(f"📄 LECCIONES: {Leccion.objects.count()}")
print(f"📎 MATERIALES: {Material.objects.count()}")
print(f"✍️ INSCRIPCIONES: {Inscripcion.objects.count()}")
print(f"📝 EVALUACIONES: {Evaluacion.objects.count()}")
print(f"❓ PREGUNTAS: {Pregunta.objects.count()}")
print("\n" + "=" * 60)
