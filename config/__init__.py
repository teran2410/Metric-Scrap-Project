"""
Config package for Metric Scrap Project
Re-exports all configuration modules for backward compatibility
"""

# Import all from specialized modules
from .colors import *
from .mappings import *
from .targets import *
from .paths import *

__all__ = [
    # Colors
    'COLOR_HEADER', 'COLOR_ROW', 'COLOR_TOTAL', 'COLOR_TEXT',
    'COLOR_BAR', 'COLOR_BAR_EXCEED', 'COLOR_TARGET_LINE', 'COLOR_BG_CONTRIB',
    
    # Mappings
    'DAYS_ES', 'MONTHS_NUM_TO_ES', 'MONTHS_ES_TO_NUM',
    'WEEK_MONTH_MAPPING_2025', 'WEEK_DATE_RANGES_2025',
    'get_week_number_sunday_saturday', 'get_week_number_vectorized',
    
    # Targets
    'TARGET_RATES', 'TARGET_WEEK_RATES',
    
    # Paths
    'DATA_FILE_PATH', 'SCRAP_SHEET_NAME', 'VENTAS_SHEET_NAME', 'HORAS_SHEET_NAME',
    'APP_TITLE', 'APP_WIDTH', 'APP_HEIGHT', 'APP_THEME', 'APP_COLOR_THEME', 'APP_ICON_PATH',
    'REPORTS_FOLDER', 'WEEK_REPORTS_FOLDER', 'MONTHLY_REPORTS_FOLDER',
    'TOP_CONTRIBUTORS_COUNT', 'REASON_CODES'
]
