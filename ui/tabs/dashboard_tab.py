"""
dashboard_tab.py - Tab principal con dashboard de KPIs
Muestra métricas en tiempo real, gráficos de tendencia y alertas
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout,
                             QGroupBox, QSizePolicy, QComboBox, QSpinBox,
                             QDateEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QHorizontalBarSeries
import logging
from datetime import datetime

from ui.widgets import KPICard, MetricCard, AlertCard, TrendChart
from src.analysis.kpi_calculator import calculate_dashboard_kpis, DashboardKPIs

logger = logging.getLogger(__name__)


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
        
        # Sección 2: Gráfico de Tendencia
        trend_section = self._create_trend_section()
        content_layout.addWidget(trend_section)
        
        # Sección 3: Gráficos de barras (Items y Locations)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        items_chart_section = self._create_items_chart_section()
        charts_layout.addWidget(items_chart_section, 1)
        
        locations_chart_section = self._create_locations_chart_section()
        charts_layout.addWidget(locations_chart_section, 1)
        
        content_layout.addLayout(charts_layout)
        
        # Sección 4: Top Contributors y Alertas
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
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
        self.trend_chart.setMinimumHeight(300)
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
            
            # Actualizar KPIs principales
            self._update_main_kpis(kpis)
            
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
            
            logger.info("Dashboard actualizado exitosamente")
            
        except Exception as e:
            logger.error(f"Error actualizando dashboard: {e}", exc_info=True)
    
    def _update_main_kpis(self, kpis: DashboardKPIs):
        """Actualiza las tarjetas de KPIs principales"""
        # Scrap Rate - mantener como decimal (27.50), comparación como %
        rate_color = "#4caf50" if kpis.meets_target else "#f44336"
        self.rate_card.set_value(f"{kpis.current_scrap_rate:.2f}", rate_color)
        
        if kpis.rate_change_pct is not None:
            comparison = f"{abs(kpis.rate_change_pct):.1f}% vs semana anterior"
            # Para scrap rate: si baja es positivo (verde), si sube es negativo (rojo)
            is_improving = kpis.rate_change_pct < 0
            self.rate_card.set_comparison(comparison, is_improving)
        else:
            self.rate_card.set_comparison("Sin datos previos", True)
        
        # Total Scrap - agregar % de diferencia
        self.scrap_card.set_value(f"${kpis.current_total_scrap:,.0f}")
        if kpis.scrap_change_pct is not None:
            scrap_comparison = f"{abs(kpis.scrap_change_pct):.1f}% vs semana anterior"
            scrap_positive = kpis.scrap_change_pct < 0  # Menor es mejor
            self.scrap_card.set_comparison(scrap_comparison, scrap_positive)
        else:
            self.scrap_card.set_comparison("Sin datos previos", True)
        
        # Horas - agregar % de comparación
        self.hours_card.set_value(f"{kpis.current_total_hours:,.0f}")
        if kpis.hours_change_pct is not None:
            hours_comparison = f"{abs(kpis.hours_change_pct):.1f}% vs semana anterior"
            hours_positive = kpis.hours_change_pct > 0  # Mayor es mejor
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
            from src.processors.data_loader import load_data
            from src.analysis.period_kpi_calculator import get_top_items_for_period
            
            # Cargar datos
            scrap_df, _, _, _ = load_data(force_reload=False, validate=False)
            
            # Obtener top items para el periodo
            period_config = getattr(self, 'current_period_data', {"type": "last_week"})
            top_items = get_top_items_for_period(scrap_df, period_config, top_n=10)
            
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
                # Usar solo el código del item para el label
                categories.append(item['item'][:15])
            
            series = QHorizontalBarSeries()
            series.append(bar_set)
            
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
            
            logger.info("Gráfico de items actualizado exitosamente")
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico de items: {e}", exc_info=True)
    
    def _update_locations_chart(self, kpis: DashboardKPIs):
        """Actualiza el gráfico de barras de locations"""
        try:
            from src.processors.data_loader import load_data
            from src.analysis.period_kpi_calculator import get_top_locations_for_period
            
            # Cargar datos
            scrap_df, _, _, _ = load_data(force_reload=False, validate=False)
            
            # Obtener top locations para el periodo
            period_config = getattr(self, 'current_period_data', {"type": "last_week"})
            top_locations = get_top_locations_for_period(scrap_df, period_config, top_n=10)
            
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
                categories.append(location['location'][:20])
            
            series = QHorizontalBarSeries()
            series.append(bar_set)
            
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
