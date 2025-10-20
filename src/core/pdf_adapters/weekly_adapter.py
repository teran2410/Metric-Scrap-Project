"""
weekly_adapter.py - Adapter para generar PDF semanal usando generate_weekly_pdf_report
"""
from pathlib import Path
from typing import Optional
from src.pdf_weekly_generator import generate_weekly_pdf_report, WEEK_REPORTS_FOLDER


class WeeklyPdfAdapter:
    def __init__(self, default_folder: Optional[str] = None):
        self.default_folder = default_folder

    def generate(self, df, contributors, meta: dict, output_folder: Optional[str] = None):
        week = meta.get('week') or meta.get('W') or meta.get('week_number')
        year = meta.get('year')
        locations = meta.get('locations_df')

        folder = output_folder or self.default_folder or WEEK_REPORTS_FOLDER
        Path(folder).mkdir(parents=True, exist_ok=True)

        return generate_weekly_pdf_report(
            df,
            contributors,
            week,
            year,
            scrap_df=meta.get('scrap_df'),
            locations_df=locations,
            output_folder=folder
        )
