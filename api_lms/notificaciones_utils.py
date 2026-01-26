# notificaciones_utils.py
# Utilidades para crear notificaciones automáticas
# LMS JC Digital Training

from api_lms.models import Notificacion
from django.utils import timezone


def crear_notificacion(
    usuario,
    tipo,
    titulo,
    mensaje,
    url_accion='',
    prioridad='normal'
):
    """
    Crea una notificación para un usuario
    
    Args:
        usuario: Instancia de Usuario
        tipo: Tipo de notificación (ver TIPO_CHOICES en modelo)
        titulo: Título de la notificación
        mensaje: Mensaje descriptivo
        url_accion: URL opcional para acción
        prioridad: Prioridad (baja, normal, alta, urgente)
    
    Returns:
        Instancia de Notificacion creada
    """
    notificacion = Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url_accion=url_accion,
        prioridad=prioridad,
        leida=False
    )
    return notificacion


def notificar_material_subido(material, usuario_creador):
    """
    Notifica a administradores cuando un relator sube material
    """
    from api_lms.models import Usuario
    
    # Obtener todos los administradores
    admins = Usuario.objects.filter(tipo_usuario='administrador', activo=True)
    
    titulo = f"Nuevo material pendiente de aprobación"
    mensaje = (
        f"{usuario_creador.nombre_completo()} ha subido un nuevo material "
        f"'{material.titulo}' de tipo {material.get_tipo_display()}."
    )
    
    for admin in admins:
        crear_notificacion(
            usuario=admin,
            tipo='general',  # Podríamos agregar 'material_pendiente' al modelo
            titulo=titulo,
            mensaje=mensaje,
            url_accion=f"/admin/materiales/{material.id}",
            prioridad='normal'
        )


def notificar_material_aprobado(material, aprobado_por):
    """
    Notifica al relator cuando su material es aprobado
    """
    titulo = "Material aprobado ✓"
    mensaje = (
        f"Tu material '{material.titulo}' ha sido aprobado por "
        f"{aprobado_por.nombre_completo()} y ya está disponible para usar en lecciones."
    )
    
    crear_notificacion(
        usuario=material.creado_por,
        tipo='material_aprobado',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/materiales/{material.id}",
        prioridad='normal'
    )


def notificar_material_rechazado(material, rechazado_por, motivo_rechazo):
    """
    Notifica al relator cuando su material es rechazado
    """
    titulo = "Material rechazado"
    mensaje = (
        f"Tu material '{material.titulo}' ha sido rechazado por "
        f"{rechazado_por.nombre_completo()}.\n\n"
        f"Motivo: {motivo_rechazo}"
    )
    
    crear_notificacion(
        usuario=material.creado_por,
        tipo='material_rechazado',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/materiales/{material.id}",
        prioridad='alta'
    )


def notificar_nueva_evaluacion(evaluacion, inscripcion):
    """
    Notifica a estudiante cuando hay nueva evaluación disponible
    """
    titulo = "Nueva evaluación disponible"
    mensaje = (
        f"La evaluación '{evaluacion.titulo}' ya está disponible en el curso "
        f"'{evaluacion.curso.nombre}'."
    )
    
    crear_notificacion(
        usuario=inscripcion.estudiante,
        tipo='nueva_evaluacion',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/cursos/{evaluacion.curso.id}/evaluaciones/{evaluacion.id}",
        prioridad='normal'
    )


def notificar_evaluacion_validada(intento):
    """
    Notifica al estudiante cuando su intento es validado
    """
    aprobado = intento.aprobado
    estado_texto = "aprobada ✓" if aprobado else "no aprobada"
    
    titulo = f"Evaluación {estado_texto}"
    mensaje = (
        f"Tu intento de '{intento.evaluacion.titulo}' ha sido validado.\n"
        f"Nota obtenida: {intento.puntaje}/{intento.evaluacion.puntaje_total} "
        f"({intento.porcentaje_obtenido:.1f}%)"
    )
    
    crear_notificacion(
        usuario=intento.inscripcion.estudiante,
        tipo='evaluacion_validada',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/evaluaciones/intentos/{intento.id}",
        prioridad='alta' if aprobado else 'normal'
    )


def notificar_diploma_listo(inscripcion, diploma_url, codigo_validacion):
    """
    Notifica al estudiante cuando su diploma está listo
    """
    titulo = "¡Diploma listo! 🎓"
    mensaje = (
        f"¡Felicitaciones! Has completado exitosamente el curso "
        f"'{inscripcion.curso.nombre}'.\n\n"
        f"Tu diploma ya está disponible para descargar.\n"
        f"Código de validación: {codigo_validacion}"
    )
    
    crear_notificacion(
        usuario=inscripcion.estudiante,
        tipo='diploma_listo',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=diploma_url,
        prioridad='alta'
    )


def notificar_mensaje_foro(consulta, respuesta):
    """
    Notifica al estudiante cuando responden su consulta
    """
    titulo = "Nueva respuesta en el foro"
    mensaje = (
        f"{respuesta.autor.nombre_completo()} ha respondido tu consulta "
        f"'{consulta.titulo}'."
    )
    
    crear_notificacion(
        usuario=consulta.estudiante,
        tipo='mensaje_foro',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/foro/consultas/{consulta.id}",
        prioridad='normal'
    )


def notificar_curso_proximo(inscripcion):
    """
    Notifica cuando falta poco para que inicie el curso
    """
    dias_restantes = (inscripcion.curso.fecha_inicio - timezone.now().date()).days
    
    titulo = f"Tu curso inicia en {dias_restantes} días"
    mensaje = (
        f"Recordatorio: El curso '{inscripcion.curso.nombre}' iniciará el "
        f"{inscripcion.curso.fecha_inicio.strftime('%d/%m/%Y')}."
    )
    
    crear_notificacion(
        usuario=inscripcion.estudiante,
        tipo='curso_proximo',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/cursos/{inscripcion.curso.id}",
        prioridad='normal'
    )


def notificar_sesion_sence_error(usuario, curso, mensaje_error):
    """
    Notifica errores en integración SENCE
    """
    titulo = "Error en sesión SENCE"
    mensaje = (
        f"Ha ocurrido un error con la sesión SENCE del curso '{curso.nombre}'.\n\n"
        f"Error: {mensaje_error}"
    )
    
    crear_notificacion(
        usuario=usuario,
        tipo='sesion_sence_error',
        titulo=titulo,
        mensaje=mensaje,
        url_accion=f"/admin/sence/errores",
        prioridad='urgente'
    )


def marcar_todas_leidas(usuario):
    """
    Marca todas las notificaciones de un usuario como leídas
    """
    notificaciones_pendientes = Notificacion.objects.filter(
        usuario=usuario,
        leida=False
    )
    
    for notif in notificaciones_pendientes:
        notif.marcar_como_leida()
    
    return notificaciones_pendientes.count()