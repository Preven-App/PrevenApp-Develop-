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
    path('dashboard/profesional/horario/eliminar/<int:id>/', views.eliminar_horario, name='eliminar_horario'),
    path('dashboard/profesional/reportes/', views.reportes_profesional, name='reportes_profesional'),
    path('dashboard/profesional/recursos/', views.recursos_profesional, name='recursos_profesional'),
]