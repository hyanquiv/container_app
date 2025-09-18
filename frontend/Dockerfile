# Dockerfile para frontend (Streamlit)
FROM python:3.10-slim

WORKDIR /app

# Copiar requirements primero (para aprovechar cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY app.py .

EXPOSE 3000

# Comando para correr Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=3000", "--server.address=0.0.0.0"]
