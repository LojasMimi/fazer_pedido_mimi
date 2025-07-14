import streamlit as st
import pandas as pd
import io
import os
import openpyxl

st.set_page_config(page_title="Novo Processo de Pedidos - TESTE", layout="wide")

# Título
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>🛍️ Novo Processo de Pedidos - TESTE</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sessão inicial
if "produtos_solicitados" not in st.session_state:
    st.session_state.produtos_solicitados = []

# Carregamento do CSV principal
try:
    df = pd.read_csv("cad_concatenado.csv", dtype=str).fillna("")

    # Abas para navegação
    aba_individual, aba_lote, aba_revisao = st.tabs(["🧍 Pedido Individual", "📂 Pedido em Lote", "📋 Revisar Pedidos"])

    # -----------------------------
    # Aba 1: Pedido Individual
    with aba_individual:
        with st.expander("📁 Selecione o Fornecedor e Produto", expanded=True):
            fornecedores = sorted(df["FORNECEDOR"].dropna().unique())
            fornecedor_selecionado = st.selectbox("🧾 Selecione um FORNECEDOR:", fornecedores)

            tipo_busca = st.selectbox("🔎 Buscar produto por:", ["CÓDIGO DE BARRAS", "REF"])
            coluna_busca = "CODIGO BARRA" if tipo_busca == "CÓDIGO DE BARRAS" else "CODIGO"

            df_filtrado = df[df["FORNECEDOR"] == fornecedor_selecionado]
            opcoes_produto = sorted(df_filtrado[coluna_busca].dropna().unique())
            produto_selecionado = st.selectbox(f"📦 Selecione um produto ({coluna_busca}):", opcoes_produto)

            quantidade = st.number_input("🧮 Digite a quantidade pedida:", min_value=1, step=1)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦 Adicionar Pedido"):
                produto_dados = df_filtrado[df_filtrado[coluna_busca] == produto_selecionado]
                if not produto_dados.empty:
                    produto_info = produto_dados.iloc[0]
                    codigo = produto_info["CODIGO"]
                    descricao = produto_info["DESCRICAO"]
                    cod_barras = produto_info["CODIGO BARRA"]
                    origem = "INDIVIDUAL"

                    # Verifica duplicata
                    ja_adicionado = False
                    for item in st.session_state.produtos_solicitados:
                        if item["CODIGO"] == codigo and item["CODIGO BARRA"] == cod_barras:
                            item["QTD"] = quantidade
                            item["__ORIGEM_PLANILHA__"] = origem
                            ja_adicionado = True
                            break

                    if not ja_adicionado:
                        st.session_state.produtos_solicitados.append({
                            "FORNECEDOR": fornecedor_selecionado,
                            "CODIGO BARRA": cod_barras,
                            "CODIGO": codigo,
                            "DESCRICAO": descricao,
                            "QTD": quantidade,
                            "__ORIGEM_PLANILHA__": origem
                        })

                    st.success(f"✅ Produto '{descricao}' adicionado com quantidade {quantidade}.")
                    st.toast("Produto adicionado com sucesso!")
                else:
                    st.error("❌ Produto não encontrado para o fornecedor selecionado.")

        with col2:
            if st.button("🗑️ Limpar Lista de Pedidos"):
                st.session_state.produtos_solicitados = []
                st.info("Lista de pedidos limpa com sucesso.")

        with col3:
            gerar_excel_individual = st.button("📤 Gerar Excel")

    # -----------------------------
    # Aba 2: Pedido em Lote
    with aba_lote:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Gerar Modelo Excel"):
                modelo_vazio = pd.DataFrame(columns=["CODIGO BARRA", "CODIGO", "DESCRICAO", "QTD"])
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    modelo_vazio.to_excel(writer, index=False, sheet_name="Modelo")
                output.seek(0)
                st.download_button(
                    label="⬇️ Baixar modelo Excel",
                    data=output,
                    file_name="modelo_pedido_lote.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        with col2:
            arquivo = st.file_uploader("📤 Envie o arquivo preenchido (.xlsx)", type=["xlsx"])

        if arquivo:
            with st.spinner("⏳ Processando arquivo..."):
                try:
                    nome_arquivo = os.path.basename(arquivo.name)
                    df_lote = pd.read_excel(arquivo, dtype=str).fillna("")

                    registros_adicionados = 0
                    erros_qtd = []

                    for idx, row in df_lote.iterrows():
                        cod_barras = row.get("CODIGO BARRA", "")
                        codigo = row.get("CODIGO", "")
                        descricao = row.get("DESCRICAO", "")
                        qtd_raw = str(row.get("QTD", "")).strip()

                        if not qtd_raw.isdigit():
                            erros_qtd.append(f"Linha {idx + 2}: QTD inválida '{qtd_raw}' para produto '{descricao}'")
                            continue

                        qtd = int(qtd_raw)

                        produto_match = df[(df["CODIGO"] == codigo) & (df["CODIGO BARRA"] == cod_barras)]
                        if not produto_match.empty:
                            fornecedor = produto_match.iloc[0]["FORNECEDOR"]

                            # Verifica duplicata
                            ja_adicionado = False
                            for item in st.session_state.produtos_solicitados:
                                if item["CODIGO"] == codigo and item["CODIGO BARRA"] == cod_barras:
                                    item["QTD"] = qtd
                                    item["__ORIGEM_PLANILHA__"] = nome_arquivo
                                    ja_adicionado = True
                                    break

                            if not ja_adicionado:
                                st.session_state.produtos_solicitados.append({
                                    "FORNECEDOR": fornecedor,
                                    "CODIGO BARRA": cod_barras,
                                    "CODIGO": codigo,
                                    "DESCRICAO": descricao,
                                    "QTD": qtd,
                                    "__ORIGEM_PLANILHA__": nome_arquivo
                                })
                                registros_adicionados += 1
                        else:
                            st.warning(f"❗ Produto não encontrado: {codigo} / {cod_barras}")

                    if erros_qtd:
                        st.warning("⚠️ Alguns registros foram ignorados por problemas na coluna QTD:")
                        for erro in erros_qtd:
                            st.text(f"• {erro}")

                    st.success(f"✅ {registros_adicionados} produtos adicionados com sucesso.")
                    st.toast("Pedidos em lote processados!")

                except Exception as e:
                    st.error(f"❌ Erro ao processar o arquivo: {e}")

        if st.button("🗑️ Limpar Lista de Pedidos (Lote)"):
            st.session_state.produtos_solicitados = []
            st.info("Lista de pedidos limpa com sucesso.")

    # -----------------------------
    # Aba 3: Revisar Pedidos
    with aba_revisao:
        if st.session_state.produtos_solicitados:
            st.markdown("### 📋 Produtos Solicitados")

            df_pedidos = pd.DataFrame(st.session_state.produtos_solicitados)

            # Remover coluna técnica da exibição
            colunas_visiveis = [col for col in df_pedidos.columns if col != "__ORIGEM_PLANILHA__"]
            df_visivel = df_pedidos[colunas_visiveis]

            mostrar_filtro = st.checkbox("🔍 Aplicar filtro por fornecedor", value=True)
            if mostrar_filtro:
                fornecedores_disponiveis = sorted(df_visivel["FORNECEDOR"].unique())
                filtro_forn = st.multiselect("Filtrar por fornecedor:", fornecedores_disponiveis, default=fornecedores_disponiveis)
                df_visivel = df_visivel[df_visivel["FORNECEDOR"].isin(filtro_forn)]

            st.dataframe(df_visivel, use_container_width=True, hide_index=True, height=300)

            st.markdown("### 📊 Totais por Fornecedor")
            totais = df_visivel.groupby("FORNECEDOR")["QTD"].sum().reset_index()
            st.table(totais)

            if st.button("📤 Gerar Excel com Pedidos"):
                output = io.BytesIO()
                df_exportar = df_visivel.copy()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_exportar.to_excel(writer, index=False, sheet_name='Pedidos Solicitados')
                output.seek(0)
                st.download_button(
                    label="📥 Baixar Arquivo Excel",
                    data=output,
                    file_name="relatorio_pedidos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("Nenhum pedido adicionado ainda.")

    # -----------------------------
    # Rodapé fixo
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-size: 13px; color: gray;'>"
        "APLICATIVO DESENVOLVIDO POR <strong>PABLO</strong> PARA AS <strong>LOJAS MIMI</strong>. TODOS OS DIREITOS RESERVADOS."
        "</div>",
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.error("⚠️ Arquivo 'cad_concatenado.csv' não encontrado. Coloque-o no mesmo diretório do app.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro ao processar o arquivo: {e}")
