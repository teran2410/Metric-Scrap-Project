"""
Paths and application configuration
File paths, folder locations, and app settings
"""

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
APP_TITLE = "Metric Scrap System"
APP_WIDTH = 1200
APP_HEIGHT = 1200
APP_THEME = "system"  # "light", "dark", "system"
APP_COLOR_THEME = "blue"  # "blue", "green"
APP_ICON_PATH = "assets/icon.ico"  # Formato soportado: .ico, .png (NO .svg)

# ============================================
# CONFIGURACIÓN DE REPORTES
# ============================================
REPORTS_FOLDER = "reports"
WEEK_REPORTS_FOLDER = "H:/Ingenieria/Ing. Procesos/Metricos FA/Metrico Scrap/2025/reportes/semanales"
MONTHLY_REPORTS_FOLDER = "H:/Ingenieria/Ing. Procesos/Metricos FA/Metrico Scrap/2025/reportes/mensuales"
QUARTERLY_REPORTS_FOLDER = "H:/Ingenieria/Ing. Procesos/Metricos FA/Metrico Scrap/2025/reportes/trimestrales"
ANNUAL_REPORTS_FOLDER = "H:/Ingenieria/Ing. Procesos/Metricos FA/Metrico Scrap/2025/reportes/anuales"
CUSTOM_REPORTS_FOLDER = "H:/Ingenieria/Ing. Procesos/Metricos FA/Metrico Scrap/2025/reportes/custom"
TOP_CONTRIBUTORS_COUNT = 10  # Número de principales contribuidores a mostrar

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
