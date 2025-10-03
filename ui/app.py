"""
app.py - Interfaz gráfica principal (modularizada)
"""

import customtkinter as ctk
import os

from ui.weekly_tab import WeeklyTab
from ui.future_tabs import MonthlyTab, QuarterlyTab, AnnualTab
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_THEME, APP_COLOR_THEME, APP_ICON_PATH


class ScrapRateApp(ctk.CTk):
    """Aplicación principal para análisis de Scrap Rate"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT + 50}")
        
        # Configurar tema
        ctk.set_appearance_mode(APP_THEME)
        ctk.set_default_color_theme(APP_COLOR_THEME)
        
        # Configurar ícono
        self.setup_icon()
        
        # Crear interfaz
        self.create_ui()
    
    def setup_icon(self):
        """Configura el ícono de la aplicación"""
        if os.path.exists(APP_ICON_PATH):
            try:
                self.iconbitmap(APP_ICON_PATH)
            except:
                pass
            
            try:
                self.iconphoto(True, APP_ICON_PATH)
            except:
                pass
    
    def create_ui(self):
        """Crea la interfaz de usuario"""
        
        # Título principal
        title_label = ctk.CTkLabel(
            self, 
            text="Análisis del Métrico de Scrap",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 5))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            self, 
            text="Desarrollado por Oscar Teran",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # TabView (pestañas)
        self.tabview = ctk.CTkTabview(self, width=360, height=320)
        self.tabview.pack(pady=10, padx=40)
        
        # Agregar pestañas
        self.tabview.add("Semanal")
        self.tabview.add("Mensual")
        self.tabview.add("Trimestral")
        self.tabview.add("Anual")
        
        # Crear contenido de cada pestaña
        self.create_tabs()
    
    def create_tabs(self):
        """Inicializa todas las pestañas"""
        
        # Pestaña Semanal (funcional)
        weekly_frame = self.tabview.tab("Semanal")
        self.weekly_tab = WeeklyTab(weekly_frame, self)
        
        # Pestañas futuras (en desarrollo)
        monthly_frame = self.tabview.tab("Mensual")
        self.monthly_tab = MonthlyTab(monthly_frame)
        
        quarterly_frame = self.tabview.tab("Trimestral")
        self.quarterly_tab = QuarterlyTab(quarterly_frame)
        
        annual_frame = self.tabview.tab("Anual")
        self.annual_tab = AnnualTab(annual_frame)


def run_app():
    """Ejecuta la aplicación"""
    app = ScrapRateApp()
    app.mainloop()