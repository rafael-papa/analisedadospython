from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config

app = Flask(__name__)
DB_PATH = config.DB_PATH
# Função para inicializar o banco de dados SQL
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia (
                    mes TEXT PRIMARY KEY,
                    inadimplencia REAL 

            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selic (
                    mes TEXT PRIMARY KEY,
                    selic_diaria REAL
                    )
        ''')
        conn.commit()

vazio = 0

@app.route('/')
def index():
    return render_template_string('''
        <h1>Upload de dados Econômicos</h1>
        <form action='upload' method='POST' enctype='multipart/form-data'>
            <label for='campo_inadimplencia'>Arquivo de Inadimplência (CSV): </label>
            <input name='campo_inadimplencia' type='file' required><br><br>
            
            <label for='campo_selic'>Arquivo da Taxa SELIC (CSV): </label>
            <input name='campo_selic' type='file' required><br>
            <input type='submit' value='Fazer Upload'<br>
        </form>
        <br>
        <hr>
        <br>
        <a href='/consultar'>Consultar dados armazenados</a><br>
        <a href='/graficos'>Visualizar gráficos</a><br>
        <a href='/editar_inadimplencia'>Editar dados de inadimplência</a><br>
        <a href='/correlacao'>Analisar Correlação</a><br>
                 
    ''')

@app.route('/upload', methods=['POST','GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')
    
    # Verifica se os arquivos foram enviados
    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos arquivos devem ser enviados"})

    inad_df = pd.read_csv(
            inad_file,
            sep=';',
            names=['data','inadimplencia'],
            header=0
    )
    
    selic_df =  pd.read_csv(
            selic_file,
            sep=';',
            names=['data','selic_diaria'],
            header=0
    )
    
    inad_df['data'] = pd.to_datetime(inad_df['data'], format="%d/%m/%Y")
    selic_df['data'] = pd.to_datetime(selic_df['data'], format="%d/%m/%Y")

    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(DB_PATH) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists='replace', index=False)
        selic_mensal.to_sql('selic', conn, if_exists='replace', index=False)
    return jsonify({"Mensagem":"Dados armazenados com sucesso!"})

@app.route('/consultar', methods=['GET','POST'])
def consultar():
    # Resultado se a página for carregada recebendo um POST
    if request.method == 'POST':
        tabela = request.form.get('campo_tabela')
        if tabela not in ['inadimplencia','selic']:
                return jsonify({"Erro":"Tabela Inválida."}),400
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        return df.to_html(index=False)

    # Resultado sem receber um post, ou seja, primeiro carregamento da página.
    return render_template_string('''
        <h1> Consulta de Tabelas </h1>
        <form method='POST'>
            <label for="campo_tabela"> Escolha a tabela: </label>
            <select name="campo_tabela">
                <option value="inadimplencia"> Inadimplência </option>
                <option value="selic"> Selic </option>
            </select>
            <input type="submit" value="Consultar">
        </form>
        <br><a href="/"> Voltar </a>
                                  
        ''')

@app.route('/graficos')
def graficos():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x = inad_df['mes'], y = inad_df['inadimplencia'], mode = 'lines+markers', name = 'Inadimplência'))
    fig1.update_layout(title = "Evolução da Inadimplência", xaxis_title = "Mês", yaxis_title = "%", template = "plotly_dark")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x = selic_df['mes'], y = selic_df['selic_diaria'], mode = 'lines+markers' , name = 'Taxa Selic'))
    fig2.update_layout(title = "Média mensal da Selic", xaxis_title = "Mês", yaxis_title = "Taxa %", template = "plotly_dark")

    graph_html_1 = fig1.to_html(full_html=False, include_plotlyjs = 'cdn')
    graph_html_2 = fig2.to_html(full_html=False, include_plotlyjs = False)

    return render_template_string('''
        <html>
            <head>
                <title> Gráficos Econômicos </title>
                <style>
                        .container{
                            display:flex;
                            justify-content:space-around;  
                            }
                            .graph{ width:48%;}
                </style>
                <body>
                    <h1><marquee> Gráficos Econômicos</marquee></h1>
                    <div class="container">
                        <div class="graph">{{ grafico1|safe }}</div>
                        <div class="graph">{{ grafico2|safe }}</div>
                    </div>
                </body>
            </head>
    ''', grafico1 = graph_html_1, grafico2 = graph_html_2)



@app.route('/editar_inadimplencia', methods=['POST', 'GET'])
def editar_inadimplencia():
    if request.method == 'POST':
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({'mensagem':'Valor Inválido.'})
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE inadimplencia SET inadimplencia = ? WHERE mes = ?", (novo_valor, mes))
            conn.commit()
        return jsonify({'mensagem':f'Valor atualizado para o mes {mes}'})

    return render_template_string('''
        <h1> Editar Inadimplência </h1>
        <form method="POST">
            <label for="campo_mes"> Mês (AAAA-MM): </label>
            <input type="text" name="campo_mes"><br><br>

            <label for="campo_valor"> Novo valor de Inadimplência: </label>
            <input type="text" name="campo_valor"><br>

            <input type="submit" value="Atualizar Dados">                            
        </form>
        <br>
        <a href="/"> Voltar </a>
    ''')



@app.route('/correlacao')
def correlacao():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)
        
        merged = pd.merge(inad_df, selic_df, on='mes')
        correl = merged['inadimplencia'].corr(merged['selic_diaria'])
    return vazio
    # Regressão Linear[]

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
