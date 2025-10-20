"""
custom_adapter.py - Adapter para generar PDF custom usando create_custom_report
"""
from pathlib import Path
from typing import Optional
from src.pdf_custom_generator import create_custom_report
import os
from datetime import datetime


class CustomPdfAdapter:
    def __init__(self, default_folder: Optional[str] = None):
        self.default_folder = default_folder

    def generate(self, df, contributors, meta: dict, output_folder: Optional[str] = None):
        start_date = meta.get('start_date')
        end_date = meta.get('end_date')
        reasons = meta.get('reasons_df')
        folder = output_folder or self.default_folder or 'reports'
        Path(folder).mkdir(parents=True, exist_ok=True)

        # Build a filename using start/end dates when available
        def fmt(dt):
            if dt is None:
                return 'unknown'
            if isinstance(dt, str):
                return dt.replace('-', '')
            if isinstance(dt, datetime):
                return dt.strftime('%Y%m%d')
            try:
                return dt.strftime('%Y%m%d')
            except Exception:
                return str(dt)

        start_tag = fmt(start_date)
        end_tag = fmt(end_date)
        filename = f"Scrap_Rate_Custom_{start_tag}_{end_tag}.pdf"
        filepath = os.path.join(folder, filename)

        # create_custom_report expects a file path
        create_custom_report(df, contributors, reasons, start_date, end_date, filepath)
        return filepath
