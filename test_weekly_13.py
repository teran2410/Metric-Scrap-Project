"""
Script de prueba para simular process_weekly_data de la semana 13
"""

import pandas as pd
from src.processors.data_loader import load_data
from src.processors.weekly_processor import process_weekly_data

# Cargar datos
print("Cargando datos...\n")
scrap_df, ventas_df, horas_df = load_data()

print("\n" + "=" * 80)
print("PROCESANDO SEMANA 13 DE 2025 (usando weekly_processor)")
print("=" * 80)

# Procesar semana 13 (el parámetro es 0-indexed, así que 13 es la semana ISO 13)
result = process_weekly_data(scrap_df, ventas_df, horas_df, 13, 2025)

if result is not None:
    print("\n📊 RESULTADO DEL PROCESSOR SEMANAL (COMPLETO):")
    print(result[['Day', 'D', 'W', 'M', 'Scrap', 'Hrs Prod.', 'Rate']])
    
    print("\n💰 TOTALES:")
    total_row = result[result['Day'] == 'Total']
    if not total_row.empty:
        print(f"Scrap total: ${total_row['Scrap'].values[0]:,.2f}")
        print(f"Horas total: {total_row['Hrs Prod.'].values[0]:,.2f}")
        print(f"Rate total: {total_row['Rate'].values[0]:.4f}")
else:
    print("⚠️  No se encontraron datos")

print("\n" + "=" * 80)
