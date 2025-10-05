"""
pdf_quarterly_generator.py - Generador de reportes PDF trimestrales (con paleta fría profesional y target por mes)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os

# Importa los targets mensuales desde el archivo de configuración
from config import TARGET_RATES


# ==============================
# Diccionarios de idioma
# ==============================
MONTHS_ES = {
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

QUARTERS_ES = {
    1: "Primer Trimestre (Q1)",
    2: "Segundo Trimestre (Q2)",
    3: "Tercer Trimestre (Q3)",
    4: "Cuarto Trimestre (Q4)"
}


# ==============================
# Paleta fría profesional
# ==============================
COLOR_HEADER = '#2F6690'       # Azul acero
COLOR_ROW = '#CFE0F3'          # Azul claro
COLOR_TOTAL = '#9DB4C0'        # Azul grisáceo
COLOR_TEXT = '#333333'         # Gris carbón
COLOR_BAR = '#3A7CA5'          # Azul petróleo
COLOR_BG_CONTRIB = '#E1ECF4'   # Azul muy claro para contribuidores


def generate_quarterly_pdf_report(df, contributors_df, quarter, year, scrap_df=None, output_folder='reports'):
    """
    Genera un PDF con el reporte trimestral de Scrap Rate
    """
    if df is None:
        return None

    # Crear carpeta de reportes si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Nombre del archivo
    quarter_name = QUARTERS_ES.get(quarter, f"Q{quarter}")
    filename = f"Scrap_Rate_Q{quarter}_{year}.pdf"
    filepath = os.path.join(output_folder, filename)

    # Documento base
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    # ==============================
    # Estilos de texto
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
    # Encabezado
    # ==============================
    title = Paragraph("REPORTE TRIMESTRAL DE SCRAP RATE", title_style)
    elements.append(title)

    subtitle_text = f"{quarter_name} {year} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * inch))

    # ========================================================================================
    # TABLA PRINCIPAL
    # ========================================================================================
    data = []
    headers = ['Mes', 'Trimestre', 'Año', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
    data.append(headers)

    for index, row in df.iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]

            # Mes traducido
            if col == 'Month':
                if isinstance(value, int):
                    row_data.append(MONTHS_ES.get(value, str(value)))
                    # Reemplazar el Target Rate de acuerdo al mes
                    target_rate = TARGET_RATES.get(value, 0.0)
                else:
                    row_data.append(str(value))
                    target_rate = 0.0

            # Formato de columnas numéricas
            elif col == 'Scrap':
                row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
            elif col in ['Hrs Prod.', 'Rate']:
                row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == '$ Venta (dls)':
                row_data.append(f"${value:,.0f}" if isinstance(value, (int, float)) else str(value))
            else:
                row_data.append(str(value) if value != '' else '')

        # Añade el Target Rate específico del mes
        row_data.append(f"{target_rate:.2f}")
        data.append(row_data)

    table = Table(data, repeatRows=1)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_ROW)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),

        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])
    table.setStyle(table_style)
    elements.append(table)

    # ========================================================================================
    # CONTRIBUIDORES (SEGUNDA PÁGINA)
    # ========================================================================================
    if contributors_df is not None and not contributors_df.empty:
        elements.append(PageBreak())

        contributors_title_style = ParagraphStyle(
            'ContributorsTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor(COLOR_TEXT),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        contributors_title = Paragraph("TOP CONTRIBUIDORES DE SCRAP DEL TRIMESTRE", contributors_title_style)
        elements.append(contributors_title)
        elements.append(Spacer(1, 0.3 * inch))

        contrib_data = []
        contrib_headers = ['Ranking', 'Part Number', 'Description', 'Quantity', 'Amount (USD)', '% Cumulative', 'Location']
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
                    if isinstance(value, (int, float)):
                        row_data.append(f"{value:.2f}%")
                    else:
                        row_data.append(str(value))
                else:
                    row_data.append(str(value) if value != '' else '')
            contrib_data.append(row_data)

        contrib_table = Table(contrib_data, repeatRows=1)
        contrib_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_BAR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_BG_CONTRIB)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ])

        # Resalta hasta el 80% acumulado
        for i in range(1, len(contrib_data)):
            try:
                cumulative = float(contrib_data[i][-2].replace('%', ''))
                if cumulative <= 80.0:
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#BBD6E2'))
            except Exception:
                pass

        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)

        # Pie de página
        elements.append(Spacer(1, 0.3 * inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        footer_text = "Reporte generado automáticamente por Metric Scrap System – © 2025 Oscar Teran"
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)

    # ==============================
    # Construcción final del PDF
    # ==============================
    doc.build(elements)
    return filepath
