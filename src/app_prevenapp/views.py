import re

from django.contrib import messages
from django.db import transaction  # <-- IMPORTANTE: Importar esto
from django.shortcuts import redirect, render

from .models import (
    Especialidad,
    HorarioProfesional,
    Profesional,
    Rol,
    Usuario,
    Tip,
    Categoria
)

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

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
        
        # 🚨 IMPRIMIR EN CONSOLA PARA DEBUGGEAR
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
                    correo=email, # <--- ¡AQUÍ ESTÁ LA SOLUCIÓN AL CORREO VACÍO!
                    nombres=first_name,
                    apellidos=last_name,
                    rol=rol_db,
                    estado='Activo'
                )
                nuevo_usuario.set_password(password)

                if role_select == 'usuario' or role_select is None:
                        # Capturamos los datos
                    telefono = request.POST.get('phone')
                    edad = request.POST.get('age')
                    rh = request.POST.get('rh_factor')

                    # Si el dato viene vacío, guardamos None. Si trae número, lo convertimos a entero.
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

            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrarse: {str(e)}')
            return redirect('register')

    return render(request, 'app_prevenapp/register.html')


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


@login_required(login_url='login')
def crear_tip(request):

    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil profesional.')
        return redirect('dashboard_profesional')

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        fuente = request.POST.get('fuente', '').strip()
        fecha = request.POST.get('fecha') or None
        archivo = request.FILES.get('archivo')

        if not titulo or not descripcion:
            messages.error(request, 'Completa los campos obligatorios.')
        else:
            Tip.objects.create(
                profesional=profesional,
                titulo=titulo,
                descripcion=descripcion,
                archivo=archivo,
                fuente=fuente,
                fecha=fecha
            )

            messages.success(request, '¡Tip publicado correctamente!')
            return redirect('lista_tips')

    return render(request, 'app_prevenapp/crear_tip.html')


@login_required(login_url='login')
def lista_tips(request):

    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil profesional.')
        return redirect('dashboard_profesional')

    tips = Tip.objects.filter(
        profesional=profesional
    ).order_by('-fecha')

    return render(request, 'app_prevenapp/lista_tips.html', {
        'tips': tips
    })
    
    
@login_required(login_url='login')
def editar_tip(request, id):

    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil profesional.')
        return redirect('dashboard_profesional')

    tip = get_object_or_404(
        Tip,
        idTip=id,
        profesional=profesional
    )

    if request.method == 'POST':
        tip.titulo = request.POST.get('titulo', '').strip()
        tip.descripcion = request.POST.get('descripcion', '').strip()
        tip.fuente = request.POST.get('fuente', '').strip()
        tip.fecha = request.POST.get('fecha') or None

        nuevo_archivo = request.FILES.get('archivo')

        if nuevo_archivo:
            tip.archivo = nuevo_archivo

        if not tip.titulo or not tip.descripcion:
            messages.error(request, 'Completa los campos obligatorios.')
        else:
            tip.save()
            messages.success(request, '¡Tip actualizado correctamente!')
            return redirect('lista_tips')

    return render(request, 'app_prevenapp/editar_tip.html', {
        'tip': tip
    })

    
@login_required(login_url='login')
@require_POST
def eliminar_tip(request, id):

    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil profesional.')
        return redirect('dashboard_profesional')

    tip = get_object_or_404(
        Tip,
        idTip=id,
        profesional=profesional
    )

    tip.delete()

    messages.success(request, 'Tip eliminado correctamente.')
    return redirect('lista_tips')