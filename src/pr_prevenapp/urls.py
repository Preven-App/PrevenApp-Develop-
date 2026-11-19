from django.contrib import admin
from django.urls import path, include
# 1. Importamos la configuración y la función estática
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_prevenapp.urls')),
    path('accounts/', include('allauth.urls')),
]

# 2. Le decimos a Django que sirva los archivos de media (fotos) en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)