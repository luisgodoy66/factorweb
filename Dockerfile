# Usa la imagen base de Python que prefieras
FROM python:3.12-slim

# Instala las dependencias del sistema
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    gir1.2-pango-1.0 \
    gir1.2-gdkpixbuf-2.0

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requirements
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código
COPY . /app/

# ... otros comandos ...