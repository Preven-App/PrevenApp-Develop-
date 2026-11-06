import re

from django.contrib import messages
from django.db import transaction  # <-- IMPORTANTE: Importar esto
from django.shortcuts import redirect, render

from .models import Especialidad, Profesional, Rol, Usuario


def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')

def login_view(request):
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


def dashboard_profesional(request):
    # Aquí luego irá la lógica para verificar si el usuario es realmente un profesional
    return render(request, 'app_prevenapp/dashboard_profesional.html')