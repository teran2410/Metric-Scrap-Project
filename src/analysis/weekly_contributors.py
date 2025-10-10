"""
weekly_contributors.py - Módulo para análisis de principales contribuidores de scrap
"""

import pandas as pd
from colorama import Fore, Style


def get_top_contributors_by_week(scrap_df, week_number, year, top_n=10):
    """
    Obtiene los principales contribuidores de scrap para una semana específica
    IMPORTANTE: Devuelve los items con MAYOR monto total en dólares
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        week_number (int): Número de semana a procesar
        year (int): Año a procesar
        top_n (int): Número de principales contribuidores a mostrar (default: 10)
        
    Returns:
        DataFrame: DataFrame con los principales contribuidores o None si no hay datos
    """
    
    # Hacer una copia para no modificar el original
    scrap_df = scrap_df.copy()
    
    # Convertir columnas de fecha a datetime
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    
    # Agregar columnas de semana y año
    scrap_df['Week'] = scrap_df['Create Date'].dt.strftime('%U').astype(int)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    
    # Filtrar por semana específica
    scrap_week = scrap_df[(scrap_df['Week'] == week_number) & (scrap_df['Year'] == year)]
    
    if scrap_week.empty:
        return None
    
    # Hacer copia para modificar
    scrap_week = scrap_week.copy()
    
    # Convertir a valores positivos ANTES de agrupar
    # IMPORTANTE: Usamos abs() para asegurar valores positivos
    scrap_week['Quantity'] = scrap_week['Quantity'].abs()
    scrap_week['Total Posted'] = scrap_week['Total Posted'].abs()
    
    # AGRUPAR por Item y SUMAR todos los registros del mismo item
    # Esto combina todas las veces que aparece el mismo número de parte
    contributors = scrap_week.groupby('Item', as_index=False).agg({
        'Description': 'first',      # Tomar la primera descripción
        'Quantity': 'sum',            # SUMAR todas las cantidades del mismo item
        'Total Posted': 'sum'         # SUMAR todos los montos del mismo item (YA EN POSITIVO)
    })
    
    # ORDENAR por monto total de MAYOR a MENOR (descendente)
    # ascending=False significa que los valores MÁS GRANDES van primero
    contributors = contributors.sort_values('Total Posted', ascending=False)
    
    # RESETEAR índice después de ordenar
    contributors = contributors.reset_index(drop=True)
    
    # Tomar solo los top N (los que tienen mayor monto)
    contributors = contributors.head(top_n)
    
    # CALCULAR PORCENTAJE ACUMULADO basado en el TOTAL de los TOP N
    total_top_n = contributors['Total Posted'].sum()
    if total_top_n > 0:
        contributors['Cumulative %'] = (contributors['Total Posted'].cumsum() / total_top_n * 100).round(2)
    else:
        contributors['Cumulative %'] = 0.0
    
    # Agregar columna de Ubicación (Location) si existe en el DataFrame original
    if 'Location' in scrap_week.columns:
        location_map = scrap_week.set_index('Item')['Location'].to_dict()
        contributors['Location'] = contributors['Item'].map(location_map)
    else:
        contributors['Location'] = ''

    # Agregar columna de Lugar (1, 2, 3, etc.)
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
    
    # Agregar fila de totales al final (sin % acumulado en total)
    total_row = pd.DataFrame({
        'Lugar': ['TOTAL'],
        'Número de Parte': [''],
        'Descripción': [''],
        'Cantidad Scrapeada': [''],
        'Monto (dls)': [contributors['Monto (dls)'].sum()],
        '% Acumulado': [''],
        'Ubicación': ['']
    })
    
    contributors = pd.concat([contributors, total_row], ignore_index=True)
    
    return contributors

def export_contributors_to_console(scrap_df, week, year, top_n=10):
    """
    Exporta el reporte de contribuidores (sin imprimir en consola)
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        week (int): Número de semana
        year (int): Año del reporte
        top_n (int): Número de principales contribuidores a mostrar
    """
    contributors = get_top_contributors_by_week(scrap_df, week, year, top_n)
    return contributors

def get_weekly_location_contributors(scrap_df, week_number, year, top_n=10):
    """
    Obtiene las principales celdas/ubicaciones contribuidoras de scrap para una semana específica
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        week_number (int): Número de semana a procesar
        year (int): Año a procesar
        top_n (int): Número de celdas principales a mostrar (default: 10)
        
    Returns:
        DataFrame: DataFrame con las celdas contribuidoras ordenadas por monto
    """
    
    # Hacer copia
    scrap_df = scrap_df.copy()
    
    # Convertir fecha
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    
    # Agregar semana y año
    scrap_df['Week'] = scrap_df['Create Date'].dt.strftime('%U').astype(int)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    
    # Filtrar por semana específica
    scrap_week = scrap_df[(scrap_df['Week'] == week_number) & (scrap_df['Year'] == year)]
    
    if scrap_week.empty:
        return None
    
    # Verificar que exista columna Location
    if 'Location' not in scrap_week.columns:
        return None
    
    # Convertir a valores positivos
    scrap_week = scrap_week.copy()
    scrap_week['Total Posted'] = scrap_week['Total Posted'].abs()
    
    # Agrupar por Location (Celda)
    location_contrib = scrap_week.groupby('Location', as_index=False).agg({
        'Total Posted': 'sum'
    })
    
    # Ordenar de mayor a menor
    location_contrib = location_contrib.sort_values('Total Posted', ascending=False)
    location_contrib = location_contrib.reset_index(drop=True)
    
    # Tomar top N
    location_contrib = location_contrib.head(top_n)
    
    # Calcular porcentaje acumulado
    total_amount = location_contrib['Total Posted'].sum()
    if total_amount > 0:
        location_contrib['Cumulative %'] = (
            location_contrib['Total Posted'].cumsum() / total_amount * 100
        ).round(2)
    else:
        location_contrib['Cumulative %'] = 0.0
    
    # Agregar ranking
    location_contrib.insert(0, 'Ranking', range(1, len(location_contrib) + 1))
    
    # Renombrar columnas
    location_contrib = location_contrib.rename(columns={
        'Location': 'Celda',
        'Total Posted': 'Monto (dls)'
    })
    
    # Agregar fila de totales
    total_row = pd.DataFrame({
        'Ranking': ['TOTAL'],
        'Celda': [''],
        'Monto (dls)': [location_contrib['Monto (dls)'].sum()],
        'Cumulative %': ['']
    })
    
    location_contrib = pd.concat([location_contrib, total_row], ignore_index=True)
    
    return location_contrib