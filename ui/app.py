"""
app.py - Interfaz gráfica principal (modularizada)
"""

import customtkinter as ctk
import os

from ui.tabs.weekly_tab import WeeklyTab
from ui.tabs.monthly_tab import MonthlyTab
from ui.tabs.quarterly_tab import QuarterlyTab
from ui.tabs.annual_tab import AnnualTab
from ui.tabs.custom_tab import CustomTab

from config import (
    APP_TITLE, APP_WIDTH, APP_HEIGHT, 
    APP_THEME, APP_COLOR_THEME, APP_ICON_PATH
)

class ScrapRateApp(ctk.CTk):
    """Aplicación principal para análisis de Scrap Rate"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT + 50}")
        self.resizable(False, False)  # Tamaño fijo
        
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
            font=ctk.CTkFont(size=12, weight="normal", slant="italic"),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # TabView (pestañas)
        self.tabview = ctk.CTkTabview(self, width=360, height=320)
        self.tabview.pack(pady=10, padx=40)

        # Configurar colores de pestañas
        self.tabview.configure(
            segmented_button_selected_color="#2F6690",  # Fondo de pestaña activa
            segmented_button_selected_hover_color="#9DB4C0",  # Color al pasar el mouse
        )
        
        # Agregar pestañas
        self.tabview.add("Semanal")
        self.tabview.add("Mensual")
        self.tabview.add("Trimestral")
        self.tabview.add("Anual")
        self.tabview.add("Personalizado")
        
        # Crear contenido de cada pestaña
        self.create_tabs()
    
    def create_tabs(self):
        """Inicializa todas las pestañas"""
        
        # Pestaña Semanal (terminada)
        weekly_frame = self.tabview.tab("Semanal")
        self.weekly_tab = WeeklyTab(weekly_frame, self)
        
        # Pestaña Mensual (funcional)
        monthly_frame = self.tabview.tab("Mensual")
        self.monthly_tab = MonthlyTab(monthly_frame, self)
        
        # Pestaña Trimestral (funcional)
        quarterly_frame = self.tabview.tab("Trimestral")
        self.quarterly_tab = QuarterlyTab(quarterly_frame, self)
        
        # Pestaña Anual (funcional)
        annual_frame = self.tabview.tab("Anual")
        self.anual_tab = AnnualTab(annual_frame, self)

        # Pestañas personalizada (funcional)
        custom_frame = self.tabview.tab("Personalizado")
        self.custom_tab = CustomTab(custom_frame, self)


def run_app():
    """Ejecuta la aplicación"""
    app = ScrapRateApp()
    app.mainloop()