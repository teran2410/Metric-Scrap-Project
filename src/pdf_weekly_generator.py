"""
pdf_weekly_generator.py - Módulo para la generación de reportes en PDF (versión mejorada visualmente con paleta fría)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import os
import pandas as pd
from config import (
    WEEK_REPORTS_FOLDER, COLOR_HEADER, COLOR_ROW, COLOR_TOTAL, COLOR_BAR,
    COLOR_BAR_EXCEED, COLOR_TEXT, COLOR_TARGET_LINE, COLOR_BG_CONTRIB,
    DAYS_ES, MONTHS_NUM_TO_ES
)

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

    # Estilos del documento
    styles = getSampleStyleSheet()

    # Titulos personalizado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(COLOR_TEXT),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Subtítulo personalizado
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

    subtitle_text = f"Semana {week} | Año {year} | Reporte generado automáticamente por Metric Scrap System"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)

    # Determinar si la semana está dentro de la meta comparando el rate total vs target semanal
    try:
        # Sumar columnas numéricas (ignorar celdas no numéricas como 'Total')
        total_scrap = pd.to_numeric(df['Scrap'], errors='coerce').sum()
        total_horas = pd.to_numeric(df['Hrs Prod.'], errors='coerce').sum()
        total_rate = total_scrap / total_horas if total_horas > 0 else 0

        # Obtener un target numérico representativo de la columna (normalmente el valor semanal)
        target_vals = pd.to_numeric(df['Target Rate'], errors='coerce').dropna().unique()
        target_rate = float(target_vals[0]) if len(target_vals) > 0 else 0

        within = total_rate <= target_rate
    except Exception:
        # En caso de error, asumimos dentro de meta por defecto para no bloquear la generación
        within = True
        total_rate = 0
        target_rate = 0

    header_text = "DENTRO DE META" if within else "FUERA DE META"
    header_color = colors.HexColor("#2E8B57") if within else colors.red

    header_style = ParagraphStyle(
        'TargetHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=header_color,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    elements.append(Paragraph(header_text, header_style))
    elements.append(Spacer(1, 0.2 * inch))

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
            elif col == 'W':
                if str(value) != '':  # Si no es la fila de totales
                    row_data.append(str(week))
                else:
                    row_data.append('')
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

    # IMPORTANTE: Agregar estilos ANTES de aplicar setStyle()
    for i in range(1, len(data) - 1):  # Excluir header (0) y total (-1)
        try:
            # Obtener Rate y Target Rate de la fila actual
            rate_str = str(data[i][7])  # Columna 'Rate' (índice 7)
            target_str = str(data[i][8])  # Columna 'Target Rate' (índice 8)
            
            # Convertir a float (remover $ si existe)
            rate = float(rate_str.replace('$', '').replace(',', ''))
            target = float(target_str.replace('$', '').replace(',', ''))
            
            # Si el rate excede el target, colorear la fila
            if rate > target:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor(COLOR_BAR_EXCEED))
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.white)
        except (ValueError, IndexError) as e:
            # Si hay algún error al convertir, simplemente continuar
            pass
    
    table.setStyle(table_style)
    elements.append(table)

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

        subtitle_contributors = f"Semana {week} | Año {year} | Reporte generado automáticamente por Metric Scrap System"
        subtitle_page2 = Paragraph(subtitle_contributors, subtitle_style)
        elements.append(subtitle_page2)
        elements.append(Spacer(1, 0.3 * inch))

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

        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_BAR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_BG_CONTRIB)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

        # Fila total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ])

        # Filas hasta 80% en rojo tenue
        for i in range(1, len(contrib_data)):
            try:
                cumulative = float(contrib_data[i][-2].replace('%', ''))
                if cumulative <= 80.0:
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFCCCC'))
            except Exception:
                pass

        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)

    # Construcción final del PDF
    doc.build(elements)

    return filepath