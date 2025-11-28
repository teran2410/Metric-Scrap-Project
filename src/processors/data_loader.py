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
        return None, None, None
    
    # Intentar leer las hojas
    try:
        excel_file = pd.ExcelFile(file_path)
        available_sheets = excel_file.sheet_names
        
        # Cargar hoja de Scrap
        try:
            scrap_df = pd.read_excel(file_path, sheet_name=SCRAP_SHEET_NAME)
        except Exception as e:
            return None, None, None
        
        # Cargar hoja de Ventas
        try:
            ventas_df = pd.read_excel(file_path, sheet_name=VENTAS_SHEET_NAME)
        except Exception as e:
            return None, None, None
        
        # Cargar hoja de Horas
        try:
            horas_df = pd.read_excel(file_path, sheet_name=HORAS_SHEET_NAME)
        except Exception as e:
            return None, None, None
        
        return scrap_df, ventas_df, horas_df
        
    except FileNotFoundError:
        return None, None, None
    except Exception as e:
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
        return False
    
    return True