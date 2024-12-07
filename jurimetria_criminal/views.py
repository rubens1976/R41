from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
import requests
import pandas as pd
from datetime import datetime
import logging

# Configuração do Logger
logger = logging.getLogger(__name__)

# URL da API (Substitua pela URL adequada)
API_KEY = "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
API_URLS = {
    "TJCE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search",
}

# Função para a página inicial
def home(request):
    return redirect('processos:form_busca')  # Substitua com a URL para o formulário de busca

# Função para o formulário de busca de processos
def form_busca(request):
    return render(request, 'processos/form_busca.html')

# Função para buscar os processos
def buscar_processos_cnj(request):
    if request.method == 'POST':
        tribunal = request.POST.get("tribunal")
        codigos_assunto = request.POST.get("codigos_assunto").split(',')  # Recebe os códigos de assunto
        
        # Construir a consulta da API
        payload = json.dumps({
            "size": 10000,
            "query": {
                "bool": {
                    "should": [{"match": {"classe.codigo": codigo.strip()}} for codigo in codigos_assunto],
                    "minimum_should_match": 1
                }
            },
            "sort": [{"dataAjuizamento": {"order": "desc"}}]
        })

        headers = {
            'Authorization': API_KEY,
            'Content-Type': 'application/json'
        }

        # Realiza a solicitação da API
        response = requests.post(API_URLS[tribunal], headers=headers, data=payload)
        
        if response.status_code == 200:
            dados_dict = response.json()
            processos = []

            # Extrair os dados dos processos
            for processo in dados_dict['hits']['hits']:
                numero_processo = processo['_source'].get('numeroProcesso', 'Não disponível')
                classe = processo['_source'].get('classe', {}).get('nome', 'Não disponível')
                data_ajuizamento = processo['_source'].get('dataAjuizamento', 'Não disponível')

                processos.append({
                    'numero_processo': numero_processo,
                    'classe': classe,
                    'data_ajuizamento': data_ajuizamento,
                })

            # Convertendo os dados para um DataFrame e exibindo no template
            df = pd.DataFrame(processos)
            return render(request, 'processos/resultados_busca.html', {'df': df.to_html()})
        else:
            logger.error(f"Erro ao buscar dados na API: {response.status_code}")
            return render(request, 'processos/form_busca.html', {'erro': "Erro ao buscar dados na API"})
    else:
        return render(request, 'processos/form_busca.html')  # Exibe o formulário caso o método não seja POST

# Função para a verificação de processos (ajustar conforme a necessidade)
def verificacao_processos(request):
    return render(request, 'processos/verificacao_processos.html')
