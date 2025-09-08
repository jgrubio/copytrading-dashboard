# Despliegue con Docker

Esta guía te ayudará a desplegar el Dashboard de Trading usando Docker Compose.

## Requisitos Previos

- Docker Engine 20.10+
- Docker Compose 2.0+
- Al menos 2GB de RAM disponible
- Al menos 1GB de espacio en disco

## Instalación Rápida

### 1. Clonar y Configurar

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd copytrading-dashboard

# Configurar variables de entorno
cp env.docker.example .env
# Editar .env con tus configuraciones
```

### 2. Iniciar Servicios

```bash
# Usar el script de gestión (recomendado)
./docker-manage.sh start

# O usar docker-compose directamente
docker-compose up -d
```

### 3. Verificar Instalación

```bash
# Verificar estado de los servicios
./docker-manage.sh status

# Ver logs
./docker-manage.sh logs
```

La aplicación estará disponible en: `http://localhost:5000` (o el puerto que configures en EXTERNAL_PORT)

## Configuración

### Variables de Entorno

Edita el archivo `.env` con tus configuraciones:

```bash
# ===========================================
# CONFIGURACIÓN OBLIGATORIA - CAMBIAR ESTOS
# ===========================================

# Clave secreta para la aplicación (OBLIGATORIO CAMBIAR)
SECRET_KEY=tu-clave-secreta-super-segura

# Puerto externo donde se expondrá la aplicación
EXTERNAL_PORT=5000

# ===========================================
# CONFIGURACIÓN OPCIONAL - AJUSTAR SEGÚN NECESIDADES
# ===========================================

# Configuración de limpieza
CLEANUP_DAYS=30
```

### Configuración de Proxy Reverso

Como nginx se ha eliminado del docker-compose, necesitarás configurar tu propio proxy reverso (nginx, Apache, etc.) para:

- Terminación SSL/HTTPS
- Balanceo de carga
- Cacheo de archivos estáticos
- Headers de seguridad adicionales

## Gestión de Servicios

### Script de Gestión

Usa el script `docker-manage.sh` para gestionar los servicios:

```bash
# Iniciar servicios
./docker-manage.sh start

# Detener servicios
./docker-manage.sh stop

# Reiniciar servicios
./docker-manage.sh restart

# Ver logs
./docker-manage.sh logs

# Ver estado
./docker-manage.sh status

# Abrir shell en el contenedor
./docker-manage.sh shell

# Ejecutar limpieza de archivos antiguos
./docker-manage.sh cleanup

# Crear backup
./docker-manage.sh backup

# Restaurar backup
./docker-manage.sh restore backup-file.tar.gz
```

### Comandos Docker Compose Directos

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Reconstruir imágenes
docker-compose build --no-cache

# Ejecutar comando en contenedor
docker-compose exec copytrading-dashboard bash
```

## Estructura de Servicios

### Servicios Incluidos

1. **copytrading-dashboard**: Aplicación Flask principal
2. **cleanup**: Servicio de limpieza (opcional)

### Volúmenes Persistentes

- `uploads_data`: Archivos CSV subidos por usuarios
- `logs_data`: Logs de la aplicación

### Red

Los servicios se comunican a través de la red `copytrading-network`.

## Monitoreo y Logs

### Ver Logs

```bash
# Todos los servicios
./docker-manage.sh logs

# Solo aplicación
./docker-manage.sh logs-app

```

### Health Checks

La aplicación incluye health checks automáticos:

```bash
# Verificar salud de la aplicación
curl http://localhost:5000/

# Verificar salud del contenedor
docker-compose ps
```

## Mantenimiento

### Limpieza de Archivos Antiguos

```bash
# Ejecutar limpieza manual
./docker-manage.sh cleanup

# O ejecutar directamente
docker-compose --profile maintenance run --rm cleanup
```

### Backups

```bash
# Crear backup
./docker-manage.sh backup

# Restaurar backup
./docker-manage.sh restore backup-20240101-120000.tar.gz
```

### Actualizaciones

```bash
# Actualizar servicios
./docker-manage.sh update

# O manualmente
docker-compose pull
docker-compose build
docker-compose up -d
```

## Solución de Problemas

### Problemas Comunes

1. **Puerto 80 ocupado**:
   ```bash
   # Cambiar puerto en docker-compose.yaml
   ports:
     - "8080:80"
   ```

2. **Permisos de archivos**:
   ```bash
   # Verificar permisos
   ls -la uploads/
   
   # Corregir permisos
   chmod 755 uploads/
   ```

3. **Memoria insuficiente**:
   ```bash
   # Verificar uso de memoria
   docker stats
   
   # Ajustar límites en docker-compose.yaml
   ```

### Logs de Depuración

```bash
# Ver logs detallados
docker-compose logs --tail=100 -f

# Ver logs de un servicio específico
docker-compose logs copytrading-dashboard
```

### Reiniciar Servicios

```bash
# Reiniciar solo la aplicación
docker-compose restart copytrading-dashboard

```

## Producción

### Configuración para Producción

1. **Cambiar SECRET_KEY** en `.env`
2. **Configurar HTTPS** con certificados válidos
3. **Configurar dominio** en nginx
4. **Configurar backup automático**
5. **Configurar monitoreo**

### Configuración de Dominio

Configura tu proxy reverso (nginx, Apache, etc.) para que apunte a `localhost:5000` (o el puerto que configures en EXTERNAL_PORT).

### Backup Automático

Crea un cron job para backups automáticos:

```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario
0 2 * * * cd /ruta/al/proyecto && ./docker-manage.sh backup
```

## Seguridad

### Recomendaciones

1. **Cambiar SECRET_KEY** por una clave segura
2. **Usar HTTPS** en producción
3. **Configurar firewall** para limitar acceso
4. **Mantener actualizado** Docker y las imágenes
5. **Monitorear logs** regularmente

### Headers de Seguridad

La aplicación Flask incluye headers de seguridad automáticos:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy

## Soporte

Para problemas o preguntas:

1. Revisar logs: `./docker-manage.sh logs`
2. Verificar estado: `./docker-manage.sh status`
3. Consultar documentación
4. Crear issue en el repositorio
