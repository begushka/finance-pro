import streamlit as st
import json
import os
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px # Adicionado para o gráfico de pizza

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Financeira Pro", layout="wide", page_icon="💰")

# --- BANCO DE DADOS SQLITE ---
CAMINHO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financeiro.db")

def conexao():
    banco = sqlite3.connect(CAMINHO_BANCO)
    banco.row_factory = sqlite3.Row
    return banco

def inicializar_banco():
    with conexao() as banco:
        banco.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                senha TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ativo'
            )
        """)
        banco.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                descricao TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
            )
        """)
        arquivo_legado = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.json")
        if os.path.exists(arquivo_legado):
            try:
                with open(arquivo_legado, "r", encoding="utf-8") as arquivo:
                    usuarios_legados = json.load(arquivo)
                for usuario, dados in usuarios_legados.items():
                    banco.execute(
                        "INSERT OR IGNORE INTO usuarios (usuario, senha, status) VALUES (?, ?, ?)",
                        (usuario, dados["senha"], dados.get("status", "ativo"))
                    )
            except (OSError, json.JSONDecodeError, KeyError):
                pass
        banco.execute(
            "INSERT OR IGNORE INTO usuarios (usuario, senha, status) VALUES (?, ?, ?)",
            ("begushka", "santozx", "ativo")
        )

def carregar_usuarios():
    with conexao() as banco:
        registros = banco.execute("SELECT usuario, senha, status FROM usuarios ORDER BY usuario").fetchall()
    return {item["usuario"]: {"senha": item["senha"], "status": item["status"]} for item in registros}

def criar_usuario(usuario, senha):
    try:
        with conexao() as banco:
            banco.execute(
                "INSERT INTO usuarios (usuario, senha, status) VALUES (?, ?, 'ativo')",
                (usuario, senha)
            )
        return True
    except sqlite3.IntegrityError:
        return False

def atualizar_status(usuario, status):
    with conexao() as banco:
        banco.execute("UPDATE usuarios SET status = ? WHERE usuario = ?", (status, usuario))

def carregar_dados(usuario):
    with conexao() as banco:
        registros = banco.execute(
            "SELECT tipo, valor, descricao, data FROM movimentacoes WHERE usuario = ? ORDER BY id DESC",
            (usuario,)
        ).fetchall()
    return [dict(item) for item in registros]

def adicionar_dado(usuario, tipo, valor, descricao):
    with conexao() as banco:
        banco.execute(
            "INSERT INTO movimentacoes (usuario, tipo, valor, descricao, data) VALUES (?, ?, ?, ?, ?)",
            (usuario, tipo, valor, descricao, datetime.now().strftime("%d/%m/%Y %H:%M"))
        )

def excluir_usuario(nome_usuario):
    if nome_usuario != 'begushka':
        with conexao() as banco:
            banco.execute("DELETE FROM movimentacoes WHERE usuario = ?", (nome_usuario,))
            banco.execute("DELETE FROM usuarios WHERE usuario = ?", (nome_usuario,))
        st.toast(f"Usuário {nome_usuario} removido permanentemente!")

inicializar_banco()

# --- CONTROLE DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""

# --- TELA DE LOGIN ---
def tela_login():
    st.markdown("<h1 style='text-align: center;'>🏪 Área de Acesso</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        aba_entrar, aba_registrar = st.tabs(["🔑 Entrar", "📝 Registrar"])

        with aba_entrar:
            with st.form("login_form"):
                u = st.text_input("Usuário").strip()
                p = st.text_input("Senha", type="password").strip()
                if st.form_submit_button("Acessar Sistema"):
                    banco = carregar_usuarios()
                    if u in banco and banco[u]["senha"] == p:
                        if banco[u]["status"] == "ativo":
                            st.session_state.logado = True
                            st.session_state.usuario = u
                            st.rerun()
                        else:
                            st.error("❌ Acesso suspenso. Entre em contato com o suporte.")
                    else:
                        st.error("Usuário ou senha incorretos.")

        with aba_registrar:
            with st.form("registro_form"):
                usuario = st.text_input("Novo usuário").strip()
                senha = st.text_input("Nova senha", type="password").strip()
                confirmar_senha = st.text_input("Confirmar senha", type="password").strip()
                cadastrar = st.form_submit_button("Criar conta")

                if cadastrar:
                    banco = carregar_usuarios()
                    if not usuario or not senha:
                        st.error("Preencha usuário e senha.")
                    elif usuario in banco:
                        st.error("Este usuário já está cadastrado.")
                    elif senha != confirmar_senha:
                        st.error("As senhas não conferem.")
                    else:
                        if criar_usuario(usuario, senha):
                            st.success("Conta criada! Agora você já pode entrar.")
                        else:
                            st.error("Este usuário já está cadastrado.")

# --- TELA PRINCIPAL ---
def tela_principal():
    user_logado = st.session_state.usuario
    st.sidebar.title(f"👤 Olá, {user_logado}")
    
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state.logado = False
        st.rerun()

    # --- SEÇÃO DE MARKETING ---
    st.sidebar.divider()
    st.sidebar.markdown("### 🚀 Desenvolvedor")
    st.sidebar.info("**insta: @santozx_._7**") 
    st.sidebar.caption("Soluções inteligentes em Python")

    # --- PAINEL DO ADMINISTRADOR ---
    if user_logado == "begushka":
        st.info("🛠 **Painel Administrativo Detectado**")
        with st.expander("Gerenciar Clientes"):
            aba_lista, aba_novo, aba_credenciais, aba_excluir = st.tabs(["Lista/Editar", "Cadastrar Novo", "👥 Usuários e Senhas", "🗑️ Excluir Usuário"])
            
            with aba_lista:
                banco = carregar_usuarios()
                clientes = [c for c in banco.keys() if c != "begushka"]
                if clientes:
                    c_alvo = st.selectbox("Escolha o Cliente para Editar", clientes)
                    novo_st = st.radio("Status", ["ativo", "suspenso"], index=0 if banco[c_alvo]["status"]=="ativo" else 1)
                    
                    if st.button("Salvar Alterações"):
                        atualizar_status(c_alvo, novo_st)
                        st.success(f"Dados de {c_alvo} atualizados!")
                else:
                    st.write("Nenhum cliente cadastrado.")

            with aba_novo:
                n_u = st.text_input("Nome do Usuário")
                n_p = st.text_input("Senha de Acesso")
                if st.button("Gerar Acesso"):
                    if n_u and n_p:
                        if criar_usuario(n_u, n_p):
                            st.success(f"Conta para {n_u} criada!")
                            st.rerun()
                        else:
                            st.error("Este usuário já está cadastrado.")

            with aba_credenciais:
                usuarios = carregar_usuarios()
                tabela_usuarios = pd.DataFrame([
                    {"Usuário": nome, "Senha": dados["senha"], "Status": dados["status"]}
                    for nome, dados in usuarios.items()
                ])
                st.dataframe(tabela_usuarios, use_container_width=True, hide_index=True)

            with aba_excluir:
                st.warning("Cuidado! A exclusão é permanente.")
                banco = carregar_usuarios()
                for u_nome in list(banco.keys()):
                    if u_nome != 'begushka':
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"👤 {u_nome}")
                        if c2.button("Apagar", key=f"del_{u_nome}"):
                            excluir_usuario(u_nome)
                            st.rerun()

    st.title(f"📈 Dashboard Financeiro")
    
    # --- LOGICA FINANCEIRA ---
    dados = carregar_dados(user_logado)
    st.sidebar.divider()
    st.sidebar.subheader("Novo Registro")
    tipo = st.sidebar.selectbox("Tipo", ["Entrada", "Saída"])
    valor = st.sidebar.number_input("Valor (R$)", min_value=0.0)
    desc = st.sidebar.text_input("Descrição")
    
    if st.sidebar.button("Confirmar"):
        if desc:
            adicionar_dado(user_logado, tipo.lower(), valor, desc)
            st.rerun()

    if dados:
        df = pd.DataFrame(dados)
        ent = df[df['tipo'].str.contains('entrada', case=False, na=False)]['valor'].sum()
        sai = df[df['tipo'].str.contains('saida|saída', case=False, na=False)]['valor'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {ent:.2f}")
        c2.metric("Saídas", f"R$ {sai:.2f}")
        c3.metric("Saldo", f"R$ {ent - sai:.2f}")

        st.divider()
        
        # --- GRÁFICOS ---
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("📊 Comparativo Barras")
            st.bar_chart(pd.DataFrame({'R$': [ent, sai]}, index=['Entradas', 'Saídas']))
            
        with col_g2:
            st.subheader("🍕 Distribuição %")
            # Gráfico de pizza usando Plotly para mostrar porcentagens
            fig = px.pie(values=[ent, sai], names=['Entradas', 'Saídas'], 
                        color_discrete_sequence=['#2ecc71', '#e74c3c'],
                        hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("🕒 Últimas Movimentações")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            
    else:
        st.warning("Aguardando primeiros lançamentos...")

# --- INÍCIO ---
if not st.session_state.logado:
    tela_login()
else:
    tela_principal()
