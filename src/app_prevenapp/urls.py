from django.urls import path

from . import views

urlpatterns = [
    # La ruta vacía '' significa que será la página principal
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('servicios/', views.servicios_view, name='servicios'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('registrar-tip/', views.registrar_tip, name='registrar_tip'),
    path('tips/', views.listar_tips_view, name='listar_tips'),
    path('citas/', views.citas_view, name='citas'),
    path('recursos/', views.recursos_view, name='recursos'),
    path('ajustes/', views.ajustes_view, name='ajustes'),
]