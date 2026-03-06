from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import psycopg2 
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, date # Adicionamos o 'date' aqui
import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import Response
from fpdf import FPDF
from fastapi.responses import FileResponse

# Carrega as variáveis de ambiente (localmente via .env)
load_dotenv()

app = FastAPI(title="Gerezin CRM Seguro")

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# CONFIGURAÇÕES DE SEGURANÇA E AUTENTICAÇÃO (JWT)
# ==========================================
CHAVE_SECRETA = os.getenv("SECRET_KEY", "chave_padrao_segura")
ALGORITMO = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 1440 

# Contexto de criptografia para senhas
triturador_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Configuração do usuário padrão da loja (Operador) com hash bcrypt
USUARIO_LOJA = {
    "username": os.getenv("USUARIO_LOJA", "loja"),
    "senha_triturada": triturador_senha.hash(os.getenv("SENHA_LOJA", "senha123"))
}

# URL de conexão com o banco de dados (Supabase)
URL_DO_BANCO = os.getenv("DATABASE_URL")

# Gerenciador de conexão com o PostgreSQL
def conectar_banco():
    try:
        conexao = psycopg2.connect(URL_DO_BANCO)
        return conexao
    except Exception as e:
        print("Erro ao conectar no Supabase:", e)
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")

# Geração do token JWT contendo as roles (perfis) do usuário
def criar_token_acesso(dados: dict):
    dados_para_codificar = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS)
    dados_para_codificar.update({"exp": expiracao})
    token_codificado = jwt.encode(dados_para_codificar, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token_codificado

# Middleware de validação do token JWT e extração do perfil (RBAC)
def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        dados_decodificados = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        usuario: str = dados_decodificados.get("sub")
        perfil: str = dados_decodificados.get("perfil", "operador") 
        if usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado, realize um novo login")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token malformado ou adulterado")
    
    return {"usuario": usuario, "perfil": perfil}

# Endpoint de autenticação e atribuição de perfis (Chefe / Operador)
@app.post("/login")
def portaria_login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario_digitado = form_data.username
    senha_digitada = form_data.password

    # Recupera as credenciais de administração (Chefia) das variáveis de ambiente
    user_joao = os.getenv("USUARIO_JOAO", "joao_vitor")
    senha_joao = os.getenv("SENHA_JOAO", "senha_padrao_joao")
    
    user_teco = os.getenv("USUARIO_TECO", "teco_gerezin")
    senha_teco = os.getenv("SENHA_TECO", "senha_padrao_teco")
    
    perfil = "operador"
    acesso_permitido = False

    # Validação para perfis de Administração (Chefia)
    if usuario_digitado == user_joao and senha_digitada == senha_joao:
        acesso_permitido = True
        perfil = "chefe"
    elif usuario_digitado == user_teco and senha_digitada == senha_teco:
        acesso_permitido = True
        perfil = "chefe"
    # Validação para o perfil de Operador (utiliza verificação de hash bcrypt)
    elif usuario_digitado == USUARIO_LOJA["username"] and triturador_senha.verify(senha_digitada, USUARIO_LOJA["senha_triturada"]):
        acesso_permitido = True
        perfil = "operador"

    if not acesso_permitido:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    
    # Gera o token de acesso embutindo o payload de autorização (RBAC)
    token_jwt = criar_token_acesso(dados={"sub": usuario_digitado, "perfil": perfil})
    
    return {"access_token": token_jwt, "token_type": "bearer", "perfil": perfil}


# ==========================================
# MODELOS DE DADOS E INICIALIZAÇÃO DO BANCO
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

# Executa a inicialização das tabelas no startup do servidor
criar_banco_de_dados()


# ==========================================
# ENDPOINTS DA API (CRUD E REGRAS DE NEGÓCIO)
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
    return {"mensagem": "Registro criado com sucesso!"}

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
    return {"mensagem": "Registro atualizado com sucesso!"}

@app.delete("/clientes/{cliente_id}")
def apagar_cliente(cliente_id: int, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Registro excluído com sucesso!"}

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
    return {"mensagem": "Status do serviço atualizado para Concluído."}

@app.put("/clientes/{cliente_id}/pagar")
def pagar_servico(cliente_id: int, cracha: dict = Depends(verificar_token)):
    # Proteção de rota: Apenas usuários com perfil 'chefe' podem registrar recebimentos
    if cracha.get("perfil") != "chefe":
        raise HTTPException(status_code=403, detail="Acesso negado. Nível de autorização insuficiente.")

    conexao = conectar_banco()
    caneta = conexao.cursor()
    caneta.execute("UPDATE clientes SET status_pagamento = 'Pago' WHERE id = %s", (cliente_id,))
    conexao.commit()
    caneta.close()
    conexao.close()
    return {"mensagem": "Pagamento confirmado no sistema."}


# ==========================================
# ROTA FINANCEIRA (NOVIDADE: FECHAMENTO DE MÊS)
# ==========================================
@app.get("/financeiro/mes-atual")
def puxar_dados_do_mes(cracha: dict = Depends(verificar_token)):
    # Apenas chefes podem ver os dados financeiros
    if cracha.get("perfil") != "chefe":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    conexao = conectar_banco()
    caneta = conexao.cursor(cursor_factory=RealDictCursor)

    # 1. Descobre que dia é hoje
    hoje = date.today()
    
    # 2. Volta o calendário para o dia 01 deste mês (formato Ano-Mês-Dia)
    primeiro_dia = hoje.replace(day=1).strftime("%Y-%m-%d")

    # 3. Pede ao banco de dados apenas os clientes que têm data igual ou maior que o dia 01
    caneta.execute("SELECT * FROM clientes WHERE data_servico >= %s", (primeiro_dia,))
    servicos_do_mes = caneta.fetchall()

    caneta.close()
    conexao.close()
    
    return servicos_do_mes


# ==========================================
# GERADOR DE RELATÓRIOS (PDF)
# ==========================================
@app.get("/clientes/{cliente_id}/recibo")
def gerar_recibo(cliente_id: int, cracha: dict = Depends(verificar_token)):
    conexao = conectar_banco()
    caneta = conexao.cursor(cursor_factory=RealDictCursor)
    caneta.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
    cliente = caneta.fetchone()
    caneta.close()
    conexao.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Registro não encontrado no banco de dados.")

    # Inicialização da instância FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Paleta de cores da identidade visual
    azul_escuro = (15, 23, 42)
    azul_claro = (14, 165, 233)
    cinza_texto = (100, 116, 139)
    
    # 1. Cabeçalho e Dados da Empresa
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.cell(0, 10, "GEREZIN REFRIGERAÇÃO", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(cinza_texto[0], cinza_texto[1], cinza_texto[2])
    pdf.cell(0, 6, "T.J.L Refrigeração LTDA | CNPJ: 11.074.782/0001-20", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, "Apucarana - PR | Cel: (43) 99973-9397 | Fixo: (43) 3422-7598", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Renderização da linha divisória
    pdf.ln(5)
    pdf.set_draw_color(azul_claro[0], azul_claro[1], azul_claro[2])
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # 2. Título do Documento
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(azul_claro[0], azul_claro[1], azul_claro[2])
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "  RECIBO DE PRESTAÇÃO DE SERVIÇO", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(8)

    # 3. Bloco de Informações do Cliente
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "INFORMAÇÕES DO CLIENTE:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Nome/Loja: {cliente['nome']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Telefone: {cliente['telefone']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Endereço: {cliente['endereco']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # 4. Escopo do Serviço Executado
    pdf.set_text_color(azul_escuro[0], azul_escuro[1], azul_escuro[2])
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "DETALHES DO SERVIÇO:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Serviço Realizado: {cliente['tipo_servico']}", new_x="LMARGIN", new_y="NEXT")
    
    # Formatação de data (YYYY-MM-DD para DD/MM/YYYY)
    data_formatada = cliente['data_servico'].split('-')
    data_formatada.reverse()
    pdf.cell(0, 6, f"Data da Conclusão: {'/'.join(data_formatada)}", new_x="LMARGIN", new_y="NEXT")
    if cliente['detalhes']:
        pdf.cell(0, 6, f"Observações: {cliente['detalhes']}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # 5. Fechamento Financeiro e Assinatura
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

    # Retorna o buffer de memória como Response da API
    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Recibo_Gerezin_{cliente['nome'].replace(' ', '_')}.pdf"}
    )

# ==========================================
# ROTAS DE FRONTEND E ARQUIVOS ESTÁTICOS
# ==========================================
@app.get("/")
def abrir_sistema():
    # Serve o arquivo principal do frontend (Interface do Usuário)
    return FileResponse("frontend/index.html")

@app.get("/{nome_arquivo}")
def entregar_arquivos_extras(nome_arquivo: str):
    # Serve assets estáticos (imagens, favicon, etc) a partir do diretório /frontend
    caminho = f"frontend/{nome_arquivo}"
    if os.path.exists(caminho):
        return FileResponse(caminho)
    raise HTTPException(status_code=404, detail="Asset não encontrado no servidor")