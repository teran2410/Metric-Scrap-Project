"""
Módulo para análisis de celdas (locations) contribuidoras al scrap
"""

import pandas as pd


def get_location_contributors(scrap_df, week_number, year):
    """
    Obtiene las celdas (locations) que más contribuyen al scrap
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        week_number (int): Número de semana a procesar
        year (int): Año a procesar
        
    Returns:
        DataFrame: DataFrame con celdas ordenadas por contribución (mayor a menor)
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
    
    # Convertir a valores positivos
    scrap_week['Total Posted'] = scrap_week['Total Posted'].abs()
    
    # Agrupar por Location y sumar montos
    locations = scrap_week.groupby('Location', as_index=False).agg({
        'Total Posted': 'sum'
    })
    
    # Ordenar por monto de MAYOR a MENOR
    locations = locations.sort_values('Total Posted', ascending=False)
    locations = locations.reset_index(drop=True)
    
    # Calcular porcentaje del total
    total_amount = locations['Total Posted'].sum()
    if total_amount > 0:
        locations['Percentage'] = (locations['Total Posted'] / total_amount * 100).round(2)
        locations['Cumulative %'] = locations['Percentage'].cumsum().round(2)
    else:
        locations['Percentage'] = 0.0
        locations['Cumulative %'] = 0.0
    
    # Renombrar columnas
    locations = locations.rename(columns={
        'Location': 'Celda',
        'Total Posted': 'Monto (dls)'
    })
    
    return locations