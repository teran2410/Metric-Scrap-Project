"""
Target rates configuration for scrap rate analysis
Monthly and weekly targets
"""

# ============================================
# CONFIGURACIÓN DE TARGET RATES POR MES
# ============================================
# Formato: mes (1-12): target_rate
TARGET_RATES = {
    1: 0.50,   # Enero
    2: 0.50,   # Febrero
    3: 0.40,   # Marzo
    4: 0.30,   # Abril
    5: 0.50,   # Mayo
    6: 0.50,   # Junio
    7: 0.40,   # Julio
    8: 0.50,   # Agosto
    9: 0.60,   # Septiembre
    10: 0.40,  # Octubre
    11: 0.50,  # Noviembre
    12: 0.30   # Diciembre
}

# ============================================
# CONFIGURACIÓN DE TARGET RATES POR SEMANA
# ============================================
# Formato: semana (1-53): target_rate
# NOTA: Los valores de las semanas y rates mensuales deben coincidir con WEEK_MONTH_MAPPING_2025
TARGET_WEEK_RATES = {
    # Enero
    1: TARGET_RATES[1], 2: TARGET_RATES[1], 3: TARGET_RATES[1], 4: TARGET_RATES[1], 5: TARGET_RATES[1],
    # Febrero
    6: TARGET_RATES[2], 7: TARGET_RATES[2], 8: TARGET_RATES[2], 9: TARGET_RATES[2],
    # Marzo
    10: TARGET_RATES[3], 11: TARGET_RATES[3], 12: TARGET_RATES[3], 13: TARGET_RATES[3],
    # Abril
    14: TARGET_RATES[4], 15: TARGET_RATES[4], 16: TARGET_RATES[4], 17: TARGET_RATES[4], 18: TARGET_RATES[4],
    # Mayo
    19: TARGET_RATES[5], 20: TARGET_RATES[5], 21: TARGET_RATES[5], 22: TARGET_RATES[5],
    # Junio
    23: TARGET_RATES[6], 24: TARGET_RATES[6], 25: TARGET_RATES[6], 26: TARGET_RATES[6],
    # Julio
    27: TARGET_RATES[7], 28: TARGET_RATES[7], 29: TARGET_RATES[7], 30: TARGET_RATES[7], 31: TARGET_RATES[7],
    # Agosto
    32: TARGET_RATES[8], 33: TARGET_RATES[8], 34: TARGET_RATES[8], 35: TARGET_RATES[8],
    # Septiembre
    36: TARGET_RATES[9], 37: TARGET_RATES[9], 38: TARGET_RATES[9], 39: TARGET_RATES[9],
    # Octubre
    40: TARGET_RATES[10], 41: TARGET_RATES[10], 42: TARGET_RATES[10], 43: TARGET_RATES[10], 44: TARGET_RATES[10],
    # Noviembre
    45: TARGET_RATES[11], 46: TARGET_RATES[11], 47: TARGET_RATES[11], 48: TARGET_RATES[11],
    # Diciembre
    49: TARGET_RATES[12], 50: TARGET_RATES[12], 51: TARGET_RATES[12], 52: TARGET_RATES[12], 53: TARGET_RATES[12]
}
