from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
    path('usuario/salas/', views.salas_chat_usuario, name='salas_chat_usuario'),
    path('usuario/salas/<int:sala_id>/', views.salas_chat_usuario, name='detalle_sala_chat_usuario'),
    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # Rutas del Profesional (Dashboard)
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'),
    path('dashboard/profesional/perfil/', views.perfil_profesional, name='perfil_profesional'),
    path('dashboard/profesional/reportes/', views.reportes_profesional, name='reportes_profesional'),
    path('dashboard/profesional/reportes/nuevo/', views.crear_reporte, name='crear_reporte'),
    path('dashboard/profesional/recursos/', views.recursos_profesional, name='recursos_profesional'),
    
    # Horarios
    path('dashboard/profesional/horario/', views.configurar_horario, name='configurar_horario'),
    path('dashboard/profesional/mis-horarios/', views.ver_horarios, name='ver_horarios'),
    path('dashboard/profesional/horario/eliminar/<int:id>/', views.eliminar_horario, name='eliminar_horario'),

    # Rutas para administrar Tips (Profesional)
    path('dashboard/profesional/tips/', views.lista_tips, name='lista_tips'),
    path('dashboard/profesional/tips/crear/', views.crear_tip, name='crear_tip'),
    path('dashboard/profesional/tips/editar/<int:id>/', views.editar_tip, name='editar_tip'),
    path('dashboard/profesional/tips/eliminar/<int:id>/', views.eliminar_tip, name='eliminar_tip'),
    path('dashboard/profesional/citas/', views.citas_profesional, name='citas_profesional'),
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)