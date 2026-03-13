from pydantic import BaseModel

class ClienteCreate(BaseModel):
    nome: str
    telefone: str
    tipo_servico: str
    endereco: str
    data_servico: str
    status_servico: str
    status_pagamento: str
    ligar_mais_tarde: bool
    detalhes: str
    valor: str

class DadosConclusao(BaseModel):
    valor: str
    status_pagamento: str