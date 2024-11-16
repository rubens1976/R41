# processos/urls.py
from django.urls import path, include  # Adicionando o include
from django.contrib import admin  # Adicionando o admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('listar/', views.listar_processos, name='listar_processos'),  # Rota para listar processos
    path('buscar/', views.buscar_processos_cnj, name='buscar_processos_cnj'),  # Rota para buscar processos
    path('form_busca/', views.form_busca, name='form_busca'),  # Formulário de busca
    path('verificacao_processos/', views.verificacao_processos, name='verificacao_processos'),  # Verificação de processos
    path('resultados_busca/', views.buscar_processos_cnj, name='resultados_busca'),  # Resultados da busca
    path('exportar_pdf/', views.exportar_pdf, name='exportar_pdf'),  # Rota para gerar PDF dos resultados
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),  # Rota para exportar os resultados
    path('encaminhar_email/', views.encaminhar_email, name='encaminhar_email'),  # Rota para encaminhar os resultados por e-mail
    path('gerar_graficos/', views.gerar_graficos, name='gerar_graficos'),  # Rota para gerar os gráficos
    path('buscar_processos/', views.buscar_processos_cnj, name='buscar_processos_cnj'),  # Rota para buscar processos
    path('admin/', admin.site.urls),  # Corrigido para incluir a URL do admin
    path('processos/', include('processos.urls')),  # Incluindo as URLs do app processos
]
