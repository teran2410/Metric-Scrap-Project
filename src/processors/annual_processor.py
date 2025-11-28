"""
annual_processor.py - Procesamiento de datos anuales
"""

import pandas as pd
from config import TARGET_RATES


def process_annual_data(scrap_df, ventas_df, horas_df, year):
    """
    Procesa los datos de un año completo y calcula el rate de scrap por mes
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        ventas_df (DataFrame): DataFrame con datos de ventas
        horas_df (DataFrame): DataFrame con datos de horas
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con el reporte anual por meses o None si no hay datos
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
        raise ValueError("❌ La columna 'Create Date' no existe en scrap_df. Columnas disponibles: " + str(list(scrap_df.columns)))
    if 'Create Date' not in ventas_df.columns:
        raise ValueError("❌ La columna 'Create Date' no existe en ventas_df. Columnas disponibles: " + str(list(ventas_df.columns)))
    if 'Trans Date' not in horas_df.columns:
        raise ValueError("❌ La columna 'Trans Date' no existe en horas_df. Columnas disponibles: " + str(list(horas_df.columns)))
    
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
    
    if scrap_df.empty and ventas_df.empty and horas_df.empty:
        print("⚠️ No hay fechas válidas en ningún DataFrame")
        return None
    
    # Convertir scrap a positivo
    if 'Total Posted' in scrap_df.columns:
        scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    # Agregar columnas de mes y año
    scrap_df['Month'] = scrap_df['Create Date'].dt.month
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Month'] = ventas_df['Create Date'].dt.month
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Month'] = horas_df['Trans Date'].dt.month
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Filtrar por año específico
    scrap_year = scrap_df[scrap_df['Year'] == year].copy()
    ventas_year = ventas_df[ventas_df['Year'] == year].copy()
    horas_year = horas_df[horas_df['Year'] == year].copy()
    
    if scrap_year.empty and ventas_year.empty and horas_year.empty:
        print(f"⚠️ No se encontraron datos para el año {year}")
        return None
    
    # Agregar columna de trimestre
    scrap_year['Quarter'] = scrap_year['Create Date'].dt.quarter
    ventas_year['Quarter'] = ventas_year['Create Date'].dt.quarter
    horas_year['Quarter'] = horas_year['Trans Date'].dt.quarter
    
    # Agrupar por mes
    scrap_monthly = scrap_year.groupby('Month')['Total Posted'].sum()
    ventas_monthly = ventas_year.groupby('Month')['Total Posted'].sum()
    horas_monthly = horas_year.groupby('Month')['Actual Hours'].sum()
    quarter_map = scrap_year.groupby('Month')['Quarter'].first()
    
    # Crear DataFrame con todos los meses del año
    result = pd.DataFrame({'Month': range(1, 13)})
    result['Quarter'] = result['Month'].map(quarter_map).fillna(
        result['Month'].apply(lambda m: (m - 1) // 3 + 1)
    ).astype(int)
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
    
    # Agregar Target Rate por mes
    result['Target Rate'] = result['Month'].map(TARGET_RATES)
    
    # Calcular totales (sin Rate ni Target Rate)
    total_scrap = result['Scrap'].sum()
    total_horas = result['Hrs Prod.'].sum()
    total_ventas = result['$ Venta (dls)'].sum()
    
    # Agregar fila de totales
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


def get_annual_weeks_data(scrap_df, ventas_df, horas_df, year):
    """
    Obtiene los datos agrupados por semanas del año completo
    
    Args:
        scrap_df, ventas_df, horas_df: DataFrames con datos
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con datos semanales o None
    """
    # Validar DataFrames
    if scrap_df is None or ventas_df is None or horas_df is None:
        return None
    if scrap_df.empty or ventas_df.empty or horas_df.empty:
        return None
    
    # Crear copias
    scrap_df = scrap_df.copy()
    ventas_df = ventas_df.copy()
    horas_df = horas_df.copy()
    
    # Convertir fechas
    try:
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'], errors='coerce')
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'], errors='coerce')
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir fechas en get_annual_weeks_data: {e}")
        return None
    
    # Eliminar filas con fechas inválidas
    scrap_df = scrap_df.dropna(subset=['Create Date'])
    ventas_df = ventas_df.dropna(subset=['Create Date'])
    horas_df = horas_df.dropna(subset=['Trans Date'])
    
    # Convertir scrap a positivo
    if 'Total Posted' in scrap_df.columns:
        scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    # Agregar columnas de semana y año
    scrap_df['Week'] = scrap_df['Create Date'].dt.isocalendar().week.astype(int)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Week'] = ventas_df['Create Date'].dt.isocalendar().week.astype(int)
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Week'] = horas_df['Trans Date'].dt.isocalendar().week.astype(int)
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Filtrar por año
    scrap_year = scrap_df[scrap_df['Year'] == year].copy()
    ventas_year = ventas_df[ventas_df['Year'] == year].copy()
    horas_year = horas_df[horas_df['Year'] == year].copy()
    
    if scrap_year.empty and ventas_year.empty and horas_year.empty:
        return None
    
    # Agrupar por semana
    scrap_weekly = scrap_year.groupby('Week')['Total Posted'].sum()
    horas_weekly = horas_year.groupby('Week')['Actual Hours'].sum()
    
    # Crear DataFrame
    all_weeks = sorted(set(scrap_weekly.index) | set(horas_weekly.index))
    result = pd.DataFrame({'Week': all_weeks})
    result['Scrap'] = result['Week'].map(scrap_weekly).fillna(0)
    result['Hrs Prod.'] = result['Week'].map(horas_weekly).fillna(0)
    result['Rate'] = result.apply(
        lambda row: row['Scrap'] / row['Hrs Prod.'] if row['Hrs Prod.'] > 0 else 0,
        axis=1
    )
    
    return result