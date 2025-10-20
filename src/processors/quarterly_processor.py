"""
quarterly_processor.py - Procesamiento de datos trimestrales
"""

import pandas as pd
from config import TARGET_RATES


def process_quarterly_data(scrap_df, ventas_df, horas_df, quarter, year):
    """
    Procesa los datos de un trimestre específico y calcula el rate de scrap
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        ventas_df (DataFrame): DataFrame con datos de ventas
        horas_df (DataFrame): DataFrame con datos de horas
        quarter (int): Número de trimestre (1-4)
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con el reporte trimestral o None si no hay datos
    """
    
    # Convertir columnas de fecha a datetime
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    # Convertir scrap a positivo
    scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    # Agregar columnas de trimestre y año
    scrap_df['Quarter'] = scrap_df['Create Date'].dt.quarter
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Quarter'] = ventas_df['Create Date'].dt.quarter
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Quarter'] = horas_df['Trans Date'].dt.quarter
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Filtrar por trimestre específico
    scrap_quarter = scrap_df[(scrap_df['Quarter'] == quarter) & (scrap_df['Year'] == year)]
    ventas_quarter = ventas_df[(ventas_df['Quarter'] == quarter) & (ventas_df['Year'] == year)]
    horas_quarter = horas_df[(horas_df['Quarter'] == quarter) & (horas_df['Year'] == year)]
    
    if scrap_quarter.empty and ventas_quarter.empty and horas_quarter.empty:
        return None
    
    # Agregar columna de mes para agrupar por meses del trimestre
    scrap_quarter = scrap_quarter.copy()
    ventas_quarter = ventas_quarter.copy()
    horas_quarter = horas_quarter.copy()

    scrap_quarter.loc[:, 'Month'] = scrap_quarter['Create Date'].dt.month
    ventas_quarter.loc[:, 'Month'] = ventas_quarter['Create Date'].dt.month
    horas_quarter.loc[:, 'Month'] = horas_quarter['Trans Date'].dt.month
    
    # Agrupar por mes
    scrap_monthly = scrap_quarter.groupby('Month')['Total Posted'].sum()
    ventas_monthly = ventas_quarter.groupby('Month')['Total Posted'].sum()
    horas_monthly = horas_quarter.groupby('Month')['Actual Hours'].sum()
    
    # Obtener todos los meses del trimestre
    quarter_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }
    
    months = quarter_months.get(quarter, [])
    
    # Crear DataFrame con todos los meses del trimestre
    result = pd.DataFrame({'Month': months})
    result['Quarter'] = quarter
    result['Year'] = year
    
    # Rellenar datos
    result['Scrap'] = result['Month'].map(scrap_monthly).fillna(0)
    result['Hrs Prod.'] = result['Month'].map(horas_monthly).fillna(0)
    result['$ Venta (dls)'] = result['Month'].map(ventas_monthly).fillna(0)
    
    # Calcular Rate
    result['Rate'] = result.apply(
        lambda row: row['Scrap'] / row['Hrs Prod.'] if row['Hrs Prod.'] > 0 else 0,
        axis=1
    )
    
    # Agregar Target Rate del último mes del trimestre
    last_month = months[-1]  # último mes del trimestre (por ejemplo, 6 para Q2)
    target_last = TARGET_RATES.get(last_month, 0.60)
    result['Target Rate'] = target_last

    # Calcular totales (sin rate en la fila total)
    total_scrap = result['Scrap'].sum()
    total_horas = result['Hrs Prod.'].sum()
    total_ventas = result['$ Venta (dls)'].sum()
    
    # Agregar fila de totales (sin Rate ni Target Rate)
    total_row = pd.DataFrame({
        'Month': ['TOTAL'],
        'Quarter': [''],
        'Year': [''],
        'Scrap': [total_scrap],
        'Hrs Prod.': [total_horas],
        '$ Venta (dls)': [total_ventas],
        'Rate': [''],
        'Target Rate': ['']
    })
    
    result = pd.concat([result, total_row], ignore_index=True)
    
    return result