"""
Módulo para el formateo y visualización de reportes
"""

import pandas as pd
from colorama import init, Fore, Style

# Inicializar colorama para colores en consola
init(autoreset=True)


def format_output(df):
    """
    Formatea el DataFrame para una mejor visualización en consola
    
    Args:
        df (DataFrame): DataFrame con los datos del reporte
    """
    if df is None:
        return
    
    # Crear copia para formatear
    output = df.copy()
    
    # Formatear columnas numéricas con colores en Rate
    formatted_rows = []
    
    for index, row in output.iterrows():
        formatted_row = {}
        
        for col in output.columns:
            value = row[col]
            
            if col == 'Scrap' or col == 'Hrs Prod.':
                formatted_row[col] = f"{value:,.2f}" if isinstance(value, (int, float)) else value
            elif col == 'Rate':
                if isinstance(value, (int, float)):
                    rate_str = f"{value:.2f}"
                    # Obtener target rate de la misma fila
                    target = row['Target Rate']
                    if pd.notna(target) and target > 0:
                        if value >= target:
                            formatted_row[col] = f"{Fore.RED}{rate_str}{Style.RESET_ALL}"
                        else:
                            formatted_row[col] = f"{Fore.GREEN}{rate_str}{Style.RESET_ALL}"
                    else:
                        formatted_row[col] = rate_str
                else:
                    formatted_row[col] = value
            elif col == 'Target Rate':
                formatted_row[col] = f"{value:.2f}" if pd.notna(value) else ''
            elif col == '$ Venta (dls)':
                formatted_row[col] = f"${value:,.0f}" if isinstance(value, (int, float)) else value
            else:
                formatted_row[col] = value if value != '' else ''
        
        formatted_rows.append(formatted_row)
    
    # Crear nuevo DataFrame con los valores formateados
    formatted_df = pd.DataFrame(formatted_rows)
    
    # Imprimir reporte formateado
    print("\n" + "="*100)
    print("REPORTE SEMANAL DE SCRAP RATE")
    print("="*100)
    print(formatted_df.to_string(index=False))
    print("="*100 + "\n")


def export_to_console(df, week, year):
    """
    Exporta el reporte a la consola con información adicional
    
    Args:
        df (DataFrame): DataFrame con los datos del reporte
        week (int): Número de semana
        year (int): Año del reporte
    """
    # Función deshabilitada - Los datos ya no se imprimen en consola
    pass