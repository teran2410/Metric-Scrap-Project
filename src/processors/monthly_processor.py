"""
monthly_processor.py - Procesamiento de datos mensuales
"""

import pandas as pd
from config import TARGET_RATES, WEEK_MONTH_MAPPING_2025, get_week_number_vectorized


def process_monthly_data(scrap_df, ventas_df, horas_df, month, year):
    """
    Procesa los datos de un mes específico y calcula el rate de scrap.
    Usa semanas domingo-sábado según calendario fiscal de NavicoGroup.
    """
    # Hacer copias para no modificar originales
    scrap_df = scrap_df.copy()
    ventas_df = ventas_df.copy()
    horas_df = horas_df.copy()
    
    # Convertir columnas de fecha a datetime (con manejo de errores)
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'], errors='coerce')
    ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'], errors='coerce')
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'], errors='coerce')
    
    # Filtrar registros con fechas inválidas
    scrap_df = scrap_df.dropna(subset=['Create Date'])
    ventas_df = ventas_df.dropna(subset=['Create Date'])
    horas_df = horas_df.dropna(subset=['Trans Date'])
    
    # Convertir scrap a positivo
    scrap_df['Total Posted'] = scrap_df['Total Posted'].abs()
    
    # Agregar columnas de semana DOMINGO-SÁBADO y año (VECTORIZADO - MUY RÁPIDO)
    scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    ventas_df['Week'] = get_week_number_vectorized(ventas_df['Create Date'], year=year)
    ventas_df['Year'] = ventas_df['Create Date'].dt.year
    horas_df['Week'] = get_week_number_vectorized(horas_df['Trans Date'], year=year)
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Filtrar por año
    scrap_year = scrap_df[scrap_df['Year'] == year]
    ventas_year = ventas_df[ventas_df['Year'] == year]
    horas_year = horas_df[horas_df['Year'] == year]
    
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
        # Fallback: detectar automáticamente las semanas que tocan el mes (optimizado)
        scrap_year['Month'] = scrap_year['Create Date'].dt.month
        ventas_year['Month'] = ventas_year['Create Date'].dt.month
        horas_year['Month'] = horas_year['Trans Date'].dt.month
        
        weeks_set = set(scrap_year[scrap_year['Month'] == month]['Week'].unique())
        weeks_set.update(ventas_year[ventas_year['Month'] == month]['Week'].unique())
        weeks_set.update(horas_year[horas_year['Month'] == month]['Week'].unique())
        weeks_in_month = sorted(weeks_set)
    
    if not weeks_in_month or len(weeks_in_month) == 0:
        return None
    
    # Filtrar datos de esas semanas (ÚNICA VEZ)
    scrap_weeks = scrap_year[scrap_year['Week'].isin(weeks_in_month)]
    ventas_weeks = ventas_year[ventas_year['Week'].isin(weeks_in_month)]
    horas_weeks = horas_year[horas_year['Week'].isin(weeks_in_month)]
    
    # Agrupar por semana (sort=False es más rápido)
    scrap_weekly = scrap_weeks.groupby('Week', sort=False)['Total Posted'].sum()
    ventas_weekly = ventas_weeks.groupby('Week', sort=False)['Total Posted'].sum()
    horas_weekly = horas_weeks.groupby('Week', sort=False)['Actual Hours'].sum()
    
    # Crear DataFrame con todas las semanas
    result = pd.DataFrame({'Week': weeks_in_month})
    result['Month'] = month
    result['Year'] = year
    
    # Rellenar datos
    result['Scrap'] = result['Week'].map(scrap_weekly).fillna(0)
    result['Hrs Prod.'] = result['Week'].map(horas_weekly).fillna(0)
    result['$ Venta (dls)'] = result['Week'].map(ventas_weekly).fillna(0)
    
    # Calcular Rate
    result['Rate'] = result.apply(
        lambda row: row['Scrap'] / row['Hrs Prod.'] if row['Hrs Prod.'] > 0 else 0,
        axis=1
    )
    
    # Agregar Target Rate según el mes
    result['Target Rate'] = TARGET_RATES.get(month, 0.60)
    
    # Calcular totales
    total_scrap = result['Scrap'].sum()
    total_horas = result['Hrs Prod.'].sum()
    total_ventas = result['$ Venta (dls)'].sum()
    total_rate = total_scrap / total_horas if total_horas > 0 else 0
    
    # Agregar fila de totales
    total_row = pd.DataFrame({
        'Week': ['TOTAL'],
        'Month': [''],
        'Year': [''],
        'Scrap': [total_scrap],
        'Hrs Prod.': [total_horas],
        'Rate': [total_rate],
        'Target Rate': [TARGET_RATES.get(month, 0.60)],
        '$ Venta (dls)': [total_ventas]
    })
    
    result = pd.concat([result, total_row], ignore_index=True)
    
    return result