#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de la aplicación de análisis de trading
"""

import pandas as pd
import os
import sys

def test_csv_reading():
    """Prueba la lectura del archivo CSV de ejemplo"""
    print("🔍 Probando lectura del archivo CSV...")
    
    try:
        csv_path = 'demo/closedPositionsTab.csv'
        if not os.path.exists(csv_path):
            print(f"❌ Error: No se encontró el archivo {csv_path}")
            return False
        
        df = pd.read_csv(csv_path)
        print(f"✅ Archivo CSV leído correctamente")
        print(f"   - Filas: {len(df)}")
        print(f"   - Columnas: {len(df.columns)}")
        print(f"   - Columnas: {list(df.columns)}")
        
        # Verificar columnas requeridas
        required_columns = ['ID', 'Instrumentos', 'Horario de apertura', 'Precio de apertura', 
                           'Precio de cierre', 'Utilidad', 'Razón']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Error: Faltan columnas requeridas: {missing_columns}")
            return False
        
        print("✅ Todas las columnas requeridas están presentes")
        
        # Verificar tipos de datos
        print("\n📊 Información de tipos de datos:")
        print(df.dtypes)
        
        # Verificar datos de ejemplo
        print("\n📋 Primeras 3 filas:")
        print(df.head(3))
        
        return True
        
    except Exception as e:
        print(f"❌ Error al leer el CSV: {str(e)}")
        return False

def test_data_processing():
    """Prueba el procesamiento de datos"""
    print("\n🔧 Probando procesamiento de datos...")
    
    try:
        csv_path = 'demo/closedPositionsTab.csv'
        df = pd.read_csv(csv_path)
        
        # Convertir fechas con manejo de errores
        df['Horario de apertura'] = pd.to_datetime(df['Horario de apertura'], errors='coerce', format='mixed')
        df['Hora de cierre'] = pd.to_datetime(df['Hora de cierre'], errors='coerce', format='mixed')
        
        # Verificar que las fechas se convirtieron correctamente
        valid_dates = df['Horario de apertura'].notna().sum()
        total_rows = len(df)
        print(f"✅ Conversión de fechas exitosa")
        print(f"   - Fechas válidas: {valid_dates}/{total_rows}")
        
        # Filtrar solo filas con fechas válidas
        df_valid = df.dropna(subset=['Horario de apertura', 'Hora de cierre'])
        print(f"   - Filas con fechas válidas: {len(df_valid)}")
        
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
        
        print("✅ Cálculo de estadísticas mensuales exitoso")
        print(f"   - Meses únicos: {len(monthly_stats)}")
        
        # Calcular métricas generales
        total_operations = len(df_valid)
        total_profit = df_valid['Utilidad'].sum()
        avg_profit = df_valid['Utilidad'].mean()
        winning_trades = len(df_valid[df_valid['Utilidad'] > 0])
        losing_trades = len(df_valid[df_valid['Utilidad'] < 0])
        win_rate = (winning_trades / total_operations) * 100
        
        print("✅ Cálculo de métricas generales exitoso")
        print(f"   - Total operaciones: {total_operations}")
        print(f"   - Ganancia/Pérdida total: ${total_profit:.2f}")
        print(f"   - Ganancia/Pérdida promedio: ${avg_profit:.2f}")
        print(f"   - Operaciones ganadoras: {winning_trades}")
        print(f"   - Operaciones perdedoras: {losing_trades}")
        print(f"   - Porcentaje de éxito: {win_rate:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el procesamiento de datos: {str(e)}")
        return False

def test_dependencies():
    """Prueba que todas las dependencias estén disponibles"""
    print("📦 Probando dependencias...")
    
    required_packages = [
        'flask',
        'pandas', 
        'plotly',
        'dash',
        'dash_bootstrap_components',
        'dateutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dateutil':
                import dateutil
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO DISPONIBLE")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {missing_packages}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están disponibles")
    return True

def test_file_structure():
    """Prueba la estructura de archivos del proyecto"""
    print("\n📁 Probando estructura de archivos...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'demo/closedPositionsTab.csv',
        'templates/index.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Todos los archivos requeridos están presentes")
    return True

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de la aplicación de análisis de trading...\n")
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Dependencias", test_dependencies),
        ("Lectura CSV", test_csv_reading),
        ("Procesamiento de datos", test_data_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {str(e)}")
            results.append((test_name, False))
        
        print()
    
    # Resumen de resultados
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! La aplicación está lista para usar.")
        print("\nPara ejecutar la aplicación:")
        print("1. python app.py")
        print("2. Abre http://localhost:5000 en tu navegador")
        return True
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
