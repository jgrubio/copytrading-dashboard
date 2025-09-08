#!/usr/bin/env python3
"""
WSGI entry point para producción
"""
import os
import sys

# Añadir el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Importar la aplicación
from app import app

# Configurar variables de entorno si no están definidas
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'production-secret-key-change-me'

if not os.environ.get('UPLOAD_FOLDER'):
    os.environ['UPLOAD_FOLDER'] = os.path.join(project_dir, 'uploads')

# Aplicación WSGI
application = app

if __name__ == "__main__":
    # Para testing local
    app.run(host='0.0.0.0', port=5000)
