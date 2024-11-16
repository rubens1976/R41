from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('listar/', views.listar_processos, name='listar_processos'),
    path('buscar/', views.buscar_processos_cnj, name='buscar_processos_cnj'),  # Rota para buscar processos
    path('form_busca/', views.form_busca, name='form_busca'),
    path('verificacao_processos/', views.verificacao_processos, name='verificacao_processos'),
    path('resultados_busca/', views.buscar_processos_cnj, name='resultados_busca'),
    path('exportar_pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('encaminhar_email/', views.encaminhar_email, name='encaminhar_email'),
    path('gerar_graficos/', views.gerar_graficos, name='gerar_graficos'),
]
