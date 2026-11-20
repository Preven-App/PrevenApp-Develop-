from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'),
    path('dashboard/profesional/horario/', views.configurar_horario, name='configurar_horario'),
    path('accounts/', include('allauth.urls')),
    path('dashboard/profesional/mis-horarios/', views.ver_horarios, name='ver_horarios'),
    path('dashboard/profesional/perfil/', views.perfil_profesional, name='perfil_profesional'),
    path('dashboard/profesional/horario/eliminar/<int:id>/', views.eliminar_horario, name='eliminar_horario'),

    # Rutas para administrar Tips
    path('dashboard/profesional/tips/', views.lista_tips, name='lista_tips'),
    path('dashboard/profesional/tips/crear/', views.crear_tip, name='crear_tip'),
    path('dashboard/profesional/tips/editar/<int:id>/', views.editar_tip, name='editar_tip'),
    path('dashboard/profesional/tips/eliminar/<int:id>/', views.eliminar_tip, name='eliminar_tip'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)