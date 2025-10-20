"""
monthly_adapter.py - Adapter para generar PDF mensual usando generate_monthly_pdf_report
"""
from pathlib import Path
from typing import Optional
from src.pdf_monthly_generator import generate_monthly_pdf_report, MONTHS_NUM_TO_ES

class MonthlyPdfAdapter:
    def __init__(self, default_folder: Optional[str] = None):
        self.default_folder = default_folder

    def generate(self, df, contributors, meta: dict, output_folder: Optional[str] = None):
        month = meta.get('month')
        year = meta.get('year')

        # Use a sensible default folder if none provided; generator uses 'reports' by default
        folder = output_folder or self.default_folder or 'reports'
        Path(folder).mkdir(parents=True, exist_ok=True)

        return generate_monthly_pdf_report(
            df,
            contributors,
            month,
            year,
            scrap_df=meta.get('scrap_df'),
            locations_df=meta.get('locations_df'),
            output_folder=folder
        )
