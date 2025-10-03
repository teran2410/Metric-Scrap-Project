"""
Módulo para el procesamiento de datos de Scrap, Ventas y Horas
"""

import pandas as pd
from config import TARGET_RATES, DATA_FILE_PATH, SCRAP_SHEET_NAME, VENTAS_SHEET_NAME, HORAS_SHEET_NAME


def load_data(file_path=DATA_FILE_PATH):
    """
    Carga las 3 hojas del archivo Excel
    
    Args:
        file_path (str): Ruta del archivo Excel
        
    Returns:
        tuple: (scrap_df, ventas_df, horas_df) o (None, None, None) en caso de error
    """
    try:
        scrap_df = pd.read_excel(file_path, sheet_name=SCRAP_SHEET_NAME)
        ventas_df = pd.read_excel(file_path, sheet_name=VENTAS_SHEET_NAME)
        horas_df = pd.read_excel(file_path, sheet_name=HORAS_SHEET_NAME)
        return scrap_df, ventas_df, horas_df
    except Exception as e:
        return None, None, None