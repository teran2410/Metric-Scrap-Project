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