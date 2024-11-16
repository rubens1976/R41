from django.contrib import admin
from django.urls import path, include
from processos import views  # Importa as views do app processos para definir a página inicial
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Inclui URLs do app 'admin'
    path('processos/', include('processos.urls')),  # Inclui URLs do app 'processos'
    path('', views.listar_processos, name='home'),  # Define a página inicial como a listagem de processos
    path('upload/', include('upload_app.urls')),  # Inclui URLs do app de upload
    path('api/', include('api_integration.urls')),  # Inclui URLs da nova app 'api_integration'
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
