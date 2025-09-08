#!/bin/bash

# Script de gestión para Docker Compose
# Uso: ./docker-manage.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Script de gestión para Copytrading Dashboard${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start       - Iniciar todos los servicios"
    echo "  stop        - Detener todos los servicios"
    echo "  restart     - Reiniciar todos los servicios"
    echo "  build       - Construir las imágenes"
    echo "  logs        - Mostrar logs de todos los servicios"
    echo "  logs-app    - Mostrar logs solo de la aplicación"
    echo "  status      - Mostrar estado de los servicios"
    echo "  shell       - Abrir shell en el contenedor de la aplicación"
    echo "  cleanup     - Ejecutar limpieza de archivos antiguos"
    echo "  backup      - Crear backup de los archivos subidos"
    echo "  restore     - Restaurar backup"
    echo "  update      - Actualizar y reiniciar servicios"
    echo "  help        - Mostrar esta ayuda"
    echo ""
}

# Función para verificar si Docker está instalado
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

# Función para verificar archivo .env
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Advertencia: Archivo .env no encontrado${NC}"
        echo "Copiando archivo de ejemplo..."
        cp env.docker.example .env
        echo -e "${YELLOW}Por favor, edita el archivo .env con tus configuraciones${NC}"
    fi
}

# Función para crear directorios necesarios
create_directories() {
    mkdir -p uploads
    mkdir -p logs
    echo -e "${GREEN}Directorios creados${NC}"
}

# Comandos principales
case "${1:-help}" in
    start)
        echo -e "${BLUE}Iniciando servicios...${NC}"
        check_docker
        check_env
        create_directories
        docker-compose up -d
        echo -e "${GREEN}Servicios iniciados${NC}"
        ;;
    
    stop)
        echo -e "${BLUE}Deteniendo servicios...${NC}"
        check_docker
        docker-compose down
        echo -e "${GREEN}Servicios detenidos${NC}"
        ;;
    
    restart)
        echo -e "${BLUE}Reiniciando servicios...${NC}"
        check_docker
        docker-compose restart
        echo -e "${GREEN}Servicios reiniciados${NC}"
        ;;
    
    build)
        echo -e "${BLUE}Construyendo imágenes...${NC}"
        check_docker
        docker-compose build --no-cache
        echo -e "${GREEN}Imágenes construidas${NC}"
        ;;
    
    logs)
        check_docker
        docker-compose logs -f
        ;;
    
    logs-app)
        check_docker
        docker-compose logs -f copytrading-dashboard
        ;;
    
    
    status)
        check_docker
        docker-compose ps
        ;;
    
    shell)
        check_docker
        docker-compose exec copytrading-dashboard /bin/bash
        ;;
    
    cleanup)
        echo -e "${BLUE}Ejecutando limpieza de archivos antiguos...${NC}"
        check_docker
        docker-compose --profile maintenance run --rm cleanup
        echo -e "${GREEN}Limpieza completada${NC}"
        ;;
    
    backup)
        echo -e "${BLUE}Creando backup de archivos...${NC}"
        BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        tar -czf "$BACKUP_FILE" uploads/
        echo -e "${GREEN}Backup creado: $BACKUP_FILE${NC}"
        ;;
    
    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Especifica el archivo de backup${NC}"
            echo "Uso: $0 restore backup-file.tar.gz"
            exit 1
        fi
        echo -e "${BLUE}Restaurando backup: $2${NC}"
        tar -xzf "$2"
        echo -e "${GREEN}Backup restaurado${NC}"
        ;;
    
    update)
        echo -e "${BLUE}Actualizando servicios...${NC}"
        check_docker
        docker-compose pull
        docker-compose build
        docker-compose up -d
        echo -e "${GREEN}Servicios actualizados${NC}"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo -e "${RED}Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac
