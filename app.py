import os
import pdfplumber
from flask import Flask, request, render_template, redirect, url_for
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

def extrair_texto_pdf(caminho_pdf):
    texto_completo = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text()
    return texto_completo

def filtrar_informacoes_banco(texto):
    # Filtra informações relacionadas ao Banco do Nordeste
    padrao_banco = r'Banco do Nordeste.*?OAB:.*?CE'
    resultados = re.findall(padrao_banco, texto, re.DOTALL)
    return resultados

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nenhum arquivo foi enviado'
        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo selecionado'
        if file:
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(caminho)
            texto_pdf = extrair_texto_pdf(caminho)
            informacoes_banco = filtrar_informacoes_banco(texto_pdf)
            return render_template('resultado.html', informacoes=informacoes_banco)
    return render_template('upload.html')

@app.route('/resultado')
def resultado():
    return render_template('resultado.html')

if __name__ == "__main__":
    app.run(debug=True)
