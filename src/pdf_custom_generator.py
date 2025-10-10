"""
pdf_custom_generator.py - Generación de reportes PDF para rango de fechas personalizado
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


def create_custom_report(data_df, contributors_df, reasons_df, start_date, end_date, output_path):
    """
    Crea un reporte PDF con los datos de scrap para un rango de fechas personalizado
    
    Args:
        data_df (DataFrame): DataFrame con los datos del periodo
        contributors_df (DataFrame): DataFrame con los principales contribuidores
        reasons_df (DataFrame): DataFrame con las principales razones
        start_date (datetime): Fecha inicial del periodo
        end_date (datetime): Fecha final del periodo
        output_path (str): Ruta donde guardar el PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    )
    title = Paragraph(f"Reporte de Scrap<br/>Periodo: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}", title_style)
    elements.append(title)
    
    # Datos principales
    if data_df is not None and not data_df.empty:
        elements.append(Paragraph("Datos del Periodo", styles['Heading1']))
        
        # Convertir DataFrame a lista para la tabla
        data_table = [list(data_df.columns)]  # Encabezados
        for index, row in data_df.iterrows():
            data_table.append([
                str(row['Date']),
                f"{row['Scrap']:.2f}",
                f"{row['Hrs Prod.']:.2f}",
                f"{row['$ Venta (dls)']:.2f}",
                f"{row['Rate']:.4f}"
            ])
        
        # Crear tabla
        table = Table(data_table, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
    
    # Top Contributors
    if contributors_df is not None and not contributors_df.empty:
        elements.append(Paragraph("Principales Contribuidores", styles['Heading1']))
        
        contrib_data = [['Location', 'Total Scrap', 'Count', '% of Total']]
        for index, row in contributors_df.iterrows():
            contrib_data.append([
                str(row['Location']),
                f"{row['Total Scrap']:.2f}",
                str(row['Count']),
                f"{row['% of Total']:.2f}%"
            ])
        
        contrib_table = Table(contrib_data, repeatRows=1)
        contrib_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(contrib_table)
        elements.append(Spacer(1, 20))
    
    # Razones de Scrap
    if reasons_df is not None and not reasons_df.empty:
        elements.append(Paragraph("Principales Razones de Scrap", styles['Heading1']))
        
        reasons_data = [['Reason', 'Total Scrap', 'Count', '% of Total']]
        for index, row in reasons_df.iterrows():
            reasons_data.append([
                str(row['Reason']),
                f"{row['Total Scrap']:.2f}",
                str(row['Count']),
                f"{row['% of Total']:.2f}%"
            ])
        
        reasons_table = Table(reasons_data, repeatRows=1)
        reasons_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(reasons_table)
    
    # Generar PDF
    doc.build(elements)