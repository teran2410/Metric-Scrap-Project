"""
Weekly PDF Report Generator - Refactored to use BasePDFGenerator
"""

import os
import pandas as pd
from reportlab.platypus import Table, Spacer
from reportlab.lib.units import inch

from src.pdf.base_generator import BasePDFGenerator
from src.pdf.components import (
    get_main_table_style, get_contributors_table_style,
    apply_rate_conditional_coloring, apply_contributors_cumulative_coloring
)
from config import (
    WEEK_REPORTS_FOLDER, DAYS_ES, MONTHS_NUM_TO_ES
)


class WeeklyPDFGenerator(BasePDFGenerator):
    """PDF Generator for weekly scrap rate reports"""
    
    def __init__(self, output_folder=WEEK_REPORTS_FOLDER):
        super().__init__(output_folder)
    
    def _calculate_target_achievement(self, df):
        """Calculate if weekly rate meets target"""
        try:
            total_scrap = pd.to_numeric(df['Scrap'], errors='coerce').sum()
            total_horas = pd.to_numeric(df['Hrs Prod.'], errors='coerce').sum()
            total_rate = total_scrap / total_horas if total_horas > 0 else 0
            
            target_vals = pd.to_numeric(df['Target Rate'], errors='coerce').dropna().unique()
            target_rate = float(target_vals[0]) if len(target_vals) > 0 else 0
            
            within = total_rate <= target_rate
            return within, total_rate, target_rate
        except Exception:
            return True, 0, 0
    
    def _build_main_table_data(self, df, week):
        """Build main weekly report table data"""
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
                elif col == 'M':
                    if isinstance(value, (int, float)):
                        row_data.append(MONTHS_NUM_TO_ES.get(int(value), str(value)))
                    else:
                        row_data.append(str(value) if value != '' else '')
                elif col == 'W':
                    if str(value) != '':
                        row_data.append(str(week))
                    else:
                        row_data.append('')
                else:
                    if col == 'Day' and str(value) in DAYS_ES:
                        value = DAYS_ES[str(value)]
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
    
    def generate(self, df, contributors_df, week, year, scrap_df=None, locations_df=None):
        """
        Generate weekly PDF report
        
        Args:
            df: DataFrame with weekly scrap data
            contributors_df: DataFrame with top contributors
            week: Week number (1-53)
            year: Year (e.g., 2025)
            scrap_df: Optional detailed scrap data
            locations_df: Optional location data
            
        Returns:
            str: Path to generated PDF file, or None if failed
        """
        if df is None:
            return None
        
        # Close matplotlib figures
        self._close_matplotlib_figures()
        
        # Ensure output folder exists
        self._ensure_output_folder()
        
        # Create filename and document
        filename = f"Scrap_Rate_W{week}_{year}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        doc = self._create_document(filepath)
        
        # Reset elements
        self.elements = []
        
        # ============ PAGE 1: MAIN REPORT ============
        # Add title and subtitle
        self._add_main_title("REPORTE SEMANAL DEL MÉTRICO DE SCRAP")
        subtitle_text = f"Semana {week} | Año {year} | Reporte generado automáticamente por Metric Scrap System"
        self._add_subtitle(subtitle_text)
        
        # Calculate target achievement
        within, total_rate, target_rate = self._calculate_target_achievement(df)
        self._add_target_header(within)
        
        # Build and add main table
        table_data = self._build_main_table_data(df, week)
        table = Table(table_data, repeatRows=1)
        
        table_style = get_main_table_style()
        apply_rate_conditional_coloring(table_style, table_data, rate_col_idx=7, target_col_idx=8)
        
        table.setStyle(table_style)
        self.elements.append(table)
        
        # ============ PAGE 2: CONTRIBUTORS ============
        if contributors_df is not None and not contributors_df.empty:
            self._add_page_break()
            
            self._add_section_title("TOP CONTRIBUIDORES DE SCRAP")
            subtitle_contributors = f"Semana {week} | Año {year} | Reporte generado automáticamente por Metric Scrap System"
            self._add_subtitle(subtitle_contributors)
            self._add_spacer(0.3)
            
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


def generate_weekly_pdf_report(df, contributors_df, week, year, scrap_df=None, locations_df=None, output_folder=WEEK_REPORTS_FOLDER):
    """
    Legacy function interface for backward compatibility
    
    Generates a weekly PDF report using the new architecture
    """
    generator = WeeklyPDFGenerator(output_folder)
    return generator.generate(df, contributors_df, week, year, scrap_df, locations_df)
