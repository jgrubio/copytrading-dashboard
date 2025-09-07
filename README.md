# 📊 Análisis de Trading - Dashboard Web

Un servicio web completo para analizar operaciones de trading a partir de archivos CSV, con visualizaciones interactivas y análisis detallados.

## 🚀 Características

- **Subida de archivos CSV**: Interfaz drag & drop moderna y fácil de usar
- **Análisis automático**: Procesamiento automático de datos de trading
- **Gráficos interactivos**: Visualizaciones con Plotly.js
- **Métricas detalladas**: Estadísticas por mes, instrumento y razón de cierre
- **Diseño responsive**: Interfaz adaptada a todos los dispositivos
- **Validación de datos**: Verificación automática del formato CSV

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd trading_capital
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

## 🚀 Uso

1. **Ejecutar la aplicación**:
```bash
python app.py
```

2. **Abrir en el navegador**:
```
http://localhost:5000
```

3. **Subir archivo CSV**:
   - Arrastra y suelta tu archivo CSV en el área designada
   - O haz clic en "Seleccionar Archivo"
   - El sistema procesará automáticamente los datos

## 📁 Formato del Archivo CSV

El archivo debe contener las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `ID` | Identificador único de la operación | `W5680773065338676` |
| `Instrumentos` | Símbolo del instrumento | `US100.`, `XAUUSD` |
| `Horario de apertura` | Fecha y hora de apertura | `2025-09-01T12:33:25.017` |
| `Precio de apertura` | Precio de entrada | `23430.77` |
| `Precio de cierre` | Precio de salida | `23434.11` |
| `Utilidad` | Ganancia/pérdida de la operación | `0.70` |
| `Razón` | Motivo del cierre | `Usuario`, `Take Profit` |

### 📥 Descargar Archivo de Ejemplo

La aplicación incluye un archivo de ejemplo que puedes descargar para ver el formato correcto.

## 📊 Análisis Proporcionados

### 📈 Métricas Generales
- **Total de operaciones**: Número total de trades realizados
- **Ganancia/Pérdida total**: Suma de todas las ganancias/pérdidas
- **Ganancia/Pérdida promedio**: Ganancia/pérdida media por operación
- **Operaciones ganadoras**: Número de trades con ganancia positiva
- **Operaciones perdedoras**: Número de trades con pérdida
- **Porcentaje de éxito**: Ratio de operaciones ganadoras

### 📊 Gráficos Interactivos
1. **Análisis Mensual**: Ganancia/pérdida total y número de operaciones por mes
2. **Ganancia/Pérdida por Instrumento**: Top 10 instrumentos más rentables
3. **Distribución de Ganancias/Pérdidas**: Histograma de ganancias/pérdidas
4. **Evolución Temporal**: Curva de ganancia/pérdida acumulada en el tiempo
5. **Operaciones por Razón**: Distribución de motivos de cierre

### 📋 Tablas de Datos
- **Estadísticas por Mes**: Desglose mensual detallado
- **Estadísticas por Instrumento**: Análisis por tipo de activo

## 🏗️ Estructura del Proyecto

```
trading_capital/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── demo/                 # Archivos de ejemplo
│   └── closedPositionsTab.csv
├── templates/            # Plantillas HTML
│   └── index.html       # Página principal
└── uploads/             # Carpeta para archivos subidos (se crea automáticamente)
```

## 🔧 Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Gráficos**: Plotly.js
- **Estilos**: Bootstrap 5
- **Iconos**: Font Awesome
- **Procesamiento de datos**: Pandas

## 🚀 Despliegue en Producción

Para desplegar en producción, considera:

1. **Servidor WSGI**: Usar Gunicorn o uWSGI
2. **Proxy reverso**: Nginx o Apache
3. **Variables de entorno**: Configurar `FLASK_ENV=production`
4. **Seguridad**: Implementar HTTPS y validaciones adicionales

### Ejemplo con Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🐛 Solución de Problemas

### Error: "Missing required columns"
- Verifica que tu archivo CSV tenga todas las columnas requeridas
- Los nombres de las columnas deben coincidir exactamente

### Error: "Error processing file"
- Asegúrate de que el archivo sea un CSV válido
- Verifica que no haya caracteres especiales corruptos

### Gráficos no se muestran
- Verifica que JavaScript esté habilitado en tu navegador
- Revisa la consola del navegador para errores

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes preguntas o problemas:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

## 🔮 Próximas Características

- [ ] Exportación de reportes en PDF
- [ ] Análisis de riesgo (VaR, Sharpe ratio)
- [ ] Comparación de estrategias
- [ ] Alertas y notificaciones
- [ ] API REST para integraciones
- [ ] Base de datos para historial de análisis

---

**¡Disfruta analizando tus operaciones de trading! 📈**

