"""
quarterly_contributors.py - Análisis de contribuidores trimestrales de scrap
"""

import pandas as pd


def get_quarterly_contributors(scrap_df, quarter, year, top_n=10):
    """
    Obtiene los principales contribuidores de scrap para un trimestre específico.
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap (debe incluir columnas como 'Item', 'Total Posted', 'Quantity', 'Create Date')
        quarter (int): Número de trimestre (1–4)
        year (int): Año a procesar
        top_n (int): Número de principales contribuidores a mostrar (default: 10)
        
    Returns:
        DataFrame: DataFrame con los principales contribuidores trimestrales o None si no hay datos
    """
    
    # COPIA DE DATOS BASE
    # Hacemos una copia del DataFrame original para evitar modificarlo directamente
    scrap_df = scrap_df.copy()

    # Convertimos la columna 'Create Date' a formato datetime para extraer trimestre y año
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    scrap_df['Quarter'] = scrap_df['Create Date'].dt.quarter
    scrap_df['Year'] = scrap_df['Create Date'].dt.year

    # FILTRAR POR TRIMESTRE Y AÑO
    scrap_quarter = scrap_df[(scrap_df['Quarter'] == quarter) & (scrap_df['Year'] == year)]

    if scrap_quarter.empty:
        # Si no hay datos, retornamos None
        return None

    # NORMALIZACIÓN DE VALORES
    # Nos aseguramos de que todos los valores sean positivos
    # Esto evita errores si hay registros negativos (por reversas o ajustes)
    scrap_quarter = scrap_quarter.copy()
    scrap_quarter['Quantity'] = scrap_quarter['Quantity'].abs()
    scrap_quarter['Total Posted'] = scrap_quarter['Total Posted'].abs()
    
    # AGRUPAR POR NÚMERO DE PARTE
    # Sumamos la cantidad y el monto total de cada número de parte dentro del trimestre
    contributors = scrap_quarter.groupby('Item', as_index=False).agg({
        'Description': 'first',        # Tomar la primera descripción
        'Quantity': 'sum',             # SUMAR todas las cantidades del mismo item
        'Total Posted': 'sum'          # SUMAR todos los montos del mismo item (YA EN POSITIVO)
    })

    # ORDENAR Y SELECCIONAR TOP N
    contributors = contributors.sort_values('Total Posted', ascending=False)
    contributors = contributors.reset_index(drop=True)
    contributors = contributors.head(top_n)

    # CÁLCULO DE PORCENTAJE ACUMULADO
    total_top_n = contributors['Total Posted'].sum()
    if total_top_n > 0:
        contributors['Cumulative %'] = (
            contributors['Total Posted'].cumsum() / total_top_n * 100
        ).round(2)
    else:
        contributors['Cumulative %'] = 0.0

    
    # MAPEO DE UBICACIÓN (SI EXISTE)
    if 'Location' in scrap_quarter.columns:
        location_map = scrap_quarter.set_index('Item')['Location'].to_dict()
        contributors['Location'] = contributors['Item'].map(location_map)
    else:
        contributors['Location'] = ''
    
    # AGREGAR COLUMNA DE LUGAR (RANK)
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

def export_quarterly_contributors_to_console(scrap_df, quarter, year, top_n=10):
    """Obtiene el reporte de contribuidores trimestrales"""
    contributors = get_quarterly_contributors(scrap_df, quarter, year, top_n)
    return contributors