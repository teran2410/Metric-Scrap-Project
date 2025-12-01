"""
dashboard_tab.py - Tab principal con dashboard de KPIs
Muestra métricas en tiempo real, gráficos de tendencia y alertas
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout,
                             QGroupBox, QSizePolicy, QComboBox, QSpinBox,
                             QDateEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QThread
from PySide6.QtGui import QFont, QColor
from PySide6.QtCharts import (QChart, QChartView, QBarSeries, QBarSet, 
                             QBarCategoryAxis, QValueAxis, QHorizontalBarSeries,
                             QLineSeries, QScatterSeries, QAbstractBarSeries)
import logging
from datetime import datetime

from ui.widgets import KPICard, MetricCard, AlertCard, TrendChart
from src.analysis.kpi_calculator import calculate_dashboard_kpis, DashboardKPIs

logger = logging.getLogger(__name__)


class DataLoaderThread(QThread):
    """Thread para cargar datos en background sin bloquear UI"""
    data_loaded = Signal(object, object, object)  # scrap_df, ventas_df, horas_df
    error_occurred = Signal(str)
    
    def __init__(self, force_reload=False):
        super().__init__()
        self.force_reload = force_reload
    
    def run(self):
        try:
            from src.processors.data_loader import load_data
            logger.info("Iniciando carga de datos en background...")
            scrap_df, ventas_df, horas_df, _ = load_data(force_reload=self.force_reload, validate=False)
            self.data_loaded.emit(scrap_df, ventas_df, horas_df)
            logger.info("Datos cargados exitosamente en background")
        except Exception as e:
            logger.error(f"Error cargando datos en background: {e}", exc_info=True)
            self.error_occurred.emit(str(e))


class DashboardTab(QWidget):
    """
    Tab de Dashboard con KPIs en tiempo real
    """
    
    # Señales
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kpis = None
        self.current_period_type = "week"  # week, month, quarter, year, custom
        self.current_period_data = {}  # Datos del periodo seleccionado
        # Cache de datos para evitar recargas
        self.cached_scrap_df = None
        self.cached_ventas_df = None
        self.cached_horas_df = None
        # Thread de carga
        self.data_loader_thread = None
        self.is_loading = False
        # Flag para saber si los gráficos fijos ya se cargaron
        self.fixed_charts_loaded = False
        self._init_ui()
        logger.info("Dashboard tab inicializado")
    
    def _init_ui(self):
        """Inicializa la interfaz del dashboard"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Panel de filtros de periodo
        filter_panel = self._create_filter_panel()
        main_layout.addWidget(filter_panel)
        
        # Área scrolleable para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Widget contenedor del contenido
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Sección 1: KPIs Principales (3 tarjetas grandes)
        kpi_section = self._create_kpi_section()
        content_layout.addWidget(kpi_section)
        
        # Sección 2: Gráfico de Scrap Rate por Semana (ancho completo para mejor legibilidad)
        weekly_chart_section = self._create_weekly_chart_section()
        content_layout.addWidget(weekly_chart_section)
        
        # Sección 3: Gráficos alineados - Mes y Tendencia (2 columnas)
        temporal_layout = QHBoxLayout()
        temporal_layout.setSpacing(15)
        
        # Gráfico de Scrap Rate por Mes
        monthly_chart_section = self._create_monthly_chart_section()
        temporal_layout.addWidget(monthly_chart_section, 1)
        
        # Gráfico de Tendencia Histórica (alineado con mensual)
        trend_section = self._create_trend_section()
        temporal_layout.addWidget(trend_section, 1)
        
        content_layout.addLayout(temporal_layout)
        
        # Sección 4: Gráficos de barras (Items y Locations en 2 columnas)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        items_chart_section = self._create_items_chart_section()
        charts_layout.addWidget(items_chart_section, 1)
        
        locations_chart_section = self._create_locations_chart_section()
        charts_layout.addWidget(locations_chart_section, 1)
        
        content_layout.addLayout(charts_layout)
        
        # Sección 5: Top Contributors y Alertas (2 columnas)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        contributors_section = self._create_contributors_section()
        bottom_layout.addWidget(contributors_section, 1)
        
        alerts_section = self._create_alerts_section()
        bottom_layout.addWidget(alerts_section, 1)
        
        content_layout.addLayout(bottom_layout)
        
        # Spacer al final
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def _create_header(self) -> QHBoxLayout:
        """Crea el header con título y botón de refresh"""
        layout = QHBoxLayout()
        
        # Título
        title = QLabel("📊 Dashboard de Scrap Rate")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1976d2;
        """)
        layout.addWidget(title)
        
        # Última actualización
        self.last_update_label = QLabel("Última actualización: --")
        self.last_update_label.setStyleSheet("""
            font-size: 11px;
            color: #999;
        """)
        layout.addWidget(self.last_update_label, 0, Qt.AlignRight)
        
        # Botón refresh
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)
        
        return layout
    
    def _create_filter_panel(self) -> QGroupBox:
        """Crea el panel de filtros de periodo"""
        group = QGroupBox("📅 Selección de Periodo")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #1976d2;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #1976d2;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Selector de tipo de periodo
        type_label = QLabel("Periodo:")
        type_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        layout.addWidget(type_label)
        
        self.period_type_combo = QComboBox()
        self.period_type_combo.addItems([
            "Última Semana",
            "Semana Específica",
            "Mes Específico",
            "Trimestre",
            "Año Completo",
            "Rango Personalizado"
        ])
        self.period_type_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 12px;
                min-width: 150px;
                color: #000000;
            }
            QComboBox:hover {
                border-color: #1976d2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)
        self.period_type_combo.currentIndexChanged.connect(self._on_period_type_changed)
        layout.addWidget(self.period_type_combo)
        
        # Separador
        separator = QLabel("|")
        separator.setStyleSheet("color: #666;")
        layout.addWidget(separator)
        
        # Contenedor para selectores específicos
        self.selector_container = QWidget()
        self.selector_layout = QHBoxLayout(self.selector_container)
        self.selector_layout.setContentsMargins(0, 0, 0, 0)
        self.selector_layout.setSpacing(10)
        
        # Selectores para semana
        self.week_label = QLabel("Semana:")
        self.week_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.week_spin = QSpinBox()
        self.week_spin.setRange(1, 52)
        self.week_spin.setValue(1)
        self.week_spin.setStyleSheet("""
            QSpinBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 12px;
                min-width: 60px;
                color: #000000;
            }
        """)
        
        self.week_year_label = QLabel("Año:")
        self.week_year_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.week_year_spin = QSpinBox()
        self.week_year_spin.setRange(2020, 2030)
        self.week_year_spin.setValue(datetime.now().year)
        self.week_year_spin.setStyleSheet(self.week_spin.styleSheet())
        
        # Selectores para mes
        self.month_label = QLabel("Mes:")
        self.month_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        self.month_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 12px;
                min-width: 100px;
                color: #000000;
            }
            QComboBox:hover {
                border-color: #1976d2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)
        
        self.month_year_label = QLabel("Año:")
        self.month_year_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.month_year_spin = QSpinBox()
        self.month_year_spin.setRange(2020, 2030)
        self.month_year_spin.setValue(datetime.now().year)
        self.month_year_spin.setStyleSheet(self.week_spin.styleSheet())
        
        # Selectores para trimestre
        self.quarter_label = QLabel("Trimestre:")
        self.quarter_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems(["Q1", "Q2", "Q3", "Q4"])
        self.quarter_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 12px;
                min-width: 80px;
                color: #000000;
            }
            QComboBox:hover {
                border-color: #1976d2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)
        
        self.quarter_year_label = QLabel("Año:")
        self.quarter_year_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.quarter_year_spin = QSpinBox()
        self.quarter_year_spin.setRange(2020, 2030)
        self.quarter_year_spin.setValue(datetime.now().year)
        self.quarter_year_spin.setStyleSheet(self.week_spin.styleSheet())
        
        # Selector para año
        self.year_label = QLabel("Año:")
        self.year_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(datetime.now().year)
        self.year_spin.setStyleSheet(self.week_spin.styleSheet())
        
        # Selectores para rango personalizado
        self.custom_start_label = QLabel("Desde:")
        self.custom_start_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.custom_start_date = QDateEdit()
        self.custom_start_date.setCalendarPopup(True)
        self.custom_start_date.setDate(QDate.currentDate().addDays(-30))
        self.custom_start_date.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 12px;
                min-width: 100px;
                color: #000000;
            }
        """)
        
        self.custom_end_label = QLabel("Hasta:")
        self.custom_end_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
        self.custom_end_date = QDateEdit()
        self.custom_end_date.setCalendarPopup(True)
        self.custom_end_date.setDate(QDate.currentDate())
        self.custom_end_date.setStyleSheet(self.custom_start_date.styleSheet())
        
        # Ocultar todos inicialmente
        self.week_label.hide()
        self.week_spin.hide()
        self.week_year_label.hide()
        self.week_year_spin.hide()
        self.month_label.hide()
        self.month_combo.hide()
        self.month_year_label.hide()
        self.month_year_spin.hide()
        self.quarter_label.hide()
        self.quarter_combo.hide()
        self.quarter_year_label.hide()
        self.quarter_year_spin.hide()
        self.year_label.hide()
        self.year_spin.hide()
        self.custom_start_label.hide()
        self.custom_start_date.hide()
        self.custom_end_label.hide()
        self.custom_end_date.hide()
        
        layout.addWidget(self.selector_container)
        layout.addStretch()
        
        # Botón aplicar
        self.apply_btn = QPushButton("✓ Aplicar")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.apply_btn.clicked.connect(self._on_apply_filter)
        layout.addWidget(self.apply_btn)
        
        group.setLayout(layout)
        return group
    
    def _on_period_type_changed(self, index):
        """Maneja el cambio de tipo de periodo"""
        # Ocultar todos los selectores
        for widget in [
            self.week_label, self.week_spin, self.week_year_label, self.week_year_spin,
            self.month_label, self.month_combo, self.month_year_label, self.month_year_spin,
            self.quarter_label, self.quarter_combo, self.quarter_year_label, self.quarter_year_spin,
            self.year_label, self.year_spin,
            self.custom_start_label, self.custom_start_date, self.custom_end_label, self.custom_end_date
        ]:
            widget.hide()
        
        # Limpiar layout
        while self.selector_layout.count():
            self.selector_layout.takeAt(0)
        
        # Mostrar selectores según el tipo
        if index == 0:  # Última Semana
            self.current_period_type = "week"
            # No mostrar selectores
        elif index == 1:  # Semana Específica
            self.current_period_type = "week"
            self.selector_layout.addWidget(self.week_label)
            self.selector_layout.addWidget(self.week_spin)
            self.selector_layout.addWidget(self.week_year_label)
            self.selector_layout.addWidget(self.week_year_spin)
            self.week_label.show()
            self.week_spin.show()
            self.week_year_label.show()
            self.week_year_spin.show()
        elif index == 2:  # Mes Específico
            self.current_period_type = "month"
            self.selector_layout.addWidget(self.month_label)
            self.selector_layout.addWidget(self.month_combo)
            self.selector_layout.addWidget(self.month_year_label)
            self.selector_layout.addWidget(self.month_year_spin)
            self.month_label.show()
            self.month_combo.show()
            self.month_year_label.show()
            self.month_year_spin.show()
        elif index == 3:  # Trimestre
            self.current_period_type = "quarter"
            self.selector_layout.addWidget(self.quarter_label)
            self.selector_layout.addWidget(self.quarter_combo)
            self.selector_layout.addWidget(self.quarter_year_label)
            self.selector_layout.addWidget(self.quarter_year_spin)
            self.quarter_label.show()
            self.quarter_combo.show()
            self.quarter_year_label.show()
            self.quarter_year_spin.show()
        elif index == 4:  # Año Completo
            self.current_period_type = "year"
            self.selector_layout.addWidget(self.year_label)
            self.selector_layout.addWidget(self.year_spin)
            self.year_label.show()
            self.year_spin.show()
        elif index == 5:  # Rango Personalizado
            self.current_period_type = "custom"
            self.selector_layout.addWidget(self.custom_start_label)
            self.selector_layout.addWidget(self.custom_start_date)
            self.selector_layout.addWidget(self.custom_end_label)
            self.selector_layout.addWidget(self.custom_end_date)
            self.custom_start_label.show()
            self.custom_start_date.show()
            self.custom_end_label.show()
            self.custom_end_date.show()
    
    def _on_apply_filter(self):
        """Aplica el filtro seleccionado y recarga los datos"""
        try:
            # Guardar configuración del periodo
            period_index = self.period_type_combo.currentIndex()
            
            if period_index == 0:  # Última Semana
                self.current_period_data = {"type": "last_week"}
            elif period_index == 1:  # Semana Específica
                self.current_period_data = {
                    "type": "week",
                    "week": self.week_spin.value(),
                    "year": self.week_year_spin.value()
                }
            elif period_index == 2:  # Mes Específico
                self.current_period_data = {
                    "type": "month",
                    "month": self.month_combo.currentIndex() + 1,
                    "year": self.month_year_spin.value()
                }
            elif period_index == 3:  # Trimestre
                self.current_period_data = {
                    "type": "quarter",
                    "quarter": self.quarter_combo.currentIndex() + 1,
                    "year": self.quarter_year_spin.value()
                }
            elif period_index == 4:  # Año Completo
                self.current_period_data = {
                    "type": "year",
                    "year": self.year_spin.value()
                }
            elif period_index == 5:  # Rango Personalizado
                self.current_period_data = {
                    "type": "custom",
                    "start_date": self.custom_start_date.date().toPython(),
                    "end_date": self.custom_end_date.date().toPython()
                }
            
            logger.info(f"Aplicando filtro: {self.current_period_data}")
            
            # Emitir señal para recargar datos
            self.refresh_requested.emit()
            
        except Exception as e:
            logger.error(f"Error aplicando filtro: {e}", exc_info=True)
    
    def _create_kpi_section(self) -> QGroupBox:
        """Crea la sección de KPIs principales"""
        self.kpi_group = QGroupBox("Última Semana con Datos")
        self.kpi_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Tarjeta 1: Scrap Rate Actual
        self.rate_card = KPICard("Scrap Rate Actual")
        layout.addWidget(self.rate_card, 0, 0)
        
        # Tarjeta 2: Total Scrap
        self.scrap_card = KPICard("Total Scrap ($)")
        layout.addWidget(self.scrap_card, 0, 1)
        
        # Tarjeta 3: Horas Producción
        self.hours_card = KPICard("Horas Producción")
        layout.addWidget(self.hours_card, 0, 2)
        
        # Métricas secundarias
        self.target_metric = MetricCard("Target Semanal")
        layout.addWidget(self.target_metric, 1, 0)
        
        self.sales_metric = MetricCard("Total de Venta")
        layout.addWidget(self.sales_metric, 1, 1)
        
        self.week_metric = MetricCard("Semana Fiscal")
        layout.addWidget(self.week_metric, 1, 2)
        
        self.kpi_group.setLayout(layout)
        return self.kpi_group
    
    def _create_weekly_chart_section(self) -> QGroupBox:
        """Crea la sección de gráfico de Scrap Rate por Semana"""
        group = QGroupBox("Scrap Rate por Semana del Año")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Crear chart
        self.weekly_chart = QChart()
        self.weekly_chart.setTitle("")
        self.weekly_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.weekly_chart.legend().setVisible(True)
        self.weekly_chart.legend().setAlignment(Qt.AlignBottom)
        
        # Chart view
        self.weekly_chart_view = QChartView(self.weekly_chart)
        self.weekly_chart_view.setRenderHint(self.weekly_chart_view.renderHints())
        self.weekly_chart_view.setMinimumHeight(280)
        
        layout.addWidget(self.weekly_chart_view)
        group.setLayout(layout)
        return group
    
    def _create_monthly_chart_section(self) -> QGroupBox:
        """Crea la sección de gráfico de Scrap Rate por Mes"""
        group = QGroupBox("Scrap Rate por Mes del Año")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Crear chart
        self.monthly_chart = QChart()
        self.monthly_chart.setTitle("")
        self.monthly_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.monthly_chart.legend().setVisible(True)
        self.monthly_chart.legend().setAlignment(Qt.AlignBottom)
        
        # Chart view
        self.monthly_chart_view = QChartView(self.monthly_chart)
        self.monthly_chart_view.setRenderHint(self.monthly_chart_view.renderHints())
        self.monthly_chart_view.setMinimumHeight(320)
        
        layout.addWidget(self.monthly_chart_view)
        group.setLayout(layout)
        return group
    
    def _create_trend_section(self) -> QGroupBox:
        """Crea la sección del gráfico de tendencia"""
        group = QGroupBox("Tendencia Histórica")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Gráfico
        self.trend_chart = TrendChart()
        self.trend_chart.setMinimumHeight(320)
        layout.addWidget(self.trend_chart)
        
        group.setLayout(layout)
        return group
    
    def _create_items_chart_section(self) -> QGroupBox:
        """Crea la sección de gráfico de barras por items"""
        group = QGroupBox("Top 10 Items por Scrap ($)")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Crear chart
        self.items_chart = QChart()
        self.items_chart.setTitle("")
        self.items_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.items_chart.legend().setVisible(False)
        
        # Chart view
        self.items_chart_view = QChartView(self.items_chart)
        self.items_chart_view.setRenderHint(self.items_chart_view.renderHints())
        self.items_chart_view.setMinimumHeight(350)
        
        layout.addWidget(self.items_chart_view)
        group.setLayout(layout)
        return group
    
    def _create_locations_chart_section(self) -> QGroupBox:
        """Crea la sección de gráfico de barras por locations"""
        group = QGroupBox("Top 10 Celdas por Scrap ($)")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Crear chart
        self.locations_chart = QChart()
        self.locations_chart.setTitle("")
        self.locations_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.locations_chart.legend().setVisible(False)
        
        # Chart view
        self.locations_chart_view = QChartView(self.locations_chart)
        self.locations_chart_view.setRenderHint(self.locations_chart_view.renderHints())
        self.locations_chart_view.setMinimumHeight(350)
        
        layout.addWidget(self.locations_chart_view)
        group.setLayout(layout)
        return group
    
    def _create_contributors_section(self) -> QGroupBox:
        """Crea la sección de top contributors"""
        group = QGroupBox("Top 3 Contributors")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Labels para los top 3
        self.contributor_labels = []
        for i in range(3):
            label = QLabel(f"{i+1}. --")
            label.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 2px solid #1976d2;
                    border-left: 4px solid #1976d2;
                    border-radius: 4px;
                    padding: 12px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #000000;
                }
            """)
            label.setWordWrap(True)
            self.contributor_labels.append(label)
            layout.addWidget(label)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _create_alerts_section(self) -> QGroupBox:
        """Crea la sección de alertas"""
        group = QGroupBox("Alertas y Notificaciones")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Contenedor para alertas dinámicas
        self.alerts_container = QWidget()
        self.alerts_layout = QVBoxLayout(self.alerts_container)
        self.alerts_layout.setSpacing(8)
        self.alerts_layout.addStretch()
        
        layout.addWidget(self.alerts_container)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def update_dashboard(self, kpis: DashboardKPIs):
        """
        Actualiza todos los componentes del dashboard con nuevos KPIs
        
        Args:
            kpis: Objeto DashboardKPIs con todos los datos
        """
        try:
            logger.info("Actualizando dashboard con nuevos KPIs")
            self.kpis = kpis
            
            # Actualizar KPIs principales inmediatamente (no dependen de DataFrames)
            self._update_main_kpis(kpis)
            
            # Actualizar gráficos dinámicos que dependen del filtro (usan datos del kpis)
            self._update_dynamic_charts(kpis)
            
            # Cargar gráficos fijos (semana/mes del año) solo UNA VEZ en background
            if not self.fixed_charts_loaded and self.cached_scrap_df is None:
                if not self.is_loading:
                    logger.info("Iniciando carga asíncrona de datos para gráficos FIJOS (solo una vez)")
                    self.is_loading = True
                    
                    # Crear y conectar thread
                    self.data_loader_thread = DataLoaderThread(force_reload=False)
                    self.data_loader_thread.data_loaded.connect(self._on_data_loaded)
                    self.data_loader_thread.error_occurred.connect(self._on_data_error)
                    self.data_loader_thread.finished.connect(self._on_thread_finished)
                    self.data_loader_thread.start()
            elif self.cached_scrap_df is not None and not self.fixed_charts_loaded:
                # Datos ya cacheados pero gráficos no cargados
                self._update_fixed_charts()
            
            # Actualizar timestamp
            self.last_update_label.setText(
                f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
        except Exception as e:
            logger.error(f"Error actualizando dashboard: {e}", exc_info=True)
    
    def _on_data_loaded(self, scrap_df, ventas_df, horas_df):
        """Callback cuando los datos se cargan exitosamente en background"""
        logger.info("Datos recibidos del thread, actualizando caché y gráficos FIJOS")
        self.cached_scrap_df = scrap_df
        self.cached_ventas_df = ventas_df
        self.cached_horas_df = horas_df
        
        # Actualizar SOLO los gráficos fijos (semana y mes del año)
        self._update_fixed_charts()
    
    def _on_data_error(self, error_msg):
        """Callback cuando hay error cargando datos"""
        logger.error(f"Error en carga de datos: {error_msg}")
        self.show_error(f"Error cargando datos: {error_msg}")
    
    def _on_thread_finished(self):
        """Callback cuando el thread termina"""
        self.is_loading = False
        logger.info("Thread de carga finalizado")
    
    def _update_fixed_charts(self):
        """Actualiza SOLO los gráficos fijos (semana y mes del año) - se llama UNA SOLA VEZ"""
        try:
            logger.info("Actualizando gráficos FIJOS (semana y mes del año)")
            self._update_weekly_chart()
            self._update_monthly_chart()
            self.fixed_charts_loaded = True
            logger.info("Gráficos fijos cargados exitosamente (no se volverán a cargar)")
        except Exception as e:
            logger.error(f"Error actualizando gráficos fijos: {e}", exc_info=True)
    
    def _update_dynamic_charts(self, kpis: DashboardKPIs):
        """Actualiza los gráficos dinámicos que cambian con cada filtro"""
        try:
            # Actualizar gráfico de tendencia
            self._update_trend_chart(kpis)
            
            # Actualizar gráficos de barras (usan datos cacheados si están disponibles)
            if self.cached_scrap_df is not None:
                self._update_items_chart(kpis)
                self._update_locations_chart(kpis)
            
            # Actualizar top contributors
            self._update_contributors(kpis)
            
            # Actualizar alertas
            self._update_alerts(kpis)
            
            logger.info("Gráficos dinámicos actualizados")
            
        except Exception as e:
            logger.error(f"Error actualizando gráficos dinámicos: {e}", exc_info=True)
    
    def _update_all_charts(self, kpis: DashboardKPIs):
        """Actualiza todos los gráficos con los datos cacheados"""
        try:
            # Actualizar gráficos temporales (semana y mes) - usar datos cacheados
            self._update_weekly_chart()
            self._update_monthly_chart()
            
            # Actualizar gráfico de tendencia
            self._update_trend_chart(kpis)
            
            # Actualizar gráficos de barras
            self._update_items_chart(kpis)
            self._update_locations_chart(kpis)
            
            # Actualizar top contributors
            self._update_contributors(kpis)
            
            # Actualizar alertas
            self._update_alerts(kpis)
            
            # Actualizar timestamp
            from datetime import datetime
            self.last_update_label.setText(
                f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            logger.info("Todos los gráficos actualizados exitosamente")
            
        except Exception as e:
            logger.error(f"Error actualizando gráficos: {e}", exc_info=True)
    
    def _update_main_kpis(self, kpis: DashboardKPIs):
        """Actualiza las tarjetas de KPIs principales"""
        # Scrap Rate - mantener como decimal (27.50), comparación como %
        rate_color = "#4caf50" if kpis.meets_target else "#f44336"
        self.rate_card.set_value(f"{kpis.current_scrap_rate:.2f}", rate_color)
        
        # Obtener el label del periodo (semana, mes, trimestre, año, periodo)
        period_label = kpis.period_label if hasattr(kpis, 'period_label') else "semana"
        periodo_anterior = f"el {period_label} anterior" if period_label != "año" else "el año anterior"
        
        if kpis.rate_change_pct is not None:
            # Para scrap rate: si baja es positivo (verde), si sube es negativo (rojo)
            if kpis.rate_change_pct < 0:
                comparison = f"{abs(kpis.rate_change_pct):.1f}% menos que {periodo_anterior}"
                is_improving = True
            else:
                comparison = f"{abs(kpis.rate_change_pct):.1f}% más que {periodo_anterior}"
                is_improving = False
            # Invertir flecha porque menor scrap es mejor
            self.rate_card.set_comparison(comparison, is_improving, invert_arrow=True)
        else:
            self.rate_card.set_comparison("Sin datos previos", True)
        
        # Total Scrap - agregar % de diferencia
        self.scrap_card.set_value(f"${kpis.current_total_scrap:,.0f}")
        if kpis.scrap_change_pct is not None:
            # Menor scrap es mejor
            if kpis.scrap_change_pct < 0:
                scrap_comparison = f"{abs(kpis.scrap_change_pct):.1f}% menos que {periodo_anterior}"
                scrap_positive = True
            else:
                scrap_comparison = f"{abs(kpis.scrap_change_pct):.1f}% más que {periodo_anterior}"
                scrap_positive = False
            # Invertir flecha porque menor scrap es mejor
            self.scrap_card.set_comparison(scrap_comparison, scrap_positive, invert_arrow=True)
        else:
            self.scrap_card.set_comparison("Sin datos previos", True)
        
        # Horas - agregar % de comparación
        self.hours_card.set_value(f"{kpis.current_total_hours:,.0f}")
        if kpis.hours_change_pct is not None:
            # Mayor horas es mejor
            if kpis.hours_change_pct > 0:
                hours_comparison = f"{abs(kpis.hours_change_pct):.1f}% más que {periodo_anterior}"
                hours_positive = True
            else:
                hours_comparison = f"{abs(kpis.hours_change_pct):.1f}% menos que {periodo_anterior}"
                hours_positive = False
            self.hours_card.set_comparison(hours_comparison, hours_positive)
        else:
            self.hours_card.set_comparison("Sin datos previos", True)
        
        # Métricas secundarias
        # Target - mostrar como decimal (0.5) no como % (50%)
        self.target_metric.set_value(f"{kpis.current_target:.1f}")
        
        # Total de Venta (reemplaza varianza)
        if kpis.total_sales is not None and kpis.total_sales > 0:
            self.sales_metric.set_value(f"${kpis.total_sales:,.0f}")
        else:
            self.sales_metric.set_value("---")
        
        self.week_metric.set_value(f"W{kpis.current_week}")
    
    def _update_trend_chart(self, kpis: DashboardKPIs):
        """Actualiza el gráfico de tendencia"""
        if kpis.historical_weeks:
            self.trend_chart.update_data(kpis.historical_weeks, kpis.current_target)
    
    def _update_weekly_chart(self):
        """Actualiza el gráfico de scrap rate por semana"""
        try:
            from src.analysis.period_kpi_calculator import get_weekly_scrap_rates_for_year
            
            # Usar datos cacheados en lugar de recargar
            if self.cached_scrap_df is None:
                logger.warning("No hay datos cacheados, saltando actualización semanal")
                return
            
            # Obtener año actual o del filtro
            year = self.current_period_data.get('year', datetime.now().year)
            
            # Obtener datos de todas las semanas usando caché
            weekly_data = get_weekly_scrap_rates_for_year(
                self.cached_scrap_df, 
                self.cached_ventas_df, 
                self.cached_horas_df, 
                year
            )
            
            if not weekly_data:
                logger.warning("No hay datos semanales para mostrar")
                return
            
            # Limpiar chart
            self.weekly_chart.removeAllSeries()
            for axis in self.weekly_chart.axes():
                self.weekly_chart.removeAxis(axis)
            
            # Crear series de línea para scrap rate (solo la línea principal)
            rate_series = QLineSeries()
            rate_series.setName("Scrap Rate")
            
            # Series de etiquetas para puntos que CUMPLEN meta (posición ABAJO)
            green_labels = QScatterSeries()
            green_labels.setName("_labels_green")
            green_labels.setMarkerSize(1)  # Invisible
            green_labels.setColor(QColor(0, 0, 0, 0))  # Transparente
            green_labels.setPointLabelsVisible(True)
            green_labels.setPointLabelsFormat("@yPoint")
            green_labels.setPointLabelsColor(QColor("#2e7d32"))
            green_labels.setPointLabelsClipping(False)
            label_font_green = QFont()
            label_font_green.setPointSize(7)
            label_font_green.setBold(True)
            green_labels.setPointLabelsFont(label_font_green)
            
            # Scatter para puntos verdes visibles
            green_scatter = QScatterSeries()
            green_scatter.setName("Cumple Target")
            green_scatter.setMarkerSize(10)
            green_scatter.setColor(QColor("#4caf50"))
            
            # Series de etiquetas para puntos que NO CUMPLEN meta (posición ARRIBA)
            red_labels = QScatterSeries()
            red_labels.setName("_labels_red")
            red_labels.setMarkerSize(1)  # Invisible
            red_labels.setColor(QColor(0, 0, 0, 0))  # Transparente
            red_labels.setPointLabelsVisible(True)
            red_labels.setPointLabelsFormat("@yPoint")
            red_labels.setPointLabelsColor(QColor("#c62828"))
            red_labels.setPointLabelsClipping(False)
            label_font_red = QFont()
            label_font_red.setPointSize(7)
            label_font_red.setBold(True)
            red_labels.setPointLabelsFont(label_font_red)
            
            # Scatter para puntos rojos visibles
            red_scatter = QScatterSeries()
            red_scatter.setName("No Cumple Target")
            red_scatter.setMarkerSize(10)
            red_scatter.setColor(QColor("#f44336"))
            
            # Agregar datos
            has_any_data = False
            for week_data in weekly_data:
                if week_data['has_data']:
                    week = week_data['week']
                    rate = round(week_data['scrap_rate'], 2)  # Redondear a 2 decimales
                    rate_series.append(week, rate)
                    has_any_data = True
                    
                    if week_data['meets_target']:
                        # Cumple: etiqueta abajo (offset negativo en Y - mismo que mensual)
                        green_labels.append(week, rate - 0.15)
                        green_scatter.append(week, rate)
                    else:
                        # No cumple: etiqueta arriba (offset positivo en Y - mismo que mensual)
                        red_labels.append(week, rate + 0.15)
                        red_scatter.append(week, rate)
            
            if not has_any_data:
                logger.warning("No hay datos con valores para graficar semanas")
                return
            
            # Línea de target dinámica (varía según la semana)
            target_series = QLineSeries()
            target_series.setName("Target")
            
            # Agregar punto de target para cada semana
            for week_data in weekly_data:
                week = week_data['week']
                target = week_data['target']
                target_series.append(week, target)
            
            # Estilo de línea de target (punteada)
            pen = target_series.pen()
            pen.setStyle(Qt.DashLine)
            pen.setColor(QColor("#ff9800"))
            pen.setWidth(2)
            target_series.setPen(pen)
            
            # Agregar series al chart (orden importante para z-index)
            self.weekly_chart.addSeries(rate_series)
            self.weekly_chart.addSeries(target_series)
            self.weekly_chart.addSeries(green_scatter)
            self.weekly_chart.addSeries(red_scatter)
            self.weekly_chart.addSeries(green_labels)
            self.weekly_chart.addSeries(red_labels)
            
            # Ocultar de leyenda las series de etiquetas
            self.weekly_chart.legend().markers(green_labels)[0].setVisible(False)
            self.weekly_chart.legend().markers(red_labels)[0].setVisible(False)
            
            # Ejes
            axis_x = QValueAxis()
            axis_x.setTitleText("Semana")
            axis_x.setRange(0.5, len(weekly_data) + 0.5)
            axis_x.setTickCount(min(13, len(weekly_data) + 1))
            axis_x.setLabelFormat("%d")
            axis_x.setLabelsColor("#000000")
            self.weekly_chart.addAxis(axis_x, Qt.AlignBottom)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Scrap Rate (%)")
            rates_with_data = [w['scrap_rate'] for w in weekly_data if w['has_data']]
            targets_with_data = [w['target'] for w in weekly_data if w['has_data']]
            max_rate = max(rates_with_data) if rates_with_data else 1.0
            max_target = max(targets_with_data) if targets_with_data else 0.5
            axis_y.setRange(0, max(max_rate * 1.2, max_target * 1.5))
            axis_y.setLabelFormat("%.1f")
            axis_y.setLabelsColor("#000000")
            self.weekly_chart.addAxis(axis_y, Qt.AlignLeft)
            
            # Attach series to axes
            for series in [rate_series, target_series, green_scatter, red_scatter, green_labels, red_labels]:
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)
            
            self.weekly_chart.setBackgroundBrush(Qt.white)
            
            logger.info(f"Gráfico semanal actualizado con {len(weekly_data)} semanas")
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico semanal: {e}", exc_info=True)
    
    def _update_monthly_chart(self):
        """Actualiza el gráfico de scrap rate por mes"""
        try:
            from src.analysis.period_kpi_calculator import get_monthly_scrap_rates_for_year
            
            # Usar datos cacheados en lugar de recargar
            if self.cached_scrap_df is None:
                logger.warning("No hay datos cacheados, saltando actualización mensual")
                return
            
            # Obtener año actual o del filtro
            year = self.current_period_data.get('year', datetime.now().year)
            
            # Obtener datos de todos los meses usando caché
            monthly_data = get_monthly_scrap_rates_for_year(
                self.cached_scrap_df,
                self.cached_ventas_df,
                self.cached_horas_df,
                year
            )
            
            if not monthly_data:
                logger.warning("No hay datos mensuales para mostrar")
                return
            
            # Limpiar chart
            self.monthly_chart.removeAllSeries()
            for axis in self.monthly_chart.axes():
                self.monthly_chart.removeAxis(axis)
            
            # Crear series de línea para scrap rate (solo la línea principal)
            rate_series = QLineSeries()
            rate_series.setName("Scrap Rate")
            
            # Series de etiquetas para puntos que CUMPLEN meta (posición ABAJO)
            green_labels = QScatterSeries()
            green_labels.setName("_labels_green")
            green_labels.setMarkerSize(1)
            green_labels.setColor(QColor(0, 0, 0, 0))
            green_labels.setPointLabelsVisible(True)
            green_labels.setPointLabelsFormat("@yPoint")
            green_labels.setPointLabelsColor(QColor("#2e7d32"))
            green_labels.setPointLabelsClipping(False)
            label_font_green = QFont()
            label_font_green.setPointSize(9)
            label_font_green.setBold(True)
            green_labels.setPointLabelsFont(label_font_green)
            
            green_scatter = QScatterSeries()
            green_scatter.setName("Cumple Target")
            green_scatter.setMarkerSize(12)
            green_scatter.setColor(QColor("#4caf50"))
            
            # Series de etiquetas para puntos que NO CUMPLEN meta (posición ARRIBA)
            red_labels = QScatterSeries()
            red_labels.setName("_labels_red")
            red_labels.setMarkerSize(1)
            red_labels.setColor(QColor(0, 0, 0, 0))
            red_labels.setPointLabelsVisible(True)
            red_labels.setPointLabelsFormat("@yPoint")
            red_labels.setPointLabelsColor(QColor("#c62828"))
            red_labels.setPointLabelsClipping(False)
            label_font_red = QFont()
            label_font_red.setPointSize(9)
            label_font_red.setBold(True)
            red_labels.setPointLabelsFont(label_font_red)
            
            red_scatter = QScatterSeries()
            red_scatter.setName("No Cumple Target")
            red_scatter.setMarkerSize(12)
            red_scatter.setColor(QColor("#f44336"))
            
            # Agregar datos
            has_any_data = False
            for month_data in monthly_data:
                if month_data['has_data']:
                    month = month_data['month']
                    rate = round(month_data['scrap_rate'], 2)  # Redondear a 2 decimales
                    rate_series.append(month, rate)
                    has_any_data = True
                    
                    if month_data['meets_target']:
                        # Cumple: etiqueta abajo (offset negativo)
                        green_labels.append(month, rate - 0.06)
                        green_scatter.append(month, rate)
                    else:
                        # No cumple: etiqueta arriba (offset positivo)
                        red_labels.append(month, rate + 0.06)
                        red_scatter.append(month, rate)
            
            if not has_any_data:
                logger.warning("No hay datos con valores para graficar")
                return
            
            # Línea de target dinámica (varía según el mes)
            target_series = QLineSeries()
            target_series.setName("Target")
            
            # Agregar punto de target para cada mes
            for month_data in monthly_data:
                month = month_data['month']
                target = month_data['target']
                target_series.append(month, target)
            
            # Estilo de línea de target
            pen = target_series.pen()
            pen.setStyle(Qt.DashLine)
            pen.setColor(QColor("#ff9800"))
            pen.setWidth(2)
            target_series.setPen(pen)
            
            # Agregar series
            self.monthly_chart.addSeries(rate_series)
            self.monthly_chart.addSeries(target_series)
            self.monthly_chart.addSeries(green_scatter)
            self.monthly_chart.addSeries(red_scatter)
            self.monthly_chart.addSeries(green_labels)
            self.monthly_chart.addSeries(red_labels)
            
            # Ocultar de leyenda las series de etiquetas
            self.monthly_chart.legend().markers(green_labels)[0].setVisible(False)
            self.monthly_chart.legend().markers(red_labels)[0].setVisible(False)
            
            # Eje X (valores numéricos 1-12)
            axis_x = QValueAxis()
            axis_x.setTitleText("Mes")
            axis_x.setRange(0.5, len(monthly_data) + 0.5)
            axis_x.setTickCount(len(monthly_data))
            axis_x.setLabelFormat("%d")
            axis_x.setLabelsColor("#000000")
            self.monthly_chart.addAxis(axis_x, Qt.AlignBottom)
            
            # Eje Y
            axis_y = QValueAxis()
            axis_y.setTitleText("Scrap Rate (%)")
            rates_with_data = [m['scrap_rate'] for m in monthly_data if m['has_data']]
            targets_with_data = [m['target'] for m in monthly_data if m['has_data']]
            max_rate = max(rates_with_data) if rates_with_data else 1.0
            max_target = max(targets_with_data) if targets_with_data else 0.5
            axis_y.setRange(0, max(max_rate * 1.2, max_target * 1.5))
            axis_y.setLabelFormat("%.1f")
            axis_y.setLabelsColor("#000000")
            self.monthly_chart.addAxis(axis_y, Qt.AlignLeft)
            
            # Attach series a ambos ejes
            for series in [rate_series, target_series, green_scatter, red_scatter, green_labels, red_labels]:
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)
            
            self.monthly_chart.setBackgroundBrush(Qt.white)
            
            logger.info(f"Gráfico mensual actualizado con {len(monthly_data)} meses")
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico mensual: {e}", exc_info=True)
    
    def _update_contributors(self, kpis: DashboardKPIs):
        """Actualiza la lista de top contributors"""
        for i, label in enumerate(self.contributor_labels):
            if i < len(kpis.top_contributors):
                contrib = kpis.top_contributors[i]
                text = (f"{i+1}. <b>{contrib['item']}</b><br/>"
                       f"   {contrib['description']}<br/>"
                       f"   <b>${contrib['amount']:,.2f}</b> "
                       f"({contrib['percentage']:.1f}%)")
                label.setText(text)
                label.setStyleSheet("""
                    QLabel {
                        background-color: #fff3e0;
                        border-left: 4px solid #ff9800;
                        border-radius: 4px;
                        padding: 12px;
                        font-size: 13px;
                        color: #000000;
                    }
                """)
            else:
                label.setText(f"{i+1}. --")
                label.setStyleSheet("""
                    QLabel {
                        background-color: #f5f5f5;
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        padding: 12px;
                        font-size: 13px;
                        color: #000000;
                    }
                """)
    
    def _update_items_chart(self, kpis: DashboardKPIs):
        """Actualiza el gráfico de barras de items"""
        try:
            from src.analysis.period_kpi_calculator import get_top_items_for_period
            
            # Usar datos cacheados
            if self.cached_scrap_df is None:
                logger.warning("No hay datos cacheados para items")
                return
            
            # Obtener top items para el periodo
            period_config = getattr(self, 'current_period_data', {"type": "last_week"})
            top_items = get_top_items_for_period(self.cached_scrap_df, period_config, top_n=10)
            
            logger.info(f"Top items obtenidos: {len(top_items)}")
            
            if not top_items:
                logger.warning("No hay items para mostrar en el gráfico")
                return
            
            # Limpiar chart anterior
            self.items_chart.removeAllSeries()
            for axis in self.items_chart.axes():
                self.items_chart.removeAxis(axis)
            
            # Crear series horizontal
            bar_set = QBarSet("Scrap Amount")
            bar_set.setColor("#1976d2")
            
            categories = []
            for item in reversed(top_items):  # Revertir para mostrar mayor arriba
                bar_set.append(item['amount'])
                # Solo el código del item en el eje
                categories.append(item['item'][:15])
            
            series = QHorizontalBarSeries()
            series.append(bar_set)
            
            # Habilitar etiquetas en las barras
            bar_set.setLabelColor("#000000")
            series.setLabelsVisible(True)
            series.setLabelsPosition(QAbstractBarSeries.LabelsOutsideEnd)
            series.setLabelsFormat("$@value")
            
            self.items_chart.addSeries(series)
            
            # Eje Y (categorías - items)
            axis_y = QBarCategoryAxis()
            axis_y.append(categories)
            axis_y.setLabelsColor("#000000")
            self.items_chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            # Eje X (valores)
            axis_x = QValueAxis()
            axis_x.setLabelFormat("$%.0f")
            axis_x.setLabelsColor("#000000")
            max_value = max(item['amount'] for item in top_items)
            axis_x.setRange(0, max_value * 1.1)
            self.items_chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            # Estilo
            self.items_chart.setBackgroundBrush(Qt.white)
            
            # Estilo
            self.items_chart.setBackgroundBrush(Qt.white)
            
            logger.info("Gráfico de items actualizado exitosamente")
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico de items: {e}", exc_info=True)
    
    def _update_locations_chart(self, kpis: DashboardKPIs):
        """Actualiza el gráfico de barras de locations"""
        try:
            from src.analysis.period_kpi_calculator import get_top_locations_for_period
            
            # Usar datos cacheados
            if self.cached_scrap_df is None:
                logger.warning("No hay datos cacheados para locations")
                return
            
            # Obtener top locations para el periodo
            period_config = getattr(self, 'current_period_data', {"type": "last_week"})
            top_locations = get_top_locations_for_period(self.cached_scrap_df, period_config, top_n=10)
            
            if not top_locations:
                return
            
            # Limpiar chart anterior
            self.locations_chart.removeAllSeries()
            for axis in self.locations_chart.axes():
                self.locations_chart.removeAxis(axis)
            
            # Crear series horizontal
            bar_set = QBarSet("Scrap Amount")
            bar_set.setColor("#ff9800")
            
            categories = []
            for location in reversed(top_locations):  # Revertir para mostrar mayor arriba
                bar_set.append(location['amount'])
                # Solo el nombre de la celda en el eje
                categories.append(location['location'][:20])
            
            series = QHorizontalBarSeries()
            series.append(bar_set)
            
            # Habilitar etiquetas en las barras
            bar_set.setLabelColor("#000000")
            series.setLabelsVisible(True)
            series.setLabelsPosition(QAbstractBarSeries.LabelsOutsideEnd)
            series.setLabelsFormat("$@value")
            
            self.locations_chart.addSeries(series)
            
            # Eje Y (categorías - locations)
            axis_y = QBarCategoryAxis()
            axis_y.append(categories)
            axis_y.setLabelsColor("#000000")
            self.locations_chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            # Eje X (valores)
            axis_x = QValueAxis()
            axis_x.setLabelFormat("$%.0f")
            axis_x.setLabelsColor("#000000")
            max_value = max(loc['amount'] for loc in top_locations)
            axis_x.setRange(0, max_value * 1.1)
            self.locations_chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            # Estilo
            self.locations_chart.setBackgroundBrush(Qt.white)
            
            # Estilo
            self.locations_chart.setBackgroundBrush(Qt.white)
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico de locations: {e}", exc_info=True)
    
    def _update_alerts(self, kpis: DashboardKPIs):
        """Actualiza las alertas"""
        # Limpiar alertas anteriores
        while self.alerts_layout.count() > 1:  # Mantener el stretch
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Agregar nuevas alertas
        if kpis.alerts:
            for alert in kpis.alerts:
                alert_card = AlertCard(severity=alert['severity'])
                alert_card.set_alert(alert['title'], alert['message'])
                self.alerts_layout.insertWidget(self.alerts_layout.count() - 1, alert_card)
        else:
            # Sin alertas - mostrar mensaje positivo
            no_alert = AlertCard(severity='success')
            no_alert.set_alert(
                "Todo en Orden", 
                "No hay alertas activas en este momento",
                'success'
            )
            self.alerts_layout.insertWidget(0, no_alert)
    
    def show_loading(self):
        """Muestra estado de carga"""
        self.rate_card.set_value("...")
        self.scrap_card.set_value("...")
        self.hours_card.set_value("...")
        self.last_update_label.setText("Cargando datos...")
    
    def show_error(self, message: str):
        """Muestra mensaje de error"""
        self.rate_card.set_value("Error", "#f44336")
        self.rate_card.set_comparison(message, False)
        self.last_update_label.setText("Error al cargar datos")
