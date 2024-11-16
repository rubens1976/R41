from django.urls import path
from . import views

urlpatterns = [
    path('verificar-processos/', views.verificacao_processos, name='verificacao_processos'),
    # Adicione outras rotas conforme necessário
]
