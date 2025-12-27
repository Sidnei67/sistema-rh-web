import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
from datetime import datetime, date # <--- MUDANÇA 1 AQUI

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
from datetime import datetime, date

# --- CONFIGURAÇÃO ---
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/1JvYrEt0P3fcnCsINtN7zWcKRPoEjRtcCZqR-UAZOBxo/edit?gid=0#gid=0" # <--- MANTENHA O SEU LINK!

st.set_page_config(page_title="RH + Google Sheets", layout="wide")

# ==========================================
# 🔐 SISTEMA DE LOGIN (PORTÃO DE SEGURANÇA)
# ==========================================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    # Mostra apenas a tela de login
    st.title("🔒 Acesso Restrito - RH")
    
    senha_digitada = st.text_input("Digite a senha de administrador:", type="password")
    
    if st.button("Entrar"):
        # Tenta pegar a senha do arquivo secrets, se não achar, usa "admin" como padrão
        senha_correta = st.secrets.get("passwords", {}).get("admin", "admin")
        
        if senha_digitada == senha_correta:
            st.session_state["logado"] = True
            st.success("Logado com sucesso!")
            time.sleep(0.5)
            st.rerun() # Recarrega a página para mostrar o sistema
        else:
            st.error("Senha incorreta.")
    
    st.stop() # 🛑 PARE AQUI! Não carrega o resto do código se não estiver logado.

# ==========================================
# 🚀 O SEU SISTEMA COMEÇA AQUI (Só carrega se passou do login)
# ==========================================

st.title("🌐 Controle de Funcionários")

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES ---
def get_data():
    return conn.read(spreadsheet=LINK_PLANILHA, worksheet="Dados", ttl=0)

def add_funcionario(nome, cargo, salario, email, data_admissao):
    try:
        df_atual = get_data()
        novo_dado = pd.DataFrame([{
            "nome": nome,
            "cargo": cargo,
            "salario": salario,
            "email": email,
            "data_admissao": data_admissao.strftime("%d/%m/%Y") 
        }])
        df_atualizado = pd.concat([df_atual, novo_dado], ignore_index=True)
        conn.update(spreadsheet=LINK_PLANILHA, worksheet="Dados", data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def delete_funcionario(index_to_delete):
    try:
        df_atual = get_data()
        df_atualizado = df_atual.drop(index_to_delete)
        conn.update(spreadsheet=LINK_PLANILHA, worksheet="Dados", data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")
        return False

# --- INTERFACE ---
# Adicionei um botão de SAIR na barra lateral
if st.sidebar.button("Sair (Logout)"):
    st.session_state["logado"] = False
    st.rerun()

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
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail Corporativo")
        with col2:
            cargo = st.selectbox("Cargo", ["Dev", "Analista", "Gerente", "RH", "Suporte"])
            salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0)
            data_admissao = st.date_input("Data de Admissão", value=date.today(), min_value=date(1950, 1, 1), format="DD/MM/YYYY")
        
        if st.form_submit_button("Salvar Funcionário"):
            if nome:
                if add_funcionario(nome, cargo, salario, email, data_admissao):
                    st.success("✅ Funcionário salvo!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("O campo Nome é obrigatório.")

elif menu_option == "Excluir":
    st.subheader("Excluir")
    try:
        df = get_data()
        if not df.empty:
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

# --- CONFIGURAÇÃO ---
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/1JvYrEt0P3fcnCsINtN7zWcKRPoEjRtcCZqR-UAZOBxo/edit?gid=0#gid=0"

st.set_page_config(page_title="RH + Google Sheets", layout="wide")
st.title("🌐 Controle de Funcionários")

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES ---
def get_data():
    return conn.read(spreadsheet=LINK_PLANILHA, worksheet="Dados", ttl=0)

def add_funcionario(nome, cargo, salario, email, data_admissao):
    try:
        df_atual = get_data()
        
        novo_dado = pd.DataFrame([{
            "nome": nome,
            "cargo": cargo,
            "salario": salario,
            "email": email,
            "data_admissao": data_admissao.strftime("%d/%m/%Y") 
        }])
        
        df_atualizado = pd.concat([df_atual, novo_dado], ignore_index=True)
        conn.update(spreadsheet=LINK_PLANILHA, worksheet="Dados", data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def delete_funcionario(index_to_delete):
    try:
        df_atual = get_data()
        df_atualizado = df_atual.drop(index_to_delete)
        conn.update(spreadsheet=LINK_PLANILHA, worksheet="Dados", data=df_atualizado)
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
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail Corporativo")
            
        with col2:
            cargo = st.selectbox("Cargo")
            salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0)
            
            # --- MUDANÇA 2 AQUI (DATA COM LIMITE ANTIGO) ---
            data_admissao = st.date_input(
                "Data de Admissão",
                value=date.today(),
                min_value=date(1950, 1, 1), # Permite anos antigos
                max_value=date.today(),
                format="DD/MM/YYYY"
            )
        
        if st.form_submit_button("Salvar Funcionário"):
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


