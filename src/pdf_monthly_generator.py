"""
pdf_monthly_generator.py - Generador de reportes PDF mensuales (paleta fría)
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
from config import (
    MONTHS_NUM_TO_ES, COLOR_BAR, COLOR_BAR_EXCEED, COLOR_BG_CONTRIB,
    COLOR_HEADER, COLOR_TEXT, COLOR_TARGET_LINE, COLOR_TOTAL, COLOR_ROW
)
import os
import matplotlib
matplotlib.use("Agg") # Usar backend no interactivo
import matplotlib.pyplot as plt

def generate_monthly_pdf_report(df, contributors_df, month, year, scrap_df=None, locations_df=None, output_folder='reports'):
    """
    Genera un PDF con el reporte mensual de Scrap Rate
    """
    if df is None:
        return None

    # Crear carpeta de reportes si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Nombre del archivo
    month_name = MONTHS_NUM_TO_ES.get(month, "Mes")
    filename = f"Scrap_Rate_{month_name}_{year}.pdf"
    filepath = os.path.join(output_folder, filename)

    # Crear documento PDF
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    # Estilos de texto
    styles = getSampleStyleSheet()

    # Estilo de título y subtítulo
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

    # Título
    title = Paragraph("REPORTE MENSUAL DEL MÉTRICO DE SCRAP", title_style)
    elements.append(title)

    # Subtítulo
    subtitle_text = f"{month_name} de {year} | Reporte generado automáticamente por Metric Scrap System"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * inch))

    # Determinar si la semana está dentro de la meta comparando el rate total vs target semanal
    target_rate = df['Target Rate'].iloc[0] if 'Target Rate' in df.columns else 0.0
    total_rate = df['Rate'].iloc[-1]
    meets_target = total_rate <= target_rate
    target_status = "✅ Dentro de la Meta" if meets_target else "❌ Fuera de la Meta"
    target_style = ParagraphStyle(
        'TargetStatus',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(COLOR_TEXT),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
        )


    # ==============================================
    # PRIMERA TABLA: REPORTE MENSUAL POR SEMANAS
    # ==============================================
    data = []
    headers = ['Semana', 'Mes', 'Año', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
    data.append(headers)

    for _, row in df.iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]
            if col == 'Scrap':
                row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == 'Hrs Prod.':
                row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
            elif col in ['Rate', 'Target Rate']:
                row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
            elif col == '$ Venta (dls)':
                row_data.append(f"${value:,.0f}" if isinstance(value, (int, float)) else str(value))
            else:
                row_data.append(str(value) if value != '' else '')
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

    # ==============================================
    # GRÁFICA: SCRAP RATE POR SEMANA DEL MES
    # ==============================================
    weeks = df['Week'][:-1]
    rates = df['Rate'][:-1]
    target = df['Target Rate'].iloc[0] if 'Target Rate' in df.columns else 0.0

    fig, ax1 = plt.subplots(figsize=(8, 3))
    bars = ax1.bar(weeks, rates, color=COLOR_BAR)

    for bar, rate in zip(bars, rates):
        if rate > target:
            bar.set_color(COLOR_BAR_EXCEED)
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{rate:.2f}", ha='center', va='bottom', fontsize=9,
                 color=COLOR_TEXT, fontweight='bold')

    ax1.axhline(y=target, color=COLOR_TARGET_LINE, linewidth=2, linestyle='--')
    ax1.set_xlabel("Semana")
    ax1.set_ylabel("Rate")
    plt.tight_layout()

    # Guardar imagen temporal
    chart_path = os.path.join(output_folder, "temp_chart_monthly.png")
    plt.savefig(chart_path, dpi=100)
    plt.close()

    # Insertar gráfica
    img = Image(chart_path, width=7 * inch, height=2.5 * inch)
    elements.append(img)
    elements.append(Spacer(1, 0.3 * inch))

    # ==============================================
    # PÁGINA 2: CONTRIBUIDORES
    # ==============================================
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

        for _, row in contributors_df.iterrows():
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
                    row_data.append(str(value) if value != '' else '')
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
        for i in range(1, len(contrib_data) - 1):
            try:
                cumulative_str = contrib_data[i][-2]
                cumulative = float(cumulative_str.replace('%', ''))
                if cumulative <= 80.0:
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#BBD6E2'))
            except (ValueError, IndexError):
                pass

        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)

        # ========================================================
        # GRÁFICA DE PARETO: CELDAS CONTRIBUIDORAS
        # ========================================================
        if locations_df is not None and not locations_df.empty:
            
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
                
                # Título
                plt.title("Top 10 Celdas Contribuidoras", 
                         fontweight='bold', fontsize=13, pad=5, color=COLOR_TEXT)
                
                # Agregar leyenda
                ax2.legend(loc='upper left', fontsize=9, framealpha=0.9)
                
                # Ajustar layout
                plt.tight_layout()
                
                # Guardar imagen temporal
                chart_pareto_path = os.path.join(output_folder, "temp_monthly_pareto.png")
                plt.savefig(chart_pareto_path, dpi=100, bbox_inches='tight')
                plt.close()
                
                # Insertar gráfica en el PDF
                img_pareto = Image(chart_pareto_path, width=8 * inch, height=4 * inch)
                elements.append(img_pareto)

    # Construir PDF
    doc.build(elements)

    # Limpiar imágenes temporales
    if os.path.exists(chart_path):
        os.remove(chart_path)
    if 'chart_pareto_path' in locals() and os.path.exists(chart_pareto_path):
        os.remove(chart_pareto_path)

    return filepath