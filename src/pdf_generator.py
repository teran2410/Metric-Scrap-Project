"""
Módulo para la generación de reportes en PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os


def generate_pdf_report(df, contributors_df, week, year, output_folder='reports'):
    """
    Genera un PDF con el reporte de Scrap Rate y principales contribuidores
    
    Args:
        df (DataFrame): DataFrame con los datos del reporte semanal
        contributors_df (DataFrame): DataFrame con los principales contribuidores
        week (int): Número de semana
        year (int): Año del reporte
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Scrap_Rate_W{week}_{year}_{timestamp}.pdf"
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
        textColor=colors.HexColor('#1f77b4'),
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
    
    # ============================================
    # PRIMERA TABLA: REPORTE SEMANAL
    # ============================================
    # Preparar datos para la tabla
    data = []
    
    # Encabezados
    headers = ['Day', 'D', 'W', 'M', 'Scrap', 'Hrs Prod.', 'Rate', 'Target Rate', '$ Venta (dls)']
    data.append(headers)
    
    # Datos del DataFrame
    for index, row in df.iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]
            
            # Formatear valores según el tipo
            if col == 'Scrap' or col == 'Hrs Prod.':
                if isinstance(value, (int, float)):
                    row_data.append(f"{value:,.2f}")
                else:
                    row_data.append(str(value))
            elif col == 'Rate' or col == 'Target Rate':
                if isinstance(value, (int, float)):
                    row_data.append(f"{value:.2f}")
                else:
                    row_data.append(str(value))
            elif col == '$ Venta (dls)':
                if isinstance(value, (int, float)):
                    row_data.append(f"${value:,.0f}")
                else:
                    row_data.append(str(value))
            else:
                row_data.append(str(value) if value != '' else '')
        
        data.append(row_data)
    
    # Crear tabla
    table = Table(data, repeatRows=1)
    
    # Estilo de la tabla
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Cuerpo de la tabla
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -2), 1, colors.grey),
        
        # Fila de totales (última fila)
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9d9d9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        
        # Padding
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    
    # Resaltar columna de Rate según Target Rate
    for i in range(1, len(data) - 1):  # Excluir encabezado y total
        try:
            rate = float(data[i][6]) if data[i][6] else 0
            target = float(data[i][7]) if data[i][7] else 0
            
            if rate >= target:
                # Rojo si excede el target
                table_style.add('BACKGROUND', (6, i), (6, i), colors.HexColor('#ffcccc'))
            elif rate > 0:
                # Verde si está dentro del target
                table_style.add('BACKGROUND', (6, i), (6, i), colors.HexColor('#ccffcc'))
        except (ValueError, IndexError):
            pass
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Agregar salto de página para la segunda tabla
    elements.append(PageBreak())
    
    # ============================================
    # SEGUNDA TABLA: TOP CONTRIBUIDORES (Página 2)
    # ============================================
    if contributors_df is not None and not contributors_df.empty:
        # Título de la segunda página
        page2_title = Paragraph("REPORTE SEMANAL DE SCRAP RATE", title_style)
        elements.append(page2_title)
        elements.append(Paragraph(subtitle_text, subtitle_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Título de la segunda sección
        contributors_title_style = ParagraphStyle(
            'ContributorsTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#d62728'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        contributors_title = Paragraph("TOP CONTRIBUIDORES DE SCRAP", contributors_title_style)
        elements.append(contributors_title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Preparar datos de contribuidores
        contrib_data = []
        contrib_headers = ['Lugar', 'Número de Parte', 'Descripción', 'Cantidad', 'Monto (dls)']
        contrib_data.append(contrib_headers)
        
        for index, row in contributors_df.iterrows():
            row_data = []
            for col in contributors_df.columns:
                value = row[col]
                
                if col == 'Cantidad Scrapeada':
                    if isinstance(value, (int, float)):
                        row_data.append(f"{value:,.2f}")
                    else:
                        row_data.append(str(value))
                elif col == 'Monto (dls)':
                    if isinstance(value, (int, float)):
                        row_data.append(f"${value:,.2f}")
                    else:
                        row_data.append(str(value))
                else:
                    row_data.append(str(value) if value != '' else '')
            
            contrib_data.append(row_data)
        
        # Crear tabla de contribuidores
        contrib_table = Table(contrib_data, repeatRows=1)
        
        # Estilo de la tabla de contribuidores
        contrib_table_style = TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Cuerpo de la tabla
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            
            # Fila de totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9d9d9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            
            # Alinear descripción a la izquierda
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ])
        
        # Resaltar los top 3 contribuidores
        for i in range(1, min(4, len(contrib_data))):
            contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ffcccc'))
        
        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)
        
        # Agregar nota al pie en la misma página
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        footer_text = "Generado automáticamente por Sistema de Análisis de Scrap Rate"
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
    else:
        # Si no hay contribuidores, agregar nota al pie después de la primera tabla
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        footer_text = "Generado automáticamente por Sistema de Análisis de Scrap Rate"
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
    
    # Construir PDF
    doc.build(elements)
    
    return filepath