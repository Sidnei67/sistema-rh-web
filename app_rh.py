import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
from datetime import datetime, date

# --- CONFIGURAÇÃO ---
# MANTENHA O SEU LINK AQUI (Não apague o que já estava funcionando!)
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/1JvYrEt0P3fcnCsINtN7zWcKRPoEjRtcCZqR-UAZOBxo/edit?gid=0#gid=0"

st.set_page_config(page_title="RH + Google Sheets", layout="wide")
st.title("🌐 Controle de Funcionários")

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES ---


def get_data():
    return conn.read(spreadsheet=LINK_PLANILHA, worksheet="Dados", ttl=0)

# 1. ATUALIZAMOS AQUI: A função agora recebe mais dados


def add_funcionario(nome, cargo, salario, email, data_admissao):
    try:
        df_atual = get_data()

        # 2. ATUALIZAMOS AQUI: O pacote de dados agora tem os campos novos
        novo_dado = pd.DataFrame([{
            "nome": nome,
            "cargo": cargo,
            "salario": salario,
            "email": email,
            # Convertendo a data para texto para salvar na planilha
            data_admissao = st.date_input(
    "Data de Admissão",
    value=date.today(),             # Começa com a data de hoje
    min_value=date(1950, 1, 1),     # Permite datas desde 1950
    max_value=date.today(),         # Não permite datas futuras
    format="DD/MM/YYYY"             # Formato brasileiro visual
)
        }])

        df_atualizado = pd.concat([df_atual, novo_dado], ignore_index=True)
        conn.update(spreadsheet=LINK_PLANILHA,
                    worksheet="Dados", data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False


def delete_funcionario(index_to_delete):
    try:
        df_atual = get_data()
        df_atualizado = df_atual.drop(index_to_delete)
        conn.update(spreadsheet=LINK_PLANILHA,
                    worksheet="Dados", data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")
        return False


# --- INTERFACE ---
menu_option = st.sidebar.radio("Menu", ["Visualizar", "Cadastrar", "Excluir"])

if menu_option == "Visualizar":
    st.subheader("Equipe Atual")
    try:
        df = get_data()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

elif menu_option == "Cadastrar":
    st.subheader("Novo Cadastro")
    with st.form("form_add"):
        # Layout: Colunas para ficar mais bonito
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail Corporativo")  # NOVO CAMPO

        with col2:
            cargo = st.text_input(
                "Cargo")
            salario = st.number_input(
                "Salário (R$)", min_value=0.0, step=100.0)
            data_admissao = st.date_input("Data de Admissão")  # NOVO CAMPO

        if st.form_submit_button("Salvar Funcionário"):
            # 3. ATUALIZAMOS AQUI: Enviamos os novos campos para a função
            if nome:
                if add_funcionario(nome, cargo, salario, email, data_admissao):
                    st.success("✅ Funcionário salvo com sucesso!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("O campo Nome é obrigatório.")

elif menu_option == "Excluir":
    st.subheader("Excluir")
    try:
        df = get_data()
        if not df.empty:
            # Mostra ID e Nome para facilitar
            opcoes = [f"{i} - {row['nome']}" for i, row in df.iterrows()]
            escolha = st.selectbox("Selecione para remover:", opcoes)

            if st.button("Confirmar Exclusão", type="primary"):
                index = int(escolha.split(" - ")[0])
                if delete_funcionario(index):
                    st.success("Removido!")
                    time.sleep(1)
                    st.rerun()
    except:
        st.write("Sem dados.")



