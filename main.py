from ui.app import run_app
from src.utils.logging_config import setup_logging
import logging

def main():
    # Configurar logging (cambiar a DEBUG para más detalles)
    setup_logging(level=logging.INFO)
    
    # Ejecutar aplicación PySide6
    run_app()

if __name__ == "__main__":
    main()