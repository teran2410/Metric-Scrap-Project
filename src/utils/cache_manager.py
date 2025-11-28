"""
cache_manager.py - Sistema de caché en memoria para DataFrames

Evita recargar datos del Excel si no han cambiado, mejorando significativamente
la velocidad de generación de reportes subsecuentes.
"""

import os
import pandas as pd
from datetime import datetime
import logging
from config import SCRAP_SHEET_NAME, VENTAS_SHEET_NAME, HORAS_SHEET_NAME
from src.utils.exceptions import DataLoadError, CacheError

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestor de caché para DataFrames cargados desde archivos Excel.
    
    Mantiene los datos en memoria y solo recarga si el archivo fuente ha cambiado.
    """
    
    def __init__(self):
        """Inicializa el gestor de caché"""
        self._cache = {}
        logger.info("CacheManager inicializado")
    
    def get(self, file_path, force_reload=False):
        """
        Obtiene datos desde caché o carga desde archivo si es necesario.
        
        Args:
            file_path (str): Ruta al archivo Excel
            force_reload (bool): Si True, fuerza recarga ignorando caché
            
        Returns:
            tuple: (scrap_df, ventas_df, horas_df)
            
        Raises:
            DataLoadError: Si hay problemas cargando el archivo
            CacheError: Si hay problemas con el sistema de caché
        """
        try:
            # Normalizar ruta
            file_path = os.path.abspath(file_path)
            
            # Verificar si archivo existe
            if not os.path.exists(file_path):
                logger.error(f"Archivo no encontrado: {file_path}")
                raise DataLoadError(
                    file_path, 
                    reason="El archivo no existe en la ubicación especificada"
                )
            
            # Obtener timestamp del archivo
            try:
                file_mtime = os.path.getmtime(file_path)
            except OSError as e:
                logger.error(f"Error accediendo al archivo: {e}")
                raise DataLoadError(
                    file_path,
                    reason="No se puede acceder al archivo (permisos insuficientes o archivo bloqueado)",
                    original_error=e
                )
            
            # Verificar si necesitamos recargar
            needs_reload = force_reload
            
            if file_path in self._cache:
                cached_mtime = self._cache[file_path]['mtime']
                if file_mtime > cached_mtime:
                    logger.info(f"Archivo modificado, recargando: {os.path.basename(file_path)}")
                    needs_reload = True
                else:
                    logger.info(f"Usando datos en caché: {os.path.basename(file_path)}")
            else:
                logger.info(f"Primera carga del archivo: {os.path.basename(file_path)}")
                needs_reload = True
            
            # Si necesitamos recargar, cargar desde archivo
            if needs_reload:
                data = self._load_from_file(file_path, file_mtime)
                return data
            
            # Retornar desde caché
            cached_data = self._cache[file_path]['data']
            logger.info(f"Cache hit - DataFrames recuperados de memoria")
            return cached_data
            
        except (DataLoadError, CacheError):
            # Re-lanzar excepciones personalizadas
            raise
        except Exception as e:
            # Capturar cualquier otro error inesperado
            logger.error(f"Error inesperado en CacheManager.get(): {e}", exc_info=True)
            raise CacheError(
                operation="obtener datos",
                reason="Error inesperado al acceder al caché",
                original_error=e
            )
    
    def _load_from_file(self, file_path, file_mtime):
        """
        Carga datos desde archivo Excel y los almacena en caché.
        
        Args:
            file_path (str): Ruta al archivo Excel
            file_mtime (float): Timestamp de modificación del archivo
            
        Returns:
            tuple: (scrap_df, ventas_df, horas_df)
            
        Raises:
            DataLoadError: Si hay problemas leyendo el archivo Excel
        """
        try:
            start_time = datetime.now()
            logger.info(f"Cargando datos desde: {os.path.basename(file_path)}")
            
            # Cargar hojas del Excel usando nombres de configuración
            try:
                scrap_df = pd.read_excel(file_path, sheet_name=SCRAP_SHEET_NAME)
            except ValueError as e:
                raise DataLoadError(
                    file_path,
                    reason=f"Hoja '{SCRAP_SHEET_NAME}' no encontrada en el archivo Excel",
                    original_error=e
                )
            
            try:
                ventas_df = pd.read_excel(file_path, sheet_name=VENTAS_SHEET_NAME)
            except ValueError as e:
                raise DataLoadError(
                    file_path,
                    reason=f"Hoja '{VENTAS_SHEET_NAME}' no encontrada en el archivo Excel",
                    original_error=e
                )
            
            try:
                horas_df = pd.read_excel(file_path, sheet_name=HORAS_SHEET_NAME)
            except ValueError as e:
                raise DataLoadError(
                    file_path,
                    reason=f"Hoja '{HORAS_SHEET_NAME}' no encontrada en el archivo Excel",
                    original_error=e
                )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Datos cargados en {elapsed:.2f} segundos")
            logger.info(f"  - {SCRAP_SHEET_NAME}: {len(scrap_df)} filas")
            logger.info(f"  - {VENTAS_SHEET_NAME}: {len(ventas_df)} filas")
            logger.info(f"  - {HORAS_SHEET_NAME}: {len(horas_df)} filas")
            
            # Guardar en caché
            data = (scrap_df, ventas_df, horas_df)
            self._cache[file_path] = {
                'data': data,
                'mtime': file_mtime,
                'loaded_at': datetime.now()
            }
            
            logger.info(f"Datos almacenados en caché")
            return data
            
        except DataLoadError:
            # Re-lanzar excepciones de carga
            raise
        except Exception as e:
            # Capturar otros errores (formato inválido, archivo corrupto, etc.)
            logger.error(f"Error leyendo archivo Excel: {e}", exc_info=True)
            raise DataLoadError(
                file_path,
                reason=f"El archivo no es un Excel válido o está corrupto: {str(e)}",
                original_error=e
            )
    
    def clear(self, file_path=None):
        """
        Limpia el caché.
        
        Args:
            file_path (str, optional): Si se especifica, limpia solo ese archivo.
                                      Si es None, limpia todo el caché.
        """
        if file_path is None:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Caché completo limpiado ({count} archivos)")
        else:
            file_path = os.path.abspath(file_path)
            if file_path in self._cache:
                del self._cache[file_path]
                logger.info(f"Caché limpiado para: {os.path.basename(file_path)}")
            else:
                logger.warning(f"Archivo no encontrado en caché: {os.path.basename(file_path)}")
    
    def get_cache_info(self):
        """
        Obtiene información sobre el estado actual del caché.
        
        Returns:
            dict: Información del caché con archivos y timestamps
        """
        info = {}
        for file_path, cache_entry in self._cache.items():
            info[os.path.basename(file_path)] = {
                'full_path': file_path,
                'loaded_at': cache_entry['loaded_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'file_modified': datetime.fromtimestamp(cache_entry['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            }
        return info
    
    def is_cached(self, file_path):
        """
        Verifica si un archivo está en caché.
        
        Args:
            file_path (str): Ruta al archivo
            
        Returns:
            bool: True si está en caché, False en caso contrario
        """
        file_path = os.path.abspath(file_path)
        return file_path in self._cache


# Instancia global del cache manager
_cache_manager = CacheManager()


def get_cache_manager():
    """
    Obtiene la instancia global del CacheManager.
    
    Returns:
        CacheManager: Instancia del gestor de caché
    """
    return _cache_manager
