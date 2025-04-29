from pydantic import BaseModel

class ChamadoCreate(BaseModel):
    descricao: str
    cliente: str
    status_atual: str
    historico: str

class ChamadoUpdate(BaseModel):
    status_atual: str

