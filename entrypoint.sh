#!/bin/bash

# Script de inicialización para el contenedor
set -e

# Asegurar que el directorio de uploads tenga los permisos correctos
if [ -d "/app/uploads" ]; then
    chown -R appuser:appuser /app/uploads 2>/dev/null || true
    chmod 755 /app/uploads
fi

# Ejecutar el comando original
exec "$@"
