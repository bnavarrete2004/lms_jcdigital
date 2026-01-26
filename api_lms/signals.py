# signals.py
# Signals para generación automática de notificaciones
# LMS JC Digital Training

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from api_lms.models import Material, ForoRespuesta
from .notificaciones_utils import (
    notificar_material_subido,
    notificar_material_aprobado,
    notificar_material_rechazado,
    notificar_mensaje_foro
)


@receiver(post_save, sender=Material)
def notificar_creacion_material(sender, instance, created, **kwargs):
    """
    Notifica a administradores cuando un relator sube un nuevo material
    """
    if created and instance.estado == 'pendiente':
        # Notificar solo si es creación (no actualización)
        notificar_material_subido(instance, instance.creado_por)


@receiver(pre_save, sender=Material)
def detectar_cambio_estado_material(sender, instance, **kwargs):
    """
    Detecta cambios en el estado del material y genera notificaciones
    """
    if not instance.pk:
        # Material nuevo, no hacer nada (lo maneja post_save)
        return
    
    try:
        # Obtener estado anterior
        material_anterior = Material.objects.get(pk=instance.pk)
        estado_anterior = material_anterior.estado
        estado_nuevo = instance.estado
        
        # Si el estado cambió de 'pendiente' a 'aprobado'
        if estado_anterior == 'pendiente' and estado_nuevo == 'aprobado':
            # Guardar info para usar en post_save
            instance._notificar_aprobacion = True
            instance._aprobado_por = instance.aprobado_por
        
        # Si el estado cambió a 'rechazado'
        elif estado_nuevo == 'rechazado' and estado_anterior != 'rechazado':
            # Guardar info para usar en post_save
            instance._notificar_rechazo = True
            instance._rechazado_por = instance.aprobado_por
            instance._motivo_rechazo = instance.notas_revision or "No se especificó motivo"
    
    except Material.DoesNotExist:
        pass


@receiver(post_save, sender=Material)
def notificar_cambio_estado_material(sender, instance, created, **kwargs):
    """
    Envía notificaciones cuando cambia el estado del material
    """
    if created:
        return  # Ya se maneja en otro signal
    
    # Notificar aprobación
    if hasattr(instance, '_notificar_aprobacion') and instance._notificar_aprobacion:
        notificar_material_aprobado(instance, instance._aprobado_por)
        delattr(instance, '_notificar_aprobacion')
        delattr(instance, '_aprobado_por')
    
    # Notificar rechazo
    if hasattr(instance, '_notificar_rechazo') and instance._notificar_rechazo:
        notificar_material_rechazado(
            instance, 
            instance._rechazado_por,
            instance._motivo_rechazo
        )
        delattr(instance, '_notificar_rechazo')
        delattr(instance, '_rechazado_por')
        delattr(instance, '_motivo_rechazo')


@receiver(post_save, sender=ForoRespuesta)
def notificar_respuesta_foro(sender, instance, created, **kwargs):
    """
    Notifica al estudiante cuando responden su consulta
    """
    if created:
        consulta = instance.consulta
        # Solo notificar si el autor de la respuesta NO es el mismo estudiante
        if consulta.estudiante != instance.autor:
            notificar_mensaje_foro(consulta, instance)