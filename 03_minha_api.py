from flask import Flask, render_template

# Criar o app flask
app = Flask(__name__)

# Rota da página inicial
@app.route('/')
def home():
    return "<h1>Bem vindo à pagina inicial</h1>"

# Rota do sobre
@app.route('/sobre')
def sobre():
    return "Feito com carinho ♥ por Caio"

# rota com variável na url
@app.route('/ola/<nome>')
def ola(nome):
    return f"<h1>Olá {nome}!</h1>"

# Iniciar o servidor flask
if  __name__ == '__main__':
    app.run(debug=True)

