"""
annual_contributors.py - Análisis de contribuidores anuales de scrap
"""

import pandas as pd


def get_annual_contributors(scrap_df, year, top_n=10):
    """
    Obtiene los principales contribuidores de scrap para un año completo
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        year (int): Año a procesar
        top_n (int): Número de principales contribuidores
        
    Returns:
        DataFrame: DataFrame con los principales contribuidores o None
    """
    # Validar entrada
    if scrap_df is None or scrap_df.empty:
        print("⚠️ scrap_df está vacío en get_annual_contributors")
        return None
    
    if 'Create Date' not in scrap_df.columns:
        print(f"❌ Columna 'Create Date' no existe. Columnas: {list(scrap_df.columns)}")
        return None
    
    # Crear copia para no modificar el original
    scrap_df = scrap_df.copy()
    
    # Convertir fecha con manejo de errores
    try:
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir Create Date: {e}")
        return None
    
    # Eliminar filas con fechas inválidas
    scrap_df = scrap_df.dropna(subset=['Create Date'])
    
    if scrap_df.empty:
        print("⚠️ No hay fechas válidas después de la conversión")
        return None
    
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    
    scrap_year = scrap_df[scrap_df['Year'] == year]
    
    if scrap_year.empty:
        print(f"⚠️ No hay datos para el año {year}")
        return None
    
    scrap_year = scrap_year.copy()
    scrap_year['Quantity'] = scrap_year['Quantity'].abs()
    scrap_year['Total Posted'] = scrap_year['Total Posted'].abs()
    
    contributors = scrap_year.groupby('Item', as_index=False).agg({
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
        'Location': 'Ubicación',
        'Quantity': 'Cantidad Scrapeada',
        'Total Posted': 'Monto (dls)',
        'Cumulative %': '% Acumulado'
    })
    
    total_row = pd.DataFrame({
        'Lugar': ['TOTAL'],
        'Número de Parte': [''],
        'Descripción': [''],
        'Ubicación': [''],
        'Cantidad Scrapeada': [''],
        'Monto (dls)': [contributors['Monto (dls)'].sum()],
        '% Acumulado': ['']
    })
    
    contributors = pd.concat([contributors, total_row], ignore_index=True)
    
    return contributors


def get_annual_location_contributors(scrap_df, year, top_n=10):
    """
    Obtiene las celdas (locations) que más contribuyeron al scrap anual
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        year (int): Año a procesar
        top_n (int): Número de celdas a mostrar
        
    Returns:
        DataFrame: DataFrame con celdas ordenadas por contribución
    """
    # Validar entrada
    if scrap_df is None or scrap_df.empty:
        print("⚠️ scrap_df está vacío en get_annual_location_contributors")
        return None
    
    if 'Create Date' not in scrap_df.columns:
        print(f"❌ Columna 'Create Date' no existe. Columnas: {list(scrap_df.columns)}")
        return None
    
    # Crear copia
    scrap_df = scrap_df.copy()
    
    # Convertir fecha
    try:
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir Create Date: {e}")
        return None
    
    # Eliminar fechas inválidas
    scrap_df = scrap_df.dropna(subset=['Create Date'])
    
    if scrap_df.empty:
        print("⚠️ No hay fechas válidas")
        return None
    
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    
    scrap_year = scrap_df[scrap_df['Year'] == year]
    
    if scrap_year.empty:
        print(f"⚠️ No hay datos para el año {year}")
        return None
    
    scrap_year = scrap_year.copy()
    scrap_year['Total Posted'] = scrap_year['Total Posted'].abs()
    
    locations = scrap_year.groupby('Location', as_index=False).agg({
        'Total Posted': 'sum'
    })
    
    locations = locations.sort_values('Total Posted', ascending=False)
    locations = locations.reset_index(drop=True)
    locations = locations.head(top_n)
    
    total_amount = locations['Total Posted'].sum()
    if total_amount > 0:
        locations['Percentage'] = (locations['Total Posted'] / total_amount * 100).round(2)
        locations['Cumulative %'] = locations['Percentage'].cumsum().round(2)
    else:
        locations['Percentage'] = 0.0
        locations['Cumulative %'] = 0.0
    
    locations = locations.rename(columns={
        'Location': 'Celda',
        'Total Posted': 'Monto (dls)'
    })
    
    return locations


def export_annual_contributors_to_console(scrap_df, year, top_n=10):
    """Obtiene el reporte de contribuidores anuales"""
    try:
        contributors = get_annual_contributors(scrap_df, year, top_n)
        return contributors
    except Exception as e:
        print(f"❌ Error en export_annual_contributors_to_console: {e}")
        return None