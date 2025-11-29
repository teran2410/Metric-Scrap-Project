"""
dashboard_dialog.py - Diálogo del Dashboard de KPIs
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QThread, Signal
import logging

from ui.tabs.dashboard_tab import DashboardTab
from src.analysis.period_kpi_calculator import calculate_period_kpis
from src.processors.data_loader import load_data

logger = logging.getLogger(__name__)


class DashboardLoadThread(QThread):
    """Thread para cargar datos del dashboard en background"""
    
    finished = Signal(object)  # Emite DashboardKPIs o None
    error = Signal(str)
    
    def __init__(self, period_config=None):
        super().__init__()
        self.period_config = period_config or {"type": "last_week"}
    
    def run(self):
        """Carga datos y calcula KPIs"""
        try:
            logger.info(f"Iniciando carga de datos para dashboard - Periodo: {self.period_config}")
            
            # Cargar datos
            scrap_df, ventas_df, horas_df, _ = load_data(force_reload=False, validate=False)
            
            if scrap_df is None or horas_df is None:
                self.error.emit("No se pudieron cargar los datos")
                return
            
            # Calcular KPIs según el periodo
            kpis = calculate_period_kpis(scrap_df, ventas_df, horas_df, self.period_config)
            
            if kpis is None:
                self.error.emit("No hay datos disponibles para el periodo seleccionado")
                return
            
            self.finished.emit(kpis)
            logger.info("Datos del dashboard cargados exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando datos del dashboard: {e}", exc_info=True)
            self.error.emit(str(e))


class DashboardDialog(QDialog):
    """
    Diálogo modal para mostrar el dashboard de KPIs
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_thread = None
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Dashboard de Scrap Rate")
        self.setMinimumSize(1200, 800)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Dashboard tab
        self.dashboard = DashboardTab(self)
        self.dashboard.refresh_requested.connect(self._load_data)
        layout.addWidget(self.dashboard)
    
    def _load_data(self):
        """Carga datos en background"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.dashboard.show_loading()
        
        # Obtener configuración del periodo desde el dashboard
        period_config = getattr(self.dashboard, 'current_period_data', {"type": "last_week"})
        
        self.load_thread = DashboardLoadThread(period_config)
        self.load_thread.finished.connect(self._on_data_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.start()
    
    def _on_data_loaded(self, kpis):
        """Callback cuando los datos se cargan exitosamente"""
        from src.analysis.period_kpi_calculator import get_period_label
        
        # Actualizar título del grupo de KPIs
        period_label = get_period_label(self.dashboard.current_period_data)
        self.dashboard.kpi_group.setTitle(period_label)
        
        self.dashboard.update_dashboard(kpis)
    
    def _on_load_error(self, error_msg):
        """Callback cuando hay error al cargar"""
        self.dashboard.show_error(error_msg)
        QMessageBox.warning(
            self,
            "Error Cargando Datos",
            f"No se pudieron cargar los datos del dashboard:\n\n{error_msg}"
        )
    
    def closeEvent(self, event):
        """Maneja el cierre del diálogo"""
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.terminate()
            self.load_thread.wait()
        event.accept()
