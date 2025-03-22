import pandas as pd

# Carregar arquivo do Excel
arquivo = 'C:/Users/sabado/Desktop/PAPA Python Analise de Dados/PAPA/01_base_vendas.xlsx'

# Carregar os dados das duas abas do Excel
df1 = pd.read_excel(arquivo, sheet_name='Relatório de Vendas')
df2 = pd.read_excel(arquivo, sheet_name='Relatório de Vendas1')

# Exibir as primeiras para conferir como estão os dados
print('Relatorio de Vendas 1:')
print(df2.head())

print('Relatorio de Vendas 2:')
print(df2.head())

# Verificar se tem duplicatas nas duas planilhas

print('\nDuplicatas no "relatório de vendas 1"')
print(df1.duplicated().sum())

print('\nDuplicatas no "relatório de vendas 2"')
print(df2.duplicated().sum())

# Agora vamos fazer o merge dos dois Dataframes
# Vamos combinar as tabelas apenas pelas linhas (concatenar), já que as colunas são as mesmas

df_consolidado = pd.concat([df1, df2], ignore_index=True)
print('\n Dados Consolidados')
print(df_consolidado.head())

# Verificar se há dados duplicados no dataframe consolidado
print('\nDuplicatas no "Consolidado"')
print(df_consolidado.duplicated().sum())

# Remover as duplicatas caso existam
df_consolidado = df_consolidado.drop_duplicates()

# Exibir o número de clientes por cidade
clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('\nNumero de clientes por cidade:')
print(clientes_por_cidade)

# Exibir o numero de vendas por plano
vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()
print('\nNumero de vendas por plano:')
print(vendas_por_plano)

# Exibir as 3 primeiras cidades com mais clientes
top3_cidades = clientes_por_cidade.head(3)
print('\nTop 3 cidades com mais clientes:')
print(top3_cidades)

# Adicionar a coluna de status (exemplo ficticio de analise)
# Vamos classificar os planos como Premium se for Enterprise, senão é padrão.

df_consolidado['Status'] = df_consolidado['Plano Vendido'].apply(lambda x: 'Premium' if x == 'Enterprise' else 'Padrao')
# A função lambda do Python é uma função avançada que faz repetir em todos os valores, substituindo o For ou o While.

# Exibir distribuição dos Status
status_dist = df_consolidado['Status'].value_counts()
print('\nDistribuição de Status por planos:')
print(status_dist)

# Salvar o dataframe consolidado em dois formatos

# Em Excel:
df_consolidado.to_excel('dados_consolidados.xlsx', index=False)

# Em CSV:
df_consolidado.to_csv('dados_consolidados.csv', index=False)

# Exibir a mensagem final
print("Dados gerados com sucesso. Consulte na sua pasta.")