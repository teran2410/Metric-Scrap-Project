"""
kpi_card.py - Widgets de tarjetas para mostrar KPIs en el dashboard
"""

from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import logging

logger = logging.getLogger(__name__)


class KPICard(QFrame):
    """
    Tarjeta para mostrar un KPI principal con valor, label y comparación
    """
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz de la tarjeta"""
        # Estilo del frame
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            KPICard {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            KPICard:hover {
                border-color: #1976d2;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Título
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            color: #666;
            font-size: 12px;
            font-weight: normal;
        """)
        layout.addWidget(self.title_label)
        
        # Valor principal
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet("""
            color: #1976d2;
            font-size: 36px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)
        
        # Comparación/cambio
        self.comparison_label = QLabel("")
        self.comparison_label.setStyleSheet("""
            color: #666;
            font-size: 11px;
        """)
        layout.addWidget(self.comparison_label)
        
        layout.addStretch()
    
    def set_value(self, value: str, color: str = "#1976d2"):
        """
        Establece el valor principal
        
        Args:
            value: Texto del valor
            color: Color del valor (hex)
        """
        self.value_label.setText(value)
        self.value_label.setStyleSheet(f"""
            color: {color};
            font-size: 36px;
            font-weight: bold;
        """)
    
    def set_comparison(self, text: str, is_positive: bool = True, invert_arrow: bool = False):
        """
        Establece el texto de comparación
        
        Args:
            text: Texto de comparación
            is_positive: Si es un cambio positivo (verde) o negativo (rojo)
            invert_arrow: Si se debe invertir la dirección de la flecha (para métricas donde menor es mejor)
        """
        color = "#4caf50" if is_positive else "#f44336"
        
        # Para métricas donde menor es mejor (como scrap), invertir la flecha
        if invert_arrow:
            arrow = "↓" if is_positive else "↑"
        else:
            arrow = "↑" if is_positive else "↓"
        
        self.comparison_label.setText(f"{arrow} {text}")
        self.comparison_label.setStyleSheet(f"""
            color: {color};
            font-size: 12px;
            font-weight: bold;
        """)


class MetricCard(QFrame):
    """
    Tarjeta compacta para métricas secundarias
    """
    
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.label_text = label
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz"""
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("""
            MetricCard {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Label
        label = QLabel(self.label_text)
        label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(label)
        
        # Valor
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet("""
            color: #333;
            font-size: 20px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        """Establece el valor de la métrica"""
        self.value_label.setText(value)


class AlertCard(QFrame):
    """
    Tarjeta para mostrar alertas con severidad
    """
    
    SEVERITY_COLORS = {
        'critical': {'bg': '#ffebee', 'border': '#f44336', 'icon': '🔴'},
        'warning': {'bg': '#fff3e0', 'border': '#ff9800', 'icon': '⚠️'},
        'info': {'bg': '#e3f2fd', 'border': '#2196f3', 'icon': 'ℹ️'},
        'success': {'bg': '#e8f5e9', 'border': '#4caf50', 'icon': '✅'}
    }
    
    def __init__(self, severity: str = 'info', parent=None):
        super().__init__(parent)
        self.severity = severity
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz"""
        colors = self.SEVERITY_COLORS.get(self.severity, self.SEVERITY_COLORS['info'])
        
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet(f"""
            AlertCard {{
                background-color: {colors['bg']};
                border-left: 4px solid {colors['border']};
                border-radius: 4px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Icono
        self.icon_label = QLabel(colors['icon'])
        self.icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.icon_label)
        
        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        self.title_label = QLabel("")
        self.title_label.setStyleSheet("""
            color: #333;
            font-size: 13px;
            font-weight: bold;
        """)
        content_layout.addWidget(self.title_label)
        
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("""
            color: #666;
            font-size: 11px;
        """)
        self.message_label.setWordWrap(True)
        content_layout.addWidget(self.message_label)
        
        layout.addLayout(content_layout, 1)
    
    def set_alert(self, title: str, message: str, severity: str = None):
        """
        Establece el contenido de la alerta
        
        Args:
            title: Título de la alerta
            message: Mensaje de la alerta
            severity: Severidad (critical, warning, info, success)
        """
        if severity and severity != self.severity:
            self.severity = severity
            self._init_ui()
        
        self.title_label.setText(title)
        self.message_label.setText(message)


class TrendChart(QChartView):
    """
    Gráfico de línea para mostrar tendencia de scrap rate
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart = QChart()
        self.setChart(self.chart)
        self._init_chart()
    
    def _init_chart(self):
        """Inicializa el gráfico"""
        self.chart.setTitle("Tendencia Scrap Rate (Últimas 4 Semanas)")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        # Estilo
        self.setRenderHint(QPainter.Antialiasing)
        self.chart.setBackgroundBrush(QColor("#ffffff"))
        self.chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
        
        # Sin bordes
        self.setStyleSheet("border: none;")
    
    def update_data(self, weeks_data: list, target_rate: float = 0.25):
        """
        Actualiza los datos del gráfico
        
        Args:
            weeks_data: Lista de WeeklyKPI con datos históricos
            target_rate: Tasa objetivo para línea de referencia
        """
        try:
            # Limpiar series anteriores
            self.chart.removeAllSeries()
            
            # Limpiar ejes anteriores
            for axis in self.chart.axes():
                self.chart.removeAxis(axis)
            
            if not weeks_data:
                return
            
            # Serie de scrap rate
            series = QLineSeries()
            series.setName("Scrap Rate")
            
            for i, week_data in enumerate(weeks_data):
                series.append(i, week_data.scrap_rate)
            
            # Serie de target
            target_series = QLineSeries()
            target_series.setName("Target")
            for i in range(len(weeks_data)):
                target_series.append(i, target_rate)
            
            # Agregar series al gráfico
            self.chart.addSeries(series)
            self.chart.addSeries(target_series)
            
            # Configurar ejes
            axis_x = QValueAxis()
            axis_x.setTitleText("Semana")
            axis_x.setLabelFormat("%d")
            axis_x.setTickCount(len(weeks_data))
            axis_x.setRange(0, len(weeks_data) - 1)
            
            # Eje Y con rango dinámico
            max_rate = max([w.scrap_rate for w in weeks_data] + [target_rate])
            min_rate = min([w.scrap_rate for w in weeks_data] + [target_rate])
            range_padding = (max_rate - min_rate) * 0.2
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Rate")
            axis_y.setLabelFormat("%.2f")
            axis_y.setRange(max(0, min_rate - range_padding), max_rate + range_padding)
            
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            self.chart.addAxis(axis_y, Qt.AlignLeft)
            
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            target_series.attachAxis(axis_x)
            target_series.attachAxis(axis_y)
            
            # Colores
            pen_series = QPen(QColor("#1976d2"))
            pen_series.setWidth(3)
            series.setPen(pen_series)
            
            pen_target = QPen(QColor("#f44336"))
            pen_target.setWidth(2)
            pen_target.setStyle(Qt.DashLine)
            target_series.setPen(pen_target)
            
            logger.info(f"Gráfico actualizado con {len(weeks_data)} semanas de datos")
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico: {e}", exc_info=True)
