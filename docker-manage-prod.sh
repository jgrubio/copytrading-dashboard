#!/bin/bash

# Script de gestión para producción
# Uso: ./docker-manage-prod.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Script de gestión de Docker para Copytrading Dashboard (Producción)${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar servicios en producción"
    echo "  stop      - Detener servicios"
    echo "  restart   - Reiniciar servicios"
    echo "  logs      - Ver logs de todos los servicios"
    echo "  logs-app  - Ver logs solo de la aplicación"
    echo "  status    - Ver estado de los servicios"
    echo "  build     - Construir imágenes"
    echo "  cleanup   - Ejecutar limpieza de archivos antiguos"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Variables de entorno:"
    echo "  EXTERNAL_PORT - Puerto externo (default: 5000)"
    echo "  UPLOAD_PATH   - Ruta del directorio de uploads (default: ./uploads)"
    echo "  SECRET_KEY    - Clave secreta para la aplicación"
    echo ""
}

# Función para verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker no está instalado${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose no está instalado${NC}"
        exit 1
    fi
}

# Función para crear directorio de uploads si no existe
create_uploads_dir() {
    local upload_path="${UPLOAD_PATH:-./uploads}"
    if [ ! -d "$upload_path" ]; then
        echo -e "${YELLOW}Creando directorio de uploads: $upload_path${NC}"
        mkdir -p "$upload_path"
        chmod 777 "$upload_path"
    fi
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}Estado de los servicios:${NC}"
    docker-compose -f docker-compose-prod.yaml ps
}

# Función para ver logs
show_logs() {
    local service="${1:-}"
    if [ -n "$service" ]; then
        docker-compose -f docker-compose-prod.yaml logs -f "$service"
    else
        docker-compose -f docker-compose-prod.yaml logs -f
    fi
}

# Función principal
main() {
    check_docker
    
    case "${1:-help}" in
        start)
            echo -e "${GREEN}Iniciando servicios en producción...${NC}"
            create_uploads_dir
            docker-compose -f docker-compose-prod.yaml up -d --build
            echo -e "${GREEN}Servicios iniciados. Verifica el estado con: $0 status${NC}"
            ;;
        stop)
            echo -e "${YELLOW}Deteniendo servicios...${NC}"
            docker-compose -f docker-compose-prod.yaml down
            echo -e "${GREEN}Servicios detenidos${NC}"
            ;;
        restart)
            echo -e "${YELLOW}Reiniciando servicios...${NC}"
            docker-compose -f docker-compose-prod.yaml down
            create_uploads_dir
            docker-compose -f docker-compose-prod.yaml up -d --build
            echo -e "${GREEN}Servicios reiniciados${NC}"
            ;;
        logs)
            show_logs
            ;;
        logs-app)
            show_logs "copytrading-dashboard"
            ;;
        status)
            show_status
            ;;
        build)
            echo -e "${BLUE}Construyendo imágenes...${NC}"
            docker-compose -f docker-compose-prod.yaml build --no-cache
            echo -e "${GREEN}Imágenes construidas${NC}"
            ;;
        cleanup)
            echo -e "${BLUE}Ejecutando limpieza de archivos antiguos...${NC}"
            docker-compose -f docker-compose-prod.yaml --profile maintenance run --rm cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Comando desconocido: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
