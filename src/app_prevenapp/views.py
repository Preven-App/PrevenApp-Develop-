import re
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import (
    Categoria, Cita, ContactoEmergencia, Especialidad, Profesional,
    Recurso, Rol, Tip, Usuario, Reporte, HorarioProfesional,
    Chat, Mensaje, SalaChat, UsuarioChat
)

# ==========================================
# 1. VISTAS PÚBLICAS Y DE AUTENTICACIÓN
# ==========================================

def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')


def login_view(request):
    if request.method == 'POST':
        # Capturamos lo que el usuario escribió (puede ser correo o username)
        login_input = request.POST.get('email') 
        password = request.POST.get('password')
        
        # 1. PRIMER INTENTO: Autenticación estándar (por username)
        user = authenticate(request, username=login_input, password=password)
        
        # 2. SEGUNDO INTENTO: Si falla, buscar por el campo 'correo' o 'email'
        if user is None:
            try:
                # Busca coincidencia en el campo 'correo' del modelo o en el 'email' de Django
                user_obj = Usuario.objects.filter(Q(correo=login_input) | Q(email=login_input)).first()
                if user_obj:
                    # Autenticamos usando el username real de ese usuario
                    user = authenticate(request, username=user_obj.username, password=password)
            except Exception:
                pass

        # 3. VERIFICACIÓN Y REDIRECCIÓN POR ROLES
        if user is not None:
            login(request, user)
            
            # Si es Administrador o Superusuario
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
                
            # Si tiene el rol explícito de Administrador
            elif user.rol and user.rol.nombre.lower() in ['administrador', 'admin']:
                if user.is_staff:
                    return redirect('/admin/')
                else:
                    messages.error(request, 'Tienes rol de Admin, pero no permisos de Staff.')
                    return redirect('login')
                    
            # Si es Profesional
            elif user.rol and user.rol.nombre.lower() == 'profesional':
                return redirect('dashboard_profesional')
                
            # Si es Adolescente / Usuario (Redirigimos a su nuevo Dashboard)
            else:
                messages.success(request, f'¡Bienvenido a tu espacio seguro, {user.nombres}!')
                return redirect('dashboard_usuario') # <-- AQUÍ ESTÁ EL CAMBIO PRINCIPAL
        else:
            # Si no se pudo autenticar
            messages.error(request, 'Usuario, correo o contraseña incorrectos. Intenta de nuevo.')
            return redirect('login')

    return render(request, 'app_prevenapp/login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role_select = request.POST.get('role_select')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('login') # Redirigimos al login

        if len(password) < 10 or not re.search(r'[A-Z]', password) or len(re.findall(r'\d', password)) < 5 or not re.search(r'[^A-Za-z0-9]', password):
            messages.error(request, 'La contraseña no cumple con los requisitos de seguridad.')
            return redirect('login') # Redirigimos al login

        try:
            with transaction.atomic():
                if role_select == 'profesional':
                    rol_db, _ = Rol.objects.get_or_create(nombre='Profesional')
                else:
                    rol_db, _ = Rol.objects.get_or_create(nombre='Adolescente')

                nuevo_usuario = Usuario(
                    username=email,
                    email=email,
                    correo=email,
                    nombres=first_name,
                    apellidos=last_name,
                    rol=rol_db,
                    estado='Activo'
                )
                nuevo_usuario.set_password(password)

                if role_select == 'usuario' or role_select is None:
                    telefono = request.POST.get('phone')
                    edad = request.POST.get('age')
                    rh = request.POST.get('rh_factor')

                    nuevo_usuario.telefono = telefono if telefono else None
                    try:
                        nuevo_usuario.edad = int(edad) if edad else None
                    except ValueError:
                        nuevo_usuario.edad = None
                    nuevo_usuario.rh = rh if rh else None

                nuevo_usuario.save()

                if role_select == 'profesional':
                    nombre_especialidad = request.POST.get('specialty', '').strip()
                    documento = request.POST.get('document_id')
                    licencia = request.POST.get('license')

                    if not nombre_especialidad or not documento or not licencia:
                        raise ValueError("Faltan campos obligatorios de profesional.")
                    
                    nombre_especialidad_limpio = nombre_especialidad.strip().capitalize()
                    especialidad_db, _ = Especialidad.objects.get_or_create(nombre=nombre_especialidad_limpio)
                    
                    nuevo_profesional = Profesional(
                        usuario=nuevo_usuario,
                        especialidad=especialidad_db,
                        documento_identidad=documento,
                        credencial_profesional=licencia,
                        estado='Pendiente'
                    )
                    nuevo_profesional.save()

            login(request, nuevo_usuario, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, '¡Registro exitoso!')
            
            if role_select == 'profesional':
                return redirect('dashboard_profesional')
            else:
                return redirect('dashboard_usuario')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrarse: {str(e)}')
            return redirect('login') # Redirigimos al login si falla

    # 🔴 AQUÍ ESTABA EL ERROR: Cambiamos register.html por login.html
    return render(request, 'app_prevenapp/login.html')

# ==========================================
# 2. VISTAS DE USUARIOS (ADOLESCENTES)
# ==========================================

@login_required
def servicios_view(request):
    return render(request, 'app_prevenapp/servicios.html')

@login_required
def estadisticas(request):
    return render(request, 'app_prevenapp/estadisticas.html')

@login_required
def citas_view(request):
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        notas = request.POST.get('notas', '').strip()

        if motivo and fecha and hora:
            Cita.objects.create(usuario=request.user, motivo=motivo, fecha=fecha, hora=hora, notas=notas)
            messages.success(request, 'Tu cita ha sido registrada con estado Pendiente.')
            return redirect('citas')
        messages.error(request, 'Por favor completa el motivo, la fecha y la hora.')

    citas = Cita.objects.filter(usuario=request.user)
    return render(request, 'app_prevenapp/citas.html', {'citas': citas})

@login_required
def recursos_view(request):
    # (Tu lógica existente para recursos)
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        categoria_id = request.POST.get('categoria')
        tipo = request.POST.get('tipo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if titulo and categoria_id:
            categoria = Categoria.objects.filter(pk=categoria_id).first()
            if categoria:
                Recurso.objects.create(categoria=categoria, titulo=titulo, tipo=tipo or 'Guía', descripcion=descripcion, creado_por=getattr(request.user, 'idUsuario', request.user.pk))
                messages.success(request, 'El recurso se registró correctamente.')
                return redirect('recursos')
        messages.error(request, 'Completa al menos el título y la categoría.')

    buscar = request.GET.get('q', '').strip()
    categoria_seleccionada = request.GET.get('categoria', '').strip()
    recursos = Recurso.objects.select_related('categoria').order_by('-idRecurso')
    if buscar:
        recursos = recursos.filter(titulo__icontains=buscar) | recursos.filter(descripcion__icontains=buscar)
    if categoria_seleccionada:
        recursos = recursos.filter(categoria__idCategoria=categoria_seleccionada)

    return render(request, 'app_prevenapp/recursos.html', {'recursos': recursos, 'categorias': Categoria.objects.all(), 'buscar': buscar, 'categoria_seleccionada': categoria_seleccionada})

@login_required
def ajustes_view(request):
    usuario = request.user
    contacto = ContactoEmergencia.objects.filter(usuario=usuario).first()
    
    if request.method == 'POST':
        seccion = request.POST.get('seccion', 'perfil')
        
        if seccion == 'perfil':
            # 1. Actualizamos los campos de texto
            usuario.nombres = request.POST.get('nombres', '').strip()
            usuario.apellidos = request.POST.get('apellidos', '').strip()
            usuario.correo = request.POST.get('correo', '').strip()
            usuario.telefono = request.POST.get('telefono', '').strip()
            usuario.eps = request.POST.get('eps', '').strip()
            usuario.rh = request.POST.get('rh', '').strip()
            
            edad_raw = request.POST.get('edad', '').strip()
            usuario.edad = int(edad_raw) if edad_raw.isdigit() else None
            usuario.sexo = request.POST.get('sexo', '').strip() or None
            
            # 🔴 2. CAPTURAMOS LA FOTO DE PERFIL
            # Verificamos si el usuario subió un archivo en el input con name="foto_perfil"
            if 'foto_perfil' in request.FILES:
                usuario.foto_perfil = request.FILES['foto_perfil']
                
            # 3. Guardamos todos los cambios en la base de datos
            usuario.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('ajustes')
            
        elif seccion == 'emergencia':
            # Lógica para guardar el contacto de emergencia
            nombre_contacto = request.POST.get('contacto_nombre', '').strip()
            telefono_contacto = request.POST.get('contacto_telefono', '').strip()
            
            if contacto:
                # Si ya existe, actualizamos
                contacto.nombre = nombre_contacto
                contacto.telefono = telefono_contacto
                contacto.save()
            else:
                # Si no existe, creamos uno nuevo vinculado al usuario
                ContactoEmergencia.objects.create(
                    usuario=usuario,
                    nombre=nombre_contacto,
                    telefono=telefono_contacto
                )
                
            messages.success(request, 'Contacto de emergencia actualizado.')
            return redirect('ajustes')

    return render(request, 'app_prevenapp/ajustes.html', {'usuario': usuario, 'contacto': contacto})

# Tips (Público/Adolescentes)
@login_required
def listar_tips_view(request):
    tips_aprobados = Tip.objects.filter(estado='Aprobado')
    return render(request, 'app_prevenapp/listar_tips.html', {'tips': tips_aprobados})

@login_required
def registrar_tip(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria_id = request.POST.get('categoria')
        if titulo and contenido:
            categoria_obj = Categoria.objects.filter(idCategoria=categoria_id).first() if categoria_id else None
            Tip.objects.create(titulo=titulo, contenido=contenido, categoria=categoria_obj, autor=request.user, estado='Pendiente')
            messages.success(request, '¡Tip registrado con éxito!')
            return redirect('registrar_tip')
        else:
            messages.error(request, 'Completa los campos obligatorios.')
    return render(request, 'app_prevenapp/registrar_tip.html', {'categorias': categorias})


# ==========================================
# 3. VISTAS DEL PROFESIONAL (DASHBOARD)
# ==========================================

@login_required(login_url='login')
def dashboard_profesional(request):
    return render(request, 'app_prevenapp/dashboard_profesional.html')

@login_required(login_url='login')
def configurar_horario(request):
    profesional = request.user.profesional
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin') or None
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        dias_guardados = 0

        for dia in dias:
            if request.POST.get(f'{dia}_activo') == '1':
                HorarioProfesional.objects.create(
                    profesional=profesional,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    dias_semana=dia.capitalize(),
                    hora_inicio=request.POST.get(f'{dia}_inicio'),
                    hora_fin=request.POST.get(f'{dia}_fin'),
                    num_citas=request.POST.get(f'{dia}_citas')
                )
                dias_guardados += 1

        if dias_guardados > 0:
            messages.success(request, f'¡Éxito! Se guardaron {dias_guardados} días de disponibilidad.')
            return redirect('ver_horarios')
        else:
            messages.error(request, 'Debes activar al menos un día.')
            return redirect('configurar_horario')
    return render(request, 'app_prevenapp/configurar_horario.html')

@login_required(login_url='login')
def ver_horarios(request):
    try:
        horarios = HorarioProfesional.objects.filter(profesional=request.user.profesional).order_by('idHorario_Profesional')
    except Exception:
        horarios = []
    return render(request, 'app_prevenapp/ver_horarios.html', {'horarios': horarios})

@login_required(login_url='login')
def eliminar_horario(request, id):
    horario = get_object_or_404(HorarioProfesional, idHorario_Profesional=id, profesional=request.user.profesional)
    horario.delete()
    return redirect('ver_horarios')

@login_required(login_url='login')
def perfil_profesional(request):
    if request.method == 'POST':
        usuario = request.user
        usuario.nombres = request.POST.get('nombres')
        usuario.apellidos = request.POST.get('apellidos')
        usuario.correo = request.POST.get('correo')
        usuario.telefono = request.POST.get('telefono')
        if 'foto_perfil' in request.FILES:
            usuario.foto_perfil = request.FILES['foto_perfil']
        usuario.save()
        messages.success(request, '¡Perfil actualizado exitosamente!')
        return redirect('perfil_profesional')
    return render(request, 'app_prevenapp/perfil_profesional.html')

@login_required(login_url='login')
def reportes_profesional(request):
    try:
        profesional = request.user.profesional
        reportes = Reporte.objects.filter(profesional=profesional).select_related('usuario').order_by('-fecha')
        kpis = {
            'pacientes_asignados': reportes.values('usuario').distinct().count(),
            'en_riesgo_alto': reportes.filter(nivel_riesgo='Alto').values('usuario').distinct().count(),
            'reportes_pendientes': reportes.filter(observaciones__isnull=True).count(),
        }
    except Profesional.DoesNotExist:
        reportes = []
        kpis = {'pacientes_asignados': 0, 'en_riesgo_alto': 0, 'reportes_pendientes': 0}
    return render(request, 'app_prevenapp/reportes_profesional.html', {'reportes': reportes, 'kpis': kpis})

@login_required(login_url='login')
def recursos_profesional(request):
    return render(request, 'app_prevenapp/recursos_profesional.html')

# Tips (Gestión del Profesional)
@login_required(login_url='login')
def crear_tip(request):
    categorias = Categoria.objects.all()
    
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil profesional.')
        return redirect('dashboard_profesional')

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        contenido = request.POST.get('descripcion', '').strip() # Recibimos el texto del HTML
        categoria_id = request.POST.get('categoria')
        fuente = request.POST.get('fuente', '').strip()
        fecha = request.POST.get('fecha') or None
        archivo = request.FILES.get('archivo')

        if not titulo or not contenido or not categoria_id:
            messages.error(request, 'Completa los campos obligatorios.')
        else:
            categoria_obj = Categoria.objects.filter(idCategoria=categoria_id).first()
            
            # Guardamos en el campo 'contenido' del modelo
            Tip.objects.create(
                autor=request.user, 
                titulo=titulo, 
                contenido=contenido, 
                categoria=categoria_obj, 
                archivo=archivo, 
                fuente=fuente, 
                fecha=fecha,
                estado='Pendiente'
            )
            messages.success(request, '¡Tip publicado correctamente!')
            return redirect('lista_tips')
            
    return render(request, 'app_prevenapp/crear_tip.html', {'categorias': categorias})

@login_required(login_url='login')
def lista_tips(request):
    # 🔴 CORREGIDO: Filtramos por 'autor' (el usuario logueado), no por 'profesional'
    tips = Tip.objects.filter(autor=request.user).order_by('-fecha')
    
    return render(request, 'app_prevenapp/lista_tips.html', {'tips': tips})

@login_required(login_url='login')
def editar_tip(request, id):
    # 🔴 CORREGIDO: Buscamos por 'autor' (el usuario logueado) en lugar de 'profesional'
    tip = get_object_or_404(Tip, idTip=id, autor=request.user)

    if request.method == 'POST':
        tip.titulo = request.POST.get('titulo', '').strip()
        
        # Capturamos el texto del formulario. 
        # Guardamos en 'contenido' (o 'descripcion' dependiendo de cómo esté tu modelo)
        texto_ingresado = request.POST.get('descripcion', '').strip()
        tip.contenido = texto_ingresado 
        if hasattr(tip, 'descripcion'): # Si tu modelo usa 'descripcion', también lo actualizamos
            tip.descripcion = texto_ingresado

        tip.fuente = request.POST.get('fuente', '').strip()
        tip.fecha = request.POST.get('fecha') or None

        nuevo_archivo = request.FILES.get('archivo')
        if nuevo_archivo:
            tip.archivo = nuevo_archivo

        if not tip.titulo or not texto_ingresado:
            messages.error(request, 'Completa los campos obligatorios.')
        else:
            tip.save()
            messages.success(request, '¡Tip actualizado correctamente!')
            return redirect('lista_tips')

    return render(request, 'app_prevenapp/editar_tip.html', {'tip': tip})


@login_required(login_url='login')
@require_POST
def eliminar_tip(request, id):
    # 🔴 CORREGIDO: Buscamos por 'autor' en lugar de 'profesional'
    tip = get_object_or_404(Tip, idTip=id, autor=request.user)
    
    tip.delete()
    messages.success(request, 'Tip eliminado correctamente.')
    return redirect('lista_tips')

# ==========================================
# 4. VISTAS DE CHAT (SALAS)
# ==========================================

@login_required(login_url='login')
def salas_chat(request, sala_id=None):
    salas = SalaChat.objects.select_related('profesional', 'profesional__usuario').order_by('-idSala_chat')

    if request.method == 'POST' and request.POST.get('accion') == 'crear_sala':
        tema = (request.POST.get('tema') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        profesional = getattr(request.user, 'profesional', None)

        if not profesional:
            messages.error(request, 'Solo los profesionales pueden crear salas.')
            return redirect('salas_chat')

        if not tema:
            messages.error(request, 'Debes escribir un tema para la sala.')
            return redirect('salas_chat')

        nueva_sala = SalaChat.objects.create(profesional=profesional, tema=tema, descripcion=descripcion, estado='Activa', fecha=timezone.now())
        _obtener_o_crear_chat_de_sala(nueva_sala, request.user)
        messages.success(request, 'Sala creada correctamente.')
        return redirect('detalle_sala_chat', sala_id=nueva_sala.idSala_chat)

    sala_activa = None
    chat_activo = None
    mensajes_sala = []

    if sala_id is not None:
        sala_activa = get_object_or_404(SalaChat, idSala_chat=sala_id)
    elif salas.exists():
        sala_activa = salas.first()

    if sala_activa is not None:
        chat_activo = _obtener_o_crear_chat_de_sala(sala_activa, request.user)
        if request.method == 'POST' and request.POST.get('accion') == 'enviar_mensaje':
            contenido = (request.POST.get('mensaje') or '').strip()
            if contenido:
                Mensaje.objects.create(chat=chat_activo, usuario=request.user, mensaje=contenido, fecha=timezone.now())
            return redirect('detalle_sala_chat', sala_id=sala_activa.idSala_chat)

        mensajes_sala = Mensaje.objects.filter(chat=chat_activo).select_related('usuario').order_by('fecha', 'idMensaje')

    contexto = {
        'salas': salas,
        'sala_activa': sala_activa,
        'mensajes_sala': mensajes_sala,
        'es_profesional': hasattr(request.user, 'profesional'),
    }
    return render(request, 'app_prevenapp/salas_chat.html', contexto)

def _obtener_o_crear_chat_de_sala(sala, usuario):
    """Obtiene o crea un Chat asociado a una SalaChat y vincula al usuario."""
    titulo_sala = f"Sala #{sala.idSala_chat}: {sala.tema or 'General'}"
    chat = Chat.objects.filter(titulo=titulo_sala, tipo='sala').first()

    if chat is None:
        creador_id = sala.profesional.usuario.idUsuario if sala.profesional and sala.profesional.usuario else None
        chat = Chat.objects.create(titulo=titulo_sala, tipo='sala', creado_por=creador_id, fecha=timezone.now())

    if usuario.is_authenticated:
        UsuarioChat.objects.get_or_create(chat=chat, usuario=usuario)

    return chat

@login_required(login_url='login')
def dashboard_usuario(request):
    return render(request, 'app_prevenapp/dashboard_usuario.html')

# Vista temporal para el chatbot
@login_required(login_url='login')
def chatbot_view(request):
    return render(request, 'app_prevenapp/chatbot.html') # Tendrás que crear este HTML luego