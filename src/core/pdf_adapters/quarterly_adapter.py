"""
quarterly_adapter.py - Adapter para generar PDF trimestral usando generate_quarterly_pdf_report
"""
from pathlib import Path
from typing import Optional
from src.pdf_quarterly_generator import generate_quarterly_pdf_report


class QuarterlyPdfAdapter:
    def __init__(self, default_folder: Optional[str] = None):
        self.default_folder = default_folder

    def generate(self, df, contributors, meta: dict, output_folder: Optional[str] = None):
        quarter = meta.get('quarter')
        year = meta.get('year')

        folder = output_folder or self.default_folder or 'reports'
        Path(folder).mkdir(parents=True, exist_ok=True)

        return generate_quarterly_pdf_report(
            df,
            contributors,
            quarter,
            year,
            scrap_df=meta.get('scrap_df'),
            output_folder=folder
        )
