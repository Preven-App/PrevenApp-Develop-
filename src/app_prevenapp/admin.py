from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# IMPORTACIONES DE UNFOLD
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import *

# ==========================================
# 1. PERSONALIZACIÓN DEL USUARIO
# ==========================================
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin, ModelAdmin): # <-- Hereda de BaseUserAdmin (el alias) y ModelAdmin
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ('username', 'nombres', 'apellidos', 'correo', 'rol', 'estado')
    list_filter = ('rol', 'estado', 'is_staff')
    search_fields = ('username', 'correo', 'nombres', 'apellidos')
    list_editable = ('rol', 'estado')
    list_display_links = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'nombres', 'apellidos', 'correo', 'telefono', 'edad', 'sexo', 'eps', 'rh', 'estado')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'nombres', 'apellidos', 'correo', 'estado')}),
    )

# ==========================================
# 2. PERSONALIZACIÓN DEL PROFESIONAL
# ==========================================
@admin.register(Profesional)
class ProfesionalAdmin(ModelAdmin):
    list_display = ('usuario', 'especialidad', 'documento_identidad', 'estado')
    search_fields = ('usuario__nombres', 'usuario__apellidos', 'documento_identidad')
    list_filter = ('especialidad', 'estado')
    list_editable = ('estado',)
    list_display_links = ('usuario',)

# ==========================================
# 3. PERSONALIZACIÓN DEL TIP (Para moderación)
# ==========================================
@admin.register(Tip)
class TipAdmin(ModelAdmin):
    # Ajusta los campos a los que realmente tiene el modelo ahora
    list_display = ('titulo', 'autor', 'categoria', 'estado')
    list_filter = ('estado', 'categoria')
    search_fields = ('titulo', 'contenido')
    list_editable = ('estado',)

# ==========================================
# 4. PERSONALIZACIÓN DEL MODELO DE CITA
# ==========================================
@admin.register(Cita)
class CitaAdmin(ModelAdmin): # <-- Cambiado a ModelAdmin de Unfold
    list_display = ('usuario', 'profesional', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__nombres', 'usuario__apellidos')

# ==========================================
# 5. REGISTRO DEL RESTO DE MODELOS CON UNFOLD
# ==========================================
modelos_a_registrar = [
    Rol, Especialidad, Categoria, Actividad, ParticipacionActividad,
    Recurso, RecursoFavorito, Servicio, Chat, UsuarioChat,
    Mensaje, SalaChat, HistorialChatbot, ContactoEmergencia,
    HorarioProfesional, Inquietud, Reporte
]

# Al pasarle ModelAdmin como segundo argumento, 
# Unfold aplicará su diseño a estos modelos automáticamente.
for modelo in modelos_a_registrar:
    admin.site.register(modelo, ModelAdmin)