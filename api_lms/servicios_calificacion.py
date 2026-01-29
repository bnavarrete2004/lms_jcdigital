# servicios_calificacion.py
# Servicios de cálculo de notas y gestión de aprobación
# LMS JC Digital Training

from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.utils import timezone
from api_lms.models import Evaluacion, IntentoEvaluacion, Inscripcion


# =====================================================
# FUNCIONES DE CÁLCULO DE NOTAS - ESCALA CHILENA
# =====================================================

def calcular_puntaje_aprobacion(puntaje_maximo, porcentaje_exigencia):
    """
    Calcula el puntaje mínimo necesario para aprobar.
    
    Args:
        puntaje_maximo (float): Puntaje total de la evaluación
        porcentaje_exigencia (int): Porcentaje de exigencia (ej: 60)
    
    Returns:
        float: Puntaje necesario para aprobar
    
    Ejemplo:
        >>> calcular_puntaje_aprobacion(100, 60)
        60.0
    """
    return (puntaje_maximo * porcentaje_exigencia) / 100


def aproximar_nota(nota_decimal):
    """
    Aplica la aproximación estándar usada en Chile:
    - Truncar a 2 decimales
    - Si la centésima es >= 5, redondear la décima hacia arriba
    - Si la centésima es < 5, mantener la décima
    
    Args:
        nota_decimal (float): Nota con decimales
    
    Returns:
        Decimal: Nota aproximada a 1 decimal
    
    Ejemplos:
        >>> aproximar_nota(3.94)
        Decimal('3.9')
        >>> aproximar_nota(3.95)
        Decimal('4.0')
        >>> aproximar_nota(5.146)
        Decimal('5.1')
        >>> aproximar_nota(5.951)
        Decimal('6.0')
    """
    # Convertir a Decimal para mayor precisión
    nota = Decimal(str(nota_decimal))
    
    # Truncar a 2 decimales (sin redondear)
    nota_truncada = nota.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Obtener la centésima
    centesima = int(str(nota_truncada).split('.')[-1]) % 10 if '.' in str(nota_truncada) else 0
    
    # Redondear a 1 decimal
    if centesima >= 5:
        # Redondear hacia arriba
        nota_final = nota_truncada.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    else:
        # Truncar (redondear hacia abajo)
        nota_final = (nota_truncada * 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) / 10
    
    return nota_final


def calcular_nota(puntaje_obtenido, puntaje_maximo, porcentaje_exigencia=60, 
                 nota_minima=1.0, nota_maxima=7.0, nota_aprobacion=4.0):
    """
    Calcula la nota usando el sistema de escala de dos tramos.
    
    El sistema divide la escala en dos tramos:
    - Tramo 1: Desde nota mínima hasta nota de aprobación (0 pts → puntaje_aprobacion)
    - Tramo 2: Desde nota de aprobación hasta nota máxima (puntaje_aprobacion → puntaje_maximo)
    
    Args:
        puntaje_obtenido (float): Puntos obtenidos por el estudiante
        puntaje_maximo (float): Puntaje total de la evaluación
        porcentaje_exigencia (int): Porcentaje de exigencia (default: 60)
        nota_minima (float): Nota mínima de la escala (default: 1.0)
        nota_maxima (float): Nota máxima de la escala (default: 7.0)
        nota_aprobacion (float): Nota de aprobación (default: 4.0)
    
    Returns:
        Decimal: Nota calculada y aproximada
    
    Ejemplos:
        >>> calcular_nota(60, 100, 60)  # Justo el puntaje de aprobación
        Decimal('4.0')
        >>> calcular_nota(80, 100, 60)  # 80% = nota ~5.5
        Decimal('5.5')
        >>> calcular_nota(100, 100, 60)  # Puntaje perfecto
        Decimal('7.0')
        >>> calcular_nota(0, 100, 60)  # Sin puntaje
        Decimal('1.0')
    """
    # Validaciones
    if puntaje_obtenido < 0:
        puntaje_obtenido = 0
    if puntaje_obtenido > puntaje_maximo:
        puntaje_obtenido = puntaje_maximo
    
    # Calcular puntaje de aprobación
    puntaje_aprobacion = calcular_puntaje_aprobacion(puntaje_maximo, porcentaje_exigencia)
    
    # Determinar en qué tramo estamos
    if puntaje_obtenido <= puntaje_aprobacion:
        # TRAMO 1: De nota mínima a nota de aprobación
        # Fórmula: nota = nota_minima + (puntaje_obtenido / puntaje_aprobacion) * (nota_aprobacion - nota_minima)
        if puntaje_aprobacion == 0:
            nota_calculada = nota_minima
        else:
            nota_calculada = nota_minima + (puntaje_obtenido / puntaje_aprobacion) * (nota_aprobacion - nota_minima)
    else:
        # TRAMO 2: De nota de aprobación a nota máxima
        # Fórmula: nota = nota_aprobacion + ((puntaje_obtenido - puntaje_aprobacion) / (puntaje_maximo - puntaje_aprobacion)) * (nota_maxima - nota_aprobacion)
        puntaje_sobre_aprobacion = puntaje_obtenido - puntaje_aprobacion
        rango_puntaje = puntaje_maximo - puntaje_aprobacion
        rango_nota = nota_maxima - nota_aprobacion
        
        if rango_puntaje == 0:
            nota_calculada = nota_maxima
        else:
            nota_calculada = nota_aprobacion + (puntaje_sobre_aprobacion / rango_puntaje) * rango_nota
    
    # Aplicar aproximación
    nota_final = aproximar_nota(nota_calculada)
    
    return nota_final


# =====================================================
# FUNCIONES DE GESTIÓN DE EVALUACIONES
# =====================================================

def validar_pesos_evaluaciones(curso):
    """
    Valida que los pesos de las evaluaciones de un curso sumen 100%.
    
    Args:
        curso: Instancia del modelo Curso
    
    Raises:
        ValidationError: Si los pesos no suman 100%
    
    Returns:
        dict: Información sobre las evaluaciones y sus pesos
    """
    evaluaciones = curso.evaluaciones.all()
    
    if not evaluaciones.exists():
        raise ValidationError("El curso no tiene evaluaciones configuradas.")
    
    suma_pesos = sum(float(e.peso_porcentaje) for e in evaluaciones)
    
    # Tolerancia de 0.01 por errores de redondeo
    if abs(suma_pesos - 100.0) > 0.01:
        raise ValidationError(
            f"Los pesos de las evaluaciones deben sumar 100%. "
            f"Actualmente suman: {suma_pesos}%"
        )
    
    return {
        'valido': True,
        'suma_pesos': suma_pesos,
        'cantidad_evaluaciones': evaluaciones.count(),
        'evaluaciones': [
            {
                'nombre': e.nombre,
                'tipo': e.get_tipo_display(),
                'peso': float(e.peso_porcentaje)
            }
            for e in evaluaciones
        ]
    }


def calcular_nota_final_curso(inscripcion):
    """
    Calcula la nota final del curso como promedio ponderado de las evaluaciones.
    
    Solo considera los intentos completados con la mejor nota de cada evaluación.
    
    Args:
        inscripcion: Instancia del modelo Inscripcion
    
    Returns:
        Decimal: Nota final calculada (0.0 si no hay intentos completados)
    
    Raises:
        ValidationError: Si los pesos de las evaluaciones no suman 100%
    """
    curso = inscripcion.curso
    
    # Validar que los pesos sumen 100%
    try:
        validar_pesos_evaluaciones(curso)
    except ValidationError as e:
        raise ValidationError(f"Error en configuración de evaluaciones: {str(e)}")
    
    # Obtener todas las evaluaciones del curso
    evaluaciones = curso.evaluaciones.all()
    
    if not evaluaciones.exists():
        return Decimal('0.0')
    
    nota_final = Decimal('0.0')
    evaluaciones_completadas = 0
    
    for evaluacion in evaluaciones:
        # Obtener el mejor intento completado de esta evaluación
        mejor_intento = IntentoEvaluacion.objects.filter(
            inscripcion=inscripcion,
            evaluacion=evaluacion,
            estado='completado',
            nota_obtenida__isnull=False
        ).order_by('-nota_obtenida').first()
        
        if mejor_intento:
            # Aplicar el peso de la evaluación
            peso_decimal = Decimal(str(evaluacion.peso_porcentaje)) / Decimal('100')
            nota_ponderada = Decimal(str(mejor_intento.nota_obtenida)) * peso_decimal
            nota_final += nota_ponderada
            evaluaciones_completadas += 1
    
    # Si no hay evaluaciones completadas, retornar 0
    if evaluaciones_completadas == 0:
        return Decimal('0.0')
    
    # Aproximar a 1 decimal
    nota_final_aproximada = aproximar_nota(float(nota_final))
    
    return nota_final_aproximada


# =====================================================
# FUNCIONES DE VERIFICACIÓN DE APROBACIÓN
# =====================================================

def verificar_requisitos_aprobacion(inscripcion, porcentaje_asistencia_minimo=75, nota_minima_aprobacion=4.0):
    """
    Verifica si un estudiante cumple los requisitos para aprobar el curso.
    
    Requisitos:
    1. Nota final >= 4.0 (o la nota mínima configurada)
    2. Asistencia >= 75% (o el porcentaje mínimo configurado)
    
    Args:
        inscripcion: Instancia del modelo Inscripcion
        porcentaje_asistencia_minimo (int): Porcentaje mínimo de asistencia requerido (default: 75)
        nota_minima_aprobacion (float): Nota mínima para aprobar (default: 4.0)
    
    Returns:
        dict: Diccionario con información sobre el cumplimiento de requisitos
            {
                'cumple_requisitos': bool,
                'nota_final': Decimal,
                'cumple_nota': bool,
                'porcentaje_asistencia': int,
                'cumple_asistencia': bool,
                'motivos_no_cumplimiento': list
            }
    """
    # Calcular nota final si no está calculada
    if not inscripcion.nota_final_calculada:
        nota_final = calcular_nota_final_curso(inscripcion)
        inscripcion.nota_final_calculada = nota_final
        inscripcion.save(update_fields=['nota_final_calculada'])
    else:
        nota_final = inscripcion.nota_final_calculada
    
    # Obtener porcentaje de asistencia
    porcentaje_asistencia = inscripcion.porcentaje_asistencia
    
    # Verificar cumplimiento de nota
    cumple_nota = nota_final >= Decimal(str(nota_minima_aprobacion))
    
    # Verificar cumplimiento de asistencia
    cumple_asistencia = porcentaje_asistencia >= porcentaje_asistencia_minimo
    
    # Determinar si cumple ambos requisitos
    cumple_requisitos = cumple_nota and cumple_asistencia
    
    # Generar lista de motivos de no cumplimiento
    motivos_no_cumplimiento = []
    if not cumple_nota:
        motivos_no_cumplimiento.append(
            f"Nota insuficiente: {nota_final} (mínimo requerido: {nota_minima_aprobacion})"
        )
    if not cumple_asistencia:
        motivos_no_cumplimiento.append(
            f"Asistencia insuficiente: {porcentaje_asistencia}% (mínimo requerido: {porcentaje_asistencia_minimo}%)"
        )
    
    return {
        'cumple_requisitos': cumple_requisitos,
        'nota_final': nota_final,
        'cumple_nota': cumple_nota,
        'porcentaje_asistencia': porcentaje_asistencia,
        'cumple_asistencia': cumple_asistencia,
        'motivos_no_cumplimiento': motivos_no_cumplimiento
    }


# =====================================================
# FUNCIONES DE ACTUALIZACIÓN DE ESTADO
# =====================================================

def actualizar_estado_inscripcion_automatico(inscripcion):
    """
    Calcula la nota final, verifica requisitos y actualiza el estado de la inscripción.
    
    Esta función NO aprueba/reprueba automáticamente. Solo:
    1. Calcula la nota final del curso
    2. Verifica si cumple requisitos
    3. Actualiza campos de cálculo automático
    4. Cambia estado a 'pendiente_revision' si corresponde
    
    La aprobación/reprobación final debe ser realizada por un administrador.
    
    Args:
        inscripcion: Instancia del modelo Inscripcion
    
    Returns:
        dict: Información sobre el cálculo y verificación realizada
    """
    # Calcular nota final
    nota_final = calcular_nota_final_curso(inscripcion)
    
    # Verificar requisitos
    verificacion = verificar_requisitos_aprobacion(inscripcion)
    
    # Actualizar campos de cálculo automático
    inscripcion.nota_final_calculada = nota_final
    inscripcion.cumple_requisitos_aprobacion = verificacion['cumple_requisitos']
    
    # Si el estudiante completó todas las evaluaciones, cambiar a pendiente_revision
    curso = inscripcion.curso
    total_evaluaciones = curso.evaluaciones.count()
    
    evaluaciones_completadas = IntentoEvaluacion.objects.filter(
        inscripcion=inscripcion,
        estado='completado'
    ).values('evaluacion').distinct().count()
    
    if evaluaciones_completadas >= total_evaluaciones and total_evaluaciones > 0:
        # Cambiar estado solo si estaba en 'en_curso' o 'completado'
        if inscripcion.estado in ['en_curso', 'completado']:
            inscripcion.estado = 'pendiente_revision'
    
    inscripcion.save()
    
    return {
        'nota_final': nota_final,
        'cumple_requisitos': verificacion['cumple_requisitos'],
        'estado_actualizado': inscripcion.estado,
        'verificacion_detalle': verificacion
    }


def aprobar_inscripcion_manual(inscripcion, aprobado_por, justificacion=''):
    """
    Aprueba una inscripción manualmente (decisión del administrador).
    
    Args:
        inscripcion: Instancia del modelo Inscripcion
        aprobado_por: Usuario administrador que aprueba
        justificacion (str): Justificación (obligatoria si no cumple requisitos)
    
    Returns:
        dict: Información sobre la aprobación
    
    Raises:
        ValidationError: Si falta justificación cuando no cumple requisitos
    """
    # Verificar si cumple requisitos
    verificacion = verificar_requisitos_aprobacion(inscripcion)
    cumple_requisitos = verificacion['cumple_requisitos']
    
    # Si no cumple requisitos, la justificación es obligatoria
    if not cumple_requisitos and not justificacion:
        raise ValidationError(
            "Debe proporcionar una justificación para aprobar a un estudiante "
            "que no cumple los requisitos automáticos."
        )
    
    # Actualizar inscripción
    inscripcion.estado = 'aprobado'
    inscripcion.nota_final = inscripcion.nota_final_calculada
    inscripcion.aprobacion_manual = not cumple_requisitos  # True si fue decisión excepcional
    inscripcion.justificacion_aprobacion = justificacion
    inscripcion.revisado_por = aprobado_por
    inscripcion.fecha_revision = timezone.now()
    inscripcion.save()
    
    return {
        'aprobado': True,
        'aprobacion_manual': inscripcion.aprobacion_manual,
        'nota_final': inscripcion.nota_final,
        'mensaje': 'Inscripción aprobada exitosamente'
    }


def reprobar_inscripcion_manual(inscripcion, reprobado_por, justificacion=''):
    """
    Reprueba una inscripción manualmente (decisión del administrador).
    
    Args:
        inscripcion: Instancia del modelo Inscripcion
        reprobado_por: Usuario administrador que reprueba
        justificacion (str): Justificación (obligatoria si cumple requisitos)
    
    Returns:
        dict: Información sobre la reprobación
    
    Raises:
        ValidationError: Si falta justificación cuando cumple requisitos
    """
    # Verificar si cumple requisitos
    verificacion = verificar_requisitos_aprobacion(inscripcion)
    cumple_requisitos = verificacion['cumple_requisitos']
    
    # Si cumple requisitos, la justificación es obligatoria
    if cumple_requisitos and not justificacion:
        raise ValidationError(
            "Debe proporcionar una justificación para reprobar a un estudiante "
            "que cumple los requisitos automáticos."
        )
    
    # Actualizar inscripción
    inscripcion.estado = 'reprobado'
    inscripcion.nota_final = inscripcion.nota_final_calculada
    inscripcion.aprobacion_manual = cumple_requisitos  # True si fue decisión excepcional
    inscripcion.justificacion_aprobacion = justificacion
    inscripcion.revisado_por = reprobado_por
    inscripcion.fecha_revision = timezone.now()
    inscripcion.save()
    
    return {
        'aprobado': False,
        'aprobacion_manual': inscripcion.aprobacion_manual,
        'nota_final': inscripcion.nota_final,
        'mensaje': 'Inscripción reprobada'
    }