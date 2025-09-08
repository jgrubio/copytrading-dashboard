# Guía de Despliegue en Producción

## Configuración del Servidor

### 1. Instalación de Dependencias

```bash
# Instalar dependencias de producción
pip install -r requirements.production.txt
```

### 2. Configuración de Variables de Entorno

Copia el archivo de ejemplo y configura las variables:

```bash
cp env.production.example .env
```

Edita el archivo `.env` con tus valores:

```bash
# Configuración de Flask
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=tu-clave-secreta-super-segura-aqui

# Configuración del servidor
HOST=127.0.0.1
PORT=5000

# Configuración de HTTPS (si usas SSL)
HTTPS=true

# Configuración de archivos
UPLOAD_FOLDER=/var/www/copytrading-dashboard/uploads

# Configuración de logging
LOG_LEVEL=INFO
```

### 3. Crear Directorios Necesarios

```bash
# Crear directorio de uploads
sudo mkdir -p /var/www/copytrading-dashboard/uploads
sudo chown www-data:www-data /var/www/copytrading-dashboard/uploads
sudo chmod 755 /var/www/copytrading-dashboard/uploads
```

### 4. Iniciar la Aplicación

#### Opción A: Con el script de inicio
```bash
./start_production.sh
```

#### Opción B: Con Gunicorn directamente
```bash
gunicorn --config gunicorn.conf.py wsgi:application
```

#### Opción C: Con systemd (recomendado)

Crear archivo `/etc/systemd/system/copytrading-dashboard.service`:

```ini
[Unit]
Description=Copytrading Dashboard
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/copytrading-dashboard
Environment=PATH=/var/www/copytrading-dashboard/venv/bin
ExecStart=/var/www/copytrading-dashboard/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable copytrading-dashboard
sudo systemctl start copytrading-dashboard
```

## Configuración de Nginx

### Configuración básica para nginx:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    # Redirección a HTTPS (opcional)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    # Configuración SSL
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Configuración de seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Archivos estáticos (si los tienes)
    location /static/ {
        alias /var/www/copytrading-dashboard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy a la aplicación Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Configuración de uploads
    location /uploads/ {
        alias /var/www/copytrading-dashboard/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # Límites de tamaño de archivo
    client_max_body_size 16M;
}
```

## Monitoreo y Logs

### Ver logs de la aplicación:
```bash
# Si usas systemd
sudo journalctl -u copytrading-dashboard -f

# Si usas Gunicorn directamente
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log
```

### Verificar estado del servicio:
```bash
sudo systemctl status copytrading-dashboard
```

## Mantenimiento

### Actualizar la aplicación:
```bash
cd /var/www/copytrading-dashboard
git pull origin main
sudo systemctl restart copytrading-dashboard
```

### Limpiar archivos antiguos:
```bash
# Eliminar archivos CSV más antiguos de 30 días
find /var/www/copytrading-dashboard/uploads -name "*.csv" -mtime +30 -delete
```

## Seguridad

- Cambia la `SECRET_KEY` por una clave segura y única
- Usa HTTPS en producción
- Configura un firewall adecuado
- Mantén el sistema y dependencias actualizadas
- Considera usar un proxy reverso como Cloudflare
- Implementa rate limiting si es necesario
