"""
Monthly PDF Report Generator - Refactored to use BasePDFGenerator
"""

import os
import pandas as pd
from reportlab.platypus import Table
from reportlab.lib.units import inch
import logging

from src.pdf.base_generator import BasePDFGenerator
from src.pdf.components import (
    get_main_table_style, get_contributors_table_style,
    apply_contributors_cumulative_coloring
)
from config import MONTHS_NUM_TO_ES, MONTHS_ES_TO_NUM

logger = logging.getLogger(__name__)


class MonthlyPDFGenerator(BasePDFGenerator):
    """PDF Generator for monthly scrap rate reports"""
    
    def __init__(self, output_folder='reports'):
        super().__init__(output_folder)
    
    def _calculate_target_achievement(self, df):
        """Calculate if monthly rate meets target"""
        try:
            # Convert to numeric to handle potential string values
            target_rate = pd.to_numeric(df['Target Rate'].iloc[0], errors='coerce') if 'Target Rate' in df.columns else 0.0
            total_rate = pd.to_numeric(df['Rate'].iloc[-1], errors='coerce')
            
            # Handle NaN values
            if pd.isna(target_rate):
                target_rate = 0.0
            if pd.isna(total_rate):
                total_rate = 0.0
            
            within = total_rate <= target_rate
            return within, total_rate, target_rate
        except Exception as e:
            logger.warning(f"Error calculating target achievement: {e}")
            return True, 0, 0
    
    def _build_main_table_data(self, df):
        """Build main monthly report table data (by weeks)"""
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
    
    def generate(self, df, contributors_df, month, year, scrap_df=None, locations_df=None):
        """
        Generate monthly PDF report
        
        Args:
            df: DataFrame with monthly scrap data (aggregated by weeks)
            contributors_df: DataFrame with top contributors
            month: Month number (1-12) or name string
            year: Year (e.g., 2025)
            scrap_df: Optional detailed scrap data
            locations_df: Optional location data
            
        Returns:
            str: Path to generated PDF file, or None if failed
        """
        if df is None:
            logger.warning("DataFrame is None, aborting PDF generation")
            return None
        
        # Determine month name
        if isinstance(month, int):
            month_name = MONTHS_NUM_TO_ES.get(month, "Mes")
        elif isinstance(month, str):
            month_name = month if month in MONTHS_ES_TO_NUM else "Mes"
        else:
            month_name = "Mes"
        
        logger.info(f"Starting monthly PDF generation: {month_name} {year}")
        
        # Close matplotlib figures
        self._close_matplotlib_figures()
        
        # Ensure output folder exists
        self._ensure_output_folder()
        
        # Create filename and document
        filename = f"Scrap_Rate_{month_name}_{year}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        doc = self._create_document(filepath)
        
        # Reset elements
        self.elements = []
        
        # ============ PAGE 1: MAIN REPORT ============
        # Add title and subtitle
        self._add_main_title("REPORTE MENSUAL DEL MÉTRICO DE SCRAP")
        subtitle_text = f"{month_name} | Año {year} | Reporte generado automáticamente por Metric Scrap System"
        self._add_subtitle(subtitle_text)
        self._add_spacer(0.3)
        
        # Calculate target achievement
        within, total_rate, target_rate = self._calculate_target_achievement(df)
        self._add_target_header(within)
        
        # Build and add main table
        table_data = self._build_main_table_data(df)
        table = Table(table_data, repeatRows=1)
        
        table_style = get_main_table_style()
        # Note: Monthly report doesn't use conditional row coloring by default
        
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


def generate_monthly_pdf_report(df, contributors_df, month, year, scrap_df=None, locations_df=None, output_folder='reports'):
    """
    Legacy function interface for backward compatibility
    
    Generates a monthly PDF report using the new architecture
    """
    generator = MonthlyPDFGenerator(output_folder)
    return generator.generate(df, contributors_df, month, year, scrap_df, locations_df)
