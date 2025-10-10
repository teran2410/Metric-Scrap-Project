"""
Config.py Archivo de configuración para el análisis de Scrap Rate
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
TARGET_WEEK_RATES = {
    1: 0.50, 2: 0.50, 3: 0.50, 4: 0.50, # Enero
    5: 0.50, 6: 0.50, 7: 0.50, 8: 0.50, # Febrero
    9: 0.40, 10: 0.40, 11: 0.40, 12: 0.40, 13: 0.40, # Marzo
    14: 0.30, 15: 0.30, 16: 0.30, 17: 0.30, # Abril
    18: 0.50, 19: 0.50, 20: 0.50, 21: 0.50, # Mayo
    22: 0.50, 23: 0.50, 24: 0.50, 25: 0.50, 26: 0.50, # Junio
    27: 0.40, 28: 0.40, 29: 0.40, 30: 0.40, # Julio
    31: 0.50, 32: 0.50, 33: 0.50, 34: 0.50, # Agosto
    35: 0.60, 36: 0.60, 37: 0.60, 38: 0.60, 39: 0.60, # Septiembre
    40: 0.40, 41: 0.40, 42: 0.40, 43: 0.40, # Octubre
    44: 0.50, 45: 0.50, 46: 0.50, 47: 0.50, # Noviembre
    48: 0.30, 49: 0.30, 50: 0.30, 51: 0.30, 52: 0.30, 53: 0.30 # Diciembre
}

# ============================================
# CONFIGURACIÓN DE REASON CODES
# ============================================
REASON_CODES = {
    'SCP': 'SCRAP & REWORK',
    'SCI': 'SCRAP COMM INTERMITTENT BLJCK',
    'SQE': 'SCRAP VENDOR QUALITY ISSUES',
    'CCP': 'CORRECT CONSUMPTION PARTS ACCT',
    'CPS': 'CORRECT PRODUCT SUPPLIES ACCOUNT',
    'CSC': 'CORRECT SCRAP & RW',
    'SDV': 'SCRAP DOUBLE DOWN VALIDATION'
}

# ============================================
# RUTAS DE ARCHIVOS
# ============================================
DATA_FILE_PATH = 'data/test pandas.xlsx'  # Ruta local
# DATA_FILE_PATH = 'H:/Ingenieria/Ing. Procesos/Metricos FA/Metrico Scrap/2025/database.xlsx' # Ruta en red SI FUNCIONA
SCRAP_SHEET_NAME = 'Scrap Database'
VENTAS_SHEET_NAME = 'Ventas Database'
HORAS_SHEET_NAME = 'Horas Database'

# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN 
# ============================================
APP_TITLE = "Scrap Analyzer"
APP_WIDTH = 450
APP_HEIGHT = 450
APP_THEME = "system" # "light", "dark", "system"
APP_COLOR_THEME = "blue" # "blue", "green"
APP_ICON_PATH = "assets/icon.ico"

# ============================================
# CONFIGURACIÓN DE REPORTES
# ============================================
REPORTS_FOLDER = "reports"
TOP_CONTRIBUTORS_COUNT = 10  # Número de principales contribuidores a mostrar