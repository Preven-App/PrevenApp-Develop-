from django.urls import path, include

from . import views

urlpatterns = [
    # La ruta vacía '' significa que será la página principal
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'),
    path('dashboard/profesional/horario/', views.configurar_horario, name='configurar_horario'),
    path('accounts/', include('allauth.urls')),
    path('dashboard/profesional/mis-horarios/', views.ver_horarios, name='ver_horarios'),
    path('dashboard/profesional/perfil/', views.perfil_profesional, name='perfil_profesional'),
]