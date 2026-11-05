from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# ==========================================
# 1. PERSONALIZACIÓN DEL USUARIO (Muy importante)
# ==========================================
# Como Usuario hereda de AbstractUser, debemos usar UserAdmin
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Columnas que se verán en la tabla principal
    list_display = ('username', 'nombres', 'apellidos', 'correo', 'rol', 'estado')
    # Filtros laterales
    list_filter = ('rol', 'estado', 'is_staff')
    # Barra de búsqueda
    search_fields = ('username', 'correo', 'nombres', 'apellidos')
    
    # Agregamos nuestros campos personalizados al formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'nombres', 'apellidos', 'correo', 'telefono', 'edad', 'sexo', 'eps', 'rh', 'estado')}),
    )
    # Agregamos campos al formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'nombres', 'apellidos', 'correo', 'estado')}),
    )

# ==========================================
# 2. PERSONALIZACIÓN DEL PROFESIONAL
# ==========================================
@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'especialidad', 'documento_identidad', 'estado')
    search_fields = ('usuario__nombres', 'usuario__apellidos', 'documento_identidad')
    list_filter = ('especialidad', 'estado')

# ==========================================
# 3. REGISTRO DEL RESTO DE MODELOS
# ==========================================
# Para no escribir 20 líneas, usamos un bucle para registrar los demás
modelos_a_registrar = [
    Rol, Especialidad, Categoria, Actividad, ParticipacionActividad,
    Recurso, RecursoFavorito, Tip, Servicio, Chat, UsuarioChat,
    Mensaje, SalaChat, HistorialChatbot, ContactoEmergencia, Cita,
    HorarioProfesional, Inquietud, Reporte
]

for modelo in modelos_a_registrar:
    admin.site.register(modelo)