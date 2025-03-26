# Usa la imagen base de Python que prefieras
FROM python:3.10-slim

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

# Expone el puerto en el que correrá la aplicación
EXPOSE 3000

# Establece las variables de entorno necesarias
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=factorweb25.settings

# Comando para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]