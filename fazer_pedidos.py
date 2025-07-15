import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO

st.set_page_config(page_title="Processo de Pedidos - TESTE", layout="wide")

CSV_URL = "https://raw.githubusercontent.com/LojasMimi/fazer_pedido_mimi/refs/heads/main/cad_concatenado.csv"

st.markdown("<h1 style='text-align: center; color: #1E90FF;'>🛍️ Processo de Pedidos - TESTE</h1>", unsafe_allow_html=True)
st.markdown("---")

if "produtos_solicitados" not in st.session_state:
    st.session_state.produtos_solicitados = []

try:
    df = pd.read_csv(CSV_URL, dtype=str).fillna("")

    def get_origem_produto(fornecedor: str, codigo: str) -> str:
        match = df[(df["FORNECEDOR"] == fornecedor) & (df["CODIGO"] == codigo)]
        if not match.empty:
            return match.iloc[0].get("ORIGEM", "").strip()
        return ""

    aba_individual, aba_lote, aba_revisao = st.tabs(["🧍 Pedido Individual", "📂 Pedido em Lote", "📋 Revisar Pedidos"])

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

        if st.button("📦 Adicionar Pedido"):
            produto_dados = df_filtrado[df_filtrado[coluna_busca] == produto_selecionado]
            if not produto_dados.empty:
                produto_info = produto_dados.iloc[0]
                codigo = produto_info["CODIGO"]
                descricao = produto_info["DESCRICAO"]
                cod_barras = produto_info["CODIGO BARRA"]
                origem = get_origem_produto(fornecedor_selecionado, codigo)

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

    # Aba 2: Pedido em Lote
    with aba_lote:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Gerar Modelo Excel"):
                modelo_vazio = pd.DataFrame(columns=["CODIGO BARRA", "CODIGO", "QTD"])
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
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

        tipo_busca_lote = st.selectbox("🔍 Identificador de busca para o lote:", ["CÓDIGO DE BARRAS", "REF"])
        coluna_busca_lote = "CODIGO BARRA" if tipo_busca_lote == "CÓDIGO DE BARRAS" else "CODIGO"

        if arquivo:
            with st.spinner("⏳ Processando arquivo..."):
                try:
                    wb = load_workbook(filename=BytesIO(arquivo.read()))
                    ws = wb.active
                    data = ws.values
                    cols = next(data)
                    df_lote = pd.DataFrame(data, columns=cols).fillna("")

                    registros_adicionados = 0
                    erros_qtd = []

                    for idx, row in df_lote.iterrows():
                        identificador_valor = str(row.get(coluna_busca_lote, "")).strip()
                        qtd_raw = str(row.get("QTD", "")).strip()

                        if not qtd_raw.isdigit():
                            erros_qtd.append(f"Linha {idx + 2}: QTD inválida '{qtd_raw}'")
                            continue

                        qtd = int(qtd_raw)
                        produto_match = df[df[coluna_busca_lote] == identificador_valor]
                        if not produto_match.empty:
                            produto_info = produto_match.iloc[0]
                            fornecedor = produto_info["FORNECEDOR"]
                            codigo = produto_info["CODIGO"]
                            cod_barras = produto_info["CODIGO BARRA"]
                            descricao = produto_info["DESCRICAO"]
                            origem = get_origem_produto(fornecedor, codigo)

                            ja_adicionado = False
                            for item in st.session_state.produtos_solicitados:
                                if item["CODIGO"] == codigo and item["CODIGO BARRA"] == cod_barras:
                                    item["QTD"] = qtd
                                    item["__ORIGEM_PLANILHA__"] = origem
                                    ja_adicionado = True
                                    break

                            if not ja_adicionado:
                                st.session_state.produtos_solicitados.append({
                                    "FORNECEDOR": fornecedor,
                                    "CODIGO BARRA": cod_barras,
                                    "CODIGO": codigo,
                                    "DESCRICAO": descricao,
                                    "QTD": qtd,
                                    "__ORIGEM_PLANILHA__": origem
                                })
                                registros_adicionados += 1
                        else:
                            st.warning(f"❗ Produto não encontrado com valor '{identificador_valor}' na coluna '{coluna_busca_lote}'.")

                    if erros_qtd:
                        st.warning("⚠️ Alguns registros foram ignorados por problemas na coluna QTD:")
                        for erro in erros_qtd:
                            st.text(f"• {erro}")

                    st.success(f"✅ {registros_adicionados} produtos adicionados com sucesso.")
                    st.toast("Pedidos em lote processados!")

                except Exception as e:
                    st.error(f"❌ Erro ao processar o arquivo: {e}")

    # Aba 3: Revisar Pedidos
    with aba_revisao:
        if st.session_state.produtos_solicitados:
            st.markdown("### 📋 Produtos Solicitados")

            df_pedidos = pd.DataFrame(st.session_state.produtos_solicitados)

            mostrar_filtro = st.checkbox("🔍 Aplicar filtro por fornecedor", value=True)
            if mostrar_filtro:
                fornecedores_disponiveis = sorted(df_pedidos["FORNECEDOR"].unique())
                filtro_forn = st.multiselect("Filtrar por fornecedor:", fornecedores_disponiveis, default=fornecedores_disponiveis)
                df_pedidos = df_pedidos[df_pedidos["FORNECEDOR"].isin(filtro_forn)]

            st.dataframe(df_pedidos, use_container_width=True, hide_index=True, height=300)

            st.markdown("### 📊 Totais por Fornecedor")
            totais = df_pedidos.groupby("FORNECEDOR")["QTD"].sum().reset_index()
            st.table(totais)

            if st.button("📤 Gerar Excel com Pedidos"):
                output = BytesIO()
                df_exportar = df_pedidos.copy()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
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

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-size: 13px; color: gray;'>"
        "APLICATIVO DESENVOLVIDO POR <strong>PABLO</strong> PARA AS <strong>LOJAS MIMI</strong>. TODOS OS DIREITOS RESERVADOS."
        "</div>",
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.error("⚠️ Arquivo 'cad_concatenado.csv' não encontrado.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro ao processar o arquivo: {e}")
