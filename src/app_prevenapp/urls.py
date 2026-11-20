from django.urls import path, include
from . import views

urlpatterns = [
    # Rutas Principales y Autenticación
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('accounts/', include('allauth.urls')),
    
    # Rutas de la Aplicación (Adolescentes y Público)
    path('servicios/', views.servicios_view, name='servicios'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('registrar-tip/', views.registrar_tip, name='registrar_tip'),
    path('tips/', views.listar_tips_view, name='listar_tips'),
    path('citas/', views.citas_view, name='citas'),
    path('recursos/', views.recursos_view, name='recursos'),
    path('ajustes/', views.ajustes_view, name='ajustes'),
    path('salas/', views.salas_chat, name='salas_chat'),
    path('salas/<int:sala_id>/', views.salas_chat, name='detalle_sala_chat'),

    # Rutas del Profesional (Dashboard)
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'),
    path('dashboard/profesional/horario/', views.configurar_horario, name='configurar_horario'),
    path('dashboard/profesional/mis-horarios/', views.ver_horarios, name='ver_horarios'),
    path('dashboard/profesional/horario/eliminar/<int:id>/', views.eliminar_horario, name='eliminar_horario'),
    path('dashboard/profesional/perfil/', views.perfil_profesional, name='perfil_profesional'),
    path('dashboard/profesional/reportes/', views.reportes_profesional, name='reportes_profesional'),
    path('dashboard/profesional/recursos/', views.recursos_profesional, name='recursos_profesional'),
]