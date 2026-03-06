from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import psycopg2 # O tradutor para o Supabase
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import Response
from fpdf import FPDF
from fastapi.responses import FileResponse

# Carrega as senhas do arquivo .env (quando rodando no seu computador)
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
# CONFIGURAÇÕES DE SEGURANÇA AVANÇADA
# ==========================================
CHAVE_SECRETA = os.getenv("SECRET_KEY", "chave_padrao_segura")
ALGORITMO = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 1440 

triturador_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Cria o usuário da loja triturando a senha que vem do .env
USUARIO_LOJA = {
    "username": os.getenv("USUARIO_LOJA", "loja"),
    "senha_triturada": triturador_senha.hash(os.getenv("SENHA_LOJA", "senha123"))
}

# Pegando a URL do Supabase do cofre
URL_DO_BANCO = os.getenv("DATABASE_URL")

# Função para conectar no banco da nuvem
def conectar_banco():
    try:
        conexao = psycopg2.connect(URL_DO_BANCO)
        return conexao
    except Exception as e:
        print("Erro ao conectar no Supabase:", e)
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")

def criar_token_acesso(dados: dict):
    dados_para_codificar = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS)
    dados_para_codificar.update({"exp": expiracao})
    token_codificado = jwt.encode(dados_para_codificar, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token_codificado

def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        dados_decodificados = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        usuario: str = dados_decodificados.get("sub")
        perfil: str = dados_decodificados.get("perfil", "operador") # Puxa o cargo do crachá
        if usuario is None:
            raise HTTPException(status_code=401, detail="Crachá inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Crachá vencido, faça login novamente")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Crachá falso")
    
    # Devolve um dicionário com nome e cargo
    return {"usuario": usuario, "perfil": perfil}

@app.post("/login")
def portaria_login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario_digitado = form_data.username
    senha_digitada = form_data.password

    # Puxando os usuários e senhas dos chefes do cofre (.env)
    user_joao = os.getenv("USUARIO_JOAO", "joao_vitor")
    senha_joao = os.getenv("SENHA_JOAO", "senha_padrao_joao")
    
    user_teco = os.getenv("USUARIO_TECO", "teco_gerezin")
    senha_teco = os.getenv("SENHA_TECO", "senha_padrao_teco")
    
    perfil = "operador"
    acesso_permitido = False

    # Verifica João (Chefe)
    if usuario_digitado == user_joao and senha_digitada == senha_joao:
        acesso_permitido = True
        perfil = "chefe"
    # Verifica Teco (Chefe)
    elif usuario_digitado == user_teco and senha_digitada == senha_teco:
        acesso_permitido = True
        perfil = "chefe"
    # Verifica Loja (Operador padrão - usando a senha triturada)
    elif usuario_digitado == USUARIO_LOJA["username"] and triturador_senha.verify(senha_digitada, USUARIO_LOJA["senha_triturada"]):
        acesso_permitido = True
        perfil = "operador"

    if not acesso_permitido:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    # Coloca o perfil dentro do crachá (token)
    token_jwt = criar_token_acesso(dados={"sub": usuario_digitado, "perfil": perfil})
    
    # Devolve para a tela (o HTML precisa saber o perfil para esconder a aba financeiro)
    return {"access_token": token_jwt, "token_type": "bearer", "perfil": perfil}


# ==========================================
# MOLDES DOS DADOS E CRIAÇÃO DA TABELA NA NUVEM
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
    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
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
    caneta.close()
    conexao.close()

criar_banco_de_dados()

# ==========================================
# AS ROTAS DO SISTEMA (PostgreSQL)
# ==========================================

@app.get("/clientes")
def listar_clientes(cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor(cursor_factory=RealDictCursor)
    caneta.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes_crus = caneta.fetchall()
    caneta.close()
    conexao.close()
    return clientes_crus

@app.post("/clientes")
def cadastrar_cliente(c: ClienteNovo, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute(
        "INSERT INTO clientes (nome, telefone, tipo_servico, endereco, data_servico, status_servico, status_pagamento, ligar_mais_tarde, detalhes, valor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (c.nome, c.telefone, c.tipo_servico, c.endereco, c.data_servico, c.status_servico, c.status_pagamento, c.ligar_mais_tarde, c.detalhes, c.valor)
    )
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Salvo com sucesso!"}

@app.put("/clientes/{cliente_id}")
def atualizar_cliente_completo(cliente_id: int, c: ClienteNovo, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute('''
        UPDATE clientes 
        SET nome = %s, telefone = %s, tipo_servico = %s, endereco = %s, data_servico = %s, 
            status_servico = %s, status_pagamento = %s, ligar_mais_tarde = %s, detalhes = %s, valor = %s
        WHERE id = %s
    ''', (c.nome, c.telefone, c.tipo_servico, c.endereco, c.data_servico, c.status_servico, c.status_pagamento, c.ligar_mais_tarde, c.detalhes, c.valor, cliente_id))
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Cadastro atualizado com sucesso!"}

@app.delete("/clientes/{cliente_id}")
def apagar_cliente(cliente_id: int, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Apagado com sucesso!"}

@app.put("/clientes/{cliente_id}/concluir")
def concluir_servico(cliente_id: int, dados: DadosConclusao, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute(
        "UPDATE clientes SET status_servico = 'Concluído', valor = %s, status_pagamento = %s WHERE id = %s",
        (dados.valor, dados.status_pagamento, cliente_id)
    )
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Concluído e faturado!"}

@app.put("/clientes/{cliente_id}/pagar")
def pagar_servico(cliente_id: int, cracha: dict = Depends(verificar_token)):
    # Proteção na porta do banco. Só chefe pode registrar pagamentos diretos!
    if cracha.get("perfil") != "chefe":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas a gerência pode registrar recebimentos.")

    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute("UPDATE clientes SET status_pagamento = 'Pago' WHERE id = %s", (cliente_id,))
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Pagamento registrado!"}

@app.get("/clientes/{cliente_id}/recibo")
def gerar_recibo(cliente_id: int, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor(cursor_factory=RealDictCursor)
    caneta.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
    cliente = caneta.fetchone()
    caneta.close()
    conexao.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Criando o PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Definindo as cores da marca
    azul_escuro = (15, 23, 42)
    azul_claro = (14, 165, 233)
    cinza_texto = (100, 116, 139)
    
    # ==========================================
    # 1. CABEÇALHO DA EMPRESA
    # ==========================================
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.cell(0, 10, "GEREZIN REFRIGERAÇÃO", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(cinza_texto[0], cinza_texto[1], cinza_texto[2])
    pdf.cell(0, 6, "T.J.L Refrigeração LTDA | CNPJ: 11.074.782/0001-20", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, "Apucarana - PR | Cel: (43) 99973-9397 | Fixo: (43) 3422-7598", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Linha divisória colorida
    pdf.ln(5)
    pdf.set_draw_color(azul_claro[0], azul_claro[1], azul_claro[2])
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # ==========================================
    # 2. TÍTULO DO DOCUMENTO
    # ==========================================
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(azul_claro[0], azul_claro[1], azul_claro[2])
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "  RECIBO DE PRESTAÇÃO DE SERVIÇO", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(8)

    # ==========================================
    # 3. DADOS DO CLIENTE
    # ==========================================
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "INFORMAÇÕES DO CLIENTE:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Nome/Loja: {cliente['nome']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Telefone: {cliente['telefone']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Endereço: {cliente['endereco']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # ==========================================
    # 4. DADOS DO SERVIÇO
    # ==========================================
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "DETALHES DO SERVIÇO:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Serviço Realizado: {cliente['tipo_servico']}", new_x="LMARGIN", new_y="NEXT")
    data_formatada = cliente['data_servico'].split('-')
    data_formatada.reverse()
    pdf.cell(0, 6, f"Data da Conclusão: {'/'.join(data_formatada)}", new_x="LMARGIN", new_y="NEXT")
    if cliente['detalhes']:
        pdf.cell(0, 6, f"Observações: {cliente['detalhes']}", new_x="LMARGIN", new_y="NEXT")
    
    # Linha divisória fina
    pdf.ln(5)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # ==========================================
    # 5. VALOR E ASSINATURA
    # ==========================================
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, f"VALOR TOTAL COBRADO: R$ {cliente['valor']}", new_x="LMARGIN", new_y="NEXT", align="R")
    
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(cinza_texto[0], cinza_texto[1], cinza_texto[2])
    texto_situacao = "Recebimento confirmado." if cliente['status_pagamento'] == "Pago" else "Pagamento pendente."
    pdf.cell(0, 6, texto_situacao, new_x="LMARGIN", new_y="NEXT", align="R")
    
    pdf.ln(40)
    pdf.set_draw_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.cell(0, 6, "T.J.L Refrigeração LTDA", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, "Assinatura do Responsável Técnico", new_x="LMARGIN", new_y="NEXT", align="C")

    # Gera e devolve o arquivo
    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Recibo_Gerezin_{cliente['nome'].replace(' ', '_')}.pdf"}
    )

# ==========================================
# ROTAS PARA ENTREGAR A TELA (FRONTEND)
# ==========================================
@app.get("/")
def abrir_sistema():
    return FileResponse("index.html")

@app.get("/{nome_arquivo}")
def entregar_arquivos_extras(nome_arquivo: str):
    import os
    if os.path.exists(nome_arquivo):
        return FileResponse(nome_arquivo)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")