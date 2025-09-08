from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.io as pio
import tempfile

def create_app():
    app = Flask(__name__)
    
    # Configuración de producción
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración para nginx
    app.config['PREFERRED_URL_SCHEME'] = 'https' if os.environ.get('HTTPS', 'false').lower() == 'true' else 'http'
    
    # Configuraciones de seguridad
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('HTTPS', 'false').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configuración de headers de seguridad
    @app.after_request
    def set_security_headers(response):
        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        # Prevenir MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Habilitar XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Política de referrer
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Solo agregar HSTS si usamos HTTPS
        if os.environ.get('HTTPS', 'false').lower() == 'true':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    return app

app = create_app()

# Configurar carpeta de uploads
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    # Validación adicional de seguridad
    if not file.filename or '..' in file.filename or '/' in file.filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    try:
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Guardar el archivo físicamente
        file.save(filepath)
        
        # Leer el archivo CSV desde el archivo guardado
        df = pd.read_csv(filepath)
        
        # Validar que tenga las columnas necesarias
        required_columns = ['ID', 'Instrumentos', 'Horario de apertura', 'Precio de apertura', 
                           'Precio de cierre', 'Utilidad', 'Razón']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {missing_columns}'}), 400
        
        # Procesar los datos
        analysis_data = process_trading_data(df)
        
        return jsonify(analysis_data)
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

def process_trading_data(df):
    """Procesa los datos de trading y genera análisis"""
    
    # Convertir fechas con manejo de errores
    df['Horario de apertura'] = pd.to_datetime(df['Horario de apertura'], errors='coerce', format='mixed')
    df['Hora de cierre'] = pd.to_datetime(df['Hora de cierre'], errors='coerce', format='mixed')
    
    # Filtrar solo filas con fechas válidas
    df_valid = df.dropna(subset=['Horario de apertura', 'Hora de cierre'])
    
    
    # Extraer mes y año
    df_valid['Mes'] = df_valid['Horario de apertura'].dt.to_period('M')
    df_valid['Año'] = df_valid['Horario de apertura'].dt.year
    
    # Calcular métricas por mes
    monthly_stats = df_valid.groupby('Mes').agg({
        'Utilidad': ['sum', 'count', 'mean'],
        'ID': 'count'
    }).round(2)
    
    monthly_stats.columns = ['Ganancia/Pérdida Total', 'Número Operaciones', 'Ganancia/Pérdida Promedio', 'Total Operaciones']
    monthly_stats = monthly_stats.reset_index()
    monthly_stats['Mes'] = monthly_stats['Mes'].astype(str)
    
    # Calcular métricas por instrumento
    instrument_stats = df_valid.groupby('Instrumentos').agg({
        'Utilidad': ['sum', 'count', 'mean']
    }).round(2)
    
    instrument_stats.columns = ['Ganancia/Pérdida Total', 'Número Operaciones', 'Ganancia/Pérdida Promedio']
    instrument_stats = instrument_stats.reset_index()
    
    # Calcular totales para la fila de sumatorio
    instrument_totals = {
        'Instrumentos': 'TOTAL',
        'Ganancia/Pérdida Total': instrument_stats['Ganancia/Pérdida Total'].sum(),
        'Número Operaciones': instrument_stats['Número Operaciones'].sum(),
        'Ganancia/Pérdida Promedio': instrument_stats['Ganancia/Pérdida Total'].sum() / instrument_stats['Número Operaciones'].sum() if instrument_stats['Número Operaciones'].sum() > 0 else 0
    }
    
    # Agregar la fila de totales al final
    instrument_stats = pd.concat([instrument_stats, pd.DataFrame([instrument_totals])], ignore_index=True)
    
    
    # Calcular métricas por razón de cierre
    reason_stats = df_valid.groupby('Razón').agg({
        'Utilidad': ['sum', 'count', 'mean']
    }).round(2)
    
    reason_stats.columns = ['Ganancia/Pérdida Total', 'Número Operaciones', 'Ganancia/Pérdida Promedio']
    reason_stats = reason_stats.reset_index()
    
    # Métricas generales
    total_operations = len(df_valid)
    total_profit = df_valid['Utilidad'].sum()
    winning_trades = len(df_valid[df_valid['Utilidad'] > 0])
    losing_trades = len(df_valid[df_valid['Utilidad'] < 0])
    win_rate = (winning_trades / total_operations) * 100 if total_operations > 0 else 0
    
    # Calcular costos adicionales
    total_swap = df_valid['Swap'].sum()
    
    # Generar gráficos
    charts = generate_charts(df_valid, monthly_stats, instrument_stats, reason_stats)
    
    return {
        'summary': {
            'total_operations': total_operations,
            'total_profit': round(total_profit, 2),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'total_swap': round(total_swap, 2)
        },
        'monthly_stats': monthly_stats.to_dict('records'),
        'instrument_stats': instrument_stats.to_dict('records'),
        'reason_stats': reason_stats.to_dict('records'),
        'charts': charts
    }

def generate_charts(df, monthly_stats, instrument_stats, reason_stats):
    """Genera los gráficos de análisis"""
    
    # 1. Gráfico de ganancia/pérdida por instrumento
    # Ordenar por ganancia/pérdida total descendente y excluir la fila TOTAL
    instrument_stats_for_chart = instrument_stats[instrument_stats['Instrumentos'] != 'TOTAL'].copy()
    instrument_stats_sorted = instrument_stats_for_chart.sort_values('Ganancia/Pérdida Total', ascending=False)
    
    fig_instrument = px.bar(
        instrument_stats_sorted.head(15),  # Top 15 instrumentos
        x='Instrumentos',
        y='Ganancia/Pérdida Total',
        title='Ganancia/Pérdida Total por Instrumento (Top 15)',
        color='Ganancia/Pérdida Total',
        color_continuous_scale='RdYlGn',
        height=500
    )
    
    fig_instrument.update_layout(
        xaxis_title='Instrumento',
        yaxis_title='Ganancia/Pérdida Total ($)',
        showlegend=False,
        xaxis={'tickangle': 45}
    )
    
    # 2. Gráfico de evolución temporal
    df_sorted = df.sort_values('Horario de apertura').copy()
    df_sorted['Ganancia/Pérdida Acumulada'] = df_sorted['Utilidad'].cumsum()
    
    fig_evolution = px.line(
        df_sorted,
        x='Horario de apertura',
        y='Ganancia/Pérdida Acumulada',
        title='Evolución de Ganancia/Pérdida Acumulada en el Tiempo',
        height=500
    )
    
    fig_evolution.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Ganancia/Pérdida Acumulada ($)',
        showlegend=False,
        hovermode='x unified'
    )
    
    # Agregar línea horizontal en y=0 para referencia
    fig_evolution.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    # Convertir gráficos a JSON con datos explícitos
    charts = {
        'instrument': {
            'data': [{
                'x': instrument_stats_sorted.head(15)['Instrumentos'].tolist(),
                'y': instrument_stats_sorted.head(15)['Ganancia/Pérdida Total'].tolist(),
                'type': 'bar',
                'marker': {
                    'color': instrument_stats_sorted.head(15)['Ganancia/Pérdida Total'].tolist(),
                    'colorscale': 'RdYlGn'
                }
            }],
            'layout': {
                'title': 'Ganancia/Pérdida Total por Instrumento (Top 15)',
                'xaxis': {'title': 'Instrumento', 'tickangle': 45},
                'yaxis': {'title': 'Ganancia/Pérdida Total ($)'},
                'height': 500
            }
        },
        'evolution': {
            'data': [{
                'x': df_sorted['Horario de apertura'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'y': df_sorted['Ganancia/Pérdida Acumulada'].tolist(),
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Ganancia/Pérdida Acumulada'
            }],
            'layout': {
                'title': 'Evolución de Ganancia/Pérdida Acumulada en el Tiempo',
                'xaxis': {'title': 'Fecha'},
                'yaxis': {'title': 'Ganancia/Pérdida Acumulada ($)'},
                'height': 500,
                'shapes': [{
                    'type': 'line',
                    'x0': df_sorted['Horario de apertura'].min(),
                    'x1': df_sorted['Horario de apertura'].max(),
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'red', 'dash': 'dash'}
                }]
            }
        }
    }
    
    return charts

@app.route('/files')
def list_files():
    """Lista todos los archivos subidos"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.csv'):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file_stats = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': file_stats.st_size,
                    'uploaded': datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Ordenar por fecha de subida (más reciente primero)
        files.sort(key=lambda x: x['uploaded'], reverse=True)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': f'Error listing files: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Descarga un archivo específico"""
    try:
        # Validar que el archivo existe y es un CSV
        if not filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Elimina un archivo específico"""
    try:
        # Validar que el archivo existe y es un CSV
        if not filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(filepath)
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'error': f'Error deleting file: {str(e)}'}), 500

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """Genera un PDF con el análisis de trading"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Crear archivo PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Generar el PDF
        create_trading_pdf(data, pdf_path)
        
        # Enviar el archivo PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'trading_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

def create_trading_pdf(data, output_path):
    """Crea un PDF con el análisis de trading"""
    
    # Configurar el documento
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#667eea')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#764ba2')
    )
    
    # Título principal
    story.append(Paragraph("Análisis de Trading Galáctico", title_style))
    story.append(Spacer(1, 20))
    
    # Fecha de generación
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        textColor=colors.grey
    )
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style))
    story.append(Spacer(1, 30))
    
    # Resumen de métricas
    story.append(Paragraph("Resumen de Métricas", heading_style))
    
    summary_data = data.get('summary', {})
    summary_table_data = [
        ['Métrica', 'Valor'],
        ['Total de Operaciones', str(summary_data.get('total_operations', 0))],
        ['Ganancia/Pérdida Total', f"${summary_data.get('total_profit', 0):,.2f}"],
        ['Coste Total Swap', f"${summary_data.get('total_swap', 0):,.2f}"],
        ['Operaciones Ganadoras', str(summary_data.get('winning_trades', 0))],
        ['Operaciones Perdedoras', str(summary_data.get('losing_trades', 0))],
        ['Porcentaje de Éxito', f"{summary_data.get('win_rate', 0):.2f}%"]
    ]
    
    summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Gráficos
    charts = data.get('charts', {})
    
    # Gráfico de instrumentos
    if 'instrument' in charts:
        story.append(Paragraph("Ganancia/Pérdida por Instrumento", heading_style))
        instrument_chart_path = create_chart_image(charts['instrument'], 'instrument')
        if instrument_chart_path:
            story.append(Image(instrument_chart_path, width=6*inch, height=4*inch))
            story.append(Spacer(1, 20))
    
    # Gráfico de evolución temporal
    if 'evolution' in charts:
        story.append(Paragraph("Evolución Temporal de Ganancia/Pérdida", heading_style))
        evolution_chart_path = create_chart_image(charts['evolution'], 'evolution')
        if evolution_chart_path:
            story.append(Image(evolution_chart_path, width=6*inch, height=4*inch))
            story.append(Spacer(1, 20))
    
    # Tabla de estadísticas por mes
    monthly_stats = data.get('monthly_stats', [])
    if monthly_stats:
        story.append(Paragraph("Estadísticas por Mes", heading_style))
        
        monthly_table_data = [['Mes', 'Ganancia/Pérdida Total', 'Operaciones', 'Promedio']]
        for row in monthly_stats:
            monthly_table_data.append([
                str(row.get('Mes', '')),
                f"${row.get('Ganancia/Pérdida Total', 0):,.2f}",
                str(row.get('Número Operaciones', 0)),
                f"${row.get('Ganancia/Pérdida Promedio', 0):,.2f}"
            ])
        
        monthly_table = Table(monthly_table_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch])
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        story.append(monthly_table)
        story.append(Spacer(1, 20))
    
    # Tabla de estadísticas por instrumento
    instrument_stats = data.get('instrument_stats', [])
    if instrument_stats:
        story.append(Paragraph("Estadísticas por Instrumento", heading_style))
        
        instrument_table_data = [['Instrumento', 'Ganancia/Pérdida Total', 'Operaciones', 'Promedio']]
        for row in instrument_stats:
            instrument_table_data.append([
                str(row.get('Instrumentos', '')),
                f"${row.get('Ganancia/Pérdida Total', 0):,.2f}",
                str(row.get('Número Operaciones', 0)),
                f"${row.get('Ganancia/Pérdida Promedio', 0):,.2f}"
            ])
        
        instrument_table = Table(instrument_table_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
        instrument_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            # Destacar la fila TOTAL
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffeb3b')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        
        story.append(instrument_table)
    
    # Construir el PDF
    doc.build(story)

def create_chart_image(chart_data, chart_type):
    """Crea una imagen del gráfico para incluir en el PDF"""
    try:
        # Crear figura de Plotly
        if chart_type == 'instrument':
            fig = go.Figure(data=chart_data['data'], layout=chart_data['layout'])
        elif chart_type == 'evolution':
            fig = go.Figure(data=chart_data['data'], layout=chart_data['layout'])
        else:
            return None
        
        # Configurar el layout para mejor visualización en PDF
        fig.update_layout(
            width=800,
            height=600,
            margin=dict(l=50, r=50, t=50, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        # Crear archivo temporal para la imagen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image_path = tmp_file.name
        
        # Convertir a imagen
        pio.write_image(fig, image_path, format='png', width=800, height=600, scale=2)
        
        return image_path
        
    except Exception as e:
        print(f"Error creating chart image: {e}")
        return None


if __name__ == '__main__':
    # Configuración para desarrollo
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(debug=debug_mode, host=host, port=port)
