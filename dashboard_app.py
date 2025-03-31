# Importação das bibliotecas necessárias
import streamlit as st         # Biblioteca para criação de dashboards
from streamlit_folium import st_folium  # Para integração com Folium
import pandas as pd           # Biblioteca para manipulação de dados
import matplotlib.pyplot as plt  # Para gráficos
import folium                   # Biblioteca para mapas interativos


# Carregando o arquivo de dados
df = pd.read_csv("finanAgroGoias2014-2024.csv" , encoding='utf-8', sep=';')

print(df.head(10))

#troca todos os '-' por zero
df = df.replace('-', '0')
print(df.head(10))

#verificar o tipo de dado das colunas
print(df.dtypes)

#verificando o tipo de dado das colunas
tipos = df['2014'].apply(type)
print(tipos)

# df.iloc[:, 1:] seleciona todas as colunas, exceto a primeira
# col.str.replace('.', '', regex=False) remove os pontos e 
# col.str.replace(',', '.', regex=False) troca a vírgula por ponto
df.iloc[:, 1:] = df.iloc[:, 1:].apply(
    lambda col: pd.to_numeric(
        col.str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
        errors='coerce'
    )
)

print(df.head(10))
#Verificando o tipo de dado da coluna 2020
tipos = df['2020'].apply(type)
tipos.head(10)

# Seleciona as colunas numéricas (int e float)
numeric_cols = df.select_dtypes(include=['float', 'int']).columns

# Aplica o arredondamento de 2 casas decimais nas colunas numéricas
df[numeric_cols] = df[numeric_cols].round(2)

# Calcula a média das colunas a partir da segunda (colunas de 2014 a 2024) 
# para cada linha (localidade)
df["Md_Invest"] = df.iloc[:, 1:].mean(axis=1)

#arrendondar para duas casas decimais
df["Md_Invest"] = df["Md_Invest"].round(2)


# Inserir uma linha com a média de investimento para cada ano

# 1. Calcula a média das colunas de investimento (excluindo a coluna 'Localidade')
# df.iloc[:, 1:] seleciona todas as colunas a partir da segunda (índices dos anos)
mean_values = df.iloc[:, 1:].mean()

# 2. Cria uma lista com o rótulo "Média" para a primeira coluna e os valores médios para as demais
nova_linha = ["Média"] + mean_values.tolist()

# 3. Converte a lista em um DataFrame com as mesmas colunas do df original
linha_media = pd.DataFrame([nova_linha], columns=df.columns)

# 4. Concatena a nova linha ao dataframe original (ignore_index=True para reindexar)
df = pd.concat([df, linha_media], ignore_index=True)


# Seleciona as colunas numéricas (int e float)
numeric_cols = df.select_dtypes(include=['float', 'int']).columns

# Aplica o arredondamento de 2 casas decimais nas colunas numéricas
df[numeric_cols] = df[numeric_cols].round(2)

#iniciar o dashboard
# Configuração do layout da tabela na página
st.set_page_config(layout="wide")

# Configuração do título
st.title('Dashboard Financeiro - Agro Goiás - 2014-2024')
#st.write('Dashboard Financeiro - Tabela Geral')
st.dataframe(df.style.format({'Md_Invest': '{:.2f}'}))

#mostra a tabela com a média de investimento (nova linha) de cada ano arredondada para duas casas decimais
#st.dataframe(df.style.format({'2014': '{:.2f}', '2015': '{:.2f}', 
                #'2016': '{:.2f}', '2017': '{:.2f}', '2018': '{:.2f}', '2019': '{:.2f}', '2020': '{:.2f}',
                #'2021': '{:.2f}', '2022': '{:.2f}', '2023': '{:.2f}', '2024': '{:.2f}'}))


# Cria um widget de seleção para escolher a localidade
# Removendo espaços antes e depois dos nomes das localidades (strip)
df["Localidade"] = df["Localidade"].astype(str).str.strip()


# Atualizar lista de localidades após limpeza
localidades = df.loc[df["Localidade"] != "Média", "Localidade"].unique().tolist()
# Opção Todos para seleção
opcoes_localidade = ["Todos"] + localidades
localidade_selecionada = st.sidebar.selectbox("Selecione a Localidade:", opcoes_localidade)
# Colunas com os anos (assumindo que primeira coluna é 'Localidade' e última 'Md_Invest')
colunas_anos = df.columns[1:-1]

#Definindo o layout do gráfico, primeira linha com 2 colunas
col1, col2 = st.columns(2)
#Segunda linha com 3 colunas
col3, col4 = st.columns(2)

with col1:
    # Filtro para localidade escolhida
    if localidade_selecionada == "Todos":
        # Filtrando excluindo a linha "Média"
        df_plot = df[df["Localidade"] != "Média"]
        # Calcula média por ano
        investimentos_ano = df_plot[colunas_anos].mean()
        st.write("### Média dos investimentos por ano (Todas as localidades):")
        st.bar_chart(investimentos_ano)
    else:
        # Certifique-se de que a seleção e os dados tenham exatamente o mesmo formato
        df_local = df[df["Localidade"] == localidade_selecionada]
        # Exibir dataframe para conferir se está correto (debug)
        st.write(f"Dados filtrados para {localidade_selecionada}:")
        st.dataframe(df_local)
        if not df_local.empty:
            investimentos_local = df_local.iloc[0][colunas_anos]
            st.write(f"Evolução dos investimentos para {localidade_selecionada}:")
            st.bar_chart(investimentos_local)
        else:
            st.error("Nenhum dado encontrado para essa localidade. Confira o nome exato.")

with col2:
    st.write("### Gráfico de Linhas: Evolução dos Investimentos")
    # Reaproveita os mesmos dados do gráfico de barras para a linha
    if localidade_selecionada == "Todos":
        investimentos_ano = df[df["Localidade"] != "Média"].loc[:, colunas_anos].mean()
    else:
        investimentos_ano = df_local.iloc[0][colunas_anos]
    st.line_chart(investimentos_ano)

with col3:
    st.write("### Comparação da Cidade com a Média Geral")
    # Verifica se uma localidade específica foi selecionada
    if localidade_selecionada != "Todos" and not df_local.empty:
        # Pega os dados da localidade
        investimentos_local = df_local.iloc[0][colunas_anos]
                # Calcula a média geral das localidades (excluindo linha de média adicionada)
        investimentos_media = df[df["Localidade"] != "Média"].loc[:, colunas_anos].mean()
        # Cria DataFrame para visualização
        df_comparacao = pd.DataFrame({
            "Ano": colunas_anos,
            localidade_selecionada: investimentos_local.values,
            "Média Geral": investimentos_media.values
        })
        # Define o ano como índice para melhorar a visualização
        df_comparacao.set_index("Ano", inplace=True)
        # Exibe o gráfico
        st.bar_chart(df_comparacao)
    else:
        st.info("Selecione uma localidade para visualizar a comparação.")

with col4:
    # Passo 7: Exibir um quadro com o ano de maior investimento da cidade selecionada
    st.write("### Ano com Maior Investimento")
    # Verifica se foi selecionada uma localidade específica e se os dados filtrados não estão vazios
    if localidade_selecionada != "Todos" and not df_local.empty:
        # Seleciona os investimentos da localidade para as colunas dos anos
        investimentos_local = df_local.iloc[0][colunas_anos]
        # Encontra o ano com o maior investimento (o índice com o valor máximo)
        ano_max = investimentos_local.idxmax()
        valor_max = investimentos_local.max()
        # Exibe a informação utilizando st.metric
        st.metric(label="Ano com Maior Investimento", value=ano_max, delta=f"Valor: {valor_max:.2f}")
    else:
        st.info("Selecione uma localidade específica para visualizar o ano com maior investimento.")
