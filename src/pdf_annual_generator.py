"""
pdf_annual_generator.py - Generador de reportes PDF anuales (paleta fría)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.processors.annual_processor import get_annual_weeks_data
from src.analysis.annual_contributors import get_annual_location_contributors
from config import TARGET_RATES

# Paleta fría profesional
COLOR_HEADER = '#2F6690'       # Azul acero
COLOR_ROW = '#CFE0F3'          # Azul claro
COLOR_TOTAL = '#9DB4C0'        # Azul grisáceo
COLOR_TEXT = '#333333'         # Gris carbón
COLOR_BAR = '#3A7CA5'          # Azul petróleo
COLOR_BAR_EXCEED = '#7D8597'   # Gris azulado
COLOR_TARGET_LINE = '#E9A44C'  # Naranja ámbar (contraste)
COLOR_BG_CONTRIB = '#E1ECF4'   # Azul muy claro para contribuidores

# Diccionario de meses
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

def generate_annual_pdf_report(df, contributors_df, year, scrap_df, ventas_df, horas_df, output_folder='reports'):
    """Genera un PDF con el reporte anual de Scrap Rate"""
    if df is None:
        return None
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    filename = f"Scrap_Rate_Anual_{year}.pdf"
    filepath = os.path.join(output_folder, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter), rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                  textColor=colors.HexColor(COLOR_TEXT), spaceAfter=10,
                                  alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=11,
                                     textColor=colors.grey, spaceAfter=10, alignment=TA_CENTER)
    
    # PÁGINA 1: TABLA DE RESULTADOS MENSUALES
    title = Paragraph(f"REPORTE ANUAL DE SCRAP RATE - {year}", title_style)
    elements.append(title)
    
    subtitle_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * inch))
    
    data = []
    headers = ['Mes', 'Trimestre', 'Año', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
    data.append(headers)
    
    for _, row in df.iterrows():
        row_data = []
        month_value = None
        
        for col in df.columns:
            value = row[col]
            
            if col == 'Month':
                if isinstance(value, int):
                    month_value = value
                    row_data.append(MONTHS_ES.get(value, str(value)))
                else:
                    row_data.append(str(value))
            
            elif col == 'Target Rate':
                if month_value and isinstance(month_value, int):
                    target_rate = TARGET_RATES.get(month_value, 0.0)
                    row_data.append(f"{target_rate:.2f}")
                else:
                    row_data.append(str(value) if value != '' else '')
            
            elif col == 'Scrap':
                row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
            elif col in ['Hrs Prod.', 'Rate']:
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
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor(COLOR_ROW)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLOR_TEXT)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(COLOR_TOTAL)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    table.setStyle(table_style)
    elements.append(table)
    
    # PÁGINA 2: GRÁFICAS
    elements.append(PageBreak())
    
    # Gráfica 1: Por meses
    months_data = df[:-1]  # Excluir total
    months_names = [MONTHS_ES.get(m, str(m)) for m in months_data['Month']]
    rates_monthly = months_data['Rate']
    targets_monthly = months_data['Target Rate']
    
    fig, ax = plt.subplots(figsize=(9, 3.5))
    bars = ax.bar(months_names, rates_monthly, color=COLOR_BAR)
    
    for bar, rate, target in zip(bars, rates_monthly, targets_monthly):
        if rate > target:
            bar.set_color(COLOR_BAR_EXCEED)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{rate:.2f}", ha='center', va='bottom', fontsize=8, color=COLOR_TEXT, fontweight='bold')
    
    ax.set_xlabel("Mes")
    ax.set_ylabel("Rate")
    ax.set_title("Scrap Rate por Mes", fontweight='bold')
    plt.tight_layout()
    
    chart_months_path = os.path.join(output_folder, "temp_annual_months.png")
    plt.savefig(chart_months_path, dpi=100)
    plt.close()
    
    img_months = Image(chart_months_path, width=7 * inch, height=2.8 * inch)
    elements.append(img_months)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Gráfica 2: Por semanas
    weeks_data = get_annual_weeks_data(scrap_df, ventas_df, horas_df, year)
    
    if weeks_data is not None and not weeks_data.empty:
        # Tomar muestras cada 4 semanas para mejor legibilidad
        sample_weeks = weeks_data[::4]
        
        fig, ax = plt.subplots(figsize=(9, 3))
        bars = ax.bar(sample_weeks['Week'].astype(str), sample_weeks['Rate'], color=COLOR_BAR)
        
        # Calcular target promedio anual
        avg_target = sum(TARGET_RATES.values()) / len(TARGET_RATES)
        
        for bar, rate in zip(bars, sample_weeks['Rate']):
            if rate > avg_target:
                bar.set_color(COLOR_BAR_EXCEED)
        
        ax.set_xlabel("Semana")
        ax.set_ylabel("Rate")
        ax.set_title("Scrap Rate por Semana (muestra)", fontweight='bold')
        plt.tight_layout()
        
        chart_weeks_path = os.path.join(output_folder, "temp_annual_weeks.png")
        plt.savefig(chart_weeks_path, dpi=100)
        plt.close()
        
        img_weeks = Image(chart_weeks_path, width=7 * inch, height=2.4 * inch)
        elements.append(img_weeks)
    
    # PÁGINA 3: TOP CONTRIBUIDORES
    if contributors_df is not None and not contributors_df.empty:
        elements.append(PageBreak())
        
        contrib_title_style = ParagraphStyle('ContribTitle', parent=styles['Heading2'], fontSize=18,
                                              textColor=colors.HexColor(COLOR_TEXT), spaceAfter=15,
                                              alignment=TA_CENTER, fontName='Helvetica-Bold')
        contrib_title = Paragraph("TOP CONTRIBUIDORES DE SCRAP DEL AÑO", contrib_title_style)
        elements.append(contrib_title)
        elements.append(Spacer(1, 0.3 * inch))
        
        contrib_data = []
        contrib_headers = ['Ranking', 'Part Number', 'Description', 'Quantity', 'Amount (USD)', '% Cumulative', 'Location']
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
        
        for i in range(1, len(contrib_data) - 1):
            try:
                cumulative = float(contrib_data[i][-2].replace('%', ''))
                if cumulative <= 80.0:
                    contrib_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#BBD6E2'))
            except:
                pass
        
        contrib_table.setStyle(contrib_table_style)
        elements.append(contrib_table)
    
    # PÁGINA 4: PARETO DE CELDAS
    locations_data = get_annual_location_contributors(scrap_df, year, top_n=10)
    
    if locations_data is not None and not locations_data.empty:
        elements.append(PageBreak())
        
        pareto_title = Paragraph("PARETO: CELDAS CONTRIBUIDORAS AL SCRAP ANUAL", contrib_title_style)
        elements.append(pareto_title)
        elements.append(Spacer(1, 0.3 * inch))
        
        fig, ax1 = plt.subplots(figsize=(9, 4))
        
        x_pos = range(len(locations_data))
        bars = ax1.bar(x_pos, locations_data['Monto (dls)'], color=COLOR_BAR, alpha=0.7)
        ax1.set_xlabel('Celda')
        ax1.set_ylabel('Monto (USD)', color=COLOR_BAR)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(locations_data['Celda'], rotation=45, ha='right')
        ax1.tick_params(axis='y', labelcolor=COLOR_BAR)
        
        ax2 = ax1.twinx()
        ax2.plot(x_pos, locations_data['Cumulative %'], color='#E9A44C', marker='o', linewidth=2, markersize=6)
        ax2.set_ylabel('% Acumulado', color='#E9A44C')
        ax2.tick_params(axis='y', labelcolor='#E9A44C')
        ax2.set_ylim([0, 105])
        ax2.axhline(y=80, color='orange', linestyle='--', linewidth=1.5)
        
        plt.title("Principio de Pareto - Top 10 Celdas", fontweight='bold', pad=20)
        
        for bar, amount in zip(bars, locations_data['Monto (dls)']):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                     f'${amount:,.0f}', ha='center', va='bottom', fontsize=7)
        
        plt.tight_layout()
        
        chart_pareto_path = os.path.join(output_folder, "temp_annual_pareto.png")
        plt.savefig(chart_pareto_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        img_pareto = Image(chart_pareto_path, width=7 * inch, height=3.5 * inch)
        elements.append(img_pareto)
        
        elements.append(Spacer(1, 0.3 * inch))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                                       textColor=colors.grey, alignment=TA_RIGHT)
        footer_text = "Reporte generado automáticamente por Metric Scrap System – © 2025 Oscar Teran"
        elements.append(Paragraph(footer_text, footer_style))
    
    doc.build(elements)
    
    # Limpiar imágenes temporales
    for path in [chart_months_path, chart_weeks_path if weeks_data is not None else None, chart_pareto_path if locations_data is not None else None]:
        if path and os.path.exists(path):
            os.remove(path)
    
    return filepath