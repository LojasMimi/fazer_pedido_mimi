
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Novo Processo de Pedidos - TESTE")
st.title("NOVO PROCESSO DE PEDIDOS - TESTE")

# Inicializa armazenamento
if "produtos_solicitados" not in st.session_state:
    st.session_state.produtos_solicitados = []

if "resultado_final" not in st.session_state:
    st.session_state.resultado_final = pd.DataFrame()

# Upload do Excel
uploaded_file = st.file_uploader("Importe a planilha Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Leitura automática, sem especificar engine
        xls = pd.read_excel(uploaded_file, sheet_name=None, header=13)

        fornecedores_set = set()
        abas_validas = {}

        # Coleta fornecedores únicos e abas válidas
        for nome_aba, df in xls.items():
            if "Fornecedor" in df.columns:
                abas_validas[nome_aba] = df
                fornecedores_set.update(df["Fornecedor"].dropna().unique())

        if fornecedores_set:
            fornecedores = sorted(list(fornecedores_set))
            fornecedor_selecionado = st.selectbox("Selecione um fornecedor:", fornecedores)

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
                    "Fornecedor", "COD SISTEMA", "CODIGO BARRA",
                    "CODIGO", "DESCRIÇÃO", "QT PD"
                ]
                colunas_presentes = [col for col in colunas_desejadas if col in resultado_final.columns]
                resultado_filtrado = resultado_final[colunas_presentes]

                st.subheader(f"Resultados para o fornecedor: {fornecedor_selecionado}")
                st.dataframe(resultado_filtrado, use_container_width=True)

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
                            cod = dados_produto.iloc[0]["CODIGO"]
                            desc = dados_produto.iloc[0]["DESCRIÇÃO"]

                            # Substitui se já foi adicionado
                            ja_adicionado = False
                            for p in st.session_state.produtos_solicitados:
                                if p["CODIGO"] == cod:
                                    p["QT PD"] = quantidade
                                    ja_adicionado = True
                                    break

                            if not ja_adicionado:
                                st.session_state.produtos_solicitados.append({
                                    "CODIGO": cod,
                                    "DESCRIÇÃO": desc,
                                    "QT PD": quantidade
                                })

                            st.success(f"Produto '{desc}' com quantidade {quantidade} adicionado com sucesso.")
                        else:
                            st.warning("Produto não encontrado nos dados.")

                if st.session_state.produtos_solicitados:
                    st.subheader("QUANTIDADES SOLICITADAS")
                    df_solicitados = pd.DataFrame(st.session_state.produtos_solicitados)
                    st.dataframe(df_solicitados, use_container_width=True)

                    if st.button("Exportar Arquivo"):
                        df_exportacao = pd.DataFrame(st.session_state.produtos_solicitados)

                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_exportacao.to_excel(writer, index=False, sheet_name='Pedidos Solicitados')

                        output.seek(0)

                        st.download_button(
                            label="📥 Baixar Arquivo Atualizado",
                            data=output,
                            file_name="pedidos_solicitados.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
