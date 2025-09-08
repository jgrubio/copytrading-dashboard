# Configuración de Gunicorn para producción

import os
import multiprocessing

# Configuración del servidor
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de procesos
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Configuración de archivos estáticos (nginx se encargará de esto)
# raw_env = [
#     'UPLOAD_FOLDER=/var/www/copytrading-dashboard/uploads',
#     'SECRET_KEY=your-secret-key-here'
# ]
