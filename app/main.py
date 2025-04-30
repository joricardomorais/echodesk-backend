from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app import database, schemas

app = FastAPI()

@app.get("/")
def read_root():
    try:
        versao = database.testar_conexao()
        return {"mensagem": "EchoDesk está rodando!", "PostgreSQL": versao}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/chamados")
def listar_chamados():
    try:
        database.cur.execute("SELECT chamado, descricao, cliente, status_atual, historico FROM chamados ORDER BY chamado DESC")
        chamados = database.cur.fetchall()
        resultado = []
        for c in chamados:
            resultado.append({
                "chamado": c[0],
                "descricao": c[1],
                "cliente": c[2],
                "status_atual": c[3],
                "historico": c[4]
            })
        return resultado
    except Exception as e:
        return {"erro": str(e)}

@app.get("/chamados/{chamado_id}")
def obter_chamado_por_id(chamado_id: int):
    try:
        database.cur.execute("SELECT chamado, descricao, cliente, status_atual, historico FROM chamados WHERE chamado = %s", (chamado_id,))
        resultado = database.cur.fetchone()
        if resultado:
            return {
                "chamado": resultado[0],
                "descricao": resultado[1],
                "cliente": resultado[2],
                "status_atual": resultado[3],
                "historico": resultado[4]
            }
        else:
            raise HTTPException(status_code=404, detail="Chamado não encontrado")
    except Exception as e:
        return {"erro": str(e)}

@app.post("/chamados")
def criar_chamado(chamado: schemas.ChamadoCreate):
    try:
        database.inserir_chamado(
            chamado.descricao,
            chamado.cliente,
            chamado.status_atual,
            chamado.historico
        )
        return {"mensagem": "Chamado criado com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}

@app.put("/chamados/{chamado}")
def atualizar_chamado(chamado: int, dados: schemas.ChamadoUpdate):
    try:
        database.atualizar_chamado(
            chamado,
            dados.status_atual
        )
        return {"mensagem": f"Chamado {chamado} atualizado com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/chamados/status/{status_atual}")
def listar_chamados_por_status(status_atual: str):
    try:
        chamados = database.buscar_chamados_por_status(status_atual)
        if not chamados:
            return {"mensagem": "Nenhum chamado encontrado com esse status."}
        resultado = []
        for c in chamados:
            resultado.append({
                "chamado": c[0],
                "descricao": c[1],
                "cliente": c[2],
                "status_atual": c[3],
                "historico": c[4]
            })
        return resultado
    except Exception as e:
        return {"erro": str(e)}

@app.get("/chamados/cliente/{cliente}")
def listar_chamados_por_cliente(cliente: str):
    try:
        chamados = database.buscar_chamados_por_cliente(cliente)
        if not chamados:
            return {"mensagem": "Nenhum chamado encontrado para esse cliente."}
        resultado = []
        for c in chamados:
            resultado.append({
                "chamado": c[0],
                "descricao": c[1],
                "cliente": c[2],
                "status_atual": c[3],
                "historico": c[4]
            })
        return resultado
    except Exception as e:
        return {"erro": str(e)}