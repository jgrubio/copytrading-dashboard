# Dockerfile para el dashboard de trading
FROM python:3.11-slim

# Metadatos
LABEL maintainer="tu-email@ejemplo.com"
LABEL description="Dashboard de análisis de trading"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=false

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.production.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.production.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio de uploads y dar permisos
RUN mkdir -p uploads && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/uploads && \
    chmod 777 /app/uploads

# Copiar y configurar script de entrada
COPY entrypoint-prod.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Comando por defecto
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
