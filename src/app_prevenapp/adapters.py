# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    # Dejamos que el modelo se encargue de asignar el rol por defecto
    pass