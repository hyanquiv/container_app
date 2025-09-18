# Dockerfile para backend (Flask)
FROM python:3.10-slim

WORKDIR /app

# Copiar requirements primero
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Instalar MUSCLE desde repositorios
RUN apt-get update && apt-get install -y muscle && rm -rf /var/lib/apt/lists/*

# Copiar código fuente
COPY . .
COPY exec/ ./exec/
    

EXPOSE 5000

# Comando para iniciar Flask
CMD ["python", "app.py"]
