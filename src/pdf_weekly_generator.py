"""
pdf_weekly_generator.py - Módulo para la generación de reportes en PDF (versión mejorada visualmente)
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
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_weekly_pdf_report(df, contributors_df, week, year, scrap_df=None, output_folder='reports'):
    """
    Genera un PDF con el reporte de Scrap Rate y principales contribuidores
    """
    if df is None:
        return None

    # Crear carpeta si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename = f"Scrap_Rate_W{week}_{year}.pdf"
    filepath = os.path.join(output_folder, filename)

    # Crear documento
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
    # Estilos globales del documento
    # ==============================
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=10,
        alignment=TA_CENTER
    )

    # ==============================
    # Encabezado principal
    # ==============================
    title = Paragraph("REPORTE SEMANAL DEL MÉTRICO DE SCRAP", title_style)
    elements.append(title)

    subtitle_text = f"Semana {week} | Año {year} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
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
            else:
                row_data.append(str(value) if value != '' else '')
        data.append(row_data)

    table = Table(data, repeatRows=1)
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B82F6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor("#F3F4F6")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),

        # Fila total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E5E7EB")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor("#1E40AF")),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#9CA3AF")),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    table.setStyle(table_style)
    elements.append(table)

    # ========================================================================================
    # GRÁFICA: SCRAP RATE POR DÍA
    # ========================================================================================
    days = df['Day'][:-1]
    rates = df['Rate'][:-1]
    target = df['Target Rate'].iloc[0] if 'Target Rate' in df.columns else 0.0

    fig, ax = plt.subplots(figsize=(8, 3))
    bars = ax.bar(days, rates, color="#3B82F6", edgecolor="#1E40AF", linewidth=0.8)

    # Resaltar valores sobre el target
    for bar, rate in zip(bars, rates):
        color = "#EF4444" if rate > target else "#3B82F6"
        bar.set_color(color)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{rate:.2f}", ha='center', va='bottom', fontsize=9, fontweight='bold', color="#374151")

    # Línea de objetivo
    ax.axhline(y=target, color="#DC2626", linewidth=1.8, linestyle="--", label=f"Target ({target:.2f})")
    ax.set_ylabel("Rate", fontsize=10, fontweight="bold")
    ax.set_xlabel("Días", fontsize=10, fontweight="bold")
    ax.legend(frameon=False, fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    chart1_path = os.path.join(output_folder, "temp_chart_rates.png")
    plt.savefig(chart1_path, dpi=120)
    plt.close()

    img1 = Image(chart1_path, width=7 * inch, height=2.5 * inch)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(img1)

    # ========================================================================================
    # PÁGINA 2: CONTRIBUIDORES (si existen)
    # ========================================================================================
    if contributors_df is not None and not contributors_df.empty:
        elements.append(PageBreak())
        contributors_title_style = ParagraphStyle(
            'ContributorsTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        contributors_title = Paragraph("TOP CONTRIBUIDORES DE SCRAP", contributors_title_style)
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
                    row_data.append(f"{value:.2f}%" if isinstance(value, (int, float)) else str(value))
                else:
                    row_data.append(str(value))
            contrib_data.append(row_data)

        contrib_table = Table(contrib_data, repeatRows=1)
        contrib_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#9CA3AF")),
        ])

        # Resaltar filas hasta 80%
        for i in range(1, len(contrib_data)):
            try:
                cumulative = float(contrib_data[i][-2].replace('%', ''))
                if cumulative <= 80.0:
                    contrib_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#DBEAFE"))
            except Exception:
                pass

        contrib_table.setStyle(contrib_style)
        elements.append(contrib_table)

        # Footer
        elements.append(Spacer(1, 0.4 * inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor("#6B7280"),
            alignment=TA_RIGHT
        )
        footer_text = "Reporte generado automáticamente por Metric Scrap System – © 2025 Oscar Teran"
        elements.append(Paragraph(footer_text, footer_style))

    # Construcción final del PDF
    doc.build(elements)

    if os.path.exists(chart1_path):
        os.remove(chart1_path)

    return filepath