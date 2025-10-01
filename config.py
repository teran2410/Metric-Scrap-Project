"""
Archivo de configuración para el análisis de Scrap Rate
"""

# ============================================
# CONFIGURACIÓN DE TARGET RATES POR MES
# ============================================
# Formato: mes (1-12): target_rate
TARGET_RATES = {
    1: 0.60,   # Enero
    2: 0.60,   # Febrero
    3: 0.60,   # Marzo
    4: 0.60,   # Abril
    5: 0.60,   # Mayo
    6: 0.60,   # Junio
    7: 0.60,   # Julio
    8: 0.60,   # Agosto
    9: 0.60,   # Septiembre
    10: 0.60,  # Octubre
    11: 0.60,  # Noviembre
    12: 0.60   # Diciembre
}

# ============================================
# RUTAS DE ARCHIVOS
# ============================================
DATA_FILE_PATH = 'data/test pandas.xlsx'
SCRAP_SHEET_NAME = 'Scrap Database'
VENTAS_SHEET_NAME = 'Ventas Database'
HORAS_SHEET_NAME = 'Horas Database'

# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================
APP_TITLE = "Análisis de Scrap Rate"
APP_WIDTH = 400
APP_HEIGHT = 450
APP_THEME = "dark"
APP_COLOR_THEME = "blue"

# ============================================
# CONFIGURACIÓN DE REPORTES
# ============================================
REPORTS_FOLDER = "reports"
TOP_CONTRIBUTORS_COUNT = 10  # Número de principales contribuidores a mostrar