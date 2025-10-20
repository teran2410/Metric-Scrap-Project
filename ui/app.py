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

# Importar report service y adapters si existen
try:
    from src.core.report_service import ReportService
    from src.core.pdf_adapters.weekly_adapter import WeeklyPdfAdapter
    from src.processors.data_loader import load_data as _load_data
    from src.processors.weekly_processor import process_weekly_data as _process_weekly
    from src.analysis.weekly_contributors import get_weekly_contributors as _analyze_weekly
except Exception:
    ReportService = None
    WeeklyPdfAdapter = None
 
try:
    from src.core.pdf_adapters.monthly_adapter import MonthlyPdfAdapter
    from src.processors.monthly_processor import process_monthly_data as _process_monthly
    from src.analysis.monthly_contributors import get_monthly_contributors as _analyze_monthly
except Exception:
    MonthlyPdfAdapter = None
    _process_monthly = None
    _analyze_monthly = None

try:
    from src.core.pdf_adapters.quarterly_adapter import QuarterlyPdfAdapter
    from src.processors.quarterly_processor import process_quarterly_data as _process_quarterly
    from src.analysis.quarterly_contributors import get_quarterly_contributors as _analyze_quarterly
except Exception:
    QuarterlyPdfAdapter = None
    _process_quarterly = None
    _analyze_quarterly = None

try:
    from src.core.pdf_adapters.annual_adapter import AnnualPdfAdapter
    from src.processors.anual_processor import process_anual_data as _process_annual
    from src.analysis.annual_contributors import get_annual_contributors as _analyze_annual
except Exception:
    AnnualPdfAdapter = None
    _process_annual = None
    _analyze_annual = None

try:
    from src.core.pdf_adapters.custom_adapter import CustomPdfAdapter
    from src.processors.custom_processor import process_custom_data as _process_custom
    from src.analysis.custom_contributors import get_custom_contributors as _analyze_custom
except Exception:
    CustomPdfAdapter = None
    _process_custom = None
    _analyze_custom = None

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
        # Si el ReportService está disponible, crear una instancia para inyección
        if ReportService and WeeklyPdfAdapter:
            weekly_adapter = WeeklyPdfAdapter()
            loader = type('Loader', (), {'load_data': staticmethod(_load_data)})()
            service = ReportService(loader, _process_weekly, _analyze_weekly, weekly_adapter)
            self.report_service_weekly = service
        self.weekly_tab = WeeklyTab(weekly_frame, self)
        
        # Pestaña Mensual (funcional)
        monthly_frame = self.tabview.tab("Mensual")
        # Si los componentes para Monthly están disponibles, crear el service
        if ReportService and MonthlyPdfAdapter and _process_monthly and _analyze_monthly:
            monthly_adapter = MonthlyPdfAdapter()
            loader = type('Loader', (), {'load_data': staticmethod(_load_data)})()
            self.report_service_monthly = ReportService(loader, _process_monthly, _analyze_monthly, monthly_adapter)
        self.monthly_tab = MonthlyTab(monthly_frame, self)
        
        # Pestaña Trimestral (funcional)
        quarterly_frame = self.tabview.tab("Trimestral")
        if ReportService and QuarterlyPdfAdapter and _process_quarterly and _analyze_quarterly:
            quarterly_adapter = QuarterlyPdfAdapter()
            loader = type('Loader', (), {'load_data': staticmethod(_load_data)})()
            self.report_service_quarterly = ReportService(loader, _process_quarterly, _analyze_quarterly, quarterly_adapter)
        self.quarterly_tab = QuarterlyTab(quarterly_frame, self)
        
        # Pestaña Anual (funcional)
        annual_frame = self.tabview.tab("Anual")
        if ReportService and AnnualPdfAdapter and _process_annual and _analyze_annual:
            annual_adapter = AnnualPdfAdapter()
            loader = type('Loader', (), {'load_data': staticmethod(_load_data)})()
            self.report_service_annual = ReportService(loader, _process_annual, _analyze_annual, annual_adapter)
        self.anual_tab = AnnualTab(annual_frame, self)

        # Pestañas personalizada (funcional)
        custom_frame = self.tabview.tab("Personalizado")
        if ReportService and CustomPdfAdapter and _process_custom and _analyze_custom:
            custom_adapter = CustomPdfAdapter()
            loader = type('Loader', (), {'load_data': staticmethod(_load_data)})()
            self.report_service_custom = ReportService(loader, _process_custom, _analyze_custom, custom_adapter)
        self.custom_tab = CustomTab(custom_frame, self)


def run_app():
    """Ejecuta la aplicación"""
    app = ScrapRateApp()
    app.mainloop()