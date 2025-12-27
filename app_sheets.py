import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
from datetime import datetime, date

# ==========================================
# ⚙️ CONFIGURAÇÃO
# ==========================================
# ⚠️ SUBSTITUA PELO SEU LINK DA PLANILHA GOOGLE:
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/1JvYrEt0P3fcnCsINtN7zWcKRPoEjRtcCZqR-UAZOBxo/edit?gid=0#gid=0"

st.set_page_config(page_title="Sistema RH", layout="wide")

# ==========================================
# 🔐 SISTEMA DE LOGIN (SEGURANÇA)
# ==========================================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔒 Acesso Restrito - RH")
    col1, col2 = st.columns([1, 2])
    with col1:
        senha_digitada = st.text_input("Digite a senha de administrador:", type="password")
        if st.button("Entrar"):
            # Pega a senha do arquivo secrets.toml ou usa "admin" como padrão
            senha_correta = st.secrets.get("passwords", {}).get("admin", "admin")
            
            if senha_digitada == senha_correta:
                st.session_state["logado"] = True
                st.success("Logado com sucesso!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop() # 🛑 O código para aqui se não tiver senha

# ==========================================
# 🚀 SISTEMA PRINCIPAL
# ==========================================

st.title("🌐 Controle de Funcionários")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES (LÓGICA) ---
def get_data():
    # Lê a aba "Dados" da planilha
    return conn.read(spreadsheet=LINK_PLANILHA, worksheet="Dados", ttl=0)

def add_funcionario(nome, cargo, departamento, salario, email, data_admissao):
    try:
        df_atual = get_data()
        
        # Cria a nova linha com TODOS os campos
        novo_dado = pd.DataFrame([{
            "nome": nome,
            "cargo": cargo,
            "departamento": departamento, # Campo novo
            "salario": salario,
            "email": email,
            "data_admissao": data_admissao.strftime("%d/%m/%Y") 
        }])
        
        # Junta e salva
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

# --- MENU LATERAL ---
with st.sidebar:
    st.write("👤 Usuário Admin")
    if st.button("Sair (Logout)"):
        st.session_state["logado"] = False
        st.rerun()
    st.divider()
    menu_option = st.radio("Navegação", ["Visualizar Equipe", "Cadastrar Novo", "Excluir"])

# --- TELA: VISUALIZAR ---
if menu_option == "Visualizar Equipe":
    st.subheader("📋 Equipe Atual")
    try:
        df = get_data()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("Erro de conexão. Verifique o Link da Planilha e o arquivo secrets.")
        st.code(str(e))

# --- TELA: CADASTRAR ---
elif menu_option == "Cadastrar Novo":
    st.subheader("📝 Novo Cadastro")
    
    with st.form("form_add"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail Corporativo")
            # Correção do erro de digitação: É st.text_input
            departamento = st.text_input("Departamento")
            
        with col2:
            cargo = st.text_iuput("Cargo")
            salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0)
            data_admissao = st.date_input("Data de Admissão", value=date.today(), min_value=date(1900, 1, 1), format="DD/MM/YYYY")
        
        # Botão de Enviar
        if st.form_submit_button("Salvar Funcionário"):
            if nome and departamento:
                # Passando todos os dados para a função
                sucesso = add_funcionario(nome, cargo, departamento, salario, email, data_admissao)
                if sucesso:
                    st.success("✅ Funcionário salvo com sucesso!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("⚠️ Preencha pelo menos Nome e Departamento.")

# --- TELA: EXCLUIR ---
elif menu_option == "Excluir":
    st.subheader("🗑️ Excluir Funcionário")
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
        else:
            st.info("Nenhum funcionário na lista.")
    except:
        st.write("Erro ao carregar lista.")


