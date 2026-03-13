from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import date
from psycopg2.extras import RealDictCursor

from database import get_db_connection
from security import get_current_user, autenticar_usuario
from models import ClienteCreate, DadosConclusao
from pdf_service import gerar_pdf_recibo

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return autenticar_usuario(form_data)

@router.get("/clientes")
def listar_clientes(current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
            return cursor.fetchall()

@router.post("/clientes")
def cadastrar_cliente(cliente: ClienteCreate, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO clientes 
                (nome, telefone, tipo_servico, endereco, data_servico, 
                 status_servico, status_pagamento, ligar_mais_tarde, detalhes, valor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (cliente.nome, cliente.telefone, cliente.tipo_servico, cliente.endereco,
                 cliente.data_servico, cliente.status_servico, cliente.status_pagamento,
                 cliente.ligar_mais_tarde, cliente.detalhes, cliente.valor)
            )
    return {"mensagem": "Registro criado com sucesso."}

@router.put("/clientes/{cliente_id}")
def atualizar_cliente(cliente_id: int, cliente: ClienteCreate, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE clientes SET
                    nome = %s, telefone = %s, tipo_servico = %s, endereco = %s,
                    data_servico = %s, status_servico = %s, status_pagamento = %s,
                    ligar_mais_tarde = %s, detalhes = %s, valor = %s
                WHERE id = %s""",
                (cliente.nome, cliente.telefone, cliente.tipo_servico, cliente.endereco,
                 cliente.data_servico, cliente.status_servico, cliente.status_pagamento,
                 cliente.ligar_mais_tarde, cliente.detalhes, cliente.valor, cliente_id)
            )
    return {"mensagem": "Registro atualizado com sucesso."}

@router.delete("/clientes/{cliente_id}")
def apagar_cliente(cliente_id: int, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    return {"mensagem": "Registro excluído com sucesso."}

@router.put("/clientes/{cliente_id}/concluir")
def concluir_servico(cliente_id: int, dados: DadosConclusao, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE clientes SET status_servico = 'Concluído', valor = %s, status_pagamento = %s WHERE id = %s",
                (dados.valor, dados.status_pagamento, cliente_id)
            )
    return {"mensagem": "Serviço concluído."}

@router.put("/clientes/{cliente_id}/pagar")
def registrar_pagamento(cliente_id: int, current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != "chefe":
        raise HTTPException(status_code=403, detail="Acesso negado.")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE clientes SET status_pagamento = 'Pago' WHERE id = %s", (cliente_id,))
    return {"mensagem": "Pagamento confirmado."}

@router.get("/financeiro/mes-atual")
def dados_financeiros_mes(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != "chefe":
        raise HTTPException(status_code=403, detail="Acesso negado.")
    primeiro_dia = date.today().replace(day=1).strftime("%Y-%m-%d")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM clientes WHERE data_servico >= %s", (primeiro_dia,))
            return cursor.fetchall()

@router.get("/clientes/{cliente_id}/recibo")
def gerar_recibo(cliente_id: int, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
            cliente = cursor.fetchone()

    if not cliente:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")

    pdf_bytes = gerar_pdf_recibo(cliente)
    filename = f"Recibo_Gerezin_{cliente['nome'].replace(' ', '_')}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )