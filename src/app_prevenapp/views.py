# app_prevenapp/views.py
from django.shortcuts import render


def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')

def login_view(request):
    return render(request, 'app_prevenapp/login.html')

def register_view(request):
    # Aquí luego irá la lógica para guardar en la base de datos
    return render(request, 'app_prevenapp/register.html')