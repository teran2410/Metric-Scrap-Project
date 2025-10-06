"""
future_tabs.py - Pestañas futuras (Trimestral, Anual)
"""

from ui.tabs.base_tab import BaseTab

class QuarterlyTab(BaseTab):
    """Pestaña para reportes trimestrales (en desarrollo)"""
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña trimestral"""
        self.create_development_message("Módulo en desarrollo")

class CustomTab(BaseTab):
    """Pestaña para reportes con fecha personalizada (en desarrollo)"""
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña personalizada"""
        self.create_development_message("Módulo en desarrollo")