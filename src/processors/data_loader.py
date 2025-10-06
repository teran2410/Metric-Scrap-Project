"""
data_loader.py - Módulo para el procesamiento de datos de Scrap, Ventas y Horas
"""

import pandas as pd
import os
from config import TARGET_RATES, DATA_FILE_PATH, SCRAP_SHEET_NAME, VENTAS_SHEET_NAME, HORAS_SHEET_NAME


def load_data(file_path=DATA_FILE_PATH):
    """
    Carga las 3 hojas del archivo Excel
    
    Args:
        file_path (str): Ruta del archivo Excel
        
    Returns:
        tuple: (scrap_df, ventas_df, horas_df) o (None, None, None) en caso de error
    """
    # Validar que el archivo existe
    if not os.path.exists(file_path):
        print(f"❌ ERROR: El archivo no existe en la ruta: {file_path}")
        print(f"📁 Ruta actual de trabajo: {os.getcwd()}")
        return None, None, None
    
    print(f"✅ Archivo encontrado: {file_path}")
    
    # Intentar leer las hojas
    try:
        # Primero, ver qué hojas tiene el archivo
        excel_file = pd.ExcelFile(file_path)
        available_sheets = excel_file.sheet_names
        print(f"📊 Hojas disponibles en el Excel: {available_sheets}")
        
        # Cargar hoja de Scrap
        try:
            print(f"⏳ Cargando hoja '{SCRAP_SHEET_NAME}'...")
            scrap_df = pd.read_excel(file_path, sheet_name=SCRAP_SHEET_NAME)
            print(f"✅ Scrap cargado: {len(scrap_df)} filas, {len(scrap_df.columns)} columnas")
            print(f"   Columnas: {list(scrap_df.columns)}")
        except Exception as e:
            print(f"❌ ERROR al cargar hoja de Scrap '{SCRAP_SHEET_NAME}': {e}")
            return None, None, None
        
        # Cargar hoja de Ventas
        try:
            print(f"⏳ Cargando hoja '{VENTAS_SHEET_NAME}'...")
            ventas_df = pd.read_excel(file_path, sheet_name=VENTAS_SHEET_NAME)
            print(f"✅ Ventas cargado: {len(ventas_df)} filas, {len(ventas_df.columns)} columnas")
            print(f"   Columnas: {list(ventas_df.columns)}")
        except Exception as e:
            print(f"❌ ERROR al cargar hoja de Ventas '{VENTAS_SHEET_NAME}': {e}")
            return None, None, None
        
        # Cargar hoja de Horas
        try:
            print(f"⏳ Cargando hoja '{HORAS_SHEET_NAME}'...")
            horas_df = pd.read_excel(file_path, sheet_name=HORAS_SHEET_NAME)
            print(f"✅ Horas cargado: {len(horas_df)} filas, {len(horas_df.columns)} columnas")
            print(f"   Columnas: {list(horas_df.columns)}")
        except Exception as e:
            print(f"❌ ERROR al cargar hoja de Horas '{HORAS_SHEET_NAME}': {e}")
            return None, None, None
        
        # Validar que las hojas no estén vacías
        if scrap_df.empty:
            print(f"⚠️ ADVERTENCIA: La hoja '{SCRAP_SHEET_NAME}' está vacía")
        if ventas_df.empty:
            print(f"⚠️ ADVERTENCIA: La hoja '{VENTAS_SHEET_NAME}' está vacía")
        if horas_df.empty:
            print(f"⚠️ ADVERTENCIA: La hoja '{HORAS_SHEET_NAME}' está vacía")
        
        print("✅ Todas las hojas cargadas correctamente\n")
        return scrap_df, ventas_df, horas_df
        
    except FileNotFoundError:
        print(f"❌ ERROR: Archivo no encontrado: {file_path}")
        return None, None, None
    except Exception as e:
        print(f"❌ ERROR inesperado al cargar el archivo: {type(e).__name__}: {e}")
        return None, None, None


def validate_data_structure(scrap_df, ventas_df, horas_df):
    """
    Valida que los DataFrames tengan las columnas necesarias
    
    Args:
        scrap_df, ventas_df, horas_df: DataFrames a validar
        
    Returns:
        bool: True si todo está correcto, False si hay problemas
    """
    required_scrap_cols = ['Create Date', 'Total Posted', 'Item', 'Description', 'Location', 'Quantity']
    required_ventas_cols = ['Create Date', 'Total Posted']
    required_horas_cols = ['Trans Date', 'Actual Hours']
    
    issues = []
    
    # Validar Scrap
    if scrap_df is not None:
        missing = [col for col in required_scrap_cols if col not in scrap_df.columns]
        if missing:
            issues.append(f"Scrap - Columnas faltantes: {missing}")
    
    # Validar Ventas
    if ventas_df is not None:
        missing = [col for col in required_ventas_cols if col not in ventas_df.columns]
        if missing:
            issues.append(f"Ventas - Columnas faltantes: {missing}")
    
    # Validar Horas
    if horas_df is not None:
        missing = [col for col in required_horas_cols if col not in horas_df.columns]
        if missing:
            issues.append(f"Horas - Columnas faltantes: {missing}")
    
    if issues:
        print("⚠️ PROBLEMAS DE ESTRUCTURA:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    print("✅ Estructura de datos validada correctamente")
    return True