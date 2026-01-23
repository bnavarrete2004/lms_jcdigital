"""
Views para upload de archivos a Cloudinary
LMS JC Digital Training
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
import cloudinary.uploader
import os

from .models import Material, Usuario
from .serializers import MaterialSerializer, UsuarioSerializer


def validar_archivo(file, tipo_material=None):
    """
    Valida tamaño y extensión del archivo
    Returns: (bool, str) - (es_valido, mensaje_error)
    """
    # Obtener configuración según tipo
    if tipo_material and tipo_material != 'enlace':
        config = settings.CLOUDINARY_SETTINGS['materiales'].get(tipo_material)
        if not config:
            return False, f"Tipo de material '{tipo_material}' no válido"
    else:
        # Es avatar
        config = settings.CLOUDINARY_SETTINGS['avatares']
    
    # Validar tamaño
    if file.size > config['max_size']:
        max_mb = config['max_size'] / (1024 * 1024)
        return False, f"El archivo excede el tamaño máximo de {max_mb:.0f} MB"
    
    # Validar extensión
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in config['extensions']:
        extensions_str = ', '.join(config['extensions'])
        return False, f"Extensión no permitida. Use: {extensions_str}"
    
    return True, None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_material(request):
    """
    POST /api/upload/material/
    
    Sube un archivo de material educativo a Cloudinary
    
    Body (multipart/form-data):
    - file: archivo a subir
    - nombre: nombre del material
    - descripcion: descripción (opcional)
    - tipo: tipo de material (pdf, video, documento, presentacion, imagen, scorm)
    - tags: tags separados por comas (opcional)
    - categoria: categoría (opcional)
    """
    
    # Verificar permisos
    if not hasattr(request.user, 'perfil'):
        return Response(
            {'error': 'Usuario sin perfil'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    usuario = request.user.perfil
    
    # Solo admin y relator pueden subir materiales
    if usuario.tipo_usuario not in ['administrador', 'relator']:
        return Response(
            {'error': 'No tiene permisos para subir materiales'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validar datos requeridos
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No se ha enviado ningún archivo'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if 'tipo' not in request.data:
        return Response(
            {'error': 'Debe especificar el tipo de material'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if 'nombre' not in request.data:
        return Response(
            {'error': 'Debe especificar el nombre del material'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    tipo = request.data['tipo']
    nombre = request.data['nombre']
    
    # Validar tipo
    tipos_validos = ['pdf', 'video', 'documento', 'presentacion', 'imagen', 'scorm']
    if tipo not in tipos_validos:
        return Response(
            {'error': f'Tipo de material no válido. Use: {", ".join(tipos_validos)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar archivo
    es_valido, error = validar_archivo(file, tipo)
    if not es_valido:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Obtener configuración del tipo
        config = settings.CLOUDINARY_SETTINGS['materiales'][tipo]
        
        # Subir a Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=config['folder'],
            resource_type='auto',  # Detecta automáticamente si es imagen, video o raw
            use_filename=True,
            unique_filename=True,
        )
        
        # Crear registro en BD
        material_data = {
            'nombre': nombre,
            'descripcion': request.data.get('descripcion', ''),
            'tipo': tipo,
            'archivo_url': upload_result['secure_url'],
            'archivo_size': file.size,
            'subido_por': usuario.id,
            'relator_autor': usuario.id if usuario.tipo_usuario == 'relator' else None,
            'estado': 'pendiente' if usuario.tipo_usuario == 'relator' else 'aprobado',
        }
        
        # Agregar campos opcionales
        if 'tags' in request.data:
            tags_str = request.data['tags']
            material_data['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        if 'categoria' in request.data:
            material_data['categoria'] = request.data['categoria']
        
        # Metadata adicional según tipo
        if tipo == 'video' and 'duration' in upload_result:
            material_data['duracion_segundos'] = int(upload_result['duration'])
        
        if tipo == 'pdf' and 'pages' in upload_result:
            material_data['total_paginas'] = upload_result['pages']
        
        # Crear material
        serializer = MaterialSerializer(data=material_data)
        if serializer.is_valid():
            material = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Material subido exitosamente',
                'material': MaterialSerializer(material).data,
                'cloudinary': {
                    'public_id': upload_result['public_id'],
                    'url': upload_result['secure_url'],
                    'format': upload_result['format'],
                    'size': upload_result['bytes'],
                }
            }, status=status.HTTP_201_CREATED)
        else:
            # Si falla la creación del material, eliminar archivo de Cloudinary
            cloudinary.uploader.destroy(upload_result['public_id'])
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {'error': f'Error al subir archivo: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """
    POST /api/upload/avatar/
    
    Sube una foto de avatar del usuario a Cloudinary
    
    Body (multipart/form-data):
    - file: imagen a subir (jpg, jpeg, png)
    """
    
    # Verificar perfil
    if not hasattr(request.user, 'perfil'):
        return Response(
            {'error': 'Usuario sin perfil'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    usuario = request.user.perfil
    
    # Validar archivo
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No se ha enviado ningún archivo'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Validar archivo
    es_valido, error = validar_archivo(file)
    if not es_valido:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Configuración de avatares
        config = settings.CLOUDINARY_SETTINGS['avatares']
        
        # Subir a Cloudinary con transformaciones
        upload_result = cloudinary.uploader.upload(
            file,
            folder=config['folder'],
            transformation=[
                {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ],
            use_filename=False,
            unique_filename=True,
        )
        
        # Actualizar usuario
        usuario.avatar_url = upload_result['secure_url']
        usuario.save()
        
        return Response({
            'success': True,
            'message': 'Avatar actualizado exitosamente',
            'usuario': UsuarioSerializer(usuario).data,
            'cloudinary': {
                'public_id': upload_result['public_id'],
                'url': upload_result['secure_url'],
                'format': upload_result['format'],
                'size': upload_result['bytes'],
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Error al subir avatar: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """
    DELETE /api/upload/avatar/
    
    Elimina el avatar del usuario
    """
    
    if not hasattr(request.user, 'perfil'):
        return Response(
            {'error': 'Usuario sin perfil'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    usuario = request.user.perfil
    
    if not usuario.avatar_url:
        return Response(
            {'error': 'El usuario no tiene avatar'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Extraer public_id de la URL (si es de Cloudinary)
        if 'cloudinary.com' in usuario.avatar_url:
            # URL típica: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/file.jpg
            parts = usuario.avatar_url.split('/')
            if len(parts) >= 2:
                # El public_id incluye folder/filename sin extensión
                public_id_parts = parts[-2:]  # folder y filename
                public_id = '/'.join(public_id_parts).rsplit('.', 1)[0]
                
                # Eliminar de Cloudinary
                cloudinary.uploader.destroy(public_id)
        
        # Limpiar URL en BD
        usuario.avatar_url = ''
        usuario.save()
        
        return Response({
            'success': True,
            'message': 'Avatar eliminado exitosamente'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Error al eliminar avatar: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )