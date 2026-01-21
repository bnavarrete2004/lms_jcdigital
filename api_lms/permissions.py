# permissions.py
# Sistema de permisos personalizados para LMS JC Digital Training
# Compatible con Django 5.0+ y DRF 3.14+

"""
IMPORTANTE: En este sistema, "estudiante" es solo un término simbólico.
En realidad, estudiante = usuario regular del sistema.
No existe distinción entre "usuario" y "estudiante", son lo mismo.

ROLES DEL SISTEMA:
- estudiante (usuario regular): Personas que toman cursos
- relator: Instructores que suben material educativo
- administrador: Control total del sistema
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


# =====================================================
# PERMISOS BASE POR ROL
# =====================================================

class IsAdministrador(BasePermission):
    """
    Permiso para administradores únicamente.
    Los administradores tienen control total del sistema.
    """
    message = "Solo los administradores pueden realizar esta acción."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and
            request.user.perfil.tipo_usuario == 'administrador'
        )


class IsRelator(BasePermission):
    """
    Permiso para relatores únicamente.
    Los relatores pueden subir material y gestionar contenido de sus cursos.
    """
    message = "Solo los relatores pueden realizar esta acción."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and
            request.user.perfil.tipo_usuario == 'relator'
        )


class IsEstudiante(BasePermission):
    """
    Permiso para estudiantes/usuarios regulares únicamente.
    NOTA: "estudiante" es solo término simbólico = usuario regular del sistema.
    Los estudiantes/usuarios solo pueden ver contenido y avanzar en sus cursos.
    """
    message = "Solo los estudiantes pueden realizar esta acción."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and
            request.user.perfil.tipo_usuario == 'estudiante'
        )


class IsRelatorOrAdministrador(BasePermission):
    """
    Permiso para relatores o administradores.
    """
    message = "Solo relatores o administradores pueden realizar esta acción."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, 'perfil')):
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario
        return tipo_usuario in ['relator', 'administrador']


# =====================================================
# PERMISOS ESPECÍFICOS POR MODELO
# =====================================================

class UsuarioPermission(BasePermission):
    """
    Permisos para el modelo Usuario:
    - Administrador: CRUD completo (crear, leer, actualizar, eliminar)
    - Relator: Solo lectura de su propio perfil
    - Estudiante: Solo lectura de su propio perfil
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Administradores tienen acceso total
        if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'administrador':
            return True
        
        # Otros usuarios solo pueden ver (GET, HEAD, OPTIONS)
        return request.method in SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Administradores pueden todo
        if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'administrador':
            return True
        
        # Usuarios solo pueden ver su propio perfil
        if request.method in SAFE_METHODS:
            return obj == request.user.perfil
        
        return False


class MaterialPermission(BasePermission):
    """
    Permisos para el modelo Material:
    - Administrador: CRUD completo + aprobar/rechazar
    - Relator: Crear (subir material), leer sus propios materiales, NO puede editar ni eliminar
    - Estudiante: Solo lectura de materiales aprobados
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores: pueden crear (POST) y leer (GET)
        if tipo_usuario == 'relator':
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']
        
        # Estudiantes: solo lectura
        if tipo_usuario == 'estudiante':
            return request.method in SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores: pueden ver sus propios materiales, NO pueden editar ni eliminar
        if tipo_usuario == 'relator':
            if request.method in SAFE_METHODS:
                return obj.relator == request.user.perfil
            return False  # NO pueden editar ni eliminar
        
        # Estudiantes: solo pueden ver materiales aprobados
        if tipo_usuario == 'estudiante':
            return request.method in SAFE_METHODS and obj.estado == 'aprobado'
        
        return False


class CursoPermission(BasePermission):
    """
    Permisos para el modelo Curso:
    - Administrador: CRUD completo
    - Relator: Solo lectura de cursos donde está asignado, NO puede crear, editar ni eliminar
    - Estudiante: Solo lectura de cursos donde está inscrito
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            # Permitir GET público para cursos destacados
            return request.method in SAFE_METHODS
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores y estudiantes: solo lectura
        return request.method in SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores: solo pueden ver cursos donde están asignados
        if tipo_usuario == 'relator':
            if request.method in SAFE_METHODS:
                return obj.relatores.filter(id=request.user.perfil.id).exists()
            return False
        
        # Estudiantes: solo pueden ver cursos donde están inscritos
        if tipo_usuario == 'estudiante':
            if request.method in SAFE_METHODS:
                return obj.inscripciones.filter(estudiante=request.user.perfil, activo=True).exists()
            return False
        
        return False


class InscripcionPermission(BasePermission):
    """
    Permisos para el modelo Inscripcion:
    - Administrador: CRUD completo
    - Relator: Solo lectura de inscripciones de sus cursos
    - Estudiante: Solo lectura de sus propias inscripciones, NO puede crear, editar ni eliminar
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores y estudiantes: solo lectura
        return request.method in SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores: pueden ver inscripciones de sus cursos
        if tipo_usuario == 'relator':
            if request.method in SAFE_METHODS:
                return obj.curso.relatores.filter(id=request.user.perfil.id).exists()
            return False
        
        # Estudiantes: solo pueden ver sus propias inscripciones
        if tipo_usuario == 'estudiante':
            if request.method in SAFE_METHODS:
                return obj.estudiante == request.user.perfil
            return False
        
        return False


class ProgresoPermission(BasePermission):
    """
    Permisos para modelos de Progreso (ProgresoModulo, ProgresoLeccion, ProgresoActividad):
    - Administrador: CRUD completo
    - Relator: Solo lectura del progreso de estudiantes en sus cursos
    - Estudiante: Puede ver y actualizar su propio progreso, NO puede eliminar
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Estudiantes: pueden ver y actualizar (GET, PATCH, PUT)
        if tipo_usuario == 'estudiante':
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'PATCH', 'PUT', 'POST']
        
        # Relatores: solo lectura
        if tipo_usuario == 'relator':
            return request.method in SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Estudiantes: pueden ver y actualizar su propio progreso, NO eliminar
        if tipo_usuario == 'estudiante':
            if request.method == 'DELETE':
                return False
            return obj.inscripcion.estudiante == request.user.perfil
        
        # Relatores: pueden ver progreso de estudiantes en sus cursos
        if tipo_usuario == 'relator':
            if request.method in SAFE_METHODS:
                return obj.inscripcion.curso.relatores.filter(id=request.user.perfil.id).exists()
            return False
        
        return False


class EvaluacionPermission(BasePermission):
    """
    Permisos para el modelo Evaluacion:
    - Administrador: CRUD completo
    - Relator: Solo lectura de evaluaciones de sus cursos, NO puede crear, editar ni eliminar
    - Estudiante: Solo lectura de evaluaciones de cursos donde está inscrito
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores y estudiantes: solo lectura
        return request.method in SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores: pueden ver evaluaciones de sus cursos
        if tipo_usuario == 'relator':
            if request.method in SAFE_METHODS:
                return obj.curso.relatores.filter(id=request.user.perfil.id).exists()
            return False
        
        # Estudiantes: pueden ver evaluaciones de cursos donde están inscritos
        if tipo_usuario == 'estudiante':
            if request.method in SAFE_METHODS:
                return obj.curso.inscripciones.filter(estudiante=request.user.perfil, activo=True).exists()
            return False
        
        return False


class ForoPermission(BasePermission):
    """
    Permisos para el modelo Foro, TemaForo y RespuestaForo:
    - Administrador: CRUD completo + puede eliminar cualquier contenido
    - Relator: Puede leer y crear temas/respuestas en foros de sus cursos, NO puede eliminar
    - Estudiante: Puede leer y crear temas/respuestas en foros de sus cursos, NO puede editar ni eliminar
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Relatores y estudiantes: pueden leer y crear
        if tipo_usuario in ['relator', 'estudiante']:
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']
        
        return False
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Determinar si el usuario tiene acceso al curso del foro
        if hasattr(obj, 'curso'):
            curso = obj.curso
        elif hasattr(obj, 'foro'):
            curso = obj.foro.curso
        else:
            return False
        
        # Relatores: pueden leer y crear en foros de sus cursos, NO pueden eliminar
        if tipo_usuario == 'relator':
            if request.method == 'DELETE':
                return False
            tiene_acceso = curso.relatores.filter(id=request.user.perfil.id).exists()
            if request.method in SAFE_METHODS or request.method == 'POST':
                return tiene_acceso
            return False
        
        # Estudiantes: pueden leer y crear, NO pueden editar ni eliminar
        if tipo_usuario == 'estudiante':
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return False
            tiene_acceso = curso.inscripciones.filter(estudiante=request.user.perfil, activo=True).exists()
            return tiene_acceso and request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']
        
        return False


class NotificacionPermission(BasePermission):
    """
    Permisos para el modelo Notificacion:
    - Todos los usuarios pueden ver y marcar como leídas sus propias notificaciones
    - Solo administradores pueden crear/eliminar notificaciones
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Otros usuarios: pueden leer y actualizar (marcar como leída)
        return request.method in ['GET', 'HEAD', 'OPTIONS', 'PATCH']
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Usuarios solo pueden ver y actualizar sus propias notificaciones
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'PATCH']:
            return obj.usuario == request.user.perfil
        
        return False


class DiplomaPermission(BasePermission):
    """
    Permisos para el modelo Diploma:
    - Administrador: CRUD completo
    - Relator: Solo lectura de diplomas de estudiantes en sus cursos
    - Estudiante: Solo lectura de sus propios diplomas
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            # Permitir verificación pública de diplomas
            if view.action == 'verificar':
                return True
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Otros usuarios: solo lectura
        return request.method in SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Solo lectura para usuarios autorizados
        if request.method in SAFE_METHODS:
            # Estudiantes: sus propios diplomas
            if tipo_usuario == 'estudiante':
                return obj.inscripcion.estudiante == request.user.perfil
            
            # Relatores: diplomas de estudiantes en sus cursos
            if tipo_usuario == 'relator':
                return obj.inscripcion.curso.relatores.filter(id=request.user.perfil.id).exists()
        
        return False


# =====================================================
# PERMISOS COMPUESTOS Y HELPERS
# =====================================================

class ReadOnlyForNonAdmin(BasePermission):
    """
    Permiso genérico: Solo lectura para no-administradores
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: acceso total
        if tipo_usuario == 'administrador':
            return True
        
        # Otros: solo lectura
        return request.method in SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso genérico: El propietario puede ver, solo admin puede modificar/eliminar
    """
    
    def has_object_permission(self, request, view, obj):
        tipo_usuario = request.user.perfil.tipo_usuario if hasattr(request.user, 'perfil') else None
        
        # Administradores: pueden todo
        if tipo_usuario == 'administrador':
            return True
        
        # Propietario: solo lectura
        if request.method in SAFE_METHODS:
            if hasattr(obj, 'usuario'):
                return obj.usuario == request.user.perfil
            if hasattr(obj, 'estudiante'):
                return obj.estudiante == request.user.perfil
            if hasattr(obj, 'relator'):
                return obj.relator == request.user.perfil
        
        return False


# =====================================================
# UTILIDADES
# =====================================================

def es_administrador(user):
    """Helper function para verificar si un usuario es administrador"""
    return (
        user and 
        user.is_authenticated and 
        hasattr(user, 'perfil') and 
        user.perfil.tipo_usuario == 'administrador'
    )


def es_relator(user):
    """Helper function para verificar si un usuario es relator"""
    return (
        user and 
        user.is_authenticated and 
        hasattr(user, 'perfil') and 
        user.perfil.tipo_usuario == 'relator'
    )


def es_estudiante(user):
    """Helper function para verificar si un usuario es estudiante"""
    return (
        user and 
        user.is_authenticated and 
        hasattr(user, 'perfil') and 
        user.perfil.tipo_usuario == 'estudiante'
    )


def tiene_acceso_curso(user, curso):
    """Helper function para verificar si un usuario tiene acceso a un curso"""
    if not user.is_authenticated:
        return False
    
    if es_administrador(user):
        return True
    
    if es_relator(user):
        return curso.relatores.filter(id=user.perfil.id).exists()
    
    if es_estudiante(user):
        return curso.inscripciones.filter(estudiante=user.perfil, activo=True).exists()
    
    return False


# =====================================================
# RESUMEN DE PERMISOS POR ROL
# =====================================================

"""
NOTA: "estudiante" = usuario regular del sistema (término simbólico)

┌─────────────────┬──────────────────┬──────────────────┬──────────────────────┐
│ MODELO          │ ADMINISTRADOR    │ RELATOR          │ ESTUDIANTE (Usuario) │
├─────────────────┼──────────────────┼──────────────────┼──────────────────────┤
│ Usuario         │ CRUD             │ R (propio)       │ R (propio)           │
│ Material        │ CRUD + Aprobar   │ C + R (propio)   │ R (aprobados)        │
│ Curso           │ CRUD             │ R (asignados)    │ R (inscritos)        │
│ Inscripción     │ CRUD             │ R (sus cursos)   │ R (propias)          │
│ Progreso        │ CRUD             │ R (sus cursos)   │ R + U (propio)       │
│ Evaluación      │ CRUD             │ R (sus cursos)   │ R (inscritos)        │
│ Foro/Tema/Resp. │ CRUD             │ R + C            │ R + C                │
│ Notificación    │ CRUD             │ R + U (propias)  │ R + U (propias)      │
│ Diploma         │ CRUD             │ R (sus cursos)   │ R (propios)          │
└─────────────────┴──────────────────┴──────────────────┴──────────────────────┘

Leyenda:
C = Create (Crear)
R = Read (Leer)
U = Update (Actualizar)
D = Delete (Eliminar)

PERMISOS ESPECÍFICOS POR ROL:

🔴 ESTUDIANTE/USUARIO (tipo_usuario='estudiante'):
   - ✅ Leer: Sus cursos inscritos, materiales aprobados, su progreso
   - ✅ Actualizar: Su propio progreso (marcar lecciones completadas)
   - ✅ Crear: Comentarios en foros de sus cursos
   - ❌ NO puede: Editar/eliminar nada, ni siquiera su propia cuenta

🟡 RELATOR (tipo_usuario='relator'):
   - ✅ Leer: Cursos asignados, progreso de sus estudiantes
   - ✅ Crear: Subir material (queda pendiente de aprobación)
   - ✅ Crear: Comentarios en foros de sus cursos
   - ❌ NO puede: Editar material subido, eliminar nada, crear/editar cursos

🟢 ADMINISTRADOR (tipo_usuario='administrador'):
   - ✅ TODO: CRUD completo en todos los modelos
   - ✅ Aprobar/Rechazar: Materiales de relatores
   - ✅ Eliminar: Usuarios, cursos, materiales, cualquier contenido
   - ✅ Gestionar: Inscripciones, diplomas, configuración del sistema
"""

# =====================================================
# FIN DE PERMISOS
# =====================================================