# diplomas_utils.py
# Utilidades para generación de diplomas PDF
# LMS JC Digital Training - CORREGIDO SEGÚN MODELOS REALES

import uuid
from datetime import datetime
from io import BytesIO
import cloudinary.uploader

from django.template.loader import render_to_string
from django.utils import timezone
from api_lms.models import PlantillaDiploma, Inscripcion
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from bs4 import BeautifulSoup

def generar_codigo_validacion():
    """
    Genera un código único de validación para el diploma
    Formato: DIP-XXXXXX (8 caracteres aleatorios)
    """
    codigo = f"DIP-{uuid.uuid4().hex[:8].upper()}"
    return codigo


def obtener_plantilla_activa():
    """
    Obtiene la plantilla de diploma activa (predeterminada o primera activa)
    """
    try:
        # Intentar obtener la predeterminada
        plantilla = PlantillaDiploma.objects.get(activa=True, predeterminada=True)
    except PlantillaDiploma.DoesNotExist:
        # Si no hay predeterminada, tomar la primera activa
        try:
            plantilla = PlantillaDiploma.objects.filter(activa=True).first()
        except:
            return None
    
    return plantilla


def generar_variables_diploma(inscripcion, codigo_validacion):
    """
    Genera el diccionario de variables para reemplazar en la plantilla
    
    Args:
        inscripcion: Instancia de Inscripcion
        codigo_validacion: Código único de validación
    
    Returns:
        dict con variables para el template
    """
    estudiante = inscripcion.estudiante
    curso = inscripcion.curso
    
    # Duración del curso
    duracion_horas = curso.horas_totales
    
    # Obtener relator principal (primer relator activo)
    relator_principal = None
    curso_relator = curso.asignaciones_relator.filter(activo=True).first()
    if curso_relator:
        relator_principal = curso_relator.relator
    
    # Fechas del curso
    # Usar fechas reales de la inscripción si existen, sino las del curso
    fecha_inicio = inscripcion.fecha_inicio_real or curso.fecha_inicio
    fecha_termino = inscripcion.fecha_fin_real or curso.fecha_fin
    
    # Formatear fechas (manejar None)
    fecha_inicio_str = fecha_inicio.strftime('%d/%m/%Y') if fecha_inicio else 'N/A'
    if hasattr(fecha_termino, 'strftime'):
        fecha_termino_str = fecha_termino.strftime('%d/%m/%Y')
    elif fecha_termino:
        # Si es datetime
        fecha_termino_str = fecha_termino.strftime('%d/%m/%Y')
    else:
        fecha_termino_str = 'N/A'
    
    variables = {
        # Datos del estudiante
        'estudiante_nombre_completo': estudiante.nombre_completo(),
        'estudiante_rut': estudiante.get_rut(),
        'estudiante_nombres': estudiante.nombres,
        'estudiante_apellidos': f"{estudiante.apellido_paterno} {estudiante.apellido_materno}",
        
        # Datos del curso
        'curso_nombre': curso.nombre,
        'curso_codigo_sence': curso.codigo_sence.codigo if curso.codigo_sence else curso.codigo_sence_curso,
        'curso_duracion_horas': duracion_horas,
        'curso_duracion_texto': f"{duracion_horas} horas cronológicas",
        'curso_fecha_inicio': fecha_inicio_str,
        'curso_fecha_termino': fecha_termino_str,
        
        # Datos de calificación
        'nota_final': f"{inscripcion.nota_final:.1f}" if inscripcion.nota_final else 'N/A',
        'porcentaje_progreso': f"{inscripcion.porcentaje_avance:.1f}%",
        
        # Relator
        'relator_nombre': relator_principal.nombre_completo() if relator_principal else 'Equipo Docente',
        'relator_titulo': relator_principal.perfil_relator.especialidad if (relator_principal and hasattr(relator_principal, 'perfil_relator')) else '',
        
        # Validación y fechas
        'codigo_validacion': codigo_validacion,
        'fecha_emision': timezone.now().strftime('%d/%m/%Y'),
        'año_emision': timezone.now().year,
        
        # Empresa
        'empresa_nombre': 'JC Digital Training',
        'empresa_rut': '76.XXX.XXX-X',  # Reemplazar con RUT real
    }
    
    return variables


def generar_html_diploma(plantilla, variables):
    """
    Genera el HTML del diploma reemplazando variables
    
    Args:
        plantilla: Instancia de PlantillaDiploma
        variables: Dict con variables a reemplazar
    
    Returns:
        str con HTML completo
    """
    html_template = plantilla.plantilla_html
    
    # Reemplazar todas las variables en el formato {{variable}}
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        html_template = html_template.replace(placeholder, str(value))
    
    return html_template

def generar_pdf_diploma(html_content):
    """
    Genera PDF usando Playwright - soporta CSS moderno con gradientes
    """
    from playwright.sync_api import sync_playwright
    from io import BytesIO
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf_path = tmp_file.name
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until='networkidle')
            page.wait_for_timeout(500)
            page.pdf(
                path=pdf_path,
                format='A4',
                landscape=True,
                print_background=True,  # IMPORTANTE para gradientes
                margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
            )
            
            browser.close()
        
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        os.unlink(pdf_path)
        
        pdf_file = BytesIO(pdf_content)
        pdf_file.seek(0)
        return pdf_file
        
    except Exception as e:
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        raise Exception(f"Error con Playwright: {str(e)}")


def subir_diploma_cloudinary(pdf_file, inscripcion, codigo_validacion):
    """
    Sube el PDF del diploma a Cloudinary
    
    Args:
        pdf_file: BytesIO con el PDF
        inscripcion: Instancia de Inscripcion
        codigo_validacion: Código único del diploma
    
    Returns:
        dict con información del archivo subido (url, public_id)
    """
    # IMPORTANTE: Asegurar que el buffer está al inicio
    pdf_file.seek(0)
    
    # Nombre del archivo
    estudiante_rut = inscripcion.estudiante.get_rut().replace('-', '')
    curso_id = inscripcion.curso.id
    filename = f"diploma_{estudiante_rut}_{curso_id}_{codigo_validacion}"
    
    # Subir a Cloudinary en carpeta 'diplomas'
    upload_result = cloudinary.uploader.upload(
        pdf_file,
        folder="diplomas",
        public_id=filename,
        resource_type="raw",  # Para PDFs
        overwrite=True
    )
    
    return {
        'url': upload_result['secure_url'],
        'public_id': upload_result['public_id'],
        'filename': filename
    }


def generar_diploma_completo(inscripcion_id):
    """
    Función principal que genera el diploma completo y lo sube a Cloudinary
    
    Args:
        inscripcion_id: ID de la inscripción
    
    Returns:
        dict con información del diploma generado
    """
    from .notificaciones_utils import notificar_diploma_listo
    
    # Obtener inscripción
    try:
        inscripcion = Inscripcion.objects.get(id=inscripcion_id)
    except Inscripcion.DoesNotExist:
        return {
            'error': 'Inscripción no encontrada',
            'success': False
        }
    
    # Validar que el estudiante completó el curso
    if inscripcion.estado != 'completado':
        return {
            'error': 'El estudiante no ha completado el curso',
            'success': False
        }
    
    # Generar código de validación
    codigo_validacion = generar_codigo_validacion()
    
    # Obtener plantilla activa
    plantilla = obtener_plantilla_activa()
    if not plantilla:
        return {
            'error': 'No hay plantilla de diploma activa',
            'success': False
        }
    
    # Generar variables
    variables = generar_variables_diploma(inscripcion, codigo_validacion)
    
    # Generar HTML
    html_content = generar_html_diploma(plantilla, variables)
    
    # Generar PDF con xhtml2pdf
    try:
        pdf_file = generar_pdf_diploma(html_content)
    except Exception as e:
        return {
            'error': f'Error al generar PDF: {str(e)}',
            'success': False
        }
    
    # Subir a Cloudinary
    try:
        upload_info = subir_diploma_cloudinary(pdf_file, inscripcion, codigo_validacion)
    except Exception as e:
        return {
            'error': f'Error al subir a Cloudinary: {str(e)}',
            'success': False
        }
    
    # Actualizar inscripción con URL y código del diploma
    inscripcion.diploma_url = upload_info['url']
    inscripcion.diploma_codigo_validacion = codigo_validacion
    inscripcion.diploma_generado = True
    inscripcion.fecha_diploma = timezone.now()
    inscripcion.save(update_fields=[
        'diploma_url', 
        'diploma_codigo_validacion', 
        'diploma_generado',
        'fecha_diploma'
    ])
    
    # Notificar al estudiante
    notificar_diploma_listo(inscripcion, upload_info['url'], codigo_validacion)
    
    return {
        'success': True,
        'diploma_url': upload_info['url'],
        'codigo_validacion': codigo_validacion,
        'filename': upload_info['filename'],
        'estudiante': inscripcion.estudiante.nombre_completo(),
        'curso': inscripcion.curso.nombre
    }

    # Notificar al estudiante
    notificar_diploma_listo(inscripcion, upload_info['url'], codigo_validacion)
    
    return {
        'success': True,
        'diploma_url': upload_info['url'],
        'codigo_validacion': codigo_validacion,
        'filename': upload_info['filename'],
        'estudiante': inscripcion.estudiante.nombre_completo(),
        'curso': inscripcion.curso.nombre
    }


def validar_codigo_diploma(codigo_validacion):
    """
    Valida un código de diploma y retorna la información asociada
    
    Args:
        codigo_validacion: Código a validar
    
    Returns:
        dict con información del diploma o error
    """
    try:
        inscripcion = Inscripcion.objects.get(diploma_codigo_validacion=codigo_validacion)
        
        # Formatear fecha de término
        fecha_termino = inscripcion.fecha_fin_real or inscripcion.curso.fecha_fin
        fecha_termino_str = fecha_termino.strftime('%d/%m/%Y') if fecha_termino else 'N/A'
        
        return {
            'valido': True,
            'estudiante': inscripcion.estudiante.nombre_completo(),
            'rut': inscripcion.estudiante.get_rut(),
            'curso': inscripcion.curso.nombre,
            'fecha_termino': fecha_termino_str,
            'nota_final': inscripcion.nota_final,
            'diploma_url': inscripcion.diploma_url
        }
    except Inscripcion.DoesNotExist:
        return {
            'valido': False,
            'error': 'Código de diploma no encontrado'
        }