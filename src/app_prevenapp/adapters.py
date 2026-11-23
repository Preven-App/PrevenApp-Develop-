# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    # Dejamos que el modelo se encargue de asignar el rol por defecto
    pass

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # Verificamos si el usuario está autenticado
        if request.user.is_authenticated:
            # Si es superusuario o staff, va al admin
            if request.user.is_superuser or request.user.is_staff:
                return reverse('admin:index')
            
            # Si tiene un rol asignado, decidimos según el nombre del rol
            if hasattr(request.user, 'rol') and request.user.rol:
                rol_nombre = request.user.rol.nombre.lower()
                
                if rol_nombre in ['administrador', 'admin']:
                    return reverse('admin:index')
                elif rol_nombre == 'profesional':
                    return reverse('dashboard_profesional')
                else:
                    # Para adolescentes y cualquier otro rol, va al dashboard de usuario
                    return reverse('dashboard_usuario')
            
            # Si no tiene rol, va al dashboard de usuario por defecto
            return reverse('dashboard_usuario')
        
        # Si no está autenticado (no debería pasar en este punto), va a la raíz
        return super().get_login_redirect_url(request)
    
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        # Si Google nos da el nombre y apellido, los copiamos a nuestros campos personalizados
        if data.get('first_name'):
            user.nombres = data.get('first_name')
        if data.get('last_name'):
            user.apellidos = data.get('last_name')
            
        return user