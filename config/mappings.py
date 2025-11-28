"""
Mappings and utility functions
Day/month translations, week calculations, and fiscal calendar mappings
"""

import pandas as pd

# ============================================
# Diccionario de traducción de días
# ============================================
DAYS_ES = {
    "Sunday": "Domingo", 
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado"
}

# ========================================================
# Diccionarios de traducción de meses
# ========================================================
# Número de mes (1-12) a nombre en español
MONTHS_NUM_TO_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril", 
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

# Nombre en español a número de mes (1-12) - diccionario inverso
MONTHS_ES_TO_NUM = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12
}

# ================================================================================
# CONFIGURACIÓN DE SEMANAS Y MESES 2025 SEGUN EL CALENDARIO FISCAL DE NAVICOGROUP
# ================================================================================
"""
Las semanas van de DOMINGO a SÁBADO.
Cuando la semana cruza meses, la semana se asigna al mes donde tenga más días de dicha semana.
Ejemplo: semana 05 del 2025 del 26 de enero al 1 de febrero se asigna a Enero porque tiene 6 días en enero y 1 en febrero.
"""
WEEK_MONTH_MAPPING_2025 = {
    1: [1, 2, 3, 4, 5],          # Enero 0.50
    2: [6, 7, 8, 9],             # Febrero 0.50
    3: [10, 11, 12, 13],         # Marzo 0.40
    4: [14, 15, 16, 17, 18],     # Abril 0.30
    5: [19, 20, 21, 22],         # Mayo 0.50
    6: [23, 24, 25, 26],         # Junio 0.50
    7: [27, 28, 29, 30, 31],     # Julio 0.40
    8: [32, 33, 34, 35],         # Agosto 0.50
    9: [36, 37, 38, 39],         # Septiembre 0.60
    10: [40, 41, 42, 43, 44],    # Octubre 0.40
    11: [45, 46, 47, 48],        # Noviembre 0.50
    12: [49, 50, 51, 52, 53]     # Diciembre 0.30
}

# Rango de fechas para cada semana fiscal 2025 (DOMINGO a SÁBADO)
# Formato: semana: (fecha_inicio, fecha_fin)
WEEK_DATE_RANGES_2025 = {
    1: ('2024-12-29', '2025-01-04'),   # Semana 1 - Enero
    2: ('2025-01-05', '2025-01-11'),   # Semana 2 - Enero
    3: ('2025-01-12', '2025-01-18'),   # Semana 3 - Enero
    4: ('2025-01-19', '2025-01-25'),   # Semana 4 - Enero
    5: ('2025-01-26', '2025-02-01'),   # Semana 5 - Febrero
    6: ('2025-02-02', '2025-02-08'),   # Semana 6 - Febrero
    7: ('2025-02-09', '2025-02-15'),   # Semana 7 - Febrero
    8: ('2025-02-16', '2025-02-22'),   # Semana 8 - Febrero
    9: ('2025-02-23', '2025-03-01'),   # Semana 9 - Marzo (cruza feb-mar)
    10: ('2025-03-02', '2025-03-08'),  # Semana 10 - Marzo
    11: ('2025-03-09', '2025-03-15'),  # Semana 11 - Marzo
    12: ('2025-03-16', '2025-03-22'),  # Semana 12 - Marzo
    13: ('2025-03-23', '2025-03-29'),  # Semana 13 - Marzo
    14: ('2025-03-30', '2025-04-05'),  # Semana 14 - Abril
    15: ('2025-04-06', '2025-04-12'),  # Semana 15 - Abril
    16: ('2025-04-13', '2025-04-19'),  # Semana 16 - Abril
    17: ('2025-04-20', '2025-04-26'),  # Semana 17 - Abril
    18: ('2025-04-27', '2025-05-03'),  # Semana 18 - Mayo
    19: ('2025-05-04', '2025-05-10'),  # Semana 19 - Mayo
    20: ('2025-05-11', '2025-05-17'),  # Semana 20 - Mayo
    21: ('2025-05-18', '2025-05-24'),  # Semana 21 - Mayo
    22: ('2025-05-25', '2025-05-31'),  # Semana 22 - Junio
    23: ('2025-06-01', '2025-06-07'),  # Semana 23 - Junio
    24: ('2025-06-08', '2025-06-14'),  # Semana 24 - Junio
    25: ('2025-06-15', '2025-06-21'),  # Semana 25 - Junio
    26: ('2025-06-22', '2025-06-28'),  # Semana 26 - Junio
    27: ('2025-06-29', '2025-07-05'),  # Semana 27 - Julio
    28: ('2025-07-06', '2025-07-12'),  # Semana 28 - Julio
    29: ('2025-07-13', '2025-07-19'),  # Semana 29 - Julio
    30: ('2025-07-20', '2025-07-26'),  # Semana 30 - Julio
    31: ('2025-07-27', '2025-08-02'),  # Semana 31 - Agosto
    32: ('2025-08-03', '2025-08-09'),  # Semana 32 - Agosto
    33: ('2025-08-10', '2025-08-16'),  # Semana 33 - Agosto
    34: ('2025-08-17', '2025-08-23'),  # Semana 34 - Agosto
    35: ('2025-08-24', '2025-08-30'),  # Semana 35 - Septiembre
    36: ('2025-08-31', '2025-09-06'),  # Semana 36 - Septiembre
    37: ('2025-09-07', '2025-09-13'),  # Semana 37 - Septiembre
    38: ('2025-09-14', '2025-09-20'),  # Semana 38 - Septiembre
    39: ('2025-09-21', '2025-09-27'),  # Semana 39 - Septiembre
    40: ('2025-09-28', '2025-10-04'),  # Semana 40 - Octubre
    41: ('2025-10-05', '2025-10-11'),  # Semana 41 - Octubre
    42: ('2025-10-12', '2025-10-18'),  # Semana 42 - Octubre
    43: ('2025-10-19', '2025-10-25'),  # Semana 43 - Octubre
    44: ('2025-10-26', '2025-11-01'),  # Semana 44 - Noviembre
    45: ('2025-11-02', '2025-11-08'),  # Semana 45 - Noviembre
    46: ('2025-11-09', '2025-11-15'),  # Semana 46 - Noviembre
    47: ('2025-11-16', '2025-11-22'),  # Semana 47 - Noviembre
    48: ('2025-11-23', '2025-11-29'),  # Semana 48 - Diciembre
    49: ('2025-11-30', '2025-12-06'),  # Semana 49 - Diciembre
    50: ('2025-12-07', '2025-12-13'),  # Semana 50 - Diciembre
    51: ('2025-12-14', '2025-12-20'),  # Semana 51 - Diciembre
    52: ('2025-12-21', '2025-12-27'),  # Semana 52 - Diciembre
    53: ('2025-12-28', '2026-01-03'),  # Semana 53 - Diciembre
}


# ============================================
# FUNCIÓN PARA CALCULAR SEMANA DOMINGO-SÁBADO
# ============================================
def get_week_number_sunday_saturday(date, year=None):
    """
    Calcula el número de semana usando domingo como primer día de la semana.
    Compatible con el calendario fiscal de NavicoGroup (domingo a sábado).
    
    Para 2025, usa el mapeo fiscal explícito de WEEK_DATE_RANGES_2025.
    Para otros años, usa strftime %U (domingo a sábado).
    
    Args:
        date: fecha (datetime o pandas Timestamp)
        year: año opcional (se extrae de date si no se proporciona)
    
    Returns:
        int: Número de semana (1-53)
    """
    if year is None:
        year = date.year
    
    # Para 2025, usar el mapeo fiscal explícito
    if year == 2025 and WEEK_DATE_RANGES_2025:
        date_only = pd.to_datetime(date).date()
        
        for week_num, (start_str, end_str) in WEEK_DATE_RANGES_2025.items():
            start_date = pd.to_datetime(start_str).date()
            end_date = pd.to_datetime(end_str).date()
            
            if start_date <= date_only <= end_date:
                return week_num
        
        # Si no se encontró en el mapeo, usar fallback
        week_num = int(date.strftime('%U'))
        return week_num if week_num > 0 else 1
    
    # Para otros años, usar strftime %U
    week_num = int(date.strftime('%U'))
    return week_num if week_num > 0 else 1


def get_week_number_vectorized(date_series, year=2025):
    """
    Versión VECTORIZADA y RÁPIDA de get_week_number_sunday_saturday.
    Calcula semanas para toda una Serie de pandas a la vez.
    
    Args:
        date_series: Serie de pandas con fechas
        year: Año (default 2025)
    
    Returns:
        Serie de pandas con números de semana
    """
    import numpy as np
    
    # Para 2025, usar el mapeo fiscal
    if year == 2025 and WEEK_DATE_RANGES_2025:
        # Crear una Serie con valores por defecto
        weeks = pd.Series(1, index=date_series.index, dtype=int)
        
        # Para cada semana en el mapeo, asignar el número de semana
        for week_num, (start_str, end_str) in WEEK_DATE_RANGES_2025.items():
            start_date = pd.to_datetime(start_str)
            end_date = pd.to_datetime(end_str)
            
            # Máscara booleana: TRUE para fechas en este rango
            mask = (date_series >= start_date) & (date_series <= end_date)
            weeks[mask] = week_num
        
        return weeks
    
    # Para otros años, usar strftime %U (vectorizado)
    weeks = date_series.dt.strftime('%U').astype(int)
    weeks = weeks.where(weeks > 0, 1)  # Reemplazar 0 con 1
    return weeks
