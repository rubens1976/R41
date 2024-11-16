# api_integration/views.py
from django.shortcuts import render

def verificacao_processos(request):
    # Sua lógica para a verificação de processos
    return render(request, 'verificacao_processos.html')
