"""
monthly_processor.py - Procesamiento de datos mensuales
"""

import pandas as pd
from config import TARGET_RATES


def process_monthly_data(scrap_df, ventas_df, horas_df, month, year):
    """
    Procesa los datos de un mes específico y calcula el rate de scrap
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        ventas_df (DataFrame): DataFrame con datos de ventas
        horas_df (DataFrame): DataFrame con datos de horas
        month (int): Número de mes (1-12)
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con el reporte mensual o None si no hay datos
    """
    
    # Convertir columnas de fecha a datetime
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    # Convertir scrap a positivo (multiplicar por -1)
    scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    # Agregar columnas de mes y año
    scrap_df['Month'] = scrap_df['Create Date'].dt.month
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Month'] = ventas_df['Create Date'].dt.month
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Month'] = horas_df['Trans Date'].dt.month
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Filtrar por mes específico
    scrap_month = scrap_df[(scrap_df['Month'] == month) & (scrap_df['Year'] == year)]
    ventas_month = ventas_df[(ventas_df['Month'] == month) & (ventas_df['Year'] == year)]
    horas_month = horas_df[(horas_df['Month'] == month) & (horas_df['Year'] == year)]
    
    if scrap_month.empty and ventas_month.empty and horas_month.empty:
        return None
    
    # Agregar columna de semana para agrupar por semanas del mes
    scrap_month['Week'] = scrap_month['Create Date'].dt.strftime('%U').astype(int)
    ventas_month['Week'] = ventas_month['Create Date'].dt.strftime('%U').astype(int)
    horas_month['Week'] = horas_month['Trans Date'].dt.strftime('%U').astype(int)
    
    # Agrupar por semana
    scrap_weekly = scrap_month.groupby('Week')['Total Posted'].sum()
    ventas_weekly = ventas_month.groupby('Week')['Total Posted'].sum()
    horas_weekly = horas_month.groupby('Week')['Actual Hours'].sum()
    
    # Obtener todas las semanas del mes
    all_weeks = sorted(set(scrap_weekly.index) | set(ventas_weekly.index) | set(horas_weekly.index))
    
    # Crear DataFrame con todas las semanas
    result = pd.DataFrame(index=all_weeks)
    result['Week'] = result.index
    result['Month'] = month
    result['Year'] = year
    
    # Rellenar datos
    result['Scrap'] = result['Week'].map(scrap_weekly).fillna(0)
    result['Hrs Prod.'] = result['Week'].map(horas_weekly).fillna(0)
    result['$ Venta (dls)'] = result['Week'].map(ventas_weekly).fillna(0)
    
    # Calcular Rate (evitar división por cero)
    result['Rate'] = result.apply(
        lambda row: row['Scrap'] / row['Hrs Prod.'] if row['Hrs Prod.'] > 0 else 0,
        axis=1
    )
    
    # Agregar Target Rate según el mes
    result['Target Rate'] = TARGET_RATES.get(month, 0.60)
    
    # Calcular totales
    total_scrap = result['Scrap'].sum()
    total_horas = result['Hrs Prod.'].sum()
    total_ventas = result['$ Venta (dls)'].sum()
    total_rate = total_scrap / total_horas if total_horas > 0 else 0
    
    # Agregar fila de totales
    total_row = pd.DataFrame({
        'Week': ['TOTAL'],
        'Month': [''],
        'Year': [''],
        'Scrap': [total_scrap],
        'Hrs Prod.': [total_horas],
        'Rate': [total_rate],
        'Target Rate': [TARGET_RATES.get(month, 0.60)],
        '$ Venta (dls)': [total_ventas]
    })
    
    result = pd.concat([result, total_row], ignore_index=True)
    
    return result