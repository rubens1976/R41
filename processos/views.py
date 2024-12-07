import environ
import json
import requests
import pandas as pd
from django.shortcuts import render, redirect
from .models import Processo
import matplotlib.pyplot as plt
import io 
import base64
import logging
from datetime import datetime
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import pandas as pd
from django.http import HttpResponse
from django.core.mail import send_mail
from django.http import HttpResponse

# Configuração do ambiente
env = environ.Env()
environ.Env.read_env()
API_KEY = env('API_KEY')  # Chave da API do arquivo .env
api_key = "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="  # Chave pública

# Configuração do Logger
logger = logging.getLogger(__name__)

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

# Função para buscar processos pela API do CNJ
def buscar_processos_cnj(request):
    if request.method == "POST":
        tribunal = request.POST.get("tribunal")
        codigos_assunto = request.POST.get("codigos_assunto").split(",")  # Recebe os códigos de assunto
        
        # Verificando se o tribunal existe no dicionário de URLs
        url = API_URLS.get(tribunal)
        if not url:
            return render(request, 'processos/form_busca.html', {'erro': "Tribunal não encontrado"})
        
        # Construindo a consulta com uma cláusula 'bool' e 'should' para múltiplos valores
        payload = json.dumps({
            "size": 10000,  # Definindo o tamanho máximo de registros para a consulta
            "query": {
                "bool": {
                    "should": [
                        {"match": {"classe.codigo": codigo.strip()}} for codigo in codigos_assunto
                    ],
                    "minimum_should_match": 1  # Pelo menos um código deve coincidir
                }
            },
            "sort": [{"dataAjuizamento": {"order": "desc"}}]  # Ordenando por data de ajuizamento (mais recente primeiro)
        })
        
        headers = {
            'Authorization': API_KEY,
            'Content-Type': 'application/json'
        }

        # Realiza a solicitação para a API
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            dados_dict = response.json()  # Resposta da API em formato JSON
            processos = []
            
            # Extraindo os dados dos processos
            for processo in dados_dict['hits']['hits']:
                numero_processo = processo['_source'].get('numeroProcesso', None)
                grau = processo['_source'].get('grau', None)
                classe = processo['_source'].get('classe', {}).get('nome', None)
                assuntos = processo['_source'].get('assuntos', [])
                data_ajuizamento = processo['_source'].get('dataAjuizamento', None)
                ultima_atualizacao = processo['_source'].get('dataHoraUltimaAtualizacao', None)
                formato = processo['_source'].get('formato', {}).get('nome', None)
                codigo = processo['_source'].get('orgaoJulgador', {}).get('codigo', None)
                orgao_julgador = processo['_source'].get('orgaoJulgador', {}).get('nome', None)
                municipio = processo['_source'].get('orgaoJulgador', {}).get('codigoMunicipioIBGE', None)
                sort = processo.get('sort', [None])[0]

                try:
                    movimentos = processo['_source'].get('movimentos', [])
                except KeyError:
                    movimentos = []

                processos.append([numero_processo, classe, data_ajuizamento, ultima_atualizacao, formato, \
                                  codigo, orgao_julgador, municipio, grau, assuntos, movimentos, sort])
            
            # Convertendo a lista de processos em um DataFrame
            df = pd.DataFrame(processos, columns=['numero_processo', 'classe', 'data_ajuizamento', 'ultima_atualizacao', \
                                                  'formato', 'codigo', 'orgao_julgador', 'municipio', 'grau', 'assuntos', \
                                                  'movimentos', 'sort'])

            # Exibindo uma amostra de 5 registros
            return render(request, 'processos/resultados_busca.html', {'df': df.head()})
        else:
            return render(request, 'processos/form_busca.html', {'erro': f"Erro ao buscar dados na API: {response.status_code}"})
    
    return render(request, 'processos/form_busca.html')  # Para o caso de requisição GET

def home(request):
    return redirect('processos:form_busca')

def form_busca(request):
    # Renderize a página HTML do formulário de busca
    return render(request, 'form_busca.html')

def verificacao_processos(request):
    return render(request, 'verificacao_processos.html')

def exportar_pdf(request):
    # Cria um buffer para gerar o PDF
    buffer = io.BytesIO()

    # Cria um objeto canvas para o PDF
    p = canvas.Canvas(buffer)

    # Adiciona conteúdo ao PDF
    p.drawString(100, 750, "Este é um exemplo de PDF gerado pelo Django.")
    p.drawString(100, 730, "Modifique este texto para o conteúdo que deseja incluir no PDF.")

    # Finaliza o PDF
    p.showPage()
    p.save()

    # Retorna a resposta do PDF
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def exportar_excel(request):
    # Exemplo de dados a serem exportados
    dados = {
        'Coluna 1': ['Valor 1', 'Valor 2', 'Valor 3'],
        'Coluna 2': ['Valor A', 'Valor B', 'Valor C'],
    }

    # Criar um DataFrame com pandas
    df = pd.DataFrame(dados)

    # Criar uma resposta HTTP com o tipo de conteúdo para Excel
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="dados.xlsx"'

    # Salvar o DataFrame como Excel no objeto de resposta
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')

    return response


def encaminhar_email(request):
    # Configurações do e-mail
    assunto = 'Exemplo de E-mail'
    mensagem = 'Este é um exemplo de e-mail enviado pelo Django.'
    remetente = 'seuemail@dominio.com'
    destinatarios = ['destinatario@dominio.com']

    try:
        # Enviar o e-mail
        send_mail(
            assunto,
            mensagem,
            remetente,
            destinatarios,
            fail_silently=False,  # Levantar erros em caso de falha
        )
        return HttpResponse('E-mail enviado com sucesso.')
    except Exception as e:
        return HttpResponse(f'Erro ao enviar o e-mail: {str(e)}')
