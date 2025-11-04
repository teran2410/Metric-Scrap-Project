"""
monthly_contributors.py - Análisis de contribuidores mensuales de scrap
"""

import pandas as pd
from config import WEEK_MONTH_MAPPING_2025, get_week_number_vectorized


def get_monthly_contributors(scrap_df, month, year, top_n=10):
    """
    Obtiene los principales contribuidores de scrap para un mes específico.
    Usa semanas domingo-sábado según calendario fiscal de NavicoGroup.
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        month (int): Número de mes a procesar (1-12)
        year (int): Año a procesar
        top_n (int): Número de principales contribuidores a mostrar
        
    Returns:
        DataFrame: DataFrame con los principales contribuidores o None si no hay datos
    """
    
    # Hacer una copia para no modificar el original
    scrap_df = scrap_df.copy()
    
    # Convertir columnas de fecha a datetime
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    
    # Agregar columnas de mes, año y semana DOMINGO-SÁBADO (VECTORIZADO)
    scrap_df['Month'] = scrap_df['Create Date'].dt.month
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
    
    # Filtrar por año
    scrap_year = scrap_df[scrap_df['Year'] == year]
    
    # Determinar las semanas del mes usando el mapeo fiscal si está disponible
    weeks_in_month = None
    if year == 2025 and WEEK_MONTH_MAPPING_2025 and month in WEEK_MONTH_MAPPING_2025:
        # Usar el mapeo fiscal explícito (eliminar duplicados preservando orden)
        seen = set()
        weeks_in_month = []
        for w in WEEK_MONTH_MAPPING_2025[month]:
            if w not in seen:
                seen.add(w)
                weeks_in_month.append(int(w))
    else:
        # Fallback: detectar automáticamente las semanas que tocan el mes
        weeks_in_month = scrap_year[scrap_year['Month'] == month]['Week'].unique()
    
    if not weeks_in_month or len(weeks_in_month) == 0:
        return None
    
    # Filtrar todas las filas de esas semanas (incluye días fuera del mes)
    scrap_month = scrap_year[scrap_year['Week'].isin(weeks_in_month)].copy()
    
    if scrap_month.empty:
        return None
    
    # Hacer copia para modificar
    scrap_month = scrap_month.copy()
    
    # Convertir a valores positivos
    scrap_month['Quantity'] = scrap_month['Quantity'].abs()
    scrap_month['Total Posted'] = scrap_month['Total Posted'].abs()
    
    # AGRUPAR por Item y SUMAR todos los registros del mismo item
    contributors = scrap_month.groupby('Item', as_index=False).agg({
        'Description': 'first',
        # 'Location': 'first',  # Agregar location
        'Quantity': 'sum',
        'Total Posted': 'sum'
    })
    
    # ORDENAR por monto total de MAYOR a MENOR
    contributors = contributors.sort_values('Total Posted', ascending=False)
    contributors = contributors.reset_index(drop=True)
    
    # Tomar solo los top N
    contributors = contributors.head(top_n)
    
    # CALCULAR PORCENTAJE ACUMULADO basado en el TOTAL de los TOP N
    total_top_n = contributors['Total Posted'].sum()
    if total_top_n > 0:
        contributors['Cumulative %'] = (contributors['Total Posted'].cumsum() / total_top_n * 100).round(2)
    else:
        contributors['Cumulative %'] = 0.0

    # Agregar columna de Ubicación (Location) si existe en el DataFrame original
    if 'Location' in scrap_month.columns:
        location_map = scrap_month.set_index('Item')['Location'].to_dict()
        contributors['Location'] = contributors['Item'].map(location_map)
    else:
        contributors['Location'] = ''
    
    # Agregar columna de Lugar
    contributors.insert(0, 'Lugar', range(1, len(contributors) + 1))
    
    # Renombrar columnas para el reporte
    contributors = contributors.rename(columns={
        'Item': 'Número de Parte',
        'Description': 'Descripción',
        'Quantity': 'Cantidad Scrapeada',
        'Total Posted': 'Monto (dls)',
        'Cumulative %': '% Acumulado',
        'Location': 'Ubicación'
    })
    
    # Agregar fila de totales
    total_row = pd.DataFrame({
        'Lugar': ['TOTAL'],
        'Número de Parte': [''],
        'Descripción': [''],
        'Cantidad Scrapeada': [''],
        'Monto (dls)': [contributors['Monto (dls)'].sum()],
        '% Acumulado': [''],
        'Ubicación': [''],
    })
    
    contributors = pd.concat([contributors, total_row], ignore_index=True)
    
    return contributors


def export_monthly_contributors_to_console(scrap_df, month, year, top_n=10):
    """
    Obtiene el reporte de contribuidores mensuales
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        month (int): Número de mes
        year (int): Año del reporte
        top_n (int): Número de principales contribuidores a mostrar
        
    Returns:
        DataFrame: DataFrame con los contribuidores
    """
    contributors = get_monthly_contributors(scrap_df, month, year, top_n)
    return contributors

def get_monthly_location_contributors(scrap_df, month, year, top_n=10):
    """
    Obtiene las principales celdas/ubicaciones contribuidoras de scrap para un mes específico.
    Usa semanas domingo-sábado según calendario fiscal de NavicoGroup.
    """
    scrap_df = scrap_df.copy()
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    scrap_df['Month'] = scrap_df['Create Date'].dt.month
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
    
    # Filtrar por año
    scrap_year = scrap_df[scrap_df['Year'] == year]
    
    # Determinar las semanas del mes usando el mapeo fiscal si está disponible
    weeks_in_month = None
    if year == 2025 and WEEK_MONTH_MAPPING_2025 and month in WEEK_MONTH_MAPPING_2025:
        # Usar el mapeo fiscal explícito (eliminar duplicados preservando orden)
        seen = set()
        weeks_in_month = []
        for w in WEEK_MONTH_MAPPING_2025[month]:
            if w not in seen:
                seen.add(w)
                weeks_in_month.append(int(w))
    else:
        # Fallback: detectar automáticamente las semanas que tocan el mes
        weeks_in_month = scrap_year[scrap_year['Month'] == month]['Week'].unique()
    
    if not weeks_in_month or len(weeks_in_month) == 0:
        return None
    
    # Filtrar todas las filas de esas semanas
    scrap_month = scrap_year[scrap_year['Week'].isin(weeks_in_month)].copy()
    
    if scrap_month.empty:
        return None
    
    if 'Location' not in scrap_month.columns:
        return None
    
    scrap_month['Total Posted'] = scrap_month['Total Posted'].abs()
    
    location_contrib = scrap_month.groupby('Location', as_index=False).agg({
        'Total Posted': 'sum'
    })
    
    location_contrib = location_contrib.sort_values('Total Posted', ascending=False)
    location_contrib = location_contrib.reset_index(drop=True)
    location_contrib = location_contrib.head(top_n)
    
    total_posted = location_contrib['Total Posted'].sum()
    location_contrib['Cumulative %'] = (location_contrib['Total Posted'].cumsum() / total_posted * 100).round(2)
    
    location_contrib.insert(0, 'Ranking', range(1, len(location_contrib) + 1))
    
    location_contrib = location_contrib.rename(columns={
        'Location': 'Celda',
        'Total Posted': 'Monto (dls)',
        'Cumulative %': '% Acumulado'
    })
    
    total_row = pd.DataFrame({
        'Ranking': ['TOTAL'],
        'Celda': [''],
        'Monto (dls)': [location_contrib['Monto (dls)'].sum()],
        '% Acumulado': ['']
    })
    
    location_contrib = pd.concat([location_contrib, total_row], ignore_index=True)
    
    return location_contrib