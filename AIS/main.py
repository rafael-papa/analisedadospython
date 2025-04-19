from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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
        <a href='/insights_3d'>Analisar Temporais Correlação</a><br>

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
    
    # Regressão linear para
    x = merged['selic_diaria']
    y = merged['inadimplencia']
    m, b = np.polyfit(x, y, 1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = x,
        y = y,
        mode = 'markers',
        name = 'Inadimplência X SELIC',
        marker = dict(
            color='rgba(0, 123, 255, 0.8)',
            size=12,
            line=dict(width=2, color='white'),
            symbol='circle'
            ),
            hovertemplate = 'SELIC: %{x:.2f}% <br> Inadimplência: %{y:.2f}% <extra> </extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x = x,
        y = m * x + b,
        mode = 'lines',
        name = 'Linha de Tendência',
        line = dict(
            color = 'rgba(200, 53, 69, 1)',
            width = 4,
            dash = 'dot'
            
        )
    ))
    fig.update_layout(
        title = {
            'text':f'<b>Correlação entre SELIC e Inadimplência</b><br><span style="font-size:16px">Coeficiente de Correlação</span>',
            'y':0.95,
            'x':0.5,
            'xanchor':'center',
            'yanchor':'top'
        },
        xaxis_title = dict(
            text = 'SELIC Média Mensal (%)',
            font = dict(family = 'Arial', size = 18,  color = 'gray')
        ),
        xaxis = dict(
            tickfont = dict(family = 'Arial', size = 14, color = 'black'),
            gridcolor = 'lightgray'
        ),
        yaxis_title = dict(
            text = 'Inadimplência (%)',
            font = dict(family = 'Arial', size = 18, color = 'gray'),
        ),
        yaxis = dict(
            tickfont = dict(family = 'Arial', size = 14, color = 'black'),
            gridcolor = 'lightgray'
        ),
        plot_bgcolor = '#f8f9fa',
        paper_bgcolor = 'white',
        font = dict(family = 'Arial', size = 14, color = 'black'),
        legend = dict(
            orientation = 'h',
            yanchor = 'bottom',
            y = 1.05,
            xanchor = 'center',
            bgcolor = 'rgba(0, 0, 0, 0)',
            borderwidth = 0
        ),
        margin = dict( l = 60, r= 60, t = 120, b = 60)
    )
    
    grafico_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return render_template_string('''
        <html>
            <head>
                <title></title>
                <style>
                    body{
                        font-family: Arial, sans-serif;
                        background-color: #ffffff;
                        color: #333
                    }
                    .container{
                        width=90%;
                        margin: auto;
                        text-align: center;    
                    }
                    h1{
                        margin-top:40px;
                    }
                    a{
                        text-decoration: none;
                        color: #007bff;
                    }
                    a:hover{
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Correlação entre SELIC e Inadimplência</h1>
                    <div> {{ grafico|safe }} </div>
                    <br>
                    <a href="/">Voltar</a>
                </div>
            </body>
        </html>
    ''', grafico = grafico_html)

@app.route('/insights_3d')
def insights_3d():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)
    merged = pd.merge(inad_df, selic_df, on='mes').sort_values('mes')
    merged['mes_idx'] = range(len(merged))

    # Aqui vemos quanto a inadimplência subiu ou caiu comparado ao mês anterior
    merged['tend_inad'] = merged['inadimplencia'].diff().fillna(0)
    trend_color = ['subiu' if x > 0 else 'caiu' if x < 0 else 'estável' for x in merged['tend_inad']]

    # Calculamos as mudanças de valor da inadimplência e da selic de um mês para outro
    merged['var_inad'] = merged['inadimplencia'].diff().fillna(0)
    merged['var_selic'] = merged['selic_diaria'].diff().fillna(0)

    # Prepararmos os dados para descobrir grupos de meses parecidos
    features = merged[['inadimplencia','selic_diaria']].copy()
    scaler = StandardScaler()
    scaler_features = scaler.fit_transform(features) # Transforma para escalar os valores entre -1 e 1

    # Usamos o kmeans para separar os meses em 3 grupos
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    merged['cluster'] = kmeans.fit_predict(scaler_features)

    # Aqui montamos um "plano inclinado" para tentar prever a inadimplencia no tempo selic
    X = merged[['mes_idx', 'selic_diaria']].values
    Y = merged['inadimplencia'].values
    A = np.c_[X, np.ones(X.shape[0])] # Adiciona uma coluna de 1s para o cálculo funcionar
    coeffs, _, _, _ = np.linalg.lstsq(A, Y, rcond=None)
   
    # Criamos uma grade de pontos para desenhar o plano de regressão
    xi = np.linspace(merged['mes_idx'].min(), merged['mes_idx'].max(),30)
    yi = np.linspace(merged['selic_diaria'].min(), merged['selic_diaria'].max(),30)
    xi, yi = np.meshgrid(xi, yi)

    # Aplicamos a equação do plano nos pontos
    zi = coeffs[0]*xi + coeffs[1]*yi + coeffs[2]

    # Criamos os pontinhos no gráfico 3D
    scatter = go.Scatter3d(
        x = merged['mes_idx'],
        y = merged['selic_diaria'],
        z = merged['inadimplencia'],
        mode = 'markers',
        marker = dict(
            size = 8,
            color = merged['cluster'],
            colorscale = 'Viridis',
            opacity = 0.9
        ),
        text = [f"Mês: {m}<br>Inadimplência{{x:.2f}}<br>Selic: {y:.2f}<br> Var Inad: {vi:.2f}<br>Var Selic: {vs:.2f}<br>Tendência{t:.2f}"
        for m, z, vi, y, vs, t in zip(
            merged['mes'], merged['inadimplencia'],merged['selic_diaria'],
            merged['var_inad'], merged['var_selic'], trend_color
        )
        ],
        hovertemplate='%{text}<extra></extra>'
    )

    # Vamos criar um plano de regressão como uma camada transparente vermelha, nossa "folha vermelha"

    surface = go.Surface(
        x = xi,
        y = yi,
        z = zi,
        showscale = False,
        colorscale = 'Reds',
        opacity = 0.5,
        name = 'Plano de Regressão'
    )

    # Juntamos os dois no gráfico
    fig = go.Figure(data=[scatter,surface])

    # Aqui vamos apenas ajustar os títulos e o layout 3D
    fig.update_layout(
        scene = dict(
            xaxis = dict(title='Tempo (Meses)', tickvals=merged['mes_idx'], ticktext = merged['mes']),
            yaxis = dict(title = 'SELIC (%)'),
            zaxis = dict(title = 'Inadimplência (%)')
        ),
        title = 'Insights Econômicos 3D com Tendência, Derivada e Clusters',
        margin = dict(l=0, r=0, t=50, b=0),
        height = 800
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template_string('''
    <html>
        <head>
            <title>Insights Econômicos 3D</title>
            <style>
                body{
                    font-family: Arial, sans-serif;
                    background-color: #f8f9fa;
                    color: #222;
                    text-align: center;
                    }
                .container{
                    width: 95%;
                    margin: auto;
                    }
                a{
                    text-decoration: none;
                    color: #007bff;
                    }
                a:hover{
                    text-decoration: underline;
                    }
            </style>
        </head>
        <body>
            <div>
                <h1>Gráfico 3D com Insights Econômicos</h1>
                <p>Análise visual com clusters, tendências e plano de regressão</p>
                <div>{{ grafico|safe }}</div>
                <br><a href='/'> Voltar </a>
            </div>
        </body>
    </html>

    ''', grafico = graph_html)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
