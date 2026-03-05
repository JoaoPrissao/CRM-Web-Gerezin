# 1. Pega um "computador" limpo e super leve na internet já com Python instalado
FROM python:3.12-slim

# 2. Cria uma pasta chamada /app dentro desse computador e entra nela
WORKDIR /app

# 3. Copia a nossa lista de compras para dentro dessa pasta
COPY requirements.txt .

# 4. Instala todas as ferramentas da lista
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todo o resto do seu código (main.py, index.html, logo_gerezin.png)
COPY . .

# 6. O comando que liga o motor quando a nuvem ligar a máquina
# (Usamos 0.0.0.0 para avisar que a internet inteira pode acessar o servidor)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]