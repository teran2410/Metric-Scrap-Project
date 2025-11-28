"""
custom_contributors.py - Análisis de contribuidores para rango de fechas personalizado
"""

import pandas as pd


def get_top_contributors_custom(scrap_df, start_date, end_date, n_top=10):
    """
    Obtiene los principales contribuidores al scrap en un rango de fechas específico
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        start_date (datetime): Fecha inicial
        end_date (datetime): Fecha final
        n_top (int): Número de contribuidores a retornar
        
    Returns:
        DataFrame: DataFrame con los principales contribuidores o None
    """
    if scrap_df is None:
        return None
    if scrap_df.empty:
        return None
    
    # Crear copia para no modificar el original
    df = scrap_df.copy()
    
    # Convertir fechas
    try:
        df['Create Date'] = pd.to_datetime(df['Create Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir fechas: {e}")
        return None
    
    # Convertir start_date y end_date a pd.Timestamp para comparación correcta
    start_date_ts = pd.Timestamp(start_date)
    end_date_ts = pd.Timestamp(end_date)
    
    # Filtrar por rango de fechas
    df = df[
        (df['Create Date'] >= start_date_ts) & 
        (df['Create Date'] <= end_date_ts)
    ]
    
    if df.empty:
        print(f"⚠️ No hay datos para el periodo {start_date} - {end_date}")
        return None
    
    # Convertir valores a positivo
    df['Quantity'] = df['Quantity'].abs()
    df['Total Posted'] = df['Total Posted'].abs()
    
    # Agrupar por Item (número de parte) como en weekly/monthly/quarterly
    contributors = df.groupby('Item', as_index=False).agg({
        'Description': 'first',
        'Location': 'first',
        'Quantity': 'sum',
        'Total Posted': 'sum'
    })
    
    # Ordenar por Total Posted descendente
    contributors = contributors.sort_values('Total Posted', ascending=False)
    
    # Reset index y tomar top n
    contributors = contributors.reset_index(drop=True)
    contributors = contributors.head(n_top)
    
    # Calcular % acumulado
    total_top_n = contributors['Total Posted'].sum()
    if total_top_n > 0:
        contributors['Cumulative %'] = (contributors['Total Posted'].cumsum() / total_top_n * 100).round(2)
    else:
        contributors['Cumulative %'] = 0.0
    
    # Agregar columna de ranking (Lugar)
    contributors.insert(0, 'Lugar', range(1, len(contributors) + 1))
    
    # Renombrar columnas para consistencia con otros reportes
    contributors = contributors.rename(columns={
        'Item': 'Número de Parte',
        'Description': 'Descripción',
        'Location': 'Ubicación',
        'Quantity': 'Cantidad Scrapeada',
        'Total Posted': 'Monto (dls)',
        'Cumulative %': '% Acumulado'
    })
    
    # Agregar fila TOTAL
    total_row = pd.DataFrame({
        'Lugar': ['TOTAL'],
        'Número de Parte': [''],
        'Descripción': [''],
        'Ubicación': [''],
        'Cantidad Scrapeada': [contributors['Cantidad Scrapeada'].sum()],
        'Monto (dls)': [contributors['Monto (dls)'].sum()],
        '% Acumulado': ['']
    })
    
    contributors = pd.concat([contributors, total_row], ignore_index=True)
    
    return contributors

def get_scrap_reasons_custom(scrap_df, start_date, end_date, n_top=10):
    """
    Obtiene las principales razones de scrap en un rango de fechas específico
    
    Args:
        scrap_df (DataFrame): DataFrame con datos de scrap
        start_date (datetime): Fecha inicial
        end_date (datetime): Fecha final
        n_top (int): Número de razones a retornar
        
    Returns:
        DataFrame: DataFrame con las principales razones de scrap o None
    """
    if scrap_df is None:
        return None
    if scrap_df.empty:
        return None
    
    # Crear copia para no modificar el original
    df = scrap_df.copy()
    
    # Convertir fechas
    try:
        df['Create Date'] = pd.to_datetime(df['Create Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir fechas: {e}")
        return None
    
    # Convertir start_date y end_date a pd.Timestamp para comparación correcta
    start_date_ts = pd.Timestamp(start_date)
    end_date_ts = pd.Timestamp(end_date)
    
    # Filtrar por rango de fechas
    df = df[
        (df['Create Date'] >= start_date_ts) & 
        (df['Create Date'] <= end_date_ts)
    ]
    
    if df.empty:
        print(f"⚠️ No hay datos para el periodo {start_date} - {end_date}")
        return None
    
    # Convertir valores a positivo
    if 'Total Posted' in df.columns:
        df['Total Posted'] = df['Total Posted'] * -1
    
    # Agrupar por razón y sumar
    reasons = df.groupby('Reason Code')['Total Posted'].agg(['sum', 'count']).reset_index()
    reasons.columns = ['Reason', 'Total Scrap', 'Count']
    
    # Ordenar por Total Scrap descendente
    reasons = reasons.sort_values('Total Scrap', ascending=False)
    
    # Tomar los top n razones
    top_reasons = reasons.head(n_top).copy()
    
    # Calcular el porcentaje del total
    total_scrap = reasons['Total Scrap'].sum()
    top_reasons.loc[:, '% of Total'] = (top_reasons['Total Scrap'] / total_scrap * 100)
    
    return top_reasons


def get_custom_contributors(scrap_df, start_date, end_date, top_n=10):
    """
    Wrapper uniforme que expone get_custom_contributors para ReportService.
    Delegará en get_top_contributors_custom.
    """
    return get_top_contributors_custom(scrap_df, start_date, end_date, n_top=top_n)