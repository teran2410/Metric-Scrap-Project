from ui.app import ScrapRateApp
from src.utils.logging_config import setup_logging
import logging

def run_app():
    # Configurar logging (cambiar a DEBUG para más detalles)
    setup_logging(level=logging.INFO)
    
    app = ScrapRateApp()
    app.mainloop()

if __name__ == "__main__":
    run_app()