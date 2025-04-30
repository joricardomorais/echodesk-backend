import psycopg2
import os
from datetime import datetime
import pytz  # ✅ Importado para aplicar fuso horário de Brasília

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:xLKoVVPlMmyeagijivkkRVlpraTxTqIg@switchyard.proxy.rlwy.net:44803/railway")

# Conecta ao banco
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Exemplo de função para testar conexão
def testar_conexao():
    cur.execute("SELECT version();")
    versao = cur.fetchone()
    return versao

# Criar Tabela no Banco de Dados
def criar_tabela_chamados():
    cur.execute("DROP TABLE IF EXISTS chamados")
    cur.execute("""
        CREATE TABLE chamados (
            chamado SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            cliente TEXT NOT NULL,
            status_atual VARCHAR(50) NOT NULL,
            historico TEXT
        );
    """)
    conn.commit()

def inserir_chamado(descricao, cliente, status_atual, historico):
    cur.execute("""
        INSERT INTO chamados (descricao, cliente, status_atual, historico)
        VALUES (%s, %s, %s, %s)
    """, (descricao, cliente, status_atual, historico))
    conn.commit()

def atualizar_chamado(chamado_id, novo_status):
    # Buscar o histórico atual
    cur.execute("SELECT historico FROM chamados WHERE chamado = %s", (chamado_id,))
    resultado = cur.fetchone()
    
    if resultado is None:
        raise Exception("Chamado não encontrado.")
    
    historico_atual = resultado[0] or ""

    # ✅ Gerar o novo trecho de histórico com fuso de Brasília
    brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(brasilia).strftime("%d/%m/%Y %H:%M")
    novo_trecho = f"[{novo_status} - {agora}]"

    # Atualizar o histórico acumulado
    if historico_atual:
        historico_novo = historico_atual + ", " + novo_trecho
    else:
        historico_novo = novo_trecho

    # Atualizar no banco
    cur.execute("""
        UPDATE chamados
        SET status_atual = %s,
            historico = %s
        WHERE chamado = %s
    """, (novo_status, historico_novo, chamado_id))
    conn.commit()

def buscar_chamados_por_status(status_atual):
    cur.execute("""
        SELECT chamado, descricao, cliente, status_atual, historico
        FROM chamados
        WHERE status_atual ILIKE %s
        ORDER BY chamado DESC
    """, (f"%{status_atual}%",))
    chamados = cur.fetchall()
    return chamados

def buscar_chamados_por_cliente(cliente):
    cur.execute("""
        SELECT chamado, descricao, cliente, status_atual, historico
        FROM chamados
        WHERE cliente ILIKE %s
        ORDER BY chamado DESC
    """, (f"%{cliente}%",))
    chamados = cur.fetchall()
    return chamados
