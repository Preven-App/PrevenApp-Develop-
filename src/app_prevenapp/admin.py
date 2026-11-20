from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# ==========================================
# 1. PERSONALIZACIÓN DEL USUARIO
# ==========================================
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'nombres', 'apellidos', 'correo', 'rol', 'estado')
    list_filter = ('rol', 'estado', 'is_staff')
    search_fields = ('username', 'correo', 'nombres', 'apellidos')

    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'nombres', 'apellidos', 'correo', 'telefono', 'edad', 'sexo', 'eps', 'rh', 'estado')}),
    )
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
# 3. PERSONALIZACIÓN DEL TIP (Para moderación)
# ==========================================
@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'categoria')
    search_fields = ('titulo', 'contenido', 'autor__username')
    list_editable = ('estado',)

# ==========================================
# 4. REGISTRO DEL RESTO DE MODELOS
# ==========================================
modelos_a_registrar = [
    Rol, Especialidad, Categoria, Actividad, ParticipacionActividad,
    Recurso, RecursoFavorito, Servicio, Chat, UsuarioChat,
    Mensaje, SalaChat, HistorialChatbot, ContactoEmergencia,
    HorarioProfesional, Inquietud, Reporte
]

for modelo in modelos_a_registrar:
    admin.site.register(modelo)

# ==========================================
# 5. PERSONALIZACIÓN DEL MODELO DE CITA
# ==========================================
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'usuario', 'profesional', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('motivo', 'usuario__username', 'usuario__correo')