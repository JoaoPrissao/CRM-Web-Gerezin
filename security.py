import os
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "chave_padrao_segura")
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

USERS = {
    os.getenv("USUARIO_JOAO", "joao_vitor"): {
        "password_hash": pwd_context.hash(os.getenv("SENHA_JOAO", "senha_padrao_joao")),
        "perfil": "chefe",
    },
    os.getenv("USUARIO_TECO", "teco_gerezin"): {
        "password_hash": pwd_context.hash(os.getenv("SENHA_TECO", "senha_padrao_teco")),
        "perfil": "chefe",
    },
    os.getenv("USUARIO_LOJA", "loja"): {
        "password_hash": pwd_context.hash(os.getenv("SENHA_LOJA", "senha123")),
        "perfil": "operador",
    },
}

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        perfil: str = payload.get("perfil", "operador")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado. Realize um novo login.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")
    return {"username": username, "perfil": perfil}

def autenticar_usuario(form_data: OAuth2PasswordRequestForm):
    user = USERS.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")
    
    token = create_access_token({"sub": form_data.username, "perfil": user["perfil"]})
    return {"access_token": token, "token_type": "bearer", "perfil": user["perfil"]}