"""
pdf_quarterly_generator.py - Generador de reportes PDF trimestrales
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


MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

QUARTERS_ES = {
    1: "Primer Trimestre (Q1)",
    2: "Segundo Trimestre (Q2)",
    3: "Tercer Trimestre (Q3)",
    4: "Cuarto Trimestre (Q4)"
}


def generate_quarterly_pdf_report(df, contributors_df, quarter, year, scrap_df=None, output_folder='reports'):
    """
    Genera un PDF con el reporte trimestral de Scrap Rate
    
    Args:
        df (DataFrame): DataFrame con los datos del reporte trimestral
        contributors_df (DataFrame): DataFrame con los principales contribuidores
        quarter (int): Número de trimestre (1-4)
        year (int): Año del reporte
        scrap_df (DataFrame): DataFrame original con datos de scrap
        output_folder (str): Carpeta donde se guardará el PDF
        
    Returns:
        str: Ruta del archivo PDF generado
    """
    if df is None:
        return None
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    quarter_name = QUARTERS_ES.get(quarter, f"Q{quarter}")
    filename = f"Scrap_Rate_Q{quarter}_{year}.pdf"
    filepath = os.path.join(output_folder, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.black,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=10,
        alignment=TA_CENTER
    )
    
    title = Paragraph("REPORTE TRIMESTRAL DE SCRAP RATE", title_style)
    elements.append(title)
    
    subtitle_text = f"{quarter_name} {year} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla
    data = []
    headers = ['Mes', 'Trimestre', 'Año', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
    data.append(headers)
    
    for index, row in df.iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]
            if col == 'Month':
                if isinstance(value, int):
                    row_data.append(MONTHS_ES.get(value, str(value)))
                else:
                    row_data.append(str(value))
            elif col == 'Scrap':
                row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == 'Hrs Prod.':
                row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == 'Rate' or col == 'Target Rate':
                row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == '$ Venta (dls)':
                row_data.append(f"${value:,.0f}" if isinstance(value, (int, float)) else str(value))
            else:
                row_data.append(str(value) if value != '' else '')
        data.append(row_data)
    
    table = Table(data, repeatRows=1)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -2), 1, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9d9d9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    table.setStyle(table_style)
    elements.append(table)
    
    # Gráfica
    months_names = [MONTHS_ES.get(m, str(m)) for m in df['Month'][:-1]]
    rates = df['Rate'][:-1]
    target = df['Target Rate'].iloc[0] if 'Target Rate' in df.columns else 0.0
    
    fig, ax1 = plt.subplots(figsize=(8, 3))
    bars = ax1.bar(months_names, rates, color='#4CAF50')
    
    for bar, rate in zip(bars, rates):
        if rate > target:
            bar.set_color('grey')
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f"{rate:.2f}", ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax1.axhline(y=target, color='red', linewidth=2)
    ax1.set_xlabel("Mes")
    ax1.set_ylabel("Rate")
    plt.tight_layout()
    
    chart_path = os.path.join(output_folder, "temp_chart_quarterly.png")
    plt.savefig(chart_path, dpi=100)
    plt.close()
    
    img = Image(chart_path, width=7*inch, height=2.5*inch)
    elements.append(img)
    elements.append(Spacer(1, 0.3*inch))
    
    # Contribuidores
    if contributors_df is not None and not contributors_df.empty:
        elements.append(PageBreak())
        
        contributors_title_style = ParagraphStyle(
            'ContributorsTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        contributors_title = Paragraph("TOP CONTRIBUIDORES DE SCRAP DEL TRIMESTRE", contributors_title_style)
        elements.append(contributors_title)
        elements.append(Spacer(1, 0.3*inch))
        
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9d9d9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ])
        
        for i in range(1, len(contrib_data) - 1):
            try:
                cumulative_str = contrib_data[i][-2]
                cumulative = float(cumulative_str.replace('%', ''))
                if cumulative <= 80.0:
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ffcccc'))
            except (ValueError, IndexError):
                pass
        
        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)
        
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        footer_text = "Generado automáticamente por Sistema de Análisis de Scrap desarrollado por Oscar Teran"
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
    
    doc.build(elements)
    
    if os.path.exists(chart_path):
        os.remove(chart_path)
    
    return filepath