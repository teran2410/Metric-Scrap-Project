"""
Script de prueba para verificar la diferencia entre reporte mensual y semanal
para la semana 13 de 2025
"""

import pandas as pd
from src.processors.data_loader import load_data

# Cargar datos
print("Cargando datos...\n")
scrap_df, ventas_df, horas_df = load_data()

# Convertir columnas de fecha
scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])

# Convertir scrap a positivo
scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1

# Agregar semana ISO
scrap_df['Week'] = scrap_df['Create Date'].dt.isocalendar().week.astype(int)
scrap_df['Year'] = scrap_df['Create Date'].dt.year
scrap_df['Month'] = scrap_df['Create Date'].dt.month
horas_df['Week'] = horas_df['Trans Date'].dt.isocalendar().week.astype(int)
horas_df['Year'] = horas_df['Trans Date'].dt.year
horas_df['Month'] = horas_df['Trans Date'].dt.month

# Filtrar semana 13 de 2025
print("=" * 80)
print("ANÁLISIS DE LA SEMANA 13 DE 2025")
print("=" * 80)

scrap_w13 = scrap_df[(scrap_df['Week'] == 13) & (scrap_df['Year'] == 2025)]
horas_w13 = horas_df[(horas_df['Week'] == 13) & (horas_df['Year'] == 2025)]

print("\n📅 FECHAS EN SEMANA 13:")
print(f"Scrap - Fechas únicas: {sorted(scrap_w13['Create Date'].dt.date.unique())}")
print(f"Horas - Fechas únicas: {sorted(horas_w13['Trans Date'].dt.date.unique())}")

print("\n📊 MESES INCLUIDOS:")
print(f"Scrap - Meses: {sorted(scrap_w13['Month'].unique())}")
print(f"Horas - Meses: {sorted(horas_w13['Month'].unique())}")

# Calcular totales
total_scrap = scrap_w13['Total Posted'].sum()
total_horas = horas_w13['Actual Hours'].sum()
rate = total_scrap / total_horas if total_horas > 0 else 0

print("\n💰 TOTALES SEMANA 13 (COMPLETA):")
print(f"Scrap: ${total_scrap:,.2f}")
print(f"Horas: {total_horas:,.2f}")
print(f"Rate: {rate:.4f}")

# Ahora verificar solo días de marzo
scrap_w13_marzo = scrap_w13[scrap_w13['Month'] == 3]
horas_w13_marzo = horas_w13[horas_w13['Month'] == 3]

total_scrap_marzo = scrap_w13_marzo['Total Posted'].sum()
total_horas_marzo = horas_w13_marzo['Actual Hours'].sum()
rate_marzo = total_scrap_marzo / total_horas_marzo if total_horas_marzo > 0 else 0

print("\n💰 TOTALES SEMANA 13 (SOLO MARZO):")
print(f"Scrap: ${total_scrap_marzo:,.2f}")
print(f"Horas: {total_horas_marzo:,.2f}")
print(f"Rate: {rate_marzo:.4f}")

print("\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
if rate != rate_marzo:
    print(f"⚠️  HAY DIFERENCIA:")
    print(f"   - Rate completo (todos los días): {rate:.4f}")
    print(f"   - Rate solo marzo: {rate_marzo:.4f}")
    print(f"\n   El reporte mensual está usando: {rate_marzo:.2f}")
    print(f"   El reporte semanal está usando: {rate:.2f}")
else:
    print(f"✅ Ambos rates son iguales: {rate:.4f}")

print("\n" + "=" * 80)
