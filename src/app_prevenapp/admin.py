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
class UsuarioAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ('username', 'nombres', 'apellidos', 'correo', 'rol', 'estado')
    list_filter = ('rol', 'estado', 'is_staff')
    search_fields = ('username', 'correo', 'nombres', 'apellidos')
    
    # 🔴 ESTO ES LO NUEVO: Permite editar estos campos directamente en la tabla
    list_editable = ('rol', 'estado') 
    
    # Le decimos a Django que el username sea el enlace para entrar a editar todo
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
    
    # 🔴 LO NUEVO: Permite editar el estado directamente en la tabla
    list_editable = ('estado',) 
    
    # Le decimos a Django que el 'usuario' sea el enlace para abrir la ventana de edición completa
    list_display_links = ('usuario',) 
# ==========================================
# 3. REGISTRO DEL RESTO DE MODELOS CON UNFOLD
# ==========================================
modelos_a_registrar = [
    Rol, Especialidad, Categoria, Actividad, ParticipacionActividad,
    Recurso, RecursoFavorito, Tip, Servicio, Chat, UsuarioChat,
    Mensaje, SalaChat, HistorialChatbot, ContactoEmergencia, Cita,
    HorarioProfesional, Inquietud, Reporte
]

# Al pasarle ModelAdmin como segundo argumento, 
# Unfold aplicará su diseño a estos modelos automáticamente.
for modelo in modelos_a_registrar:
    admin.site.register(modelo, ModelAdmin)