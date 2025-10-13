"""
pdf_weekly_generator.py - Módulo para la generación de reportes en PDF (versión mejorada visualmente con paleta fría)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os
import matplotlib
matplotlib.use("Agg") # Usar backend no interactivo
import matplotlib.pyplot as plt
from config import WEEK_REPORTS_FOLDER

# ============================================
# Paleta fría profesional
# ============================================
COLOR_HEADER = '#2F6690'       # Azul acero
COLOR_ROW = '#CFE0F3'          # Azul claro
COLOR_TOTAL = '#9DB4C0'        # Azul grisáceo
COLOR_TEXT = '#333333'         # Gris carbón
COLOR_BAR = '#3A7CA5'          # Azul petróleo
COLOR_BAR_EXCEED = '#7D8597'   # Gris azulado
COLOR_TARGET_LINE = '#E9A44C'  # Naranja ámbar (contraste)
COLOR_BG_CONTRIB = '#E1ECF4'   # Azul muy claro para contribuidores

# Diccionario de traducción de días
DAYS_ES = {
    "Sunday": "Domingo", 
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado"
}

# Diccionario de traducción de meses con formato %b
MONTHS_NUM_TO_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril", 
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

def generate_weekly_pdf_report(df, contributors_df, week, year, scrap_df=None, locations_df=None, output_folder=WEEK_REPORTS_FOLDER):
    """
    Genera un PDF con el reporte de Scrap Rate y principales contribuidores
    """
    if df is None:
        return None

    # Crear carpeta de reportes si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Nombre del archivo
    filename = f"Scrap_Rate_W{week}_{year}.pdf"
    filepath = os.path.join(output_folder, filename)

    # Crear documento base
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    # Contenedor de elementos
    elements = []

    # ==============================
    # Estilos del documento
    # ==============================
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(COLOR_TEXT),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=10,
        alignment=TA_CENTER
    )

    # ==============================
    # Encabezado principal
    # ==============================
    title = Paragraph("REPORTE SEMANAL DEL MÉTRICO DE SCRAP", title_style)
    elements.append(title)

    subtitle_text = f"Semana {week} | Año {year} | Reporte generado automáticamente por Metric Scrap System – © 2025 Oscar Teran"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * inch))

    # ========================================================================================
    # PRIMERA TABLA: REPORTE SEMANAL
    # ========================================================================================
    data = []
    headers = ['Día', 'N° Día', 'Semana', 'Mes', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
    data.append(headers)

    for index, row in df.iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]
            if col == 'Scrap':
                row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
            elif col in ['Hrs Prod.', 'Rate', 'Target Rate']:
                row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == '$ Venta (dls)':
                row_data.append(f"${value:,.0f}" if isinstance(value, (int, float)) else str(value))
            elif col == 'M':
            # Si el valor es numérico, traducir a mes
                if isinstance(value, (int, float)):
                    row_data.append(MONTHS_NUM_TO_ES.get(int(value), str(value)))
                else:
                    row_data.append(str(value) if value != '' else '')
            else:
                # Traducción de los días si aplica
                if col == 'Day' and str(value) in DAYS_ES:
                    value = DAYS_ES[str(value)]
                row_data.append(str(value) if value != '' else '')
        data.append(row_data)

    table = Table(data, repeatRows=1)
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_ROW)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),

        # Fila total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor(COLOR_HEADER)),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    table.setStyle(table_style)
    elements.append(table)

    # ==============================================
    # GRÁFICA: SCRAP RATE POR DÍA DE LA SEMANA
    # ==============================================
    # Filtrar solo los días (excluir la fila "Total")
    df_days = df[df['Day'] != 'Total'].copy()

    if not df_days.empty:
        # Extraer días y rates
        days = df_days['Day'].tolist()
        rates = df_days['Rate'].tolist()
        target = df_days['Target Rate'].iloc[0] if 'Target Rate' in df_days.columns else 0.0

        # Traducir los días al español
        days = [DAYS_ES.get(day, day) for day in days]
        
        # Crear la gráfica
        fig, ax1 = plt.subplots(figsize=(10, 4))
        
        # Crear barras
        bars = ax1.bar(range(len(days)), rates, color=COLOR_BAR, width=0.6)
        
        # Colorear barras que excedan el target y agregar valores
        for i, (bar, rate) in enumerate(zip(bars, rates)):
            if rate > target:
                bar.set_color(COLOR_BAR_EXCEED)
            # Agregar valor encima de cada barra
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{rate:.2f}", ha='center', va='bottom', fontsize=10,
                    color=COLOR_TEXT, fontweight='bold')
        
        # Línea del target
        ax1.axhline(y=target, color=COLOR_TARGET_LINE, linewidth=2.5, 
                    linestyle='--', label=f'Target Rate: {target:.2f}')
        
        # Configuración de ejes
        ax1.set_xticks(range(len(days)))
        ax1.set_xticklabels(days, rotation=0, ha='center', fontsize=10)
        
        # Agregar leyenda
        ax1.legend(loc='upper right', fontsize=9)
        
        # Agregar grid para mejor lectura
        ax1.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax1.set_axisbelow(True)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar imagen temporal
        chart_path = os.path.join(output_folder, "temp_chart_weekly.png")
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Insertar gráfica en el PDF
        elements.append(Spacer(1, 0.3 * inch))
        img = Image(chart_path, width=8 * inch, height=3 * inch)
        elements.append(img)

    # ========================================================================================
    # PÁGINA 2: CONTRIBUIDORES (si existen)
    # ========================================================================================
    if contributors_df is not None and not contributors_df.empty:
        elements.append(PageBreak())
        contributors_title_style = ParagraphStyle(
            'ContributorsTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor(COLOR_TEXT),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        contributors_title = Paragraph("TOP CONTRIBUIDORES DE SCRAP", contributors_title_style)
        elements.append(contributors_title)
        elements.append(Spacer(1, 0.1 * inch))

        contrib_data = []
        contrib_headers = ['Ranking', 'Número de parte', 'Descripción', 'Cantidad', 'Monto (USD)', '% Acumulado', 'Celda']
        contrib_data.append(contrib_headers)

        for index, row in contributors_df.iterrows():
            row_data = []
            for col in contributors_df.columns:
                value = row[col]
                if col == 'Cantidad Scrapeada':
                    row_data.append(f"{value:,.2f}" if isinstance(value, (int, float)) else str(value))
                elif col == 'Monto (dls)':
                    row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
                elif col == '% Acumulado':
                    row_data.append(f"{value:.2f}%" if isinstance(value, (int, float)) else str(value))
                else:
                    row_data.append(str(value))
            contrib_data.append(row_data)

        contrib_table = Table(contrib_data, repeatRows=1)
        contrib_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_BAR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_BG_CONTRIB)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ])

        # Filas hasta 80% en azul tenue
        for i in range(1, len(contrib_data)):
            try:
                cumulative = float(contrib_data[i][-2].replace('%', ''))
                if cumulative <= 80.0:
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#BBD6E2'))
            except Exception:
                pass

        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)

        # ========================================================
        # GRÁFICA DE PARETO: CELDAS CONTRIBUIDORAS
        # ========================================================
        if locations_df is not None and not locations_df.empty:
            
            # Título de la gráfica
            pareto_title_style = ParagraphStyle(
                'ParetoTitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor(COLOR_TEXT),
                spaceAfter=15,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            # Filtrar la fila de totales para la gráfica
            locations_chart = locations_df[locations_df['Ranking'] != 'TOTAL'].copy()
            
            if not locations_chart.empty:
                # Crear figura de Pareto
                fig, ax1 = plt.subplots(figsize=(9, 4.5))
                
                # Eje izquierdo: Barras de monto
                x_pos = range(len(locations_chart))
                bars = ax1.bar(x_pos, locations_chart['Monto (dls)'], 
                              color=COLOR_BAR, alpha=0.8, edgecolor=COLOR_HEADER, linewidth=1.5)
                
                ax1.set_ylabel('Monto (USD)', color=COLOR_BAR, fontsize=11, fontweight='bold')
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels(locations_chart['Celda'], rotation=45, ha='right', fontsize=9)
                ax1.tick_params(axis='y', labelcolor=COLOR_BAR)
                
                # Agregar valores encima de las barras
                for bar, amount in zip(bars, locations_chart['Monto (dls)']):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width() / 2, height,
                            f'${amount:,.0f}', ha='center', va='bottom', 
                            fontsize=8, fontweight='bold', color=COLOR_TEXT)
                
                # Eje derecho: Línea de porcentaje acumulado
                ax2 = ax1.twinx()
                ax2.plot(x_pos, locations_chart['Cumulative %'], 
                        color=COLOR_TARGET_LINE, marker='o', linewidth=2.5, 
                        markersize=7, markerfacecolor=COLOR_TARGET_LINE,
                        markeredgecolor='white', markeredgewidth=1.5)
                
                ax2.tick_params(axis='y', labelcolor=COLOR_TARGET_LINE)
                ax2.set_ylim([0, 105])
                
                # Línea del 80% (Regla de Pareto)
                ax2.axhline(y=80, color='orange', linestyle='--', 
                           linewidth=2, alpha=0.7)
                
                # Agregar valores de porcentaje en los puntos
                for i, (x, y) in enumerate(zip(x_pos, locations_chart['Cumulative %'])):
                    ax2.text(x, y + 2, f'{y:.1f}%', ha='center', va='bottom',
                            fontsize=7, color=COLOR_TARGET_LINE, fontweight='bold')
                
                # Título y leyenda
                plt.title("Top 10 Celdas Contribuidoras", 
                         fontweight='bold', fontsize=13, pad=5, color=COLOR_TEXT)
                
                # Agregar leyenda
                ax2.legend(loc='upper left', fontsize=9, framealpha=0.9)
                
                # Ajustar layout
                plt.tight_layout()
                
                # Guardar imagen temporal
                chart_pareto_path = os.path.join(output_folder, "temp_weekly_pareto.png")
                plt.savefig(chart_pareto_path, dpi=100, bbox_inches='tight')
                plt.close()
                
                # Insertar gráfica en el PDF
                img_pareto = Image(chart_pareto_path, width=8 * inch, height=4 * inch)
                elements.append(img_pareto)

    # Construcción final del PDF
    doc.build(elements)

    # Eliminación de archivos temporales si existen
    # primera gráfica
    if os.path.exists(chart_path):
        os.remove(chart_path)

    # grafica de pareto
    if os.path.exists(chart_pareto_path):
        os.remove(chart_pareto_path)

    return filepath