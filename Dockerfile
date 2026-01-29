# Usamos una base de Python ligera
FROM python:3.9-slim

# 1. Instalar FFmpeg en el sistema Linux del servidor (La clave del éxito)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 2. Preparar carpeta de trabajo
WORKDIR /app

# 3. Copiar tus archivos al servidor
COPY . .

# 4. Instalar librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Abrir el puerto y ejecutar la app
CMD gunicorn app:app --bind 0.0.0.0:$PORT