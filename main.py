import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import init_db
from routes import router

load_dotenv()

app = FastAPI(title="Gerezin CRM")

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:8000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco de dados
init_db()

# Importa todas as rotas (CRUD e Auth)
app.include_router(router)

# Monta a pasta de arquivos estáticos (CSS e JS)
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/{filename}")
def serve_static(filename: str):
    path = f"frontend/{filename}"
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado.")