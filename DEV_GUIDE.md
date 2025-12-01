# 🚀 GUÍA DE DESARROLLO - Metric Scrap Project

> **Última actualización:** 1 de diciembre de 2025  
> **Arquitectura:** Post-FASE 2 (Modular + Herencia)  
> **Python:** 3.12+ | **Framework GUI:** PySide6 6.10.1  
> **Estado Actual:** Dashboard dinámico con KPIs por periodo + UX refinado

---

## 📝 Historial de Cambios Recientes

### 1 de diciembre de 2025 - Optimización de Backups y UX Mejorada
**Mejoras implementadas:**
- ✅ **Launcher Dialog con Pre-carga de Datos**: Ventana inicial que carga datos en background antes de mostrar opciones de Dashboard o Generador de Reportes
- ✅ **Labels en Gráficos de Barras**: Agregado valores monetarios al final de las barras en gráficos de dashboard (formato $)
- ✅ **Título Dinámico en Gráfico de Tendencia**: Muestra rango de semanas en el título ("Últimas 4 Semanas: Semana 44 a la 47")
- ✅ **Optimización del Sistema de Backups**: Reducido máximo de backups de 10 a 3, agregado diálogo de confirmación para backups manuales
- ✅ **Revertido Análisis Pareto**: Removido intento fallido de coloración 80/20 que rompía los gráficos

**Archivos creados/modificados:**
- `ui/dialogs/launcher_dialog.py` (NUEVO - 320 líneas) - Ventana de selección con pre-carga
- `ui/dialogs/__init__.py` - Exporta LauncherDialog
- `ui/app.py` - Flujo inicial modificado para usar launcher
- `ui/tabs/dashboard_tab.py` - Labels en gráficos de barras (QAbstractBarSeries.LabelsOutsideEnd)
- `ui/widgets/kpi_card.py` - Título dinámico con rango de semanas
- `src/utils/backup_manager.py` - Máximo reducido a 3, parámetro manual=True
- `ui/dialogs/backup_manager_dialog.py` - Diálogo de confirmación para backups manuales

**Próxima mejora planificada:**
- 🚨 **Bug Crítico #22:** Las gráficas de Top 10 no se muestran en "Última Semana" (sí funcionan en "Semana Específica")
  - Prioridad: ALTA
  - Diagnóstico: Diferencia en cálculo de periodo entre auto-detectado vs manual
  - Archivos a revisar: `period_kpi_calculator.py`, `dashboard_tab.py`

---

### 29/11/2025 - Refinamiento de UX Dashboard
**Mejoras implementadas:**
- ✅ Flechas invertidas en KPIs de Scrap (↓ verde = mejora, ↑ roja = empeora)
- ✅ KPI comparisons adaptadas por periodo ("la semana anterior", "el mes anterior", etc.)
- ✅ Etiquetas de valores en puntos de gráficos (2 decimales)
- ✅ Posicionamiento inteligente de etiquetas (dentro/fuera de meta)
- ✅ Líneas de target dinámicas según configuración
- ✅ Carga asíncrona de datos en dashboard (UI no bloqueante)

**Archivos modificados:**
- `ui/widgets/kpi_card.py` - Parámetro `invert_arrow` para invertir dirección de flechas
- `ui/tabs/dashboard_tab.py` - Uso de `invert_arrow=True` en Scrap Rate y Total Scrap
- `src/analysis/kpi_calculator.py` - Campo `period_label` en DashboardKPIs
- `src/analysis/period_kpi_calculator.py` - Labels dinámicos por periodo

**Próxima mejora planificada:**
- 🚀 **Mejora #21:** Ventana de Bienvenida con Pre-carga de Datos (ALTA prioridad)
  - Splash screen con carga en background
  - Singleton GlobalDataStore para compartir datos entre módulos
  - Ventana de selección: Dashboard vs Generador de Reportes
  - Datos pre-cargados para experiencia instantánea

---

## 📋 Tabla de Contenidos

1. [Estructura del Proyecto](#-estructura-del-proyecto)
2. [Arquitectura](#️-arquitectura)
3. [Configuración Modular](#️-configuración-modular)
4. [Sistema de PDF](#-sistema-de-pdf)
5. [Procesadores de Datos](#-procesadores-de-datos)
6. [Análisis y Contribuidores](#-análisis-y-contribuidores)
7. [Dashboard de KPIs](#-dashboard-de-kpis)
8. [Interfaz de Usuario](#-interfaz-de-usuario)
9. [Guía Rápida](#-guía-rápida-de-desarrollo)
10. [Testing](#-testing)
11. [Troubleshooting](#-troubleshooting)

---

## 📁 Estructura del Proyecto

```
Metric-Scrap-Project/
├── main.py                      # Punto de entrada
├── requirements.txt             # Dependencias
├── DEV_GUIDE.md                # Esta guía
│
├── config/                      # ✨ Configuración modular
│   ├── __init__.py             # Exports centralizados
│   ├── colors.py               # Paleta de colores
│   ├── mappings.py             # Traducciones y mapeos
│   ├── targets.py              # Target rates mensuales
│   └── paths.py                # Rutas de archivos
│
├── src/                         # Lógica de negocio
│   ├── pdf/                    # ✨ Sistema PDF modular
│   │   ├── base_generator.py  # Clase base abstracta
│   │   ├── styles.py           # Estilos centralizados
│   │   ├── components.py       # Componentes reutilizables
│   │   └── generators/         # Generadores específicos
│   │       ├── weekly.py
│   │       ├── monthly.py
│   │       ├── quarterly.py
│   │       └── annual.py
│   │
│   ├── processors/             # Procesamiento de datos
│   │   ├── data_loader.py      # Carga de Excel
│   │   ├── weekly_processor.py
│   │   ├── monthly_processor.py
│   │   ├── quarterly_processor.py
│   │   ├── annual_processor.py
│   │   └── custom_processor.py
│   │
│   ├── analysis/               # Análisis de contribuidores y KPIs
│   │   ├── weekly_contributors.py
│   │   ├── monthly_contributors.py
│   │   ├── quarterly_contributors.py
│   │   ├── annual_contributors.py
│   │   ├── custom_contributors.py
│   │   ├── kpi_calculator.py          # ✨ KPIs dashboard (base)
│   │   └── period_kpi_calculator.py   # ✨ KPIs por periodo (dinámico)
│   │
│   ├── utils/                  # Utilidades
│   │   ├── logging_config.py   # Sistema de logs
│   │   ├── cache_manager.py    # Caché de datos
│   │   ├── data_validator.py   # Validación de datos
│   │   ├── exceptions.py       # Excepciones personalizadas
│   │   ├── backup_manager.py   # Sistema de backups
│   │   └── report_history.py   # Historial de reportes
│   │
│   └── pdf_custom_generator.py # Generador custom (legacy)
│
├── ui/                          # Interfaz PySide6
│   ├── app.py                  # Ventana principal
│   ├── theme_manager.py        # Temas claro/oscuro
│   ├── report_thread.py        # Threads para PDFs
│   ├── tabs/                   # Pestañas
│   │   ├── base_tab.py         # Clase base para tabs
│   │   ├── weekly_tab.py
│   │   ├── monthly_tab.py
│   │   ├── quarterly_tab.py
│   │   ├── annual_tab.py
│   │   ├── custom_tab.py
│   │   └── dashboard_tab.py    # ✨ Dashboard de KPIs dinámico
│   ├── widgets/                # ✨ Widgets personalizados
│   │   └── kpi_card.py         # Tarjetas de KPIs, gráficos
│   └── dialogs/                # Diálogos
│       ├── dashboard_dialog.py # ✨ Modal de dashboard
│       ├── validation_report.py # Reporte de validación
│       ├── log_viewer.py       # Visor de logs
│       ├── error_dialog.py     # Diálogo de errores
│       ├── history_dialog.py   # Historial de reportes
│       └── backup_manager_dialog.py # Gestor de backups
│
├── data/                        # Datos de entrada
│   └── test pandas.xlsx        # Excel source
│
├── reports/                     # PDFs generados
│   ├── Scrap_Rate_W*.pdf
│   ├── Scrap_Rate_*.pdf
│   └── Scrap_Rate_Q*.pdf
│
└── assets/                      # Recursos
    └── icon.ico                # Icono de aplicación (.ico o .png)
```

---

## 🏗️ Arquitectura

### Patrón de Diseño

**1. Configuración Modular**
- Config separado por responsabilidad (colors, targets, paths, mappings)
- Imports centralizados en `config/__init__.py`
- Cambios aislados sin efectos secundarios

**2. Herencia para PDFs**
- `BasePDFGenerator` como clase abstracta
- Generadores específicos heredan y especializan
- Código común: 70% reducción de duplicación

**3. Separación de Responsabilidades**
- **Processors:** Transforman datos crudos → DataFrames procesados
- **Analysis:** Calculan contribuidores y métricas
- **PDF Generators:** Transforman DataFrames → Reportes PDF
- **UI:** Orquesta el flujo de trabajo

**4. Threading**
- Generación de PDFs en background (QThread)
- UI responsiva durante procesamiento
- Señales para actualización de progreso

---

## ⚙️ Configuración Modular

### config/colors.py

```python
# Paleta de colores profesional (Azul frío)
COLOR_HEADER = '#2F6690'       # Headers de tablas
COLOR_ROW = '#CFE0F3'          # Filas alternadas
COLOR_TOTAL = '#9DB4C0'        # Fila de totales
COLOR_TEXT = '#333333'         # Texto general
COLOR_BAR = '#3A7CA5'          # Barras de gráficas
COLOR_BAR_EXCEED = '#7D8597'   # Barras que exceden meta
COLOR_TARGET_LINE = '#E9A44C'  # Línea de target
COLOR_BG_CONTRIB = '#E1ECF4'   # Fondo contribuidores
```

**💡 Para cambiar colores globalmente:** Solo edita estos valores.

### config/targets.py

```python
# Target rates por mes (%)
TARGET_RATES = {
    1: 0.50,   # Enero
    2: 0.50,   # Febrero
    3: 0.40,   # Marzo
    4: 0.40,   # Abril
    5: 0.40,   # Mayo
    6: 0.40,   # Junio
    7: 0.40,   # Julio
    8: 0.40,   # Agosto
    9: 0.40,   # Septiembre
    10: 0.40,  # Octubre
    11: 0.40,  # Noviembre
    12: 0.40   # Diciembre
}

# Target semanal global
WEEKLY_TARGET_RATE = 0.50
```

**💡 Para modificar metas:** Cambia estos valores. Se aplican automáticamente en todos los reportes.

### config/paths.py

```python
# Rutas de archivos
DATA_FILE_PATH = "data/test pandas.xlsx"
WEEK_REPORTS_FOLDER = "reports"
APP_ICON_PATH = "assets/icon.ico"  # Formato soportado: .ico, .png (NO .svg)
```

### config/mappings.py

```python
# Traducciones
DAYS_ES = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo",
    4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre",
    10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Funciones de utilidad
def get_month_name(month_num):
    """Obtiene nombre de mes en español"""
    return MONTHS_ES.get(month_num, "")

def get_iso_week(date):
    """Obtiene semana ISO de una fecha"""
    return date.isocalendar()[1]
```

### Uso en Código

```python
# ✅ Importación directa (recomendado)
from config import COLOR_HEADER, TARGET_RATES, DATA_FILE_PATH

# ✅ O por módulo específico
from config.colors import COLOR_HEADER
from config.targets import TARGET_RATES
from config.paths import DATA_FILE_PATH
from config.mappings import get_month_name
```

---

## 📄 Sistema de PDF

### Arquitectura de Herencia

```
BasePDFGenerator (abstracta)
    ├── WeeklyPDFGenerator
    ├── MonthlyPDFGenerator
    ├── QuarterlyPDFGenerator
    └── AnnualPDFGenerator
```

### src/pdf/base_generator.py

**Clase abstracta con funcionalidad común:**

```python
from abc import ABC, abstractmethod

class BasePDFGenerator(ABC):
    """Clase base para todos los generadores PDF"""
    
    def __init__(self, output_folder='reports'):
        self.output_folder = output_folder
        self.elements = []
    
    # ========== MÉTODOS CONCRETOS (Reutilizables) ==========
    
    def _ensure_output_folder(self):
        """Crea carpeta de salida si no existe"""
        os.makedirs(self.output_folder, exist_ok=True)
    
    def _create_document(self, filepath, landscape=False):
        """Crea SimpleDocTemplate con configuración estándar"""
        pagesize = landscape_page if landscape else letter
        return SimpleDocTemplate(
            filepath,
            pagesize=pagesize,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.6*inch,
            bottomMargin=0.4*inch
        )
    
    def _close_matplotlib_figures(self):
        """Cierra todas las figuras matplotlib para liberar memoria"""
        plt.close('all')
    
    def _add_main_title(self, text):
        """Agrega título principal al reporte"""
        from src.pdf.styles import get_title_style
        title = Paragraph(text, get_title_style())
        self.elements.append(title)
    
    def _add_subtitle(self, text):
        """Agrega subtítulo al reporte"""
        from src.pdf.styles import get_subtitle_style
        subtitle = Paragraph(text, get_subtitle_style())
        self.elements.append(subtitle)
    
    def _add_target_header(self, within_target, custom_text=None):
        """Agrega header DENTRO/FUERA DE META"""
        from src.pdf.styles import get_target_header_style
        if custom_text:
            text = custom_text
        else:
            text = "✔ DENTRO DE META" if within_target else "✘ FUERA DE META"
        
        color = colors.green if within_target else colors.red
        header = Paragraph(text, get_target_header_style(color))
        self.elements.append(header)
    
    def _add_section_title(self, text):
        """Agrega título de sección"""
        from src.pdf.styles import get_section_title_style
        section = Paragraph(text, get_section_title_style())
        self.elements.append(section)
    
    def _add_spacer(self, height_inches=0.3):
        """Agrega espacio vertical"""
        self.elements.append(Spacer(1, height_inches * inch))
    
    def _add_page_break(self):
        """Agrega salto de página"""
        self.elements.append(PageBreak())
    
    def build_and_save(self, doc):
        """Construye y guarda el PDF"""
        try:
            doc.build(self.elements)
            logging.info(f"PDF successfully built: {doc.filename}")
            return doc.filename
        except Exception as e:
            logging.error(f"Error building PDF: {e}")
            raise
    
    # ========== MÉTODOS ABSTRACTOS (Implementar en subclases) ==========
    
    @abstractmethod
    def _calculate_target_achievement(self, df):
        """
        Calcula si el periodo cumple con el target
        
        Returns:
            tuple: (within_target: bool, total_rate: float, target_rate: float)
        """
        pass
    
    @abstractmethod
    def _build_main_table_data(self, df, **kwargs):
        """
        Construye los datos de la tabla principal
        
        Returns:
            list: Lista de listas con los datos de la tabla
        """
        pass
    
    @abstractmethod
    def _build_contributors_table_data(self, contributors_df):
        """
        Construye los datos de la tabla de contribuidores
        
        Returns:
            list: Lista de listas con los datos de contribuidores
        """
        pass
```

### src/pdf/styles.py

**Estilos centralizados:**

```python
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from config import COLOR_TEXT

def get_title_style():
    """Estilo para títulos principales"""
    return ParagraphStyle(
        'CustomTitle',
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor(COLOR_TEXT),
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=28
    )

def get_subtitle_style():
    """Estilo para subtítulos"""
    return ParagraphStyle(
        'CustomSubtitle',
        fontSize=11,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )

def get_section_title_style():
    """Estilo para títulos de sección"""
    return ParagraphStyle(
        'SectionTitle',
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor(COLOR_TEXT),
        spaceAfter=12,
        leading=18
    )

def get_target_header_style(color=colors.green):
    """Estilo para header DENTRO/FUERA DE META"""
    return ParagraphStyle(
        'TargetHeader',
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=color,
        alignment=TA_CENTER,
        spaceAfter=15,
        leading=18
    )
```

### src/pdf/components.py

**Componentes reutilizables:**

```python
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from config import (
    COLOR_HEADER, COLOR_ROW, COLOR_TOTAL,
    COLOR_TEXT, COLOR_BAR_EXCEED
)

def get_main_table_style():
    """Estilo estándar para tabla principal"""
    return TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Body
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_ROW)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        
        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        
        # Borders
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(COLOR_HEADER)),
    ])

def get_contributors_table_style():
    """Estilo para tabla de contribuidores"""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(COLOR_HEADER)),
    ])

def apply_rate_conditional_coloring(table_style, data, rate_col_idx=7, target_col_idx=8):
    """
    Aplica color gris a filas donde rate > target
    
    Args:
        table_style: TableStyle a modificar
        data: Lista de datos de la tabla
        rate_col_idx: Índice de columna Rate
        target_col_idx: Índice de columna Target Rate
    """
    for i in range(1, len(data) - 1):  # Excluir header y total
        try:
            rate = float(data[i][rate_col_idx])
            target = float(data[i][target_col_idx])
            if rate > target:
                table_style.add('BACKGROUND', (0, i), (-1, i), 
                               colors.HexColor(COLOR_BAR_EXCEED))
        except (ValueError, IndexError):
            continue

def apply_contributors_cumulative_coloring(table_style, data, cumulative_col_idx=5, threshold=80.0):
    """
    Aplica color rojo tenue hasta alcanzar el threshold acumulado
    
    Args:
        table_style: TableStyle a modificar
        data: Lista de datos de la tabla
        cumulative_col_idx: Índice de columna % Acumulado
        threshold: Porcentaje threshold (default: 80%)
    """
    for i in range(1, len(data) - 1):  # Excluir header y TOTAL
        try:
            cumulative_str = str(data[i][cumulative_col_idx]).replace('%', '').strip()
            cumulative = float(cumulative_str)
            if cumulative <= threshold:
                table_style.add('BACKGROUND', (0, i), (-1, i), 
                               colors.HexColor('#FFCCCC'))
        except (ValueError, IndexError):
            continue
```

---

## 📊 Dashboard de KPIs

### Arquitectura del Dashboard

El sistema de dashboard implementa KPIs dinámicos con filtrado por periodo y visualizaciones interactivas.

### Componentes Principales

**1. src/analysis/kpi_calculator.py** - Cálculos base semanales:
```python
@dataclass
class DashboardKPIs:
    """Estructura de datos del dashboard"""
    current_rate: float
    total_scrap: float
    total_hours: float
    target_rate: float
    variance: float
    week: int
    year: int
    rate_change_pct: float
    scrap_change_abs: float
    hours_change_pct: float
    trend_direction: str
    historical_trend: List[WeeklyKPI]
    top_contributors: List[Dict]
    alerts: List[Dict]

def calculate_dashboard_kpis(scrap_df, ventas_df, horas_df) -> DashboardKPIs:
    """Calcula KPIs de la última semana con datos"""
    # Implementación...
```

**2. src/analysis/period_kpi_calculator.py** - Sistema dinámico por periodo:
```python
def calculate_period_kpis(scrap_df, ventas_df, horas_df, period_config):
    """
    Calcula KPIs para cualquier tipo de periodo
    
    Args:
        period_config: Dict con configuración
            {
                "type": "last_week" | "specific_week" | "month" | "quarter" | "year" | "custom",
                "week": int (si type == "specific_week"),
                "year": int,
                "month": int (si type == "month"),
                "quarter": int (si type == "quarter"),
                "start_date": datetime (si type == "custom"),
                "end_date": datetime (si type == "custom")
            }
    
    Returns:
        DashboardKPIs con datos del periodo seleccionado
    """
    period_type = period_config.get("type", "last_week")
    
    if period_type == "last_week":
        return _calculate_week_kpis(scrap_df, ventas_df, horas_df, None, None)
    elif period_type == "specific_week":
        return _calculate_week_kpis(scrap_df, ventas_df, horas_df, 
                                    period_config["week"], period_config["year"])
    elif period_type == "month":
        return _calculate_month_kpis(scrap_df, ventas_df, horas_df,
                                     period_config["month"], period_config["year"])
    # ... más tipos

def get_top_items_for_period(scrap_df, period_config, top_n=10):
    """Obtiene top N items por scrap para un periodo específico"""
    filtered = _filter_by_period(scrap_df, period_config, 'Posting Date')
    grouped = filtered.groupby('Item').agg({
        'Description': 'first',
        'Total Posted': 'sum'
    }).reset_index()
    return grouped.nlargest(top_n, 'Total Posted').to_dict('records')

def _filter_by_period(df, period_config, date_column='Posting Date'):
    """Función universal de filtrado por periodo"""
    # Implementación para todos los tipos...
```

**3. ui/tabs/dashboard_tab.py** - Interfaz interactiva:
```python
class DashboardTab(QWidget):
    """Tab principal de dashboard con filtros dinámicos"""
    
    refresh_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_period_type = "last_week"
        self.current_period_data = {"type": "last_week"}
        self._init_ui()
    
    def _create_filter_panel(self):
        """Crea panel de filtros dinámicos"""
        # ComboBox con 6 tipos de periodo
        period_types = [
            "Última Semana",
            "Semana Específica", 
            "Mes",
            "Trimestre",
            "Año",
            "Rango Personalizado"
        ]
        self.period_type_combo.addItems(period_types)
        self.period_type_combo.currentIndexChanged.connect(self._on_period_type_changed)
    
    def _on_period_type_changed(self, index):
        """Muestra controles apropiados según tipo seleccionado"""
        # Limpia layout
        self._clear_selector_layout()
        
        if index == 1:  # Semana Específica
            # Agregar spinboxes de semana y año
            pass
        elif index == 2:  # Mes
            # Agregar combobox de mes + spinbox año
            pass
        # ... más casos
    
    def _update_items_chart(self, kpis):
        """Actualiza gráfico de barras de items"""
        from src.analysis.period_kpi_calculator import get_top_items_for_period
        
        top_items = get_top_items_for_period(scrap_df, self.current_period_data, top_n=10)
        
        # Crear QHorizontalBarSeries
        series = QHorizontalBarSeries()
        bar_set = QBarSet("Scrap Amount")
        bar_set.setColor("#1976d2")  # Azul
        
        for item in reversed(top_items):
            bar_set.append(item['amount'])
        
        series.append(bar_set)
        self.items_chart.addSeries(series)
        
        # Configurar ejes
        axis_y = QBarCategoryAxis()  # Códigos de items
        axis_x = QValueAxis()        # Montos USD
        # ...
```

**4. ui/widgets/kpi_card.py** - Componentes visuales:
```python
class KPICard(QFrame):
    """Tarjeta grande para KPIs principales"""
    
    def set_value(self, value, unit="", is_positive=True):
        """Actualiza valor con color dinámico"""
        color = "#4caf50" if is_positive else "#f44336"
        self.value_label.setStyleSheet(f"color: {color}; font-size: 36px;")
        self.value_label.setText(f"{value}{unit}")
    
    def set_comparison(self, change_text, is_positive):
        """Muestra comparación con flecha"""
        arrow = "↑" if is_positive else "↓"
        self.comparison_label.setText(f"{arrow} {change_text}")

class TrendChart(QChartView):
    """Gráfico de línea para tendencia histórica"""
    
    def update_data(self, historical_trend, target_rate):
        """Actualiza series con datos nuevos"""
        # QLineSeries para scrap rate
        # QLineSeries punteada para target
        # ...
```

### Panel de Filtros Dinámico

**Tipos de Periodo Soportados:**

| Tipo | Controles | Comparación vs |
|------|-----------|----------------|
| Última Semana | Ninguno (auto-detecta) | Semana anterior |
| Semana Específica | SpinBox semana (1-52) + año | Semana anterior |
| Mes | ComboBox mes + SpinBox año | Mes anterior |
| Trimestre | ComboBox Q1-Q4 + SpinBox año | Trimestre anterior |
| Año | SpinBox año | Año anterior |
| Rango Personalizado | QDateEdit inicio + fin | Periodo equivalente anterior |

**Flujo de Datos:**
1. Usuario selecciona tipo en ComboBox
2. `_on_period_type_changed()` muestra controles apropiados
3. Usuario configura parámetros y presiona "Aplicar Filtro"
4. `_on_apply_filter()` construye `period_config` Dict
5. Se emite señal `refresh_requested`
6. `DashboardLoadThread` carga datos con `calculate_period_kpis()`
7. Dashboard se actualiza con nuevos KPIs y gráficos

### Gráficos de Análisis

**Top 10 Items por Scrap:**
- Tipo: QHorizontalBarSeries (barras horizontales)
- Color: Azul (#1976d2)
- Eje Y: Códigos de items (QBarCategoryAxis)
- Eje X: Montos USD (QValueAxis con formato "$%.0f")
- Datos: Top 10 items con mayor Total Posted en periodo

**Top 10 Celdas por Scrap:**
- Tipo: QHorizontalBarSeries
- Color: Naranja (#ff9800)
- Eje Y: Nombres de ubicaciones (QBarCategoryAxis)
- Eje X: Montos USD (QValueAxis)
- Datos: Top 10 ubicaciones con mayor scrap en periodo

**Actualización Dinámica:**
- Ambos gráficos se actualizan automáticamente al cambiar periodo
- Usan `get_top_items_for_period()` y `get_top_locations_for_period()`
- Filtrado universal con `_filter_by_period()`

### Sistema de Alertas

```python
def generate_alerts(kpis: DashboardKPIs, historical_trend: List[WeeklyKPI]) -> List[Dict]:
    """Genera alertas automáticas según condiciones"""
    alerts = []
    
    # Critical: Excede target >10%
    if kpis.variance > 0.10:
        alerts.append({
            "severity": "critical",
            "title": "Excede Meta Significativamente",
            "message": f"Scrap rate {kpis.variance:.1%} por encima del target"
        })
    
    # Warning: Tendencia creciente 3+ semanas
    if len(historical_trend) >= 3:
        if all(historical_trend[i].rate > historical_trend[i+1].rate 
               for i in range(len(historical_trend)-1)):
            alerts.append({
                "severity": "warning",
                "title": "Tendencia Creciente",
                "message": "Scrap rate ha aumentado 3+ semanas consecutivas"
            })
    
    # ... más condiciones
    return alerts
```

### Uso del Dashboard

**Desde la UI:**
```python
# ui/app.py

def show_dashboard(self):
    """Abre modal de dashboard"""
    from ui.dialogs import DashboardDialog
    dialog = DashboardDialog(self)
    dialog.exec()
```

**Desde código:**
```python
from src.analysis.period_kpi_calculator import calculate_period_kpis
from src.processors.data_loader import load_data

scrap_df, ventas_df, horas_df, _ = load_data()

# KPIs del último mes
period_config = {
    "type": "month",
    "month": 11,  # Noviembre
    "year": 2025
}

kpis = calculate_period_kpis(scrap_df, ventas_df, horas_df, period_config)

print(f"Scrap Rate: {kpis.current_rate:.2%}")
print(f"vs Mes Anterior: {kpis.rate_change_pct:+.1%}")
print(f"Top Contributor: {kpis.top_contributors[0]}")
```

---

## 💻 Guía Rápida de Desarrollo

### Crear Nuevo Reporte PDF

**Paso 1: Crear clase generadora**

```python
# src/pdf/generators/mi_reporte.py

from src.pdf.base_generator import BasePDFGenerator
from src.pdf.components import get_main_table_style
from reportlab.platypus import Table
import pandas as pd
import os

class MiReportePDFGenerator(BasePDFGenerator):
    """Generador para mi nuevo reporte"""
    
    def _calculate_target_achievement(self, df):
        """Implementar lógica de cumplimiento"""
        total_rate = pd.to_numeric(df['Rate'].iloc[-1], errors='coerce')
        target_rate = 0.5  # ejemplo
        within = total_rate <= target_rate if not pd.isna(total_rate) else False
        return within, total_rate, target_rate
    
    def _build_main_table_data(self, df):
        """Construir datos de tabla principal"""
        data = []
        headers = ['Columna 1', 'Columna 2', 'Columna 3']
        data.append(headers)
        
        for _, row in df.iterrows():
            row_data = [
                str(row['Col1']),
                f"{row['Col2']:.2f}",
                f"${row['Col3']:,.2f}"
            ]
            data.append(row_data)
        
        return data
    
    def _build_contributors_table_data(self, contributors_df):
        """Construir tabla de contribuidores (opcional)"""
        if contributors_df is None:
            return None
        
        data = []
        headers = ['Ranking', 'Parte', 'Cantidad', 'Monto']
        data.append(headers)
        
        for _, row in contributors_df.iterrows():
            data.append([
                str(row['Ranking']),
                str(row['Parte']),
                f"{row['Cantidad']:,.2f}",
                f"${row['Monto']:,.2f}"
            ])
        
        return data
    
    def generate(self, df, contributors_df, periodo, year):
        """Método principal de generación"""
        if df is None:
            return None
        
        # Setup
        self._close_matplotlib_figures()
        self._ensure_output_folder()
        
        filename = f"Mi_Reporte_{periodo}_{year}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        doc = self._create_document(filepath)
        
        self.elements = []
        
        # Contenido
        self._add_main_title("MI NUEVO REPORTE")
        self._add_subtitle(f"Periodo: {periodo} | Año: {year}")
        
        within, _, _ = self._calculate_target_achievement(df)
        self._add_target_header(within)
        
        self._add_spacer()
        
        # Tabla principal
        table_data = self._build_main_table_data(df)
        table = Table(table_data, repeatRows=1)
        table.setStyle(get_main_table_style())
        self.elements.append(table)
        
        # Tabla de contribuidores (opcional)
        if contributors_df is not None:
            self._add_spacer()
            self._add_section_title("PRINCIPALES CONTRIBUIDORES")
            contrib_data = self._build_contributors_table_data(contributors_df)
            contrib_table = Table(contrib_data)
            from src.pdf.components import get_contributors_table_style
            contrib_table.setStyle(get_contributors_table_style())
            self.elements.append(contrib_table)
        
        # Build PDF
        return self.build_and_save(doc)


# Función legacy para compatibilidad
def generate_mi_reporte_pdf(df, contributors_df, periodo, year, output_folder='reports'):
    generator = MiReportePDFGenerator(output_folder)
    return generator.generate(df, contributors_df, periodo, year)
```

**Tiempo estimado:** 30 minutos (vs 2 horas antes)

---

### Modificar Estilos Globales

**Cambiar color de headers en TODOS los reportes:**

```python
# config/colors.py

COLOR_HEADER = '#FF5733'  # Nuevo color rojo
```

**Cambiar tamaño de fuente de títulos:**

```python
# src/pdf/styles.py

def get_title_style():
    return ParagraphStyle(
        'CustomTitle',
        fontSize=28,  # Cambiar de 24 a 28
        # ...resto igual
    )
```

---

### Modificar Targets

```python
# config/targets.py

TARGET_RATES = {
    1: 0.45,   # Enero - cambiar de 0.50 a 0.45
    2: 0.45,   # Febrero
    3: 0.35,   # Marzo - cambiar de 0.40 a 0.35
    # ...
}
```

**Se actualiza automáticamente en:**
- Reportes mensuales
- Reportes trimestrales
- Reportes anuales
- Cálculo DENTRO/FUERA DE META

---

## 🧪 Testing

### Test de Importación

```bash
python -c "from config import COLOR_HEADER; from src.pdf.generators.weekly import WeeklyPDFGenerator; print('✓ OK')"
```

### Test de Generación Weekly

```python
from src.processors.data_loader import load_data
from src.processors.weekly_processor import process_weekly_data
from src.analysis.weekly_contributors import get_weekly_contributors
from src.pdf.generators.weekly import generate_weekly_pdf_report

# Cargar datos
scrap_df, ventas_df, horas_df = load_data()

# Procesar
df = process_weekly_data(scrap_df, ventas_df, horas_df, week=21, year=2025)
contributors = get_weekly_contributors(scrap_df, week=21, year=2025)

# Generar PDF
pdf_path = generate_weekly_pdf_report(df, contributors, 21, 2025)
print(f"✓ PDF generado: {pdf_path}")
```

### Verificar Estructura de Datos

```python
generator = WeeklyPDFGenerator()
table_data = generator._build_main_table_data(df, week=21)

print(f"Headers: {table_data[0]}")
print(f"Rows: {len(table_data) - 1}")
print(f"Sample: {table_data[1]}")
```

---

## 🐛 Troubleshooting

### Error: "Cannot find module 'config'"

```bash
# Verificar estructura
python -c "import sys; print('\n'.join(sys.path))"

# Asegurarse de ejecutar desde raíz del proyecto
cd "path/to/Metric-Scrap-Project"
python main.py
```

### PDF No Genera

```python
# Activar logs debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar permisos carpeta reports
import os
os.makedirs('reports', exist_ok=True)
```

### Estilos No Aplican

```python
# Verificar que uses funciones de src/pdf/styles.py
from src.pdf.styles import get_title_style  # ✓ Correcto
# NO: ParagraphStyle(...) directo
```

### Colores Incorrectos

```python
# Verificar imports
from config import COLOR_HEADER  # ✓ Correcto
from config.colors import COLOR_HEADER  # ✓ También correcto

# Verificar valor
print(f"COLOR_HEADER: {COLOR_HEADER}")
```

---

## 📊 Comparación Pre/Post FASE 2

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Crear reporte nuevo** | 2 horas | 30 minutos |
| **Cambiar color header** | Editar 4 archivos | 1 línea en config/colors.py |
| **Cambiar target rates** | Múltiples lugares | config/targets.py |
| **Agregar función común** | Copy-paste 4 veces | Agregar en BasePDFGenerator |
| **Debugging** | Revisar 4 archivos | Revisar base_generator.py |
| **Consistencia visual** | Manual | Automática |
| **Líneas de código** | ~1200 | ~800 (-33%) |

---

## ✅ Checklist para Nuevos Reportes

- [ ] Crear clase que hereda de `BasePDFGenerator`
- [ ] Implementar `_calculate_target_achievement()`
- [ ] Implementar `_build_main_table_data()`
- [ ] (Opcional) Implementar `_build_contributors_table_data()`
- [ ] Crear método `generate()` con lógica específica
- [ ] Agregar función legacy `generate_*_pdf()` para compatibilidad
- [ ] Importar en `ui/report_thread.py`
- [ ] Agregar case en método `_generate_*()` del thread
- [ ] Test manual de generación
- [ ] Verificar PDF generado visualmente

---

## 📞 Dependencias Clave

```txt
PySide6==6.10.1          # Qt for Python (GUI)
pandas==2.3.3            # Data manipulation
reportlab==4.4.4         # PDF generation
matplotlib==3.10.6       # Charts and graphs
openpyxl==3.1.5          # Excel I/O
```

---

## 🎯 Convenciones de Código

### Naming

- **Clases:** PascalCase (`WeeklyPDFGenerator`)
- **Funciones:** snake_case (`get_weekly_contributors`)
- **Constantes:** UPPER_SNAKE_CASE (`COLOR_HEADER`)
- **Privados:** Prefijo `_` (`_calculate_target_achievement`)

### Imports

```python
# Orden recomendado
import os
import pandas as pd
from datetime import datetime

from reportlab.lib import colors
from reportlab.platypus import Table

from config import COLOR_HEADER, TARGET_RATES
from src.pdf.base_generator import BasePDFGenerator
```

### Docstrings

```python
def process_data(df, year):
    """
    Procesa DataFrame de scrap para un año específico
    
    Args:
        df (pd.DataFrame): DataFrame con datos crudos
        year (int): Año a procesar
        
    Returns:
        pd.DataFrame: DataFrame procesado con métricas calculadas
        
    Raises:
        ValueError: Si el año está fuera de rango
    """
    pass
```

---

**📖 Para más información histórica:** Ver `FASE2_SUMMARY.md` (si existe)

**🔧 Última revisión:** Noviembre 2025
