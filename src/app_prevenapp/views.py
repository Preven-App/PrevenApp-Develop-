import re

from django.contrib import messages
from django.db import transaction  # <-- IMPORTANTE: Importar esto
from django.shortcuts import redirect, render

from .models import Especialidad, Profesional, Rol, Usuario


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