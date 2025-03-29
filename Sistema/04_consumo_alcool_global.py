from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random

# Configurar o Plotly para abrir sempre os gráficos no navegador
pio.renderers.default = 'browser'

# Carregar o CSV
# Certifique-se de que o arquivo está na mesma pasta

df = pd.read_csv('C:/Users/sabado/Desktop/Python Analise Dados/Sistema/drinks.csv')

# Cria o banco de dados sqlite com os dados CSV
conn = sqlite3.connect('C:/Users/sabado/Desktop/Python Analise Dados/Sistema/consumo_alcool.db')

df.to_sql("drinks", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

# Inicia a aplicação em Flask

app = Flask(__name__)

# Template HTML com links para cada gráfico
html_template = '''
    <h1> Dashboard - Consumo de Alcool </h1>
    <h2> Parte 01 </h2>
        <ul>
            <li><a href="/grafico1">Top 10 países com maior consumo</a></li>
            <li><a href="/grafico2">Média de consumo de bebidas</a></li>
            <li><a href="/grafico3">Consumo total por região</a></li>
            <li><a href="/grafico4">Comparativo entre tipos</a></li>
            <li><a href="/pais?nome=Brazil">Insight por País</a></li>
        </ul>
    <h2> Parte 02 </h2>
        <ul>
            <li><a href="/comparar">Comparar Tipos</a></li>
            <li><a href="/upload_avengers">Upload CSV</a></li>
            <li><a href="/apagar_avengers">Apagar_avengers</a></li>
            <li><a href="/atribui_pais">Atribuir países Avengers</a></li>
            <li><a href="/vaa">VAA: Vingadores Alcoólicos Anônimos</a></li>
        </ul>
'''

# Rota inicial com os links para os gráficos
@app.route("/")
def index():
    return render_template_string(html_template)

# Rota do gráfico de 10 paises com maior consumo de álcool
@app.route('/grafico1')
def grafico1():
    conn = sqlite3.connect('C:/Users/sabado/Desktop/Python Analise Dados/Sistema/consumo_alcool.db')
    df = pd.read_sql_query('''
        SELECT country, total_litres_of_pure_alcohol
        FROM drinks
        ORDER BY total_litres_of_pure_alcohol DESC
        LIMIT 10 
        ''', conn)
    conn.close()
    fig = px.bar(df, x="country", y="total_litres_of_pure_alcohol",  title="Top 10 países")
    return fig.to_html()

# Rota de média global de consumo por tipo de bebida
@app.route('/grafico2')
def grafico2():
    conn = sqlite3.connect('C:/Users/sabado/Desktop/Python Analise Dados/Sistema/consumo_alcool.db')
    df = pd.read_sql_query("SELECT AVG(beer_servings) AS cerveja, AVG(spirit_servings) AS destilados, AVG(wine_servings) AS vinho FROM drinks", conn)
    conn.close()
    # Crialção dos dados e definição das colunas de segmentos e valores
    df_melted = df.melt(var_name="Bebida", value_name="Média de doses")
    fig = px.bar(df_melted, x="Bebida", y="Média de doses", title="Média de Consumo Global")
    return fig.to_html() + '<br/><a href="/">Voltar ao Início</a>'

@app.route("/upload_avengers")
def upload_avengers():
    


if __name__ == '__main__':
    app.run(debug=True)