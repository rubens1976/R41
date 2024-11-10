import json
import requests
import pandas as pd

# URL da API
url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search"
api_key = "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

# Array com os códigos de assunto
codigos_assunto = [166]

# Construindo a consulta
payload = json.dumps({
  "size": 10000,
  "query": {
    "bool": {
      "should": [
        {"match": {"classe.codigo": codigo}} for codigo in codigos_assunto
      ],
      "minimum_should_match": 1
    }
  },
  "sort": [{"dataAjuizamento": {"order": "desc"}}]
})

# Cabeçalhos da solicitação
headers = {
  'Authorization': api_key,
  'Content-Type': 'application/json'
}

# Enviando a solicitação
response = requests.request("POST", url, headers=headers, data=payload)
dados_dict = response.json()

# Dicionário com mapeamento de códigos de municípios para nomes
municipios_ibge = {
    2302305: "Fortaleza",
    2304400: "Juazeiro do Norte",
    2313302: "Sobral",
    2308500: "Maracanaú",
    2302800: "Caucaia",
    2307304: "Iguatu",
    # Adicione outros códigos de municípios conforme necessário
}

# Criando uma lista para armazenar os dados dos processos
processos = []

# Extraindo os dados necessários
for processo in dados_dict['hits']['hits']:
    numero_processo = processo['_source'].get('numeroProcesso', None)
    grau = processo['_source'].get('grau', None)
    classe = processo['_source'].get('classe', {}).get('nome', None)
    
    assuntos = processo['_source'].get('assuntos', [])
    assuntos_formatado = ", ".join([assunto.get('nome', '') for assunto in assuntos])

    data_ajuizamento = processo['_source'].get('dataAjuizamento', None)
    ultima_atualizacao = processo['_source'].get('dataHoraUltimaAtualizacao', None)
    formato = processo['_source'].get('formato', {}).get('nome', None)
    codigo = processo['_source'].get('orgaoJulgador', {}).get('codigo', None)
    orgao_julgador = processo['_source'].get('orgaoJulgador', {}).get('nome', None)
    municipio_codigo = processo['_source'].get('orgaoJulgador', {}).get('codigoMunicipioIBGE', None)

    # Obtendo o nome do município a partir do código IBGE
    municipio_nome = municipios_ibge.get(municipio_codigo, "Município Desconhecido")

    movimentos = processo['_source'].get('movimentos', [])
    movimentos_formatados = []
    for mov in movimentos:
        nome = mov.get('nome', '')
        dataHora = mov.get('dataHora', '')
        descricao = mov.get('descricao', '')
        movimentos_formatados.append(f"{nome} - {descricao} - {dataHora}")
        
    movimentos_texto = "\n".join(movimentos_formatados)

    # Adicionando os dados extraídos à lista de processos
    processos.append([numero_processo, classe, data_ajuizamento, ultima_atualizacao, formato, \
                      codigo, orgao_julgador, municipio_codigo, municipio_nome, grau, assuntos_formatado, movimentos_texto])

# Criando um DataFrame com a nova coluna de nome do município
df = pd.DataFrame(processos, columns=['numero_processo', 'classe', 'data_ajuizamento', 'ultima_atualizacao', \
                                      'formato', 'codigo', 'orgao_julgador', 'municipio_codigo', 'municipio_nome', \
                                      'grau', 'assuntos', 'movimentos'])

# Exportando o DataFrame para um arquivo Excel
df.to_excel("processos_tjce_formatado.xlsx", index=False)
print("Arquivo Excel 'processos_tjce_formatado.xlsx' criado com sucesso!")
