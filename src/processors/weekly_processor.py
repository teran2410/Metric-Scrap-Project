"""
Módulo para el procesamiento de datos de Scrap, Ventas y Horas
"""

import pandas as pd
from config import TARGET_WEEK_RATES

def process_weekly_data(scrap_df, ventas_df, horas_df, week_number, year):
    """
    Procesa los datos de una semana específica y calcula el rate de scrap
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        ventas_df (DataFrame): DataFrame con datos de ventas
        horas_df (DataFrame): DataFrame con datos de horas
        week_number (int): Número de semana a procesar
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con el reporte semanal o None si no hay datos
    """
    
    # Convertir columnas de fecha a datetime
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    # Convertir scrap a positivo (multiplicar por -1)
    scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    # Agregar columnas de semana (ISO 1-53) y año
    scrap_df['Week'] = scrap_df['Create Date'].dt.isocalendar().week.astype(int)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Week'] = ventas_df['Create Date'].dt.isocalendar().week.astype(int)
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Week'] = horas_df['Trans Date'].dt.isocalendar().week.astype(int)
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Normalizar week_number: aceptar tanto 0-index (strftime('%U')) como ISO (1-53)
    if 1 <= week_number <= 53:
        actual_week_number = week_number
    elif 0 <= week_number <= 52:
        # Probablemente 0-indexed: convertir a ISO
        actual_week_number = week_number + 1
    else:
        actual_week_number = week_number

    # Filtrar por semana específica (usar semana ISO)
    scrap_week = scrap_df[(scrap_df['Week'] == actual_week_number) & (scrap_df['Year'] == year)]
    ventas_week = ventas_df[(ventas_df['Week'] == actual_week_number) & (ventas_df['Year'] == year)]
    horas_week = horas_df[(horas_df['Week'] == actual_week_number) & (horas_df['Year'] == year)]
    
    # Agrupar por fecha
    scrap_daily = scrap_week.groupby('Create Date')['Total Posted'].sum()
    ventas_daily = ventas_week.groupby('Create Date')['Total Posted'].sum()
    horas_daily = horas_week.groupby('Trans Date')['Actual Hours'].sum()
    
    # Si no hay datos en ninguna de las fuentes para la semana, devolver None
    # para que el flujo superior pueda manejar la ausencia de datos.
    if scrap_daily.empty and ventas_daily.empty and horas_daily.empty:
        return None

    # Crear lista de todos los días de la semana (Domingo a Sábado)
    all_dates = pd.date_range(
        start=scrap_daily.index.min() if not scrap_daily.empty else horas_daily.index.min(),
        end=scrap_daily.index.max() if not scrap_daily.empty else horas_daily.index.max(),
        freq='D'
    )
    
    # Asegurar que tengamos todos los días de Domingo a Sábado
    start_date = all_dates[0]
    # Ajustar al domingo anterior si no empieza en domingo
    days_since_sunday = start_date.weekday()
    if days_since_sunday != 6:  # 6 = Domingo en Python (0=Lunes, 6=Domingo)
        start_date = start_date - pd.Timedelta(days=(days_since_sunday + 1) % 7)
    
    week_dates = pd.date_range(start=start_date, periods=7, freq='D')
    
    # Crear DataFrame final
    result = pd.DataFrame(index=week_dates)
    # Nombre del día en inglés (se puede traducir usando DAYS_ES si se desea)
    result['Day'] = result.index.strftime('%A')
    result['D'] = result.index.strftime('%d').astype(int)
    # Semana ISO (1-53)
    result['W'] = result.index.to_series().dt.isocalendar().week.astype(int).values
    result['M'] = result.index.to_series().dt.month.astype(int).values

    # Rellenar datos
    result['Scrap'] = result.index.map(scrap_daily).fillna(0)
    result['Hrs Prod.'] = result.index.map(horas_daily).fillna(0)
    result['$ Venta (dls)'] = result.index.map(ventas_daily).fillna(0)
    
    # Calcular Rate (evitar división por cero)
    result['Rate'] = result.apply(
        lambda row: row['Scrap'] / row['Hrs Prod.'] if row['Hrs Prod.'] > 0 else 0,
        axis=1
    )
    
    # Determinar target rate usando la semana ISO normalizada
    target_rate_for_week = TARGET_WEEK_RATES.get(actual_week_number, 0.50)
    result['Target Rate'] = target_rate_for_week
    
    # Calcular totales
    total_scrap = result['Scrap'].sum()
    total_horas = result['Hrs Prod.'].sum()
    total_ventas = result['$ Venta (dls)'].sum()
    total_rate = total_scrap / total_horas if total_horas > 0 else 0
    
    # Agregar fila de totales
    total_row = pd.DataFrame({
        'Day': ['Total'],
        'D': [''],
        'W': [''],
        'M': [''],
        'Scrap': [total_scrap],
        'Hrs Prod.': [total_horas],
        'Rate': [total_rate],
        'Target Rate': [target_rate_for_week],
        '$ Venta (dls)': [total_ventas]
    })
    
    result = pd.concat([result, total_row], ignore_index=True)
    
    return result