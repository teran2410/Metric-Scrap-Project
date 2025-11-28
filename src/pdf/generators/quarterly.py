"""
Quarterly PDF Report Generator - Refactored to use BasePDFGenerator
"""

import os
import pandas as pd
from reportlab.platypus import Table, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
import logging

from src.pdf.base_generator import BasePDFGenerator
from src.pdf.components import (
    get_main_table_style, get_contributors_table_style,
    apply_contributors_cumulative_coloring, apply_rate_conditional_coloring
)
from config import MONTHS_NUM_TO_ES, TARGET_RATES, QUARTERLY_REPORTS_FOLDER
from src.analysis.period_comparison import PeriodComparison

logger = logging.getLogger(__name__)

QUARTERS_ES = {
    1: "Primer Trimestre (Q1)",
    2: "Segundo Trimestre (Q2)",
    3: "Tercer Trimestre (Q3)",
    4: "Cuarto Trimestre (Q4)"
}


class QuarterlyPDFGenerator(BasePDFGenerator):
    """PDF Generator for quarterly scrap rate reports"""
    
    def __init__(self, output_folder=QUARTERLY_REPORTS_FOLDER):
        super().__init__(output_folder)
    
    def _calculate_target_achievement(self, df):
        """Calculate if quarterly rate meets target"""
        try:
            # For quarterly, we check the total rate against average target
            # Convert Rate to numeric to handle potential string values
            total_rate = pd.to_numeric(df['Rate'].iloc[-1], errors='coerce')
            if pd.isna(total_rate):
                total_rate = 0.0
            
            # Calculate average target from the months in this quarter
            # Get month values to look up their targets from config
            if 'Month' in df.columns:
                months = df['Month'].dropna()
                # Exclude the 'Total' row
                months = months[months != 'Total']
                target_sum = sum(TARGET_RATES.get(int(m), 0.0) for m in months if isinstance(m, (int, float)))
                target_rate = target_sum / len(months) if len(months) > 0 else 0.0
            else:
                target_rate = 0.0
            
            within = total_rate <= target_rate
            return within, total_rate, target_rate
        except Exception as e:
            logger.warning(f"Error calculating target achievement: {e}")
            return True, 0, 0
    
    def _build_main_table_data(self, df):
        """Build main quarterly report table data (by months)"""
        data = []
        headers = ['Mes', 'Trimestre', 'Año', 'Scrap', 'Hrs Prod.', 'Venta (dls)', 'Rate', 'Target Rate']
        data.append(headers)
        
        for index, row in df.iterrows():
            row_data = []
            month_value = None
            
            for col in df.columns:
                value = row[col]
                
                # Mes traducido
                if col == 'Month':
                    if isinstance(value, int):
                        month_value = value
                        row_data.append(MONTHS_NUM_TO_ES.get(value, str(value)))
                    else:
                        row_data.append(str(value))
                
                # Target Rate - usar el del mes específico
                elif col == 'Target Rate':
                    if month_value and isinstance(month_value, int):
                        target_rate = TARGET_RATES.get(month_value, 0.0)
                        row_data.append(f"{target_rate:.2f}")
                    else:
                        row_data.append(str(value) if value != '' else '')
                
                # Formatear columnas numéricas
                elif col == 'Scrap':
                    row_data.append(f"${value:,.2f}" if isinstance(value, (int, float)) else str(value))
                elif col in ['Hrs Prod.', 'Rate']:
                    row_data.append(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
                elif col == '$ Venta (dls)':
                    row_data.append(f"${value:,.0f}" if isinstance(value, (int, float)) else str(value))
                else:
                    row_data.append(str(value) if value != '' else '')
            
            data.append(row_data)
        
        return data
    
    def _build_contributors_table_data(self, contributors_df):
        """Build contributors table data"""
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
        
        return contrib_data
    
    def _add_comparison_section(self, comparison: PeriodComparison):
        """Add period comparison section to PDF"""
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph, TableStyle
        from reportlab.lib.enums import TA_CENTER
        
        styles = getSampleStyleSheet()
        
        # Título de sección centrado
        self._add_spacer(0.3)
        title_style = ParagraphStyle(
            'ComparisonTitle',
            parent=styles['Heading2'],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.HexColor('#333333')
        )
        title = Paragraph("<b>COMPARACIÓN CON PERIODO ANTERIOR</b>", title_style)
        self.elements.append(title)
        self._add_spacer(0.2)
        
        # Construir tabla de comparación
        comparison_data = [
            ['Métrica', comparison.previous_label, comparison.period_label, 'Cambio'],
        ]
        
        # Fila de Scrap Rate con indicador
        rate_indicator = comparison.get_rate_indicator()
        comparison_data.append([
            'Scrap Rate',
            f"{comparison.previous_scrap_rate:.2f}",
            f"{comparison.current_scrap_rate:.2f}",
            f"{rate_indicator} {comparison.rate_change_pct:+.1f}%"
        ])
        
        # Fila de Total Scrap con indicador
        scrap_indicator = comparison.get_scrap_indicator()
        comparison_data.append([
            'Total Scrap',
            f"${comparison.previous_total_scrap:,.0f}",
            f"${comparison.current_total_scrap:,.0f}",
            f"{scrap_indicator} {comparison.scrap_change_pct:+.1f}%"
        ])
        
        # Fila de Horas Producción con indicador
        hours_indicator = "↓" if comparison.hours_change_pct < 0 else ("↑" if comparison.hours_change_pct > 1 else "→")
        comparison_data.append([
            'Hrs. Producción',
            f"{comparison.previous_total_hours:,.0f}",
            f"{comparison.current_total_hours:,.0f}",
            f"{hours_indicator} {comparison.hours_change_pct:+.1f}%"
        ])
        
        comparison_table = Table(comparison_data, colWidths=[2.2*inch, 1.8*inch, 1.8*inch, 1.2*inch])
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e3f2fd')]),
        ])
        
        if comparison.is_improvement():
            table_style.add('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#2e7d32'))
            table_style.add('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold')
        elif comparison.rate_change_pct > 1:
            table_style.add('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#c62828'))
            table_style.add('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold')
        
        if comparison.scrap_change_abs < 0:
            table_style.add('TEXTCOLOR', (3, 2), (3, 2), colors.HexColor('#2e7d32'))
            table_style.add('FONTNAME', (3, 2), (3, 2), 'Helvetica-Bold')
        elif comparison.scrap_change_abs > 0:
            table_style.add('TEXTCOLOR', (3, 2), (3, 2), colors.HexColor('#c62828'))
            table_style.add('FONTNAME', (3, 2), (3, 2), 'Helvetica-Bold')
        
        # Hrs. Producción (fila 3) - Lógica invertida: menos horas = rojo (deterioro)
        if comparison.hours_change_pct < -1:  # Disminución significativa de horas = ROJO (malo)
            table_style.add('TEXTCOLOR', (3, 3), (3, 3), colors.HexColor('#c62828'))
            table_style.add('FONTNAME', (3, 3), (3, 3), 'Helvetica-Bold')
        elif comparison.hours_change_pct > 1:  # Aumento de horas = VERDE (bueno)
            table_style.add('TEXTCOLOR', (3, 3), (3, 3), colors.HexColor('#2e7d32'))
            table_style.add('FONTNAME', (3, 3), (3, 3), 'Helvetica-Bold')
        else:  # Cambio menor a 1% = GRIS (neutral)
            table_style.add('TEXTCOLOR', (3, 3), (3, 3), colors.HexColor('#666666'))
        
        comparison_table.setStyle(table_style)
        self.elements.append(comparison_table)
        
        self._add_spacer(0.15)
        note_style = ParagraphStyle(
            'ComparisonNote',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        rate_indicator = comparison.get_rate_indicator()
        scrap_indicator = comparison.get_scrap_indicator()
        hours_indicator = '→' if abs(comparison.hours_change_pct) < 1 else ('↓' if comparison.hours_change_pct < 0 else '↑')
        
        note = Paragraph(
            f"<i><font color='#2e7d32'><b>↓</b></font> = Mejora (reducción) | "
            f"<font color='#c62828'><b>↑</b></font> = Deterioro (aumento) | "
            f"<font color='#666666'><b>→</b></font> = Sin cambio significativo (&lt;1%)<br/>"
            f"<b>Indicadores:</b> Scrap Rate {rate_indicator} | Total Scrap {scrap_indicator} | Horas Prod. {hours_indicator}</i>",
            note_style
        )
        self.elements.append(note)
    
    def generate(self, df, contributors_df, quarter, year, scrap_df=None, comparison=None):
        """
        Generate quarterly PDF report
        
        Args:
            df: DataFrame with quarterly scrap data (aggregated by months)
            contributors_df: DataFrame with top contributors
            quarter: Quarter number (1-4)
            year: Year (e.g., 2025)
            scrap_df: Optional detailed scrap data
            comparison: Optional PeriodComparison object for period comparison
            
        Returns:
            str: Path to generated PDF file, or None if failed
        """
        if df is None:
            logger.warning("DataFrame is None, aborting PDF generation")
            return None
        
        quarter_name = QUARTERS_ES.get(quarter, f"Q{quarter}")
        logger.info(f"Starting quarterly PDF generation: {quarter_name} {year}")
        
        # Close matplotlib figures
        self._close_matplotlib_figures()
        
        # Ensure output folder exists
        self._ensure_output_folder()
        
        # Create filename and document
        filename = f"Scrap_Rate_Q{quarter}_{year}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        doc = self._create_document(filepath)
        
        # Reset elements
        self.elements = []
        
        # ============ PAGE 1: MAIN REPORT ============
        # Add title and subtitle
        self._add_main_title("REPORTE TRIMESTRAL DE SCRAP RATE")
        subtitle_text = f"{quarter_name} | Año {year} | Reporte generado automáticamente por Metric Scrap System"
        self._add_subtitle(subtitle_text)
        self._add_spacer(0.15)
        
        # Calculate target achievement
        within, total_rate, target_rate = self._calculate_target_achievement(df)
        self._add_target_header(within)
        
        # Add comparison section if provided
        if comparison is not None:
            self._add_comparison_section(comparison)
        
        # Build and add main table
        table_data = self._build_main_table_data(df)
        table = Table(table_data, repeatRows=1)
        
        table_style = get_main_table_style()
        # Apply conditional coloring: paint rows gray where rate > target
        apply_rate_conditional_coloring(table_style, table_data, rate_col_idx=6, target_col_idx=7)
        
        table.setStyle(table_style)
        self.elements.append(table)
        
        # ============ CONTRIBUTORS SECTION (Same page) ============
        if contributors_df is not None and not contributors_df.empty:
            self._add_page_break()
            
            self._add_spacer(0.5)
            self._add_section_title("TOP CONTRIBUIDORES DE SCRAP")
            self._add_spacer(0.2)
            
            # Build contributors table
            contrib_data = self._build_contributors_table_data(contributors_df)
            contrib_table = Table(contrib_data, repeatRows=1)
            
            contrib_table_style = get_contributors_table_style()
            apply_contributors_cumulative_coloring(contrib_table_style, contrib_data, cumulative_col_idx=5, threshold=80.0)
            
            contrib_table.setStyle(contrib_table_style)
            self.elements.append(contrib_table)
        
        # Build PDF
        self.build_and_save(doc)
        
        return filepath


def generate_quarterly_pdf_report(df, contributors_df, quarter, year, scrap_df=None, comparison=None, output_folder=QUARTERLY_REPORTS_FOLDER):
    """
    Legacy function interface for backward compatibility
    
    Generates a quarterly PDF report using the new architecture
    """
    if comparison:
        logger.info(f"Comparación incluida: {comparison.period_label} vs {comparison.previous_label}")
    
    generator = QuarterlyPDFGenerator(output_folder)
    return generator.generate(df, contributors_df, quarter, year, scrap_df, comparison)
