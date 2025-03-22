from flask import Flask, jsonify, send_file
import pandas as pd
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

# Carregar o nosso arquivo do Excel
arquivo = 'C:/Users/sabado/Desktop/PAPA Python Analise de Dados/PAPA/01_base_vendas.xlsx'

df1 = pd.read_excel(arquivo, sheet_name = 'Relatório de Vendas')
df2 = pd.read_excel(arquivo, sheet_name = 'Relatório de Vendas1')

df_consolidado = pd.concat([df1,df2], ignore_index=True)

df_consolidado['Status'] = df_consolidado['Plano Vendido'].apply(lambda x: 'Premium' if x == 'Enterprise' else 'Padrao')

@app.route('/index')
def home():

    conteudo = '''
    
    <h1>API para análise de dados de vendas - Use as rotas para obter as análises!</h1>
    <br/>
    <a href='/clientes_por_cidade'>Clientes por Cidade</a><br/>
    <a href='/vendas_por_plano'>Vendas por Plano</a><br/>
    <a href='/top3_cidades'>Top 3 cidades com mais clientes</a><br/>
    <a href='/total_clientes'>Total de clientes</a><br/>
    <a href='/status_dist'>Distribuição dos Planos (Status)</a><br/>
    <a href='/download/xlsx'>Download de arquivo XLSX</a><br/>
    <a href='/download/csv'>Download de arquivo CSV</a>


'''
    return conteudo

@app.route('/clientes_por_cidade')
def clientes_por_cidade():
    clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
    return jsonify(clientes_por_cidade.to_dict())

@app.route('/vendas_por_plano')
def vendas_por_plano():
    vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()
    return jsonify(vendas_por_plano.to_dict())

# Rota para obter o top 3 cidades com mais clientes
@app.route('/top3_cidades')
def top3_cidades():
    clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
    top3_cidades = clientes_por_cidade.head(3)
    return jsonify(top3_cidades.to_dict())

# Rota para obter o número total de clientes
@app.route('/total_clientes')
def total_clientes():
    total_clientes = df_consolidado['Cliente'].nunique()
    return jsonify({"total_clientes": total_clientes})

# Rota para obter a distribuição dos planos (status)
@app.route('/status_dist')
def status_dist():
    status_dist = df_consolidado['Status'].value_counts()
    return jsonify(status_dist.to_dict())

# Rota para download do xlsx
@app.route('/download/xlsx')
def download_xlsx():
    caminho_salvar_xlsx = 'C:/Users/sabado/Desktop/PAPA Python Analise de Dados/PAPA/vendas_consolidado.xlsx'
    df_consolidado.to_excel(caminho_salvar_xlsx, index=False)
    return f"<h1>Arquivo de Excel salvo com sucesso em: {caminho_salvar_xlsx}</h1>"

# Rota para download do CSV
@app.route('/download/csv')
def download_csv():
    caminho_salvar_csv = 'C:/Users/sabado/Desktop/PAPA Python Analise de Dados/PAPA/vendas_consolidado.csv'
    df_consolidado.to_csv(caminho_salvar_csv, index=False)
    return f"<h1>Arquivo CSV salvo com sucesso em: {caminho_salvar_csv}</h1>"

if __name__ == '__main__':
    app.run(debug=True)

