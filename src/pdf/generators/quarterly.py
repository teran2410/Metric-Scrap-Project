"""
Quarterly PDF Report Generator - Refactored to use BasePDFGenerator
"""

import os
import pandas as pd
from reportlab.platypus import Table
from reportlab.lib.units import inch
import logging

from src.pdf.base_generator import BasePDFGenerator
from src.pdf.components import (
    get_main_table_style, get_contributors_table_style,
    apply_contributors_cumulative_coloring, apply_rate_conditional_coloring
)
from config import MONTHS_NUM_TO_ES, TARGET_RATES

logger = logging.getLogger(__name__)

QUARTERS_ES = {
    1: "Primer Trimestre (Q1)",
    2: "Segundo Trimestre (Q2)",
    3: "Tercer Trimestre (Q3)",
    4: "Cuarto Trimestre (Q4)"
}


class QuarterlyPDFGenerator(BasePDFGenerator):
    """PDF Generator for quarterly scrap rate reports"""
    
    def __init__(self, output_folder='reports'):
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
    
    def generate(self, df, contributors_df, quarter, year, scrap_df=None):
        """
        Generate quarterly PDF report
        
        Args:
            df: DataFrame with quarterly scrap data (aggregated by months)
            contributors_df: DataFrame with top contributors
            quarter: Quarter number (1-4)
            year: Year (e.g., 2025)
            scrap_df: Optional detailed scrap data
            
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
        self._add_spacer(0.3)
        
        # Calculate target achievement
        within, total_rate, target_rate = self._calculate_target_achievement(df)
        self._add_target_header(within)
        
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


def generate_quarterly_pdf_report(df, contributors_df, quarter, year, scrap_df=None, output_folder='reports'):
    """
    Legacy function interface for backward compatibility
    
    Generates a quarterly PDF report using the new architecture
    """
    generator = QuarterlyPDFGenerator(output_folder)
    return generator.generate(df, contributors_df, quarter, year, scrap_df)
