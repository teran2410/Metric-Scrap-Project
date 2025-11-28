"""
Módulo para el procesamiento de datos de Scrap, Ventas y Horas
"""

import pandas as pd
import logging
from config import TARGET_WEEK_RATES, get_week_number_vectorized

logger = logging.getLogger(__name__)

def process_weekly_data(scrap_df, ventas_df, horas_df, week_number, year):
    """
    Procesa los datos de una semana específica y calcula el rate de scrap.
    Usa semanas domingo-sábado según calendario fiscal de NavicoGroup.
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        ventas_df (DataFrame): DataFrame con datos de ventas
        horas_df (DataFrame): DataFrame con datos de horas
        week_number (int): Número de semana a procesar (1-53, domingo a sábado)
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con el reporte semanal o None si no hay datos
    """
    logger.info(f"=== Procesando semana {week_number} del año {year} ===")
    
    # Convertir columnas de fecha a datetime
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    # Convertir scrap a positivo usando valor absoluto (más robusto)
    scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
    
    # Agregar columnas de semana DOMINGO-SÁBADO y año (VECTORIZADO)
    scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Week'] = get_week_number_vectorized(ventas_df['Create Date'], year=year)
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Week'] = get_week_number_vectorized(horas_df['Trans Date'], year=year)
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Usar el número de semana directamente (ya no necesitamos conversión)
    actual_week_number = week_number

    # Filtrar por semana específica (usar semana domingo-sábado)
    scrap_week = scrap_df[(scrap_df['Week'] == actual_week_number) & (scrap_df['Year'] == year)]
    ventas_week = ventas_df[(ventas_df['Week'] == actual_week_number) & (ventas_df['Year'] == year)]
    horas_week = horas_df[(horas_df['Week'] == actual_week_number) & (horas_df['Year'] == year)]
    
    logger.info(f"Registros filtrados - Scrap: {len(scrap_week)}, Ventas: {len(ventas_week)}, Horas: {len(horas_week)}")
    
    # Agrupar por fecha
    scrap_daily = scrap_week.groupby('Create Date')['Total Posted'].sum()
    ventas_daily = ventas_week.groupby('Create Date')['Total Posted'].sum()
    horas_daily = horas_week.groupby('Trans Date')['Actual Hours'].sum()
    
    # Si no hay datos en ninguna de las fuentes para la semana, devolver None
    if scrap_daily.empty and ventas_daily.empty and horas_daily.empty:
        return None

    # Obtener todas las fechas con datos
    all_dates = sorted(set(scrap_daily.index) | set(horas_daily.index) | set(ventas_daily.index))
    
    if not all_dates:
        return None
    
    # Encontrar el domingo de inicio de la semana
    start_date = min(all_dates)
    # Ajustar al domingo anterior si no empieza en domingo (weekday() 6=domingo)
    days_since_sunday = (start_date.weekday() + 1) % 7  # Convertir a 0=domingo
    if days_since_sunday != 0:
        start_date = start_date - pd.Timedelta(days=days_since_sunday)
    
    # Crear rango de 7 días (domingo a sábado)
    week_dates = pd.date_range(start=start_date, periods=7, freq='D')
    
    # Crear DataFrame final
    result = pd.DataFrame(index=week_dates)
    result['Day'] = result.index.strftime('%A')
    result['D'] = result.index.strftime('%d').astype(int)
    # Usar semana domingo-sábado (VECTORIZADO)
    result['W'] = get_week_number_vectorized(result.index.to_series(), year=year).values
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