# 🚀 Guía de Despliegue en Producción

Esta guía te ayudará a desplegar el Copytrading Dashboard en un entorno de producción.

## 📋 Prerrequisitos

- Docker y Docker Compose instalados
- Acceso a un servidor Linux
- Puerto 5000 (o el que configures) disponible

## 🔧 Configuración Inicial

### 1. Preparar el entorno

```bash
# Clonar o copiar el proyecto
cd /ruta/a/tu/proyecto

# Crear directorio de uploads
mkdir -p uploads
chmod 777 uploads
```

### 2. Configurar variables de entorno

Crea un archivo `.env` con las siguientes variables:

```bash
# Clave secreta (¡CÁMBIALA!)
SECRET_KEY=tu-clave-secreta-super-segura-aqui

# Puerto externo
EXTERNAL_PORT=5000

# Ruta del directorio de uploads
UPLOAD_PATH=./uploads

# Configuración de limpieza
CLEANUP_DAYS=30

# Configuración de logs
LOG_LEVEL=info
```

## 🚀 Despliegue

### Opción 1: Usando el script de gestión (Recomendado)

```bash
# Hacer ejecutable el script
chmod +x docker-manage-prod.sh

# Iniciar servicios
./docker-manage-prod.sh start

# Ver estado
./docker-manage-prod.sh status

# Ver logs
./docker-manage-prod.sh logs-app
```

### Opción 2: Usando Docker Compose directamente

```bash
# Iniciar servicios
docker-compose -f docker-compose-prod.yaml up -d --build

# Ver logs
docker-compose -f docker-compose-prod.yaml logs -f

# Detener servicios
docker-compose -f docker-compose-prod.yaml down
```

## 📊 Comandos de Gestión

```bash
# Iniciar servicios
./docker-manage-prod.sh start

# Detener servicios
./docker-manage-prod.sh stop

# Reiniciar servicios
./docker-manage-prod.sh restart

# Ver logs de la aplicación
./docker-manage-prod.sh logs-app

# Ver logs de todos los servicios
./docker-manage-prod.sh logs

# Ver estado de los servicios
./docker-manage-prod.sh status

# Construir imágenes
./docker-manage-prod.sh build

# Ejecutar limpieza de archivos antiguos
./docker-manage-prod.sh cleanup
```

## 🔍 Verificación

Una vez desplegado, verifica que todo funciona:

```bash
# Verificar que el contenedor está corriendo
docker ps

# Verificar logs
./docker-manage-prod.sh logs-app

# Probar la aplicación
curl http://localhost:5000/
```

## 🛠️ Solución de Problemas

### Error de permisos en uploads

Si ves el error `chmod: changing permissions of '/app/uploads': Operation not permitted`:

1. **Solución 1**: Usar el docker-compose de producción
   ```bash
   ./docker-manage-prod.sh stop
   ./docker-manage-prod.sh start
   ```

2. **Solución 2**: Verificar permisos del directorio host
   ```bash
   chmod 777 uploads/
   chown -R 1000:1000 uploads/
   ```

### Error de conexión

Si no puedes acceder a la aplicación:

1. Verificar que el puerto está abierto
2. Verificar logs: `./docker-manage-prod.sh logs-app`
3. Verificar estado: `./docker-manage-prod.sh status`

### Problemas de memoria

Si el contenedor se reinicia constantemente:

1. Verificar logs para errores de memoria
2. Ajustar límites en docker-compose-prod.yaml
3. Verificar recursos del servidor

## 🔒 Seguridad

### Configuración de Nginx (Recomendado)

Si usas Nginx como proxy reverso:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Variables de entorno sensibles

- **NUNCA** uses la SECRET_KEY por defecto en producción
- Cambia todas las contraseñas y claves
- Usa HTTPS en producción

## 📈 Monitoreo

### Health Checks

El contenedor incluye health checks automáticos:

```bash
# Verificar salud del contenedor
docker inspect copytrading-dashboard | grep -A 10 Health
```

### Logs

Los logs se guardan en el volumen `logs_data`:

```bash
# Ver logs en tiempo real
./docker-manage-prod.sh logs-app

# Ver logs históricos
docker-compose -f docker-compose-prod.yaml logs --tail=100
```

## 🔄 Mantenimiento

### Limpieza automática

El servicio incluye un sistema de limpieza automática:

```bash
# Ejecutar limpieza manual
./docker-manage-prod.sh cleanup

# Configurar limpieza automática con cron
# Agregar a crontab:
# 0 2 * * * cd /ruta/al/proyecto && ./docker-manage-prod.sh cleanup
```

### Actualizaciones

Para actualizar la aplicación:

```bash
# Detener servicios
./docker-manage-prod.sh stop

# Actualizar código
git pull  # o copiar nuevos archivos

# Reconstruir y reiniciar
./docker-manage-prod.sh build
./docker-manage-prod.sh start
```

## 📞 Soporte

Si encuentras problemas:

1. Verificar logs: `./docker-manage-prod.sh logs-app`
2. Verificar estado: `./docker-manage-prod.sh status`
3. Verificar permisos del directorio uploads
4. Verificar que el puerto está disponible

## 🎯 URLs de Acceso

- **Aplicación**: `http://tu-servidor:5000`
- **Health Check**: `http://tu-servidor:5000/` (debe devolver HTML)
- **API de archivos**: `http://tu-servidor:5000/files`
- **API de PDF**: `http://tu-servidor:5000/generate_pdf` (POST)

## 📄 Funcionalidad de PDF

La aplicación incluye funcionalidad para generar reportes en PDF que incluyen:

- **Resumen de métricas**: Total de operaciones, ganancia/pérdida, porcentaje de éxito
- **Gráficos**: Ganancia/pérdida por instrumento y evolución temporal
- **Tablas detalladas**: Estadísticas por mes e instrumento
- **Diseño profesional**: Formato A4 con colores corporativos

### Dependencias adicionales para PDF

Las siguientes dependencias se instalan automáticamente en producción:

- `reportlab>=4.0.0`: Generación de PDFs
- `Pillow>=10.0.0`: Procesamiento de imágenes
- `kaleido>=0.2.1`: Conversión de gráficos Plotly a imágenes

### Uso de la funcionalidad PDF

1. Sube un archivo CSV de trading
2. Ve el análisis en la web
3. Haz clic en "Descargar Análisis en PDF"
4. El PDF se descarga automáticamente con toda la información
