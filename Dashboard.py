# importando as bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

################### configurando o layout da pagina ###################
st.set_page_config(layout='wide')

# criando função para formatação dos números
def formata_numero(valor, prefixo = ''):
    for unidade in  ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor: .2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor: .2f} milhões'

# adcionando um título
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

########################## Leitura dos dados ##############################
url = 'https://labdados.com/produtos'
# filtrando ano e regiao direto na requisição da api
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'] # cria lista de opções de região
st.sidebar.title('Filtros') # adicona titulo na barra lateral
regiao = st.sidebar.selectbox('Região', regioes) # inclui filtro na barra lateral
# se não tiver nada filtrado retorna vazio
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True) # cria filtro para todos os anos
# verifica se o filtro foi selecionado e aplica regra
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano} # cria a query da requisição
response = requests.get(url, params=query_string) # faz a requisição com a query
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# criando filtros depois da requisição
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique()) # cria filtro com vendedores
# verifica se foi selecionado algum vendedor e aplica o filtro no dataframe (dados)
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

############################ TABELAS #######################################
# Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

# Tabelas de Quantidade de vendas
vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

# Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


############################## GRÁFICOS ##########################################
# Gráfico de receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                    lat= 'lat',
                                    lon = 'lon',
                                    scope= 'south america',
                                    size= 'Preço',
                                    template= 'seaborn',
                                    hover_name= 'Local da compra',
                                    hover_data= {'lat': False, 'lon': False},
                                    title= 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                                x = 'Mes',
                                y = 'Preço',
                                markers=True,
                                range_y= (0,receita_mensal.max()),
                                color= 'Ano',
                                line_dash= 'Ano',
                                title= 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                                x = 'Local da compra',
                                y = 'Preço',
                                text_auto= True,
                                title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title= 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

# gráfico de vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                    lat= 'lat',
                                    lon = 'lon',
                                    scope= 'south america',
                                    size= 'Preço',
                                    template= 'seaborn',
                                    hover_name= 'Local da compra',
                                    hover_data= {'lat': False, 'lon': False},
                                    title= 'Vendas por estado')

fig_vendas_mensal = px.line(vendas_mensal,
                                x = 'Mes',
                                y = 'Preço',
                                markers=True,
                                range_y= (0,receita_mensal.max()),
                                color= 'Ano',
                                line_dash= 'Ano',
                                title= 'Quantidade de vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de vendas mensal')

fig_vendas_estados = px.bar(vendas_estados.head(),
                                x = 'Local da compra',
                                y = 'Preço',
                                text_auto= True,
                                title='Top 5 estados')
fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto=True,
                                title= 'Vendas por categoria')
fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade de vendas')


################################# VISUALIZAÇÃO ################################

## contruindo 3 abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    ## criando 2 colunas
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # adicionando métrica de receita total
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # adicionando gráfico de mapa
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        # adicionando grafico de barras
        st.plotly_chart(fig_receita_estados, use_container_width=True)

    with coluna2:
        # adicionando métrica de quantidade de vendas (conta linhas da tabela)
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        # adicionando gráfico de linha
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        # adicionando gráfico de categorias
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    ## criando 2 colunas
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # adicionando métrica de receita total
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # adicionando gráfico de mapa
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        # adicionando grafico de barras
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with coluna2:
        # adicionando métrica de quantidade de vendas (conta linhas da tabela)
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        # adicionando gráfico de linha
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        # adicionando gráfico de categorias
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    ## criando 2 colunas
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # adicionando métrica de receita total
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # criando gráfico de vendedor de acordo com o input
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        # adicionando métrica de quantidade de vendas (conta linhas da tabela)
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        # criando gráfico de vendedor de acordo com o input
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)        

