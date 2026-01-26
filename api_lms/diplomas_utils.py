# diplomas_utils.py
# Utilidades para generación de diplomas PDF
# LMS JC Digital Training

import uuid
from datetime import datetime
from io import BytesIO
import cloudinary.uploader
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.utils import timezone
from api_lms.models import PlantillaDiploma, Inscripcion


def generar_codigo_validacion():
    """
    Genera un código único de validación para el diploma
    Formato: DIP-XXXXXX (6 caracteres aleatorios)
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
    
    # Calcular duración total del curso
    duracion_horas = curso.duracion_horas
    
    # Obtener relator principal
    relator_principal = None
    curso_relator = curso.relatores.filter(principal=True).first()
    if curso_relator:
        relator_principal = curso_relator.relator
    
    variables = {
        # Datos del estudiante
        'estudiante_nombre_completo': estudiante.nombre_completo(),
        'estudiante_rut': estudiante.get_rut(),
        'estudiante_nombres': estudiante.nombres,
        'estudiante_apellidos': f"{estudiante.apellido_paterno} {estudiante.apellido_materno}",
        
        # Datos del curso
        'curso_nombre': curso.nombre,
        'curso_codigo_sence': curso.codigo_sence.codigo if curso.codigo_sence else 'N/A',
        'curso_duracion_horas': duracion_horas,
        'curso_duracion_texto': f"{duracion_horas} horas cronológicas",
        'curso_fecha_inicio': inscripcion.fecha_inicio.strftime('%d/%m/%Y'),
        'curso_fecha_termino': inscripcion.fecha_termino.strftime('%d/%m/%Y'),
        
        # Datos de calificación
        'nota_final': f"{inscripcion.nota_final:.1f}" if inscripcion.nota_final else 'N/A',
        'porcentaje_progreso': f"{inscripcion.porcentaje_progreso:.1f}%",
        
        # Relator
        'relator_nombre': relator_principal.nombre_completo() if relator_principal else 'Equipo Docente',
        'relator_titulo': relator_principal.perfil_relator.titulo_profesional if relator_principal and hasattr(relator_principal, 'perfil_relator') else '',
        
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
    Genera PDF desde HTML usando WeasyPrint
    
    Args:
        html_content: str con HTML completo del diploma
    
    Returns:
        BytesIO con el contenido del PDF
    """
    # CSS adicional para el PDF
    css_diploma = CSS(string='''
        @page {
            size: A4 landscape;
            margin: 0;
        }
        body {
            margin: 0;
            padding: 0;
        }
    ''')
    
    # Generar PDF
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file, stylesheets=[css_diploma])
    pdf_file.seek(0)
    
    return pdf_file


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
    
    # Generar PDF
    pdf_file = generar_pdf_diploma(html_content)
    
    # Subir a Cloudinary
    upload_info = subir_diploma_cloudinary(pdf_file, inscripcion, codigo_validacion)
    
    # Actualizar inscripción con URL y código del diploma
    inscripcion.diploma_url = upload_info['url']
    inscripcion.diploma_codigo_validacion = codigo_validacion
    inscripcion.save(update_fields=['diploma_url', 'diploma_codigo_validacion'])
    
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
        
        return {
            'valido': True,
            'estudiante': inscripcion.estudiante.nombre_completo(),
            'rut': inscripcion.estudiante.get_rut(),
            'curso': inscripcion.curso.nombre,
            'fecha_termino': inscripcion.fecha_termino.strftime('%d/%m/%Y'),
            'nota_final': inscripcion.nota_final,
            'diploma_url': inscripcion.diploma_url
        }
    except Inscripcion.DoesNotExist:
        return {
            'valido': False,
            'error': 'Código de diploma no encontrado'
        }