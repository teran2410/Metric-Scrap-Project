"""
future_tabs.py - Pestañas futuras (Mensual, Trimestral, Anual)
"""

from ui.tabs.base_tab import BaseTab

class CustomTab(BaseTab):
    """Pestaña para reportes con fecha personalizada (en desarrollo)"""
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña personalizada"""
        self.create_development_message("Módulo en desarrollo")

class MonthlyTab(BaseTab):
    """Pestaña para reportes mensuales (en desarrollo)"""
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña mensual"""
        self.create_development_message("Módulo en desarrollo")


class QuarterlyTab(BaseTab):
    """Pestaña para reportes trimestrales (en desarrollo)"""
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña trimestral"""
        self.create_development_message("Módulo en desarrollo")


class AnnualTab(BaseTab):
    """Pestaña para reportes anuales (en desarrollo)"""
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña anual"""
        self.create_development_message("Módulo en desarrollo")