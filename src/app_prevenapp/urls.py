from django.urls import path

from . import views

urlpatterns = [
    # La ruta vacía '' significa que será la página principal
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

    # Tus nuevas rutas para el módulo de comunicaciones
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chat-personal/', views.chat_personal_view, name='chat_personal'),
    path('salas-chat/', views.salas_chat_view, name='salas_chat'),
]