from django.shortcuts import render, redirect
from .models import Processo
import matplotlib.pyplot as plt
import io
import base64
import json
import requests
import logging
import pandas as pd
from datetime import datetime
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import send_mail


# Configuração do Logger
logger = logging.getLogger(__name__)

# Chave da API
API_KEY = "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

# URLs das APIs dos tribunais
API_URLS = {
    "TJAM": "https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search",
    "TJAP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjap/_search",
    "TJBA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjba/_search",
    "TJCE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search",
    "TJDFT": "https://api-publica.datajud.cnj.jus.br/api_publica_tjdft/_search",
    "TJES": "https://api-publica.datajud.cnj.jus.br/api_publica_tjes/_search",
    "TJGO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo/_search",
    "TJMA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjma/_search",
    "TJMG": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
    "TJMS": "https://api-publica.datajud.cnj.jus.br/api_publica_tjms/_search",
    "TJMT": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmt/_search",
    "TJPA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpa/_search",
    "TJPB": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpb/_search",
    "TJPE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search",
    "TJPI": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpi/_search",
    "TJPR": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search",
    "TJRJ": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search",
    "TJRN": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrn/_search",
    "TJRO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search",
    "TJRR": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrr/_search",
    "TJRS": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrs/_search",
    "TJSC": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsc/_search",
    "TJSE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjse/_search",
    "TJSP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search",
    "TJTO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjto/_search",
}

# Função para formatar datas ISO8601
def formatar_data(data_str):
    if data_str:
        try:
            return datetime.fromisoformat(data_str.replace('Z', '')).strftime('%d/%m/%Y %H:%M:%S')
        except ValueError:
            return "Dados não disponíveis"
    return "Dados não disponíveis"

# Função para converter milissegundos (timestamp) para um formato datetime
def convert_millis_to_datetime(millis):
    if millis is None:
        return "Dados não disponíveis"
    try:
        millis = int(millis)
        return datetime.utcfromtimestamp(millis / 1000).strftime('%d/%m/%Y %H:%M:%S')
    except (ValueError, TypeError):
        return "Dados não disponíveis"

# Função para gerar gráficos
def gerar_graficos(request):
    if request.method == 'GET':
        tribunal = request.GET.get('tribunal')
        codigos_assunto = request.GET.get('codigos_assunto', '').split(',')
        
        # Validação do tribunal
        if not tribunal:
            erro = "Tribunal não selecionado."
            logger.error(erro)
            return render(request, 'processos/graficos.html', {'erro': erro})
        
        # Verificar a URL do tribunal
        url = API_URLS.get(tribunal)
        if not url:
            erro = f"Tribunal '{tribunal}' não encontrado."
            logger.error(erro)
            return render(request, 'processos/graficos.html', {'erro': erro})

        # Definir o payload para a solicitação da API
        try:
            codigos_assunto = [codigo.strip() for codigo in codigos_assunto if codigo.strip().isdigit()]
            if not codigos_assunto:
                raise ValueError("Nenhum código de assunto válido fornecido.")
                
            payload = json.dumps({
                "size": 1000,
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"classe.codigo": int(codigo)}} for codigo in codigos_assunto
                        ],
                        "minimum_should_match": 1
                    }
                },
                "sort": [{"dataAjuizamento": {"order": "desc"}}]
            })
        except ValueError as ve:
            erro = str(ve)
            logger.error(erro)
            return render(request, 'processos/graficos.html', {'erro': erro})

        # Headers para a API
        headers = {
            'Authorization': API_KEY,
            'Content-Type': 'application/json'
        }

        # Realiza a solicitação POST para a API
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            dados_dict = response.json()  # Resposta da API
        except requests.RequestException as e:
            erro = f"Erro ao buscar dados na API: {str(e)}"
            logger.error(erro)
            return render(request, 'processos/graficos.html', {'erro': erro})

        # Extraindo os dados dos processos
        processos_data = [
            {
                'classe': processo.get("_source", {}).get("classe", {}).get("nome", "Dados não disponíveis"),
                'numeroProcesso': processo.get("_source", {}).get("numeroProcesso", "Dados não disponíveis")
            }
            for processo in dados_dict.get('hits', {}).get('hits', [])
        ]

        # Gerando o gráfico
        classes = [processo['classe'] for processo in processos_data]
        numero_processos = [processo['numeroProcesso'] for processo in processos_data]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(classes, numero_processos)
        ax.set_xlabel('Classe')
        ax.set_ylabel('Número de Processos')
        ax.set_title('Número de Processos por Classe')

        # Salvar o gráfico em formato base64 para passá-lo ao frontend
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        graphic_data = base64.b64encode(image_png).decode('utf-8')

        # Passar os dados para o template
        return render(request, 'processos/graficos.html', {'graphic_data': graphic_data})

# Função para renderizar a página inicial
def home(request):
    return redirect('processos:form_busca')  # Substitua com a URL correta para o seu formulário de busca

# Função para listar os processos armazenados no banco de dados local
def listar_processos(request):
    processos = Processo.objects.all()
    return render(request, 'processos/process_list.html', {'processos': processos})

# Função para buscar processos, Lógica para buscar processos
def buscar_processos_cnj(request):
    context = {
        'dados': 'Aqui vem os dados dos processos'
    }
    return render(request, 'processos/form_busca.html', context)  # Substitua o nome do template conforme necessário

# Lógica para o formulário de busca
def form_busca(request):
    return render(request, 'processos/form_busca.html')

# Lógica para verificação de processos
def verificacao_processos(request):
    context = {
        'dados': 'Aqui estão os dados dos processos'  # Altere conforme a lógica
    }
    return render(request, 'processos/verificacao_processos.html', context)  # Substitua o template conforme necessário

# Criação do arquivo PDF em memória
def exportar_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Aqui estão os dados dos processos")
    p.showPage()
    p.save()

    # Gerar o PDF e retornar como resposta HTTP
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# Sua lógica para exportação de dados para Excel aqui
def exportar_excel(request):
    dados = {'coluna1': [1, 2, 3], 'coluna2': [4, 5, 6]}  # Exemplo de dados
    df = pd.DataFrame(dados)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="dados.xlsx"'
    df.to_excel(response, index=False)
    return response

# Lógica para enviar o e-mail
def encaminhar_email(request):
    try:
        send_mail(
            'Assunto Relatório de Análise de Dados de Jurimetria',
            'Corpo do e-mail',
            'from@example.com',
            ['rubensmelo1976@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse('E-mail enviado com sucesso!')
    except Exception as e:
        return HttpResponse(f'Erro ao enviar e-mail: {str(e)}')

# Lógica para envio o e-mail
def encaminhar_email(request):
    try:
        send_mail(
            'Assunto do e-mail',
            'Corpo do e-mail',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        return HttpResponse('E-mail enviado com sucesso!')
    except Exception as e:
        return HttpResponse(f'Erro ao enviar e-mail: {str(e)}')