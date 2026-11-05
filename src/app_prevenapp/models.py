from django.contrib.auth.models import AbstractUser
from django.db import models

# ==========================================
# 1. USUARIOS Y ROLES
# ==========================================

class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre or f"Rol {self.idRol}"

class Usuario(AbstractUser):
    # Al heredar de AbstractUser ya tienes: username, password, email, first_name, last_name, etc.
    # Adaptamos los campos de tu BD:
    idUsuario = models.AutoField(primary_key=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column='Rol_idRol')
    nombres = models.CharField(max_length=45, null=True, blank=True)
    apellidos = models.CharField(max_length=45, null=True, blank=True)
    correo = models.EmailField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=20, null=True, blank=True)
    # nivel_educativo = models.CharField(max_length=45, null=True, blank=True) # Lo dejé comentado por tu instrucción
    eps = models.CharField(max_length=45, null=True, blank=True)
    rh = models.CharField(max_length=10, null=True, blank=True)
    estado = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.correo})"

class Especialidad(models.Model):
    idEspecialidad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre or "Sin especialidad"

class Profesional(models.Model):
    idProfesional = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, db_column='Especialidad_idEspecialidad')
    documento_identidad = models.CharField(max_length=20)
    credencial_profesional = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Profesional: {self.usuario.nombres} {self.usuario.apellidos}"

# ==========================================
# 2. CATEGORÍAS Y CONTENIDO (Actividades, Recursos, Tips)
# ==========================================

class Categoria(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45, null=True, blank=True)

    def __str__(self):
        return self.nombre or "Sin categoría"

class Actividad(models.Model):
    idActividad = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='Categoria_idCategoria')
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    objetivos = models.TextField(null=True, blank=True)
    instrucciones = models.TextField(null=True, blank=True)
    nivel_dificultad = models.CharField(max_length=20, null=True, blank=True)
    recursos_multimedia = models.CharField(max_length=255, null=True, blank=True)
    frecuencia = models.CharField(max_length=45, null=True, blank=True)
    duracion = models.CharField(max_length=20, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    creado_por = models.IntegerField(null=True, blank=True) # Podría ser un ForeignKey a Usuario si lo prefieres

class ParticipacionActividad(models.Model):
    idParticipacion_actividad = models.AutoField(primary_key=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='Actividad_idActividad')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    resultado = models.CharField(max_length=255, null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

class Recurso(models.Model):
    idRecurso = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='Categoria_idCategoria')
    titulo = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=45, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    creado_por = models.IntegerField(null=True, blank=True)

class RecursoFavorito(models.Model):
    idRecurso_Favorito = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, db_column='Recurso_idRecurso')
    fecha_guardado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'recurso') # Evita que un usuario guarde el mismo recurso dos veces

class Tip(models.Model):
    idTip = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='Categoria_idCategoria')
    profesional = models.ForeignKey(Profesional, on_delete=models.PROTECT, db_column='Profesional_idProfesional')
    titulo = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    archivos_enlaces = models.CharField(max_length=255, null=True, blank=True)
    fuente = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)

class Servicio(models.Model):
    idServicio = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='Categoria_idCategoria')
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=45, null=True, blank=True)
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    horario = models.CharField(max_length=100, null=True, blank=True)
    contacto = models.CharField(max_length=100, null=True, blank=True)

# ==========================================
# 3. CHATS Y COMUNICACIÓN
# ==========================================

class Chat(models.Model):
    idChat = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=45, null=True, blank=True)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    creado_por = models.IntegerField(null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

class UsuarioChat(models.Model):
    idUsuario_chat = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, db_column='Chat_idChat')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')

class Mensaje(models.Model):
    idMensaje = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, db_column='Chat_idChat')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='Usuario_idUsuario')
    mensaje = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

class SalaChat(models.Model):
    idSala_chat = models.AutoField(primary_key=True)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, db_column='Profesional_idProfesional')
    tema = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

class HistorialChatbot(models.Model):
    idHistorial_chat = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    pregunta = models.TextField(null=True, blank=True)
    respuesta = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

# ==========================================
# 4. GESTIÓN DE CITAS, HORARIOS Y EMERGENCIAS
# ==========================================

class ContactoEmergencia(models.Model):
    idContacto_Emergencia = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    nombre = models.CharField(max_length=45, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.EmailField(max_length=100, null=True, blank=True)

class Cita(models.Model):
    idCita = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, db_column='Profesional_idProfesional')
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, null=True, blank=True)

class HorarioProfesional(models.Model):
    idHorario_Profesional = models.AutoField(primary_key=True)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, db_column='Profesional_idProfesional')
    dias_semana = models.CharField(max_length=100, null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    num_citas = models.IntegerField(null=True, blank=True)
    notificaciones_activas = models.BooleanField(default=True)

# ==========================================
# 5. INQUIETUDES Y REPORTES
# ==========================================

class Inquietud(models.Model):
    idInquietud = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='Usuario_idUsuario')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='Categoria_idCategoria')
    titulo = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='Pendiente', null=True, blank=True)

class Reporte(models.Model):
    idReporte = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='Usuario_idUsuario')
    profesional = models.ForeignKey(Profesional, on_delete=models.PROTECT, db_column='Profesional_idProfesional')
    observaciones = models.TextField(null=True, blank=True)
    nivel_riesgo = models.CharField(max_length=45, null=True, blank=True)
    indicadores_seguimiento = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)