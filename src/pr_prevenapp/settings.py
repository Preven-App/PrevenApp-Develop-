"""
Django settings for pr_prevenapp project.
"""
from pathlib import Path
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ai7)%991s6i3*zwt#56=6kf0v4m8b-d%hq-t7l*x2$t8$39bcy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'unfold', # <-- Debe ir antes de django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google', # Descomenta cuando configures Google
    
    # Apps propias
    'app_prevenapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'pr_prevenapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Mejor usar ruta absoluta desde BASE_DIR
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pr_prevenapp.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-co' # Cambiado a español - Colombia
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Email (Corregido el nombre de la variable a EMAIL_BACKEND)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'app_prevenapp.Usuario'

# ==========================================
# CONFIGURACIÓN DE DJANGO UNFOLD
# ==========================================
UNFOLD = {
    "SITE_TITLE": "PrevenApp Admin",
    "SITE_HEADER": "PrevenApp",
    "SITE_SUBHEADER": "Panel de Administración",
    "SITE_SYMBOL": "health_and_safety", # Icono de Material Symbols
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "THEME": "auto", 
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
         "base": {
            "50": "oklch(98.5% .002 247.839)",  # Fondo muy claro (para modo light)
            "100": "oklch(96.7% .003 264.542)",
            "200": "oklch(92.8% .006 264.531)",
            "300": "oklch(87.2% .01 258.338)",
            "400": "oklch(70.7% .022 261.325)",
            "500": "oklch(55.1% .027 264.364)",
            "600": "oklch(44.6% .03 256.802)",   # Gris medio
            "700": "oklch(37.3% .034 259.733)",  # Gris oscuro
            "800": "oklch(27.8% .033 256.848)",  # Fondo de tarjetas en modo oscuro
            "900": "oklch(21% .034 264.665)",    # Fondo principal en modo oscuro
            "950": "oklch(13% .028 261.692)",    # Fondo más profundo (sidebar)
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Principal"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Gestión de Personas"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Usuarios"),
                        "icon": "group",
                        "link": reverse_lazy("admin:app_prevenapp_usuario_changelist"),
                    },
                    {
                        "title": _("Profesionales"),
                        "icon": "medical_services",
                        "link": reverse_lazy("admin:app_prevenapp_profesional_changelist"),
                    },
                ],
            },
            {
                "title": _("Contenido y Recursos"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Categorías"),
                        "icon": "category",
                        "link": reverse_lazy("admin:app_prevenapp_categoria_changelist"),
                    },
                    {
                        "title": _("Actividades Lúdicas"),
                        "icon": "sports_esports",
                        "link": reverse_lazy("admin:app_prevenapp_actividad_changelist"),
                    },
                ],
            },
        ],
    },
}