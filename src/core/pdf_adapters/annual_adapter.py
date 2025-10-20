"""
annual_adapter.py - Adapter para generar PDF anual usando el generador existente
"""
import os
from pathlib import Path
from typing import Optional

from src.pdf_annual_generator import generate_annual_pdf_report


class AnnualPdfAdapter:
    def __init__(self, default_folder: Optional[str] = None):
        self.default_folder = default_folder

    def generate(self, df, contributors, meta: dict, output_folder: Optional[str] = None):
        """Genera un PDF anual usando la función existente generate_annual_pdf_report.

        Args:
            df: DataFrame procesado (resultado)
            contributors: DataFrame de contribuidores
            meta: diccionario con claves: year, scrap_df, ventas_df, horas_df
            output_folder: carpeta destino (si None usa self.default_folder o la configuración interna)

        Returns:
            Ruta al archivo PDF generado
        """
        year = meta.get("year")
        scrap_df = meta.get("scrap_df")
        ventas_df = meta.get("ventas_df")
        horas_df = meta.get("horas_df")

        # Determinar carpeta final
        folder = output_folder or self.default_folder or 'reports'
        Path(folder).mkdir(parents=True, exist_ok=True)

        # Llamar al generador existente
        return generate_annual_pdf_report(df, contributors, year, scrap_df, ventas_df, horas_df, output_folder=folder)
