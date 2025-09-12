# Multi-stage build para el backend Python/Flask

# Etapa 1: Build - Instalación de dependencias
FROM python:3.11-slim as builder

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para build
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python en un directorio específico
RUN pip install --no-cache-dir --user -r requirements.txt

# Instalar Gunicorn (Supervisor se instalará en la etapa de producción)
RUN pip install --no-cache-dir --user gunicorn

# Etapa 2: Producción - Imagen limpia con artefactos necesarios
FROM python:3.11-slim as production

# Instalar supervisor y curl para healthcheck
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python desde la etapa builder
COPY --from=builder /root/.local /home/app/.local

# Copiar código fuente de la aplicación
COPY --chown=app:app . .

# Configurar PATH para que encuentre los paquetes instalados
ENV PATH=/home/app/.local/bin:$PATH

# Crear directorio para logs de supervisor
RUN mkdir -p /var/log/supervisor /var/run/supervisor && chown -R app:app /var/log/supervisor /var/run/supervisor

# Configurar Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Cambiar a usuario no-root
USER app

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para iniciar Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
