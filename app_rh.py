import streamlit as st
import sqlite3
import pandas as pd
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema RH Web", layout="wide")

# --- FUNÇÕES DE BANCO DE DADOS ---


def get_connection():
    return sqlite3.connect("funcionarios.db")


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL,
            salario REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_funcionario(nome, cargo, salario):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO funcionarios (nome, cargo, salario) VALUES (?, ?, ?)",
              (nome, cargo, salario))
    conn.commit()
    conn.close()


def get_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM funcionarios", conn)
    conn.close()
    return df


def delete_funcionario(id_func):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM funcionarios WHERE id = ?", (id_func,))
    conn.commit()
    conn.close()


# Inicializa o banco ao abrir
init_db()

# --- INTERFACE (FRONTEND) ---
st.title("🌐 Controle de Funcionários - Web")

# Layout: Menu Lateral para Ações
st.sidebar.header("Gerenciamento")
menu_option = st.sidebar.radio(
    "Escolha uma ação:", ["Visualizar Equipe", "Cadastrar Novo", "Excluir"])

# --- ABA 1: VISUALIZAR ---
if menu_option == "Visualizar Equipe":
    st.subheader("Quadro de Funcionários")
    df = get_data()

    if not df.empty:
        # Formata o salário para visualização (R$)
        df_show = df.copy()
        df_show['salario'] = df_show['salario'].apply(lambda x: f"R$ {x:.2f}")

        # Mostra tabela interativa
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        # Métricas rápidas
        col1, col2 = st.columns(2)
        col1.metric("Total de Funcionários", len(df))
        col2.metric("Média Salarial", f"R$ {df['salario'].mean():.2f}")
    else:
        st.info("Nenhum funcionário cadastrado ainda.")

# --- ABA 2: CADASTRAR ---
elif menu_option == "Cadastrar Novo":
    st.subheader("Novo Cadastro")

    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        cargo = st.selectbox("Cargo", [
                             "Desenvolvedor", "Analista de Dados", "Gerente", "RH", "Estagiário", "Outro"])
        salario = st.number_input(
            "Salário (R$)", min_value=0.0, step=100.0, format="%.2f")

        submitted = st.form_submit_button("Salvar Funcionário")

        if submitted:
            if nome and cargo:
                add_funcionario(nome, cargo, salario)
                st.success(f"✅ {nome} cadastrado com sucesso!")
                time.sleep(1)  # Pequena pausa para o usuário ler
                st.rerun()  # Atualiza a página
            else:
                st.error("Por favor, preencha o nome.")

# --- ABA 3: EXCLUIR ---
elif menu_option == "Excluir":
    st.subheader("Remover Funcionário")
    df = get_data()

    if not df.empty:
        # Cria uma lista de opções "ID - Nome"
        lista_funcionarios = df.apply(
            lambda x: f"{x['id']} - {x['nome']}", axis=1)
        escolha = st.selectbox("Selecione para excluir:", lista_funcionarios)

        if st.button("Confirmar Exclusão", type="primary"):
            id_para_excluir = escolha.split(" - ")[0]  # Pega só o ID
            delete_funcionario(id_para_excluir)
            st.warning("Funcionário removido.")
            time.sleep(1)
            st.rerun()
    else:
        st.write("Não há funcionários para excluir.")
