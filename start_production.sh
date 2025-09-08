#!/bin/bash

# Script de inicio para producción
# Asegúrate de que este archivo tenga permisos de ejecución: chmod +x start_production.sh

set -e

# Cargar variables de entorno si existe el archivo .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Crear directorio de uploads si no existe
mkdir -p "${UPLOAD_FOLDER:-uploads}"

# Verificar que las dependencias estén instaladas
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn no está instalado. Instalando dependencias de producción..."
    pip install -r requirements.production.txt
fi

# Iniciar la aplicación con Gunicorn
echo "Iniciando aplicación en modo producción..."
exec gunicorn --config gunicorn.conf.py wsgi:application
