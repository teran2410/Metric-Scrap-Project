"""
custom_processor.py - Procesamiento de datos por rango de fechas personalizado
"""

import pandas as pd
from config import TARGET_RATES


def process_custom_data(scrap_df, ventas_df, horas_df, start_date, end_date):
    """
    Procesa los datos entre dos fechas especificadas y calcula el rate de scrap
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        ventas_df (DataFrame): DataFrame con datos de ventas
        horas_df (DataFrame): DataFrame con datos de horas
        start_date (datetime): Fecha inicial
        end_date (datetime): Fecha final
        
    Returns:
        DataFrame: DataFrame con el reporte del periodo o None si no hay datos
    """
    # Validar que los DataFrames no estén vacíos
    if scrap_df is None:
        return None
    if scrap_df.empty:
        return None
    if ventas_df is None:
        return None
    if ventas_df.empty:
        return None
    if horas_df is None:
        return None
    if horas_df.empty:
        return None
    
    # Validar que existan las columnas necesarias
    if 'Create Date' not in scrap_df.columns:
        raise ValueError("❌ La columna 'Create Date' no existe en scrap_df")
    if 'Create Date' not in ventas_df.columns:
        raise ValueError("❌ La columna 'Create Date' no existe en ventas_df")
    if 'Trans Date' not in horas_df.columns:
        raise ValueError("❌ La columna 'Trans Date' no existe en horas_df")
    
    # Crear copias para no modificar los originales
    scrap_df = scrap_df.copy()
    ventas_df = ventas_df.copy()
    horas_df = horas_df.copy()
    
    # Convertir columnas de fecha a datetime
    try:
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'], errors='coerce')
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'], errors='coerce')
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'], errors='coerce')
    except Exception as e:
        raise ValueError(f"❌ Error al convertir fechas: {e}")
    
    # Eliminar filas con fechas inválidas
    scrap_df = scrap_df.dropna(subset=['Create Date'])
    ventas_df = ventas_df.dropna(subset=['Create Date'])
    horas_df = horas_df.dropna(subset=['Trans Date'])
    
    # Convertir start_date y end_date a pd.Timestamp para comparación correcta
    start_date_ts = pd.Timestamp(start_date)
    end_date_ts = pd.Timestamp(end_date)
    
    # Filtrar por rango de fechas
    scrap_filtered = scrap_df[
        (scrap_df['Create Date'] >= start_date_ts) & 
        (scrap_df['Create Date'] <= end_date_ts)
    ].copy()
    
    ventas_filtered = ventas_df[
        (ventas_df['Create Date'] >= start_date_ts) & 
        (ventas_df['Create Date'] <= end_date_ts)
    ].copy()
    
    horas_filtered = horas_df[
        (horas_df['Trans Date'] >= start_date_ts) & 
        (horas_df['Trans Date'] <= end_date_ts)
    ].copy()
    
    if scrap_filtered.empty and ventas_filtered.empty and horas_filtered.empty:
        print(f"⚠️ No se encontraron datos para el periodo {start_date} - {end_date}")
        return None
    
    # Convertir scrap a positivo
    if 'Total Posted' in scrap_filtered.columns:
        scrap_filtered['Total Posted'] = scrap_filtered['Total Posted'] * -1
    
    # Agregar columnas de fecha
    scrap_filtered['Date'] = scrap_filtered['Create Date'].dt.date
    ventas_filtered['Date'] = ventas_filtered['Create Date'].dt.date
    horas_filtered['Date'] = horas_filtered['Trans Date'].dt.date
    
    # Agrupar por fecha
    scrap_daily = scrap_filtered.groupby('Date')['Total Posted'].sum()
    ventas_daily = ventas_filtered.groupby('Date')['Total Posted'].sum()
    horas_daily = horas_filtered.groupby('Date')['Actual Hours'].sum()
    
    # Crear DataFrame con todos los días del periodo
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    result = pd.DataFrame({'Date': date_range.date})
    
    # Rellenar datos
    result['Scrap'] = result['Date'].map(scrap_daily).fillna(0)
    result['Hrs Prod.'] = result['Date'].map(horas_daily).fillna(0)
    result['$ Venta (dls)'] = result['Date'].map(ventas_daily).fillna(0)
    
    # Calcular Rate
    result['Rate'] = result.apply(
        lambda row: row['Scrap'] / row['Hrs Prod.'] if row['Hrs Prod.'] > 0 else 0,
        axis=1
    )
    
    # Calcular totales
    total_scrap = result['Scrap'].sum()
    total_horas = result['Hrs Prod.'].sum()
    total_ventas = result['$ Venta (dls)'].sum()
    total_rate = total_scrap / total_horas if total_horas > 0 else 0
    
    # Agregar fila de totales
    total_row = pd.DataFrame({
        'Date': ['TOTAL'],
        'Scrap': [total_scrap],
        'Hrs Prod.': [total_horas],
        '$ Venta (dls)': [total_ventas],
        'Rate': [total_rate]
    })
    
    result = pd.concat([result, total_row], ignore_index=True)
    
    return result