#!/bin/bash

# Script de inicialización para el contenedor
set -e

# Asegurar que el directorio de uploads tenga los permisos correctos
if [ -d "/app/uploads" ]; then
    # Intentar cambiar permisos solo si es posible
    chmod 755 /app/uploads 2>/dev/null || true
    
    # Intentar cambiar propiedad solo si tenemos permisos
    if [ -w "/app/uploads" ]; then
        chown -R appuser:appuser /app/uploads 2>/dev/null || true
    fi
fi

# Ejecutar el comando original
exec "$@"
