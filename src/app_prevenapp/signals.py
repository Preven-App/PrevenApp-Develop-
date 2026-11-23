# app_prevenapp/signals.py
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(user_logged_in)
def enviar_correo_login_google(sender, request, user, **kwargs):
    # Capturamos el objeto sociallogin para verificar si el login fue social
    sociallogin = kwargs.get('sociallogin')
    
    # Si sociallogin existe y el proveedor es Google, enviamos el correo
    if sociallogin and sociallogin.account.provider == 'google':
        asunto = 'Nuevo inicio de sesión en PrevenApp'
        mensaje = f'Hola {user.nombres or user.username},\n\nHemos detectado un nuevo inicio de sesión en tu cuenta de PrevenApp a través de Google.\n\nSi fuiste tú, puedes ignorar este mensaje. Si no reconoces esta actividad, te recomendamos cambiar tu contraseña de inmediato.\n\n¡Gracias por cuidar de tu bienestar!'
        
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Si el envío falla (por ejemplo, por credenciales incorrectas), lo veremos en la terminal
            print(f"Error al enviar el correo de notificación: {e}")