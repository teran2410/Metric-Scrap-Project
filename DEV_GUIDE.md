# 🚀 GUÍA DE DESARROLLO - Metric Scrap Project

> **Última actualización:** Noviembre 2025  
> **Arquitectura:** Post-FASE 2 (Modular + Herencia)  
> **Python:** 3.12+ | **Framework GUI:** PySide6 6.10.1

---

## 📋 Tabla de Contenidos

1. [Estructura del Proyecto](#-estructura-del-proyecto)
2. [Arquitectura](#️-arquitectura)
3. [Configuración Modular](#️-configuración-modular)
4. [Sistema de PDF](#-sistema-de-pdf)
5. [Procesadores de Datos](#-procesadores-de-datos)
6. [Análisis y Contribuidores](#-análisis-y-contribuidores)
7. [Interfaz de Usuario](#-interfaz-de-usuario)
8. [Guía Rápida](#-guía-rápida-de-desarrollo)
9. [Testing](#-testing)
10. [Troubleshooting](#-troubleshooting)

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
│   ├── analysis/               # Análisis de contribuidores
│   │   ├── weekly_contributors.py
│   │   ├── monthly_contributors.py
│   │   ├── quarterly_contributors.py
│   │   ├── annual_contributors.py
│   │   └── custom_contributors.py
│   │
│   ├── utils/                  # Utilidades
│   │   └── logging_config.py
│   │
│   └── pdf_custom_generator.py # Generador custom (legacy)
│
├── ui/                          # Interfaz PySide6
│   ├── app.py                  # Ventana principal
│   ├── theme_manager.py        # Temas claro/oscuro
│   ├── report_thread.py        # Threads para PDFs
│   └── tabs/                   # Pestañas
│       ├── base_tab.py         # Clase base para tabs
│       ├── weekly_tab.py
│       ├── monthly_tab.py
│       ├── quarterly_tab.py
│       ├── annual_tab.py
│       └── custom_tab.py
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
