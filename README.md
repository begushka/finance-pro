# Gestão Financeira

Sistema web de controle financeiro desenvolvido com Python e Streamlit.

## Funcionalidades

- Cadastro e login de usuários
- Registro de entradas e saídas financeiras
- Dashboard com saldo, gráficos e últimas movimentações
- Painel administrativo para cadastrar, editar, visualizar e excluir usuários
- Dados armazenados em banco SQLite

## Tecnologias utilizadas

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

> pra acessa o site acesse esse link https://begushka-finance-pro.streamlit.app/

## Caso queira testa o codigo ou modifica-lo

1. Clone o repositório e entre na pasta do projeto.

```bash
git clone https://github.com/begushka/finance-pro.git
cd finance-pro
```

2. Criar e Instalar Maquina Virtual

```bash
python -m venv .venv
# Em Windows:
.venv\Scripts\activate
# Em macOS/Linux:
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Inicie o sistema:

```bash
streamlit run apps.py
```

5. Abra no navegador o endereço exibido pelo Streamlit, geralmente `http://localhost:8501`.

## Banco de dados

O arquivo `financeiro.db` é criado automaticamente ao iniciar o sistema. Ele armazena usuários e movimentações financeiras localmente.

> O banco de dados e arquivos com dados de usuários não são enviados ao GitHub, pois estão no `.gitignore`.