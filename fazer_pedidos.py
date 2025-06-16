# 📦 Importação dos pacotes
import streamlit as st
import pandas as pd
import openpyxl  # Necessário para leitura de .xlsx
import xlsxwriter  # Necessário para exportar arquivos .xlsx
import xlrd  # Certifique-se de ter xlrd > 2.0.1 instalado
import io

# ⚙️ Configuração da página
st.set_page_config(page_title="Novo Processo de Pedidos - TESTE")

st.title("NOVO PROCESSO DE PEDIDOS - TESTE")

# 🔄 Inicializa o armazenamento dos produtos selecionados
if "produtos_solicitados" not in st.session_state:
    st.session_state.produtos_solicitados = []

if "resultado_final" not in st.session_state:
    st.session_state.resultado_final = pd.DataFrame()

# 📁 Upload do arquivo Excel
uploaded_file = st.file_uploader("Importe a planilha Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Lê todas as abas com cabeçalho na linha 14 (index 13)
        xls = pd.read_excel(uploaded_file, sheet_name=None, header=13, engine="openpyxl")

        fornecedores_set = set()
        abas_validas = {}

        # Coleta os fornecedores únicos e armazena abas com coluna "Fornecedor"
        for nome_aba, df in xls.items():
            if "Fornecedor" in df.columns:
                abas_validas[nome_aba] = df
                fornecedores_set.update(df["Fornecedor"].dropna().unique())

        if fornecedores_set:
            fornecedores = sorted(list(fornecedores_set))
            fornecedor_selecionado = st.selectbox("Selecione um fornecedor:", fornecedores)

            # Combina dados de todas as abas filtrando pelo fornecedor selecionado
            resultados = []
            for nome_aba, df in abas_validas.items():
                linhas_filtradas = df[df["Fornecedor"] == fornecedor_selecionado]
                if not linhas_filtradas.empty:
                    linhas_filtradas["Aba"] = nome_aba
                    resultados.append(linhas_filtradas)

            if resultados:
                resultado_final = pd.concat(resultados, ignore_index=True)
                st.session_state.resultado_final = resultado_final.copy()

                colunas_desejadas = [
                    "Fornecedor",
                    "COD SISTEMA",
                    "CODIGO BARRA",
                    "CODIGO",
                    "DESCRIÇÃO",
                    "QT PD"
                ]

                colunas_presentes = [col for col in colunas_desejadas if col in resultado_final.columns]
                resultado_filtrado = resultado_final[colunas_presentes]

                st.subheader(f"Resultados para o fornecedor: {fornecedor_selecionado}")
                st.dataframe(resultado_filtrado)

                if "DESCRIÇÃO" in resultado_filtrado.columns:
                    produtos_disponiveis = resultado_filtrado["DESCRIÇÃO"].dropna().unique()
                    produto_selecionado = st.selectbox("Selecione um produto:", sorted(produtos_disponiveis))

                    quantidade = st.number_input(
                        f"Digite a quantidade para '{produto_selecionado}':",
                        min_value=1,
                        step=1,
                        key=f"quantidade_{produto_selecionado}"
                    )

                    if st.button("Adicionar produto à lista"):
                        dados_produto = resultado_filtrado[resultado_filtrado["DESCRIÇÃO"] == produto_selecionado]

                        if not dados_produto.empty:
