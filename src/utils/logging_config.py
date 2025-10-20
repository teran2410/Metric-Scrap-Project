"""
logging_config.py - configuración centralizada de logging
"""
import logging


def setup_logging(level=logging.INFO):
    """Configura el logging básico para la aplicación."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )
    # Ejemplo: obtener un logger global
    logger = logging.getLogger('metric_scrap')
    return logger
