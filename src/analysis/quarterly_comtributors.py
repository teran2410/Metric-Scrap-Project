"""
quarterly_contributors.py - Análisis de contribuidores trimestrales de scrap
"""

import pandas as pd


def get_quarterly_contributors(scrap_df, quarter, year, top_n=10):
    """
    Obtiene los principales contribuidores de scrap para un trimestre específico
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        quarter (int): Número de trimestre (1-4)
        year (int): Año a procesar
        top_n (int): Número de principales contribuidores a mostrar
        
    Returns:
        DataFrame: DataFrame con los principales contribuidores o None si no hay datos
    """
    
    scrap_df = scrap_df.copy()
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    scrap_df['Quarter'] = scrap_df['Create Date'].dt.quarter
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    
    scrap_quarter = scrap_df[(scrap_df['Quarter'] == quarter) & (scrap_df['Year'] == year)]
    
    if scrap_quarter.empty:
        return None
    
    scrap_quarter = scrap_quarter.copy()
    scrap_quarter['Quantity'] = scrap_quarter['Quantity'].abs()
    scrap_quarter['Total Posted'] = scrap_quarter['Total Posted'].abs()
    
    contributors = scrap_quarter.groupby('Item', as_index=False).agg({
        'Description': 'first',
        'Location': 'first',
        'Quantity': 'sum',
        'Total Posted': 'sum'
    })
    
    contributors = contributors.sort_values('Total Posted', ascending=False)
    contributors = contributors.reset_index(drop=True)
    contributors = contributors.head(top_n)
    
    total_top_n = contributors['Total Posted'].sum()
    if total_top_n > 0:
        contributors['Cumulative %'] = (contributors['Total Posted'].cumsum() / total_top_n * 100).round(2)
    else:
        contributors['Cumulative %'] = 0.0
    
    contributors.insert(0, 'Lugar', range(1, len(contributors) + 1))
    
    contributors = contributors.rename(columns={
        'Item': 'Número de Parte',
        'Description': 'Descripción',
        'Location': 'Celda',
        'Quantity': 'Cantidad Scrapeada',
        'Total Posted': 'Monto (dls)',
        'Cumulative %': '% Acumulado'
    })
    
    total_row = pd.DataFrame({
        'Lugar': ['TOTAL'],
        'Número de Parte': [''],
        'Descripción': [''],
        'Celda': [''],
        'Cantidad Scrapeada': [contributors['Cantidad Scrapeada'].sum()],
        'Monto (dls)': [contributors['Monto (dls)'].sum()],
        '% Acumulado': ['']
    })
    
    contributors = pd.concat([contributors, total_row], ignore_index=True)
    
    return contributors


def export_quarterly_contributors_to_console(scrap_df, quarter, year, top_n=10):
    """Obtiene el reporte de contribuidores trimestrales"""
    contributors = get_quarterly_contributors(scrap_df, quarter, year, top_n)
    return contributors