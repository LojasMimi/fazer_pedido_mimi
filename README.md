

# 📦 Novo Processo de Pedidos – TESTE

**Versão:** 1.0

---

## 🧾 Visão Geral

Este aplicativo foi desenvolvido em **Python com Streamlit** para otimizar o processo de seleção e solicitação de produtos pelas unidades da **Lojas Mimi**. Através da importação de planilhas padrão da empresa, o sistema permite filtrar fornecedores, selecionar produtos e gerar uma planilha de pedidos personalizada e pronta para integração com o sistema interno de gestão de estoques.

---

## 🚀 Funcionalidades

* **Importação de Planilhas Excel:**
  Leitura automática de todas as abas com dados a partir da linha 14, respeitando o formato atual das planilhas corporativas.

* **Filtragem por Fornecedor:**
  Seleção dinâmica do fornecedor desejado com base nas abas válidas.

* **Visualização de Produtos Disponíveis:**
  Interface clara com listagem de produtos associados ao fornecedor escolhido.

* **Solicitação de Produtos:**
  Seleção e quantidade de produtos com controle de duplicatas e atualização de itens já adicionados.

* **Exportação de Arquivo:**
  Geração de uma planilha `.xlsx` contendo somente os produtos selecionados, pronta para uso no sistema da empresa.

* **Instruções Pós-Exportação:**
  Orientações integradas na interface para uso direto no sistema CADIMPORT, CADPLA ou CADPRO via fórmula Excel.

---

## 📁 Estrutura do Projeto

```
📦 novo-processo-pedidos/
├── 📜 fazer_pedidos.py               ← Código principal da aplicação Streamlit
├── 📜 README.md                      ← Este arquivo
```

---

## ▶️ Como Executar

### Pré-requisitos

* Python 3.8+
* Pacotes:

  * `streamlit`
  * `pandas`
  * `xlsxwriter`
  * `openpyxl`

### Instalação e Execução

```bash
pip install -r requirements.txt
streamlit run fazer_pedidos.py
```

---

## 📝 Modo de Uso

1. **Importe a planilha Excel padrão** com dados dos fornecedores.
2. **Selecione o fornecedor** desejado.
3. **Visualize os produtos disponíveis** e selecione um por vez, informando a quantidade.
4. **Adicione à lista de pedidos**.
5. Após adicionar todos os itens, clique em **"Exportar Arquivo"**.
6. Siga as **instruções pós-exportação** diretamente na interface para vincular os dados ao sistema interno.

---

## 💡 Exemplo de Fórmula para Integração

Dentro do Excel corporativo (CADIMPORT/CADPRO/CADPLA), use a fórmula abaixo para buscar as quantidades solicitadas:

```excel
=SEERRO(PROCV(CELULA_DO_CODIGO;'[pedidos_solicitados.xlsx]Pedidos Solicitados'!$A$2:$D$300;3;FALSO);"")
```

Substitua `CELULA_DO_CODIGO` pelo valor da célula que contém o código do produto (por exemplo, `G10`).

---

## 📌 Observações Técnicas

* A aplicação mantém o estado da lista de produtos solicitados durante a sessão com `st.session_state`.
* Evita duplicação de itens na solicitação e permite atualização das quantidades.
* Requer que os arquivos Excel estejam no **padrão de colunas conhecido**, com colunas como:
  `Fornecedor`, `CODIGO`, `DESCRIÇÃO`, `QT PD`, entre outras.

---

## 🔒 Segurança

* Nenhum dado é transmitido para servidores externos.
* Toda a operação é realizada localmente no navegador e na memória do sistema.

---

**© 2025 Lojas Mimi – Todos os direitos reservados.**

---


