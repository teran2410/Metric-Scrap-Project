"""
logging_config.py - Configuración avanzada de logging con rotación de archivos

Sistema de logging mejorado con:
- Archivos de log con rotación automática (últimos 7 días)
- Formato detallado con timestamp, nivel, módulo y línea
- Niveles configurables por módulo
- Logs en consola y archivo simultáneamente
"""

import logging
import logging.handlers
import os
from datetime import datetime


# Configuración de rutas
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
MAX_BYTES = 10 * 1024 * 1024  # 10 MB por archivo
BACKUP_COUNT = 7  # Mantener últimos 7 archivos


def setup_logging(level=logging.INFO, console_output=True):
    """
    Configura el sistema de logging con rotación de archivos y formato detallado.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Si True, también muestra logs en consola
        
    Returns:
        logging.Logger: Logger raíz configurado
    """
    # Crear carpeta de logs si no existe
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"✓ Carpeta de logs creada: {LOG_DIR}")
    
    # Obtener logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Formato detallado con más información
    detailed_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | Line %(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formato simple para consola
    simple_format = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # ========== HANDLER DE ARCHIVO CON ROTACIÓN ==========
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_format)
        root_logger.addHandler(file_handler)
        
        # Log inicial en archivo
        root_logger.info("="*80)
        root_logger.info("METRIC SCRAP PROJECT - Nueva sesión iniciada")
        root_logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        root_logger.info(f"Nivel de logging: {logging.getLevelName(level)}")
        root_logger.info("="*80)
        
    except Exception as e:
        print(f"⚠️ Error configurando file handler: {e}")
    
    # ========== HANDLER DE CONSOLA ==========
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_format)
        root_logger.addHandler(console_handler)
    
    # ========== CONFIGURAR NIVELES POR MÓDULO ==========
    # Reducir verbosidad de librerías externas
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('reportlab').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger (típicamente __name__)
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)


def get_log_file_path():
    """
    Obtiene la ruta completa del archivo de log actual.
    
    Returns:
        str: Ruta absoluta del archivo de log
    """
    return os.path.abspath(LOG_FILE)


def get_log_directory():
    """
    Obtiene la ruta del directorio de logs.
    
    Returns:
        str: Ruta absoluta del directorio de logs
    """
    return os.path.abspath(LOG_DIR)


def get_all_log_files():
    """
    Obtiene lista de todos los archivos de log (actual + rotados).
    
    Returns:
        list: Lista de rutas de archivos de log, ordenados por fecha (más reciente primero)
    """
    if not os.path.exists(LOG_DIR):
        return []
    
    log_files = []
    for filename in os.listdir(LOG_DIR):
        if filename.startswith('app.log'):
            filepath = os.path.join(LOG_DIR, filename)
            log_files.append(filepath)
    
    # Ordenar por fecha de modificación (más reciente primero)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    return log_files


def read_recent_logs(lines=100):
    """
    Lee las últimas N líneas del log actual.
    
    Args:
        lines: Número de líneas a leer
        
    Returns:
        str: Últimas líneas del log
    """
    try:
        if not os.path.exists(LOG_FILE):
            return "No hay archivo de log disponible."
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return ''.join(recent_lines)
    except Exception as e:
        return f"Error leyendo logs: {str(e)}"

