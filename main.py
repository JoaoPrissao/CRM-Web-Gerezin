from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# 1. Abre o cofre (.env) e carrega as senhas secretas na memória
load_dotenv()

app = FastAPI(title="Gerezin CRM Seguro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. CONFIGURAÇÕES DE SEGURANÇA AVANÇADA
# ==========================================
CHAVE_SECRETA = os.getenv("SECRET_KEY")
ALGORITMO = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 1440 # O Crachá dura 24 horas

# O Triturador de senhas (Bcrypt)
triturador_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")
# O Porteiro que pede o crachá
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Puxa o usuário e a senha do .env, e já tritura a senha na hora!
USUARIO_MESTRE = {
    "username": os.getenv("ADMIN_USERNAME"),
    "senha_triturada": triturador_senha.hash(os.getenv("ADMIN_PASSWORD"))
}

def criar_token_acesso(dados: dict):
    dados_para_codificar = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS)
    dados_para_codificar.update({"exp": expiracao})
    token_codificado = jwt.encode(dados_para_codificar, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token_codificado

# O Guarda-Costas: Função que verifica se o crachá é verdadeiro antes de liberar a ação
def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        dados_decodificados = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        usuario: str = dados_decodificados.get("sub")
        if usuario is None:
            raise HTTPException(status_code=401, detail="Crachá inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Crachá vencido, faça login novamente")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Crachá falso")
    return usuario

# ==========================================
# 3. A ROTA DE PORTARIA (Fazer Login e gerar o Crachá)
# ==========================================
@app.post("/login")
def portaria_login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != USUARIO_MESTRE["username"]:
        raise HTTPException(status_code=400, detail="Usuário incorreto")
    
    senha_correta = triturador_senha.verify(form_data.password, USUARIO_MESTRE["senha_triturada"])
    if not senha_correta:
        raise HTTPException(status_code=400, detail="Senha incorreta")
    
    token_jwt = criar_token_acesso(dados={"sub": form_data.username})
    return {"access_token": token_jwt, "token_type": "bearer"}


# ==========================================
# 4. MOLDES DOS DADOS E CRIAÇÃO DO BANCO
# ==========================================
class ClienteNovo(BaseModel):
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

def criar_banco_de_dados():
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            telefone TEXT,
            tipo_servico TEXT,
            endereco TEXT,
            data_servico TEXT,
            status_servico TEXT,
            status_pagamento TEXT,
            ligar_mais_tarde BOOLEAN,
            detalhes TEXT,
            valor TEXT
        )
    ''')
    conexao.commit()
    conexao.close()

criar_banco_de_dados()

# ==========================================
# 5. AS ROTAS DO SISTEMA (Todas Protegidas pelo Guarda-Costas)
# ==========================================

@app.get("/clientes")
def listar_clientes(usuario: str = Depends(verificar_token)):
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute("SELECT * FROM clientes")
    clientes_crus = caneta.fetchall()
    conexao.close()
    
    lista_organizada = []
    for linha in clientes_crus:
        lista_organizada.append({
            "id": linha[0], "nome": linha[1], "telefone": linha[2],
            "tipo_servico": linha[3], "endereco": linha[4], "data_servico": linha[5],
            "status_servico": linha[6], "status_pagamento": linha[7],
            "ligar_mais_tarde": linha[8], "detalhes": linha[9], "valor": linha[10]
        })
    return lista_organizada

@app.post("/clientes")
def cadastrar_cliente(c: ClienteNovo, usuario: str = Depends(verificar_token)):
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute(
        "INSERT INTO clientes (nome, telefone, tipo_servico, endereco, data_servico, status_servico, status_pagamento, ligar_mais_tarde, detalhes, valor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (c.nome, c.telefone, c.tipo_servico, c.endereco, c.data_servico, c.status_servico, c.status_pagamento, c.ligar_mais_tarde, c.detalhes, c.valor)
    )
    conexao.commit()
    conexao.close()
    return {"mensagem": "Salvo com sucesso!"}

@app.put("/clientes/{cliente_id}")
def atualizar_cliente_completo(cliente_id: int, c: ClienteNovo, usuario: str = Depends(verificar_token)):
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute('''
        UPDATE clientes 
        SET nome = ?, telefone = ?, tipo_servico = ?, endereco = ?, data_servico = ?, 
            status_servico = ?, status_pagamento = ?, ligar_mais_tarde = ?, detalhes = ?, valor = ?
        WHERE id = ?
    ''', (c.nome, c.telefone, c.tipo_servico, c.endereco, c.data_servico, c.status_servico, c.status_pagamento, c.ligar_mais_tarde, c.detalhes, c.valor, cliente_id))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Cadastro atualizado com sucesso!"}

@app.delete("/clientes/{cliente_id}")
def apagar_cliente(cliente_id: int, usuario: str = Depends(verificar_token)):
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Apagado com sucesso!"}

@app.put("/clientes/{cliente_id}/concluir")
def concluir_servico(cliente_id: int, dados: DadosConclusao, usuario: str = Depends(verificar_token)):
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute(
        "UPDATE clientes SET status_servico = 'Concluído', valor = ?, status_pagamento = ? WHERE id = ?",
        (dados.valor, dados.status_pagamento, cliente_id)
    )
    conexao.commit()
    conexao.close()
    return {"mensagem": "Concluído e faturado!"}

@app.put("/clientes/{cliente_id}/pagar")
def pagar_servico(cliente_id: int, usuario: str = Depends(verificar_token)):
    conexao = sqlite3.connect("banco_dados.db")
    caneta = conexao.cursor()
    caneta.execute("UPDATE clientes SET status_pagamento = 'Pago' WHERE id = ?", (cliente_id,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Pagamento registrado!"}