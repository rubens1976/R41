import os
import pdfplumber
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import re

def extrair_texto_pdf(caminho_pdf):
    """Extrai o texto de um arquivo PDF."""
    texto_completo = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido
    return texto_completo

def filtrar_informacoes_banco(texto):
    """Filtra e organiza informações específicas do Banco do Nordeste no texto extraído com IDs."""
    padrao_banco = r'Banco do Nordeste.*?OAB:.*?CE'
    resultados = re.findall(padrao_banco, texto, re.DOTALL)
    informacoes_organizadas = [{"ID": idx + 1, "conteudo": resultado.strip()} for idx, resultado in enumerate(resultados)]
    return informacoes_organizadas

def upload_file(request):
    """Faz o upload do arquivo PDF, extrai e filtra as informações e renderiza o resultado."""
    if request.method == 'POST' and request.FILES.get('file'):
        arquivo = request.FILES['file']
        fs = FileSystemStorage()
        caminho = fs.save(arquivo.name, arquivo)
        caminho_arquivo = os.path.join(settings.MEDIA_ROOT, caminho)

        # Extração e organização do texto
        texto_pdf = extrair_texto_pdf(caminho_arquivo)
        informacoes_banco = filtrar_informacoes_banco(texto_pdf)

        # Renderiza o template com as informações extraídas e organizadas
        return render(request, 'upload_app/resultado.html', {'informacoes': informacoes_banco})

    # Renderiza o template de upload se o método não for POST
    return render(request, 'upload_app/upload.html')

def resultado(request):
    """Renderiza a página de resultado (caso seja necessária em outra situação)."""
    return render(request, 'upload_app/resultado.html')
