import re

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .models import (
    Categoria,
    Cita,
    ContactoEmergencia,
    Especialidad,
    Profesional,
    Recurso,
    Rol,
    Tip,
    Usuario,
)


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
            Tip.objects.create(
                titulo=titulo,
                contenido=contenido,
                categoria=categoria_obj,
                autor=request.user,
                estado='Pendiente'
            )
            messages.success(request, '¡Tip registrado con éxito! Queda en espera de verificación por el administrador o un profesional.')
            return redirect('registrar_tip')
        else:
            messages.error(request, 'Por favor completa los campos obligatorios.')

    return render(request, 'app_prevenapp/registrar_tip.html', {'categorias': categorias})


@login_required
def estadisticas(request):
    return render(request, 'app_prevenapp/estadisticas.html')


@login_required
def servicios_view(request):
    return render(request, 'app_prevenapp/servicios.html')

from .models import Especialidad, HorarioProfesional, Profesional, Rol, Usuario
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Autenticar usando el backend configurado
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('servicios')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

#-----------------------------------------------------------
from django.utils import timezone
from .models import (
    Chat,
    Especialidad,
    HorarioProfesional,
    Mensaje,
    Profesional,
    Rol,
    SalaChat,
    Usuario,
    UsuarioChat,
)
#-------------------------------------------------------------

def login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email') # Lo que el usuario escribió
        password = request.POST.get('password')
        
        print(f"--> Intentando iniciar sesión con: {email_input}")
        
        # 1. Intentar autenticar (Django buscará en el campo 'username')
        user = authenticate(request, username=email_input, password=password)
        
        # 2. Si falla, es posible que hayan escrito su correo y el username sea diferente
        if user is None:
            from .models import Usuario
            try:
                # Buscamos al usuario por el campo 'correo'
                user_obj = Usuario.objects.get(correo=email_input)
                # Intentamos autenticar con su 'username' real
                user = authenticate(request, username=user_obj.username, password=password)
            except Usuario.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            print(f"--> Usuario autenticado: {user.username}")
            print(f"--> ¿Es superuser?: {user.is_superuser}")
            print(f"--> ¿Es staff?: {user.is_staff}")
            
            # Lógica de redirección
            if user.is_superuser or user.is_staff:
                print("--> Redirigiendo a /admin/")
                return redirect('/admin/')
                
            elif user.rol and user.rol.nombre.lower() in ['administrador', 'admin']:
                if user.is_staff:
                    print("--> Redirigiendo a /admin/ (por rol)")
                    return redirect('/admin/')
                else:
                    print("--> Error: Tiene rol admin pero no es staff")
                    messages.error(request, 'No tienes permisos de Staff. Contacta al superadmin.')
                    return redirect('login')
                    
            elif user.rol and user.rol.nombre.lower() == 'profesional':
                print("--> Redirigiendo a dashboard profesional")
                return redirect('dashboard_profesional')
                
            else:
                print("--> Redirigiendo a landing (usuario normal)")
                messages.success(request, '¡Bienvenido!')
                return redirect('landing')
        else:
            print("--> ERROR: Credenciales inválidas")
            messages.error(request, 'Correo o contraseña incorrectos. Intenta de nuevo.')
            return redirect('login')

    return render(request, 'app_prevenapp/login.html')

@login_required(login_url='login') # Protege la vista
def dashboard_profesional(request):
    return render(request, 'app_prevenapp/dashboard_profesional.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role_select = request.POST.get('role_select')

        print(f"DEBUG: El rol seleccionado es -> {role_select}")

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('register')

        if len(password) < 10 or not re.search(r'[A-Z]', password) or len(re.findall(r'\d', password)) < 5 or not re.search(r'[^A-Za-z0-9]', password):
            messages.error(request, 'La contraseña no cumple con los requisitos de seguridad.')
            return redirect('register')

        try:
            with transaction.atomic():
                # Asignar rol
                if role_select == 'profesional':
                    rol_db, _ = Rol.objects.get_or_create(nombre='Profesional')
                else:
                    rol_db, _ = Rol.objects.get_or_create(nombre='Adolescente')

                # Crear el Usuario
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
                    nuevo_usuario.edad = int(edad) if edad and edad.isdigit() else None
                    nuevo_usuario.rh = rh if rh else None

                nuevo_usuario.save()

                # Crear el Profesional
                if role_select == 'profesional':
                    nombre_especialidad = request.POST.get('specialty', '').strip()
                    documento = request.POST.get('document_id')
                    licencia = request.POST.get('license')

                    if not nombre_especialidad or not documento or not licencia:
                        raise ValueError("Los campos de profesional están incompletos. Revisa el formulario.")

                    especialidad_db, _ = Especialidad.objects.get_or_create(nombre=nombre_especialidad)

                    nuevo_profesional = Profesional(
                        usuario=nuevo_usuario,
                        especialidad=especialidad_db,
                        documento_identidad=documento,
                        credencial_profesional=licencia,
                        estado='Pendiente'
                    )
                    nuevo_profesional.save()

            # Autenticamos al usuario inmediatamente después del registro y lo redirigimos a 'servicios'
            login(request, nuevo_usuario, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, '¡Registro exitoso!')
            return redirect('servicios')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrarse: {str(e)}')
            return redirect('register')

    return render(request, 'app_prevenapp/register.html')


@login_required
def citas_view(request):
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        notas = request.POST.get('notas', '').strip()

        if motivo and fecha and hora:
            Cita.objects.create(
                usuario=request.user,
                motivo=motivo,
                fecha=fecha,
                hora=hora,
                notas=notas
            )
            messages.success(request, 'Tu cita ha sido registrada con estado Pendiente.')
            return redirect('citas')
        messages.error(request, 'Por favor completa el motivo, la fecha y la hora.')

    citas = Cita.objects.filter(usuario=request.user)
    return render(request, 'app_prevenapp/citas.html', {'citas': citas})


@login_required
def recursos_view(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        categoria_id = request.POST.get('categoria')
        tipo = request.POST.get('tipo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if titulo and categoria_id:
            categoria = Categoria.objects.filter(pk=categoria_id).first()
            if categoria:
                Recurso.objects.create(
                    categoria=categoria,
                    titulo=titulo,
                    tipo=tipo or 'Guía',
                    descripcion=descripcion,
                    creado_por=getattr(request.user, 'idUsuario', request.user.pk)
                )
                messages.success(request, 'El recurso educativo se registró correctamente.')
                return redirect('recursos')
        messages.error(request, 'Completa al menos el título y la categoría del recurso.')

    buscar = request.GET.get('q', '').strip()
    categoria_seleccionada = request.GET.get('categoria', '').strip()

    recursos = Recurso.objects.select_related('categoria').order_by('-idRecurso')
    if buscar:
        recursos = recursos.filter(titulo__icontains=buscar) | recursos.filter(descripcion__icontains=buscar)
    if categoria_seleccionada:
        recursos = recursos.filter(categoria__idCategoria=categoria_seleccionada)

    categorias = Categoria.objects.all()

    return render(request, 'app_prevenapp/recursos.html', {
        'recursos': recursos,
        'categorias': categorias,
        'buscar': buscar,
        'categoria_seleccionada': categoria_seleccionada,
    })


@login_required
def ajustes_view(request):
    usuario = request.user
    contacto = ContactoEmergencia.objects.filter(usuario=usuario).first()

    if request.method == 'POST':
        seccion = request.POST.get('seccion', 'perfil')

        if seccion == 'perfil':
            usuario.nombres = request.POST.get('nombres', '').strip()
            usuario.apellidos = request.POST.get('apellidos', '').strip()
            usuario.correo = request.POST.get('correo', '').strip()
            usuario.telefono = request.POST.get('telefono', '').strip()
            usuario.eps = request.POST.get('eps', '').strip()
            usuario.rh = request.POST.get('rh', '').strip()

            edad_raw = request.POST.get('edad', '').strip()
            usuario.edad = int(edad_raw) if edad_raw.isdigit() else None

            sexo_raw = request.POST.get('sexo', '').strip()
            usuario.sexo = sexo_raw or None

            usuario.save()
            messages.success(request, 'Tu información de perfil se actualizó correctamente.')
            return redirect('ajustes')

        elif seccion == 'emergencia':
            nombre_contacto = request.POST.get('contacto_nombre', '').strip()
            telefono_contacto = request.POST.get('contacto_telefono', '').strip()
            correo_contacto = request.POST.get('contacto_correo', '').strip()

            if nombre_contacto or telefono_contacto or correo_contacto:
                if contacto:
                    contacto.nombre = nombre_contacto
                    contacto.telefono = telefono_contacto
                    contacto.correo = correo_contacto or None
                    contacto.save()
                else:
                    ContactoEmergencia.objects.create(
                        usuario=usuario,
                        nombre=nombre_contacto,
                        telefono=telefono_contacto,
                        correo=correo_contacto or None
                    )
                messages.success(request, 'Tu contacto de emergencia se guardó correctamente.')
            else:
                messages.error(request, 'Ingresa al menos el nombre o teléfono del contacto de emergencia.')
            return redirect('ajustes')

    return render(request, 'app_prevenapp/ajustes.html', {
        'usuario': usuario,
        'contacto': contacto,
    })
def dashboard_profesional(request):
    # Aquí luego irá la lógica para verificar si el usuario es realmente un profesional
    return render(request, 'app_prevenapp/dashboard_profesional.html')

@login_required(login_url='login')
def configurar_horario(request):
    
    # Obtenemos el perfil del profesional logueado
    profesional = request.user.profesional

    if request.method == 'POST':
        # 1. Capturamos las fechas globales
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
        # Si la fecha fin viene vacía, guardamos None en la BD
        if not fecha_fin:
            fecha_fin = None

        # 2. Definimos los días de la semana para iterar
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        dias_guardados = 0

        # 3. Iteramos sobre cada día
        for dia in dias:
            # Verificamos si el checkbox de ese día fue marcado (envía "1")
            if request.POST.get(f'{dia}_activo') == '1':
                hora_inicio = request.POST.get(f'{dia}_inicio')
                hora_fin = request.POST.get(f'{dia}_fin')
                num_citas = request.POST.get(f'{dia}_citas')

                # Guardamos el día en la base de datos
                HorarioProfesional.objects.create(
                    profesional=profesional,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    dias_semana=dia.capitalize(), # Ej: "Lunes"
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    num_citas=num_citas
                )
                dias_guardados += 1

        # 4. Mostramos mensaje de éxito
        if dias_guardados > 0:
            messages.success(request, f'¡Éxito! Se guardaron {dias_guardados} días de disponibilidad.')
            return redirect('ver_horarios') # Redirigimos a la lista de horarios
        else:
            messages.error(request, 'Debes activar al menos un día para guardar un horario.')
            return redirect('configurar_horario')

    return render(request, 'app_prevenapp/configurar_horario.html')

@login_required(login_url='login')
def ver_horarios(request):
    try:
        # Obtenemos el perfil del profesional
        profesional = request.user.profesional
        
        # Buscamos todos sus horarios en la BD (ordenados por ID)
        horarios = HorarioProfesional.objects.filter(profesional=profesional).order_by('idHorario_Profesional')
    except Exception:
        # Si por alguna razón no tiene perfil de profesional, enviamos una lista vacía
        horarios = []

    # Enviamos la variable 'horarios' al HTML
    return render(request, 'app_prevenapp/ver_horarios.html', {'horarios': horarios})


@login_required(login_url='login')
def eliminar_horario(request, id):
    horario = get_object_or_404(HorarioProfesional, idHorario_Profesional=id, profesional=request.user.profesional)
    horario.delete()
    return redirect('ver_horarios')

@login_required(login_url='login')
def perfil_profesional(request):
    if request.method == 'POST':
        # 1. Obtenemos el usuario actual
        usuario = request.user
        
        # 2. Actualizamos los campos de texto
        usuario.nombres = request.POST.get('nombres')
        usuario.apellidos = request.POST.get('apellidos')
        usuario.correo = request.POST.get('correo')
        usuario.telefono = request.POST.get('telefono')
        
        # 3. Verificamos si el usuario subió una nueva foto
        # request.FILES es vital para manejar archivos
        if 'foto_perfil' in request.FILES:
            usuario.foto_perfil = request.FILES['foto_perfil']

        # 4. Guardamos los cambios en la Base de Datos
        usuario.save()
        
        messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
        return redirect('perfil_profesional')

    return render(request, 'app_prevenapp/perfil_profesional.html')

#------------------------------------------------------------------------------------
@login_required(login_url='login')
def salas_chat(request, sala_id=None):
    salas = SalaChat.objects.select_related('profesional', 'profesional__usuario').order_by('-idSala_chat')

    # Permitir crear una nueva sala si el usuario tiene perfil de Profesional
    if request.method == 'POST' and request.POST.get('accion') == 'crear_sala':
        tema = (request.POST.get('tema') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        profesional = getattr(request.user, 'profesional', None)

        if not profesional:
            messages.error(request, 'Solo los usuarios con perfil profesional pueden crear nuevas salas.')
            return redirect('salas_chat')

        if not tema:
            messages.error(request, 'Debes escribir un tema para la sala.')
            return redirect('salas_chat')

        nueva_sala = SalaChat.objects.create(
            profesional=profesional,
            tema=tema,
            descripcion=descripcion,
            estado='Activa',
            fecha=timezone.now(),
        )
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
                Mensaje.objects.create(
                    chat=chat_activo,
                    usuario=request.user,
                    mensaje=contenido,
                    fecha=timezone.now(),
                )
            return redirect('detalle_sala_chat', sala_id=sala_activa.idSala_chat)

        mensajes_sala = (
            Mensaje.objects.filter(chat=chat_activo)
            .select_related('usuario')
            .order_by('fecha', 'idMensaje')
        )

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
        creador_id = (
            sala.profesional.usuario.idUsuario
            if sala.profesional and sala.profesional.usuario
            else None
        )
        chat = Chat.objects.create(
            titulo=titulo_sala,
            tipo='sala',
            creado_por=creador_id,
            fecha=timezone.now(),
        )

    if usuario.is_authenticated:
        UsuarioChat.objects.get_or_create(chat=chat, usuario=usuario)

    return chat
#-----------------------------------------------------------------------------------------------------
