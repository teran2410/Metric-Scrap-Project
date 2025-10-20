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
    if scrap_df is None or scrap_df.empty:
        print("⚠️ No hay datos de scrap disponibles")
        return None
    
    # Crear copia para no modificar el original
    df = scrap_df.copy()
    
    # Convertir fechas
    try:
        df['Create Date'] = pd.to_datetime(df['Create Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir fechas: {e}")
        return None
    
    # Filtrar por rango de fechas
    df = df[
        (df['Create Date'] >= start_date) & 
        (df['Create Date'] <= end_date)
    ]
    
    if df.empty:
        print(f"⚠️ No hay datos para el periodo {start_date} - {end_date}")
        return None
    
    # Convertir valores a positivo
    if 'Total Posted' in df.columns:
        df['Total Posted'] = df['Total Posted'] * -1
    
    # Agrupar por location y sumar
    contributors = df.groupby('Location')['Total Posted'].agg(['sum', 'count']).reset_index()
    contributors.columns = ['Location', 'Total Scrap', 'Count']
    
    # Ordenar por Total Scrap descendente
    contributors = contributors.sort_values('Total Scrap', ascending=False)
    
    # Tomar los top n contribuidores
    top_contributors = contributors.head(n_top).copy()
    
    # Calcular el porcentaje del total
    total_scrap = contributors['Total Scrap'].sum()
    top_contributors.loc[:, '% of Total'] = (top_contributors['Total Scrap'] / total_scrap * 100)
    
    return top_contributors

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
    if scrap_df is None or scrap_df.empty:
        print("⚠️ No hay datos de scrap disponibles")
        return None
    
    # Crear copia para no modificar el original
    df = scrap_df.copy()
    
    # Convertir fechas
    try:
        df['Create Date'] = pd.to_datetime(df['Create Date'], errors='coerce')
    except Exception as e:
        print(f"❌ Error al convertir fechas: {e}")
        return None
    
    # Filtrar por rango de fechas
    df = df[
        (df['Create Date'] >= start_date) & 
        (df['Create Date'] <= end_date)
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