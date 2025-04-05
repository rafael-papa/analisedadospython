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
        <a href='/editar_inadimplencias'>Editar dados de inadimplência</a><br>
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
            inad_file,
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

@app.route('/consultar')
def consultar():
    return vazio

@app.route('/graficos')
def graficos():
    return vazio

@app.route('/editar_inadimplencia')
def editar_inadimplencia():
    return vazio

@app.route('/correlacao')
def correlacao():
    return vazio

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
