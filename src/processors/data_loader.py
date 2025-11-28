"""
data_loader.py - Módulo para el procesamiento de datos de Scrap, Ventas y Horas
"""

import pandas as pd
import os
import logging
from config import TARGET_RATES, DATA_FILE_PATH, SCRAP_SHEET_NAME, VENTAS_SHEET_NAME, HORAS_SHEET_NAME
from src.utils.cache_manager import get_cache_manager
from src.utils.exceptions import DataLoadError, DataValidationError
from src.utils.data_validator import validate_data
from src.utils.backup_manager import get_backup_manager

logger = logging.getLogger(__name__)


def load_data(file_path=DATA_FILE_PATH, force_reload=False, validate=True):
    """
    Carga las 3 hojas del archivo Excel usando sistema de caché.
    
    Los datos se mantienen en memoria y solo se recargan si:
    - El archivo ha sido modificado (timestamp diferente)
    - Se fuerza la recarga con force_reload=True
    - Es la primera vez que se carga
    
    Args:
        file_path (str): Ruta del archivo Excel
        force_reload (bool): Si True, fuerza recarga ignorando caché
        validate (bool): Si True, ejecuta validación avanzada de datos
        
    Returns:
        tuple: (scrap_df, ventas_df, horas_df, validation_result)
        
    Raises:
        DataLoadError: Si hay problemas cargando el archivo
        DataValidationError: Si los datos no cumplen el esquema esperado
    """
    logger.info(f"=== Iniciando carga de datos ===")
    logger.info(f"Archivo: {file_path}")
    logger.info(f"Force reload: {force_reload}")
    logger.info(f"Validación: {'Activada' if validate else 'Desactivada'}")
    
    # Validar que el archivo existe
    if not os.path.exists(file_path):
        logger.error(f"❌ Archivo no encontrado: {file_path}")
        raise DataLoadError(
            file_path,
            reason="El archivo no existe en la ubicación especificada"
        )
    
    # Obtener tamaño del archivo
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    logger.info(f"Tamaño del archivo: {file_size_mb:.2f} MB")
    
    # Crear backup automático antes de cargar (solo si se fuerza recarga)
    if force_reload:
        backup_manager = get_backup_manager()
        backup_path = backup_manager.create_backup(file_path)
        if backup_path:
            logger.info(f"✓ Backup automático creado antes de recargar datos")
    
    # Usar cache manager
    cache_manager = get_cache_manager()
    
    try:
        # Intentar obtener desde caché
        logger.debug("Consultando cache_manager...")
        result = cache_manager.get(file_path, force_reload=force_reload)
        
        scrap_df, ventas_df, horas_df = result
        logger.info(f"✓ Scrap: {len(scrap_df)} registros")
        logger.info(f"✓ Ventas: {len(ventas_df)} registros")
        logger.info(f"✓ Horas: {len(horas_df)} registros")
        
        # Validar estructura de datos (validación básica)
        logger.debug("Validando estructura básica de datos...")
        is_valid = validate_data_structure(scrap_df, ventas_df, horas_df)
        if not is_valid:
            raise DataValidationError(
                "La estructura de datos no es válida",
                details="Ejecute validate_data_structure() para ver detalles específicos"
            )
        
        # Validación avanzada (opcional)
        validation_result = None
        if validate:
            logger.info("Ejecutando validación avanzada de datos...")
            validation_result = validate_data(scrap_df, ventas_df, horas_df)
            logger.info(validation_result.get_summary())
        
        logger.info("=== Carga de datos completada exitosamente ===")
        return scrap_df, ventas_df, horas_df, validation_result
        
    except (DataLoadError, DataValidationError):
        # Re-lanzar excepciones personalizadas
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado cargando datos: {str(e)}", exc_info=True)
        raise DataLoadError(
            file_path,
            reason=f"Error inesperado: {str(e)}",
            original_error=e
        )


def clear_data_cache():
    """
    Limpia el caché de datos, forzando recarga en el próximo load_data().
    
    Útil cuando se sabe que el archivo Excel ha sido modificado externamente.
    """
    cache_manager = get_cache_manager()
    cache_manager.clear()
    logger.info("Caché de datos limpiado manualmente")


def validate_data_structure(scrap_df, ventas_df, horas_df):
    """
    Valida que los DataFrames tengan las columnas necesarias
    
    Args:
        scrap_df, ventas_df, horas_df: DataFrames a validar
        
    Returns:
        bool: True si todo está correcto
        
    Raises:
        DataValidationError: Si hay problemas con la estructura de datos
    """
    required_scrap_cols = ['Create Date', 'Total Posted', 'Item', 'Description', 'Location', 'Quantity']
    required_ventas_cols = ['Create Date', 'Total Posted']
    required_horas_cols = ['Trans Date', 'Actual Hours']
    
    issues = []
    
    # Validar Scrap
    if scrap_df is not None:
        missing = [col for col in required_scrap_cols if col not in scrap_df.columns]
        if missing:
            issues.append(f"Hoja '{SCRAP_SHEET_NAME}' - Columnas faltantes: {', '.join(missing)}")
    else:
        issues.append(f"Hoja '{SCRAP_SHEET_NAME}' está vacía o no se pudo cargar")
    
    # Validar Ventas
    if ventas_df is not None:
        missing = [col for col in required_ventas_cols if col not in ventas_df.columns]
        if missing:
            issues.append(f"Hoja '{VENTAS_SHEET_NAME}' - Columnas faltantes: {', '.join(missing)}")
    else:
        issues.append(f"Hoja '{VENTAS_SHEET_NAME}' está vacía o no se pudo cargar")
    
    # Validar Horas
    if horas_df is not None:
        missing = [col for col in required_horas_cols if col not in horas_df.columns]
        if missing:
            issues.append(f"Hoja '{HORAS_SHEET_NAME}' - Columnas faltantes: {', '.join(missing)}")
    else:
        issues.append(f"Hoja '{HORAS_SHEET_NAME}' está vacía o no se pudo cargar")
    
    if issues:
        logger.error(f"Errores de validación: {issues}")
        raise DataValidationError(
            "El archivo no tiene la estructura esperada",
            details=issues
        )
    
    logger.info("Validación de estructura de datos: OK")
    return True