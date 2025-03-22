import pandas as pd

''' Leitura simples de arquivo do Excel '''

caminho = 'C:/Users/sabado/Desktop/PAPA Python Analise de Dados/PAPA/01_base_vendas.xlsx'

df =  pd.read_excel(caminho)
# df = Data Frame

# Lendo uma planilha específica

df_clientes = pd.read_excel(caminho,sheet_name=0)
# Lendo a primeira planilha do arquivo, que está no index 0. A planilha também pode ser especificada pelo nome entre aspas simples
print(df_clientes)

df_clientes = pd.read_excel(caminho,sheet_name=1)
# Lendo a segunda planilha do arquivo, que está no index 1. A planilha também pode ser especificada pelo nome entre aspas simples
print(df_clientes)

# Lendo uma coluna específica
df_nome_clientes = pd.read_excel(caminho, sheet_name=0, usecols=['Cliente'])
print(df_nome_clientes)

# Lendo a partir de uma linha específica
df_vendas = pd.read_excel(
    caminho,
    sheet_name=0,
    skiprows=5
) 
print(df_vendas)