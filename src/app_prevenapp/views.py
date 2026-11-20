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
            return redirect('login')

    return render(request, 'app_prevenapp/login.html')


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