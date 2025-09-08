#!/bin/bash

# Script de inicialización para producción
set -e

echo "Iniciando contenedor de copytrading-dashboard..."

# Crear directorio de uploads si no existe
mkdir -p /app/uploads

# Asegurar que el directorio de uploads tenga permisos de escritura
# Usar permisos más permisivos para evitar problemas en producción
chmod 777 /app/uploads 2>/dev/null || {
    echo "Advertencia: No se pudieron cambiar los permisos del directorio uploads"
    echo "Verificando permisos actuales..."
    ls -la /app/uploads 2>/dev/null || echo "Directorio uploads no accesible"
}

# Verificar que el directorio es escribible
if [ -w "/app/uploads" ]; then
    echo "Directorio uploads es escribible"
else
    echo "Advertencia: Directorio uploads no es escribible"
fi

echo "Iniciando aplicación..."

# Ejecutar el comando original
exec "$@"
