"""
Módulo para la generación de reportes en PDF
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
matplotlib.use("Agg")  # usar backend no interactivo
import matplotlib.pyplot as plt
from src.location_analysis import get_location_contributors


def generate_pdf_report(df, contributors_df, week, year, scrap_df=None, output_folder='reports'):
    """
    Genera un PDF con el reporte de Scrap Rate y principales contribuidores
    
    Args:
        df (DataFrame): DataFrame con los datos del reporte semanal
        contributors_df (DataFrame): DataFrame con los principales contribuidores
        week (int): Número de semana
        year (int): Año del reporte
        scrap_df (DataFrame): DataFrame original con datos de scrap (para análisis de locations)
        output_folder (str): Carpeta donde se guardará el PDF
        
    Returns:
        str: Ruta del archivo PDF generado
    """
    if df is None:
        return None
    
    # Crear carpeta de reportes si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Nombre del archivo 
    filename = f"Scrap_Rate_W{week}_{year}.pdf"
    filepath = os.path.join(output_folder, filename)
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.black,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph("REPORTE SEMANAL DE SCRAP RATE", title_style)
    elements.append(title)
    
    # Subtítulo con información de semana y año
    subtitle_text = f"Semana {week} | Año {year} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # ========================================================================================
    #                         PRIMERA TABLA: REPORTE SEMANAL
    # ========================================================================================
    data = []
    headers = ['Day', 'D', 'W', 'M', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
    data.append(headers)
    
    for index, row in df.iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]
            if col == 'Scrap':
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
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
    
    # ========================================================================================
    #                         SEGUNDA PÁGINA: GRÁFICAS
    # ========================================================================================
    elements.append(PageBreak())
    
    # --- GRÁFICA 1: SCRAP RATE POR DÍA ---
    days = df['Day'][:-1]  # Excluir fila de totales
    rates = df['Rate'][:-1]
    target = df['Target Rate'].iloc[0] if 'Target Rate' in df.columns else 0.0
    
    fig, ax1 = plt.subplots(figsize=(8, 3))
    bars = ax1.bar(days, rates, color='green')
    
    # Resaltar si pasa el target
    for bar, rate in zip(bars, rates):
        if rate > target:
            bar.set_color('grey')
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f"{rate:.2f}", ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax1.axhline(y=target, color='blue', linewidth=2)
    ax1.set_title("SCRAP RATE POR DÍA", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Rate")
    plt.tight_layout()
    
    # Guardar imagen temporal 1
    chart1_path = os.path.join(output_folder, "temp_chart_rates.png")
    plt.savefig(chart1_path, dpi=100)
    plt.close()
    
    # Insertar primera gráfica en PDF
    img1 = Image(chart1_path, width=7*inch, height=2.5*inch)
    elements.append(img1)
    elements.append(Spacer(1, 0.3*inch))
    
    # ========================================================================================
    #                         PÁGINA 3: CONTRIBUIDORES (si existen)
    # ========================================================================================
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
        contributors_title = Paragraph("TOP CONTRIBUTORS OF SCRAP", contributors_title_style)
        elements.append(contributors_title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Preparar datos de contribuidores CON % ACUMULADO
        contrib_data = []
        contrib_headers = ['Ranking', 'Part Number', 'Description', 'Quantity', 'Amount (USD)', '% Cumulative']
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
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
        
        # Pintar de rojo las filas hasta alcanzar el 80% acumulado
        for i in range(1, len(contrib_data) - 1):  # Excluir encabezado y total
            try:
                # La columna % Acumulado es la última (índice -1)
                cumulative_str = contrib_data[i][-1]
                # Quitar el símbolo % y convertir a float
                cumulative = float(cumulative_str.replace('%', ''))
                
                if cumulative <= 80.0:
                    # Pintar toda la fila de rojo claro hasta el 80%
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ffcccc'))
            except (ValueError, IndexError):
                pass
        
        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        footer_text = "Generado automáticamente por Sistema de Análisis de Scrap Rate by Oscar Teran"
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
    
    # Construir PDF
    doc.build(elements)
    
    # Limpiar imágenes temporales
    if os.path.exists(chart1_path):
        os.remove(chart1_path)
    try:
        if os.path.exists(chart2_path):
            os.remove(chart2_path)
    except:
        pass
    
    return filepath