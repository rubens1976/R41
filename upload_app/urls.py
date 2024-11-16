from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),  # Define a rota principal como upload_file
    path('resultado/', views.resultado, name='resultado'),  # Rota para a página de resultado
]
