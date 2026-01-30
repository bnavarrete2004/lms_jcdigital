# views_calificacion.py
# Vistas para gestión de calificaciones y aprobación de inscripciones
# LMS JC Digital Training

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from api_lms.models import Inscripcion, IntentoEvaluacion, Evaluacion
from api_lms.serializers import InscripcionSerializer
from api_lms.servicios_calificacion import (
    calcular_nota,
    calcular_nota_final_curso,
    verificar_requisitos_aprobacion,
    actualizar_estado_inscripcion_automatico,
    aprobar_inscripcion_manual,
    reprobar_inscripcion_manual,
    validar_pesos_evaluaciones
)


# =====================================================
# ENDPOINT: CALCULAR NOTA DE INTENTO
# =====================================================

def obtener_rol_usuario(user):
    """
    Obtiene el rol del usuario de forma segura.
    Maneja tanto Usuario personalizado como User de Django con relación.
    """
    # Si el user tiene directamente el atributo tipo_usuario
    if hasattr(user, 'tipo_usuario'):
        return user.tipo_usuario
    
    # Si el user tiene directamente el atributo rol
    if hasattr(user, 'rol'):
        return user.rol
    
    # Si el user tiene una relación 'perfil' con Usuario (TU CASO)
    if hasattr(user, 'perfil'):
        perfil = user.perfil
        # Intentar tipo_usuario primero
        if hasattr(perfil, 'tipo_usuario'):
            return perfil.tipo_usuario
        # Si no, intentar rol
        if hasattr(perfil, 'rol'):
            return perfil.rol
    
    # Si el user tiene una relación 'usuario' (otro nombre posible)
    if hasattr(user, 'usuario'):
        usuario = user.usuario
        # Intentar tipo_usuario primero
        if hasattr(usuario, 'tipo_usuario'):
            return usuario.tipo_usuario
        # Si no, intentar rol
        if hasattr(usuario, 'rol'):
            return usuario.rol
    
    # Si no se encuentra rol, asumir sin permisos
    return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calcular_nota_intento(request, intento_id):
    """
    Calcula la nota de un intento de evaluación basado en el puntaje obtenido.
    
    POST /api/intentos-evaluacion/{id}/calcular-nota/
    
    Body (opcional - si no se envía, usa valores de la evaluación):
    {
        "porcentaje_exigencia": 60,  # Opcional
        "nota_minima": 1.0,           # Opcional
        "nota_maxima": 7.0,           # Opcional
        "nota_aprobacion": 4.0        # Opcional
    }
    """
    # Verificar permisos: admin o relator
    rol_usuario = obtener_rol_usuario(request.user)
    if rol_usuario not in ['administrador', 'relator']:
        return Response(
            {'error': 'No tiene permisos para calcular notas'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener intento
    intento = get_object_or_404(IntentoEvaluacion, id=intento_id)
    
    # Verificar que el intento esté completado
    if intento.estado != 'completado':
        return Response(
            {'error': 'Solo se pueden calcular notas de intentos completados'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar que tenga puntaje obtenido
    if intento.puntaje_obtenido is None or intento.puntaje_total is None:
        return Response(
            {'error': 'El intento no tiene puntaje registrado'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener configuración de la evaluación o del request
    evaluacion = intento.evaluacion
    porcentaje_exigencia = request.data.get('porcentaje_exigencia', evaluacion.porcentaje_aprobacion)
    nota_minima = request.data.get('nota_minima', float(evaluacion.nota_minima))
    nota_maxima = request.data.get('nota_maxima', float(evaluacion.nota_maxima))
    nota_aprobacion = request.data.get('nota_aprobacion', float(evaluacion.nota_aprobacion))
    
    # Calcular nota
    try:
        nota_calculada = calcular_nota(
            puntaje_obtenido=float(intento.puntaje_obtenido),
            puntaje_maximo=float(intento.puntaje_total),
            porcentaje_exigencia=porcentaje_exigencia,
            nota_minima=nota_minima,
            nota_maxima=nota_maxima,
            nota_aprobacion=nota_aprobacion
        )
        
        # Actualizar intento
        intento.nota_obtenida = float(nota_calculada)
        intento.aprobado = nota_calculada >= nota_aprobacion
        intento.save(update_fields=['nota_obtenida', 'aprobado'])
        
        return Response({
            'success': True,
            'intento_id': intento.id,
            'puntaje_obtenido': float(intento.puntaje_obtenido),
            'puntaje_total': float(intento.puntaje_total),
            'porcentaje': round((float(intento.puntaje_obtenido) / float(intento.puntaje_total)) * 100, 2),
            'nota_obtenida': float(nota_calculada),
            'aprobado': intento.aprobado,
            'configuracion_usada': {
                'porcentaje_exigencia': porcentaje_exigencia,
                'nota_minima': nota_minima,
                'nota_maxima': nota_maxima,
                'nota_aprobacion': nota_aprobacion
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error al calcular nota: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =====================================================
# ENDPOINT: CALCULAR NOTA FINAL DEL CURSO
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calcular_nota_final_inscripcion(request, inscripcion_id):
    """
    Calcula la nota final del curso y actualiza el estado de la inscripción.
    
    POST /api/inscripciones/{id}/calcular-nota-final/
    
    Realiza:
    1. Calcula nota final como promedio ponderado de evaluaciones
    2. Verifica si cumple requisitos (nota >= 4.0 Y asistencia >= 75%)
    3. Actualiza campos automáticos
    4. Cambia estado a 'pendiente_revision' si corresponde
    """
    # Verificar permisos: admin o relator
    rol_usuario = obtener_rol_usuario(request.user)
    if rol_usuario not in ['administrador', 'relator']:
        return Response(
            {'error': 'No tiene permisos para calcular notas finales'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener inscripción
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    
    try:
        # Ejecutar cálculo automático
        resultado = actualizar_estado_inscripcion_automatico(inscripcion)
        
        # Serializar inscripción actualizada
        serializer = InscripcionSerializer(inscripcion)
        
        return Response({
            'success': True,
            'inscripcion': serializer.data,
            'calculo': resultado
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error al calcular nota final: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =====================================================
# ENDPOINT: APROBAR INSCRIPCIÓN
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aprobar_inscripcion(request, inscripcion_id):
    """
    Aprueba una inscripción manualmente (decisión del administrador).
    
    POST /api/inscripciones/{id}/aprobar/
    
    Body:
    {
        "justificacion": "Texto opcional si cumple requisitos, obligatorio si no cumple"
    }
    
    Validaciones:
    - Si NO cumple requisitos → justificación es OBLIGATORIA
    - Si cumple requisitos → justificación es OPCIONAL
    """
    # Verificar permisos: solo administrador
    rol_usuario = obtener_rol_usuario(request.user)
    if rol_usuario != 'administrador':
        return Response(
            {'error': 'Solo administradores pueden aprobar inscripciones'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener inscripción
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    
    # Obtener justificación del request
    justificacion = request.data.get('justificacion', '')
    
    try:
        # Aprobar inscripción
        resultado = aprobar_inscripcion_manual(
            inscripcion=inscripcion,
            aprobado_por=request.user,
            justificacion=justificacion
        )
        
        # Serializar inscripción actualizada
        serializer = InscripcionSerializer(inscripcion)
        
        return Response({
            'success': True,
            'mensaje': resultado['mensaje'],
            'inscripcion': serializer.data,
            'aprobacion_manual': resultado['aprobacion_manual'],
            'nota_final': float(resultado['nota_final'])
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error al aprobar inscripción: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =====================================================
# ENDPOINT: REPROBAR INSCRIPCIÓN
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reprobar_inscripcion(request, inscripcion_id):
    """
    Reprueba una inscripción manualmente (decisión del administrador).
    
    POST /api/inscripciones/{id}/reprobar/
    
    Body:
    {
        "justificacion": "Texto obligatorio si cumple requisitos, opcional si no cumple"
    }
    
    Validaciones:
    - Si cumple requisitos → justificación es OBLIGATORIA
    - Si NO cumple requisitos → justificación es OPCIONAL
    """
    # Verificar permisos: solo administrador
    rol_usuario = obtener_rol_usuario(request.user)
    if rol_usuario != 'administrador':
        return Response(
            {'error': 'Solo administradores pueden reprobar inscripciones'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener inscripción
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    
    # Obtener justificación del request
    justificacion = request.data.get('justificacion', '')
    
    try:
        # Reprobar inscripción
        resultado = reprobar_inscripcion_manual(
            inscripcion=inscripcion,
            reprobado_por=request.user,
            justificacion=justificacion
        )
        
        # Serializar inscripción actualizada
        serializer = InscripcionSerializer(inscripcion)
        
        return Response({
            'success': True,
            'mensaje': resultado['mensaje'],
            'inscripcion': serializer.data,
            'aprobacion_manual': resultado['aprobacion_manual'],
            'nota_final': float(resultado['nota_final'])
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error al reprobar inscripción: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =====================================================
# ENDPOINT: OBTENER DETALLE DE CALIFICACIONES
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_calificaciones_inscripcion(request, inscripcion_id):
    """
    Obtiene el detalle completo de calificaciones de una inscripción.
    
    GET /api/inscripciones/{id}/calificaciones/
    
    Retorna:
    - Nota final calculada
    - Detalle de cada evaluación con su mejor intento
    - Verificación de requisitos
    - Estado de aprobación
    """
    # Obtener inscripción
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    
    
    # Verificar permisos: el estudiante solo ve sus propias calificaciones
    rol_usuario = obtener_rol_usuario(request.user)
    # Obtener el usuario correcto (puede ser Usuario directo o relacionado)
    if hasattr(request.user, 'perfil'):
        usuario_actual = request.user.perfil
    elif hasattr(request.user, 'tipo_usuario'):
        usuario_actual = request.user
    else:
        usuario_actual = request.user
    
    if rol_usuario == 'estudiante' and inscripcion.estudiante != usuario_actual:
        return Response(
            {'error': 'No tiene permisos para ver estas calificaciones'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener todas las evaluaciones del curso
    evaluaciones = inscripcion.curso.evaluaciones.all().order_by('orden', 'id')
    
    # Construir detalle de evaluaciones
    detalle_evaluaciones = []
    for evaluacion in evaluaciones:
        # Obtener mejor intento de esta evaluación
        mejor_intento = IntentoEvaluacion.objects.filter(
            inscripcion=inscripcion,
            evaluacion=evaluacion,
            estado='completado',
            nota_obtenida__isnull=False
        ).order_by('-nota_obtenida').first()
        
        if mejor_intento:
            detalle_evaluaciones.append({
                'evaluacion_id': evaluacion.id,
                'evaluacion_nombre': evaluacion.nombre,
                'evaluacion_tipo': evaluacion.get_tipo_display(),
                'peso_porcentaje': float(evaluacion.peso_porcentaje),
                'intento_id': mejor_intento.id,
                'numero_intento': mejor_intento.numero_intento,
                'puntaje_obtenido': float(mejor_intento.puntaje_obtenido) if mejor_intento.puntaje_obtenido else None,
                'puntaje_total': float(mejor_intento.puntaje_total) if mejor_intento.puntaje_total else None,
                'nota_obtenida': float(mejor_intento.nota_obtenida),
                'aprobado': mejor_intento.aprobado,
                'fecha_realizacion': mejor_intento.fecha_fin
            })
        else:
            detalle_evaluaciones.append({
                'evaluacion_id': evaluacion.id,
                'evaluacion_nombre': evaluacion.nombre,
                'evaluacion_tipo': evaluacion.get_tipo_display(),
                'peso_porcentaje': float(evaluacion.peso_porcentaje),
                'intento_id': None,
                'nota_obtenida': None,
                'aprobado': False,
                'mensaje': 'No realizada'
            })
    
    # Verificar requisitos
    try:
        verificacion = verificar_requisitos_aprobacion(inscripcion)
    except Exception as e:
        verificacion = {
            'error': str(e)
        }
    
    # Construir respuesta
    return Response({
        'inscripcion_id': inscripcion.id,
        'estudiante': {
            'id': inscripcion.estudiante.id,
            'nombre': f"{inscripcion.estudiante.nombres} {inscripcion.estudiante.apellido_paterno} {inscripcion.estudiante.apellido_materno}",
            'rut': f"{inscripcion.estudiante.rut_numero}-{inscripcion.estudiante.rut_dv}"
        },
        'curso': {
            'id': inscripcion.curso.id,
            'nombre': inscripcion.curso.nombre
        },
        'estado': inscripcion.estado,
        'nota_final_calculada': float(inscripcion.nota_final_calculada) if inscripcion.nota_final_calculada else None,
        'nota_final_oficial': float(inscripcion.nota_final) if inscripcion.nota_final else None,
        'porcentaje_asistencia': inscripcion.porcentaje_asistencia,
        'cumple_requisitos_aprobacion': inscripcion.cumple_requisitos_aprobacion,
        'aprobacion_manual': inscripcion.aprobacion_manual,
        'justificacion_aprobacion': inscripcion.justificacion_aprobacion,
        'revisado_por': inscripcion.revisado_por.nombre_completo() if inscripcion.revisado_por else None,
        'fecha_revision': inscripcion.fecha_revision,
        'evaluaciones': detalle_evaluaciones,
        'verificacion_requisitos': verificacion
    })


# =====================================================
# ENDPOINT: VALIDAR CONFIGURACIÓN DE EVALUACIONES
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_configuracion_evaluaciones(request, curso_id):
    """
    Valida que las evaluaciones de un curso estén correctamente configuradas.
    
    GET /api/cursos/{id}/validar-evaluaciones/
    
    Verifica:
    - Que los pesos sumen 100%
    - Que todas las evaluaciones tengan configuración válida
    """
    # Verificar permisos: admin o relator
    rol_usuario = obtener_rol_usuario(request.user)
    if rol_usuario not in ['administrador', 'relator']:
        return Response(
            {'error': 'No tiene permisos para validar configuraciones'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    from api_lms.models import Curso
    curso = get_object_or_404(Curso, id=curso_id)
    
    try:
        validacion = validar_pesos_evaluaciones(curso)
        
        return Response({
            'valido': True,
            'mensaje': 'Configuración de evaluaciones válida',
            'detalle': validacion
        })
        
    except ValidationError as e:
        return Response({
            'valido': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)