import os
import psycopg2
from fastapi import HTTPException
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
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