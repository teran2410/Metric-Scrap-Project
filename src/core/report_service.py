"""
report_service.py - Orquestador central para generación de reportes

Provee una interfaz simple para:
 - cargar datos (loader)
 - procesar datos (processor)
 - analizar contribuidores (analyzer)
 - generar PDF (pdf_adapter)

Cada dependencia se inyecta para facilitar pruebas y reemplazos.
"""

from datetime import datetime, timezone
import logging
from typing import Optional, Callable, Any, Dict

class ReportService:
    """Service que orquesta la generación de reportes.

    Esta versión es genérica: acepta callables para `processor` y `analyzer` y
    un `pdf_adapter` que implemente el método `generate(df, contributors, meta, output_folder)`.
    """

    def __init__(
        self,
        loader: Any,
        processor_callable: Callable[..., Any],
        analyzer_callable: Callable[..., Any],
        pdf_adapter: Any,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.loader = loader
        self.processor = processor_callable
        self.analyzer = analyzer_callable
        self.pdf_adapter = pdf_adapter
        self.logger = logger or logging.getLogger(__name__)

    def run_report(self, period_params: Dict[str, Any], output_folder: Optional[str] = None) -> Optional[str]:
        """Orquesta la ejecución de un reporte genérico.

        Args:
            period_params: diccionario con parámetros para el processor (ej. {'week': 12, 'year': 2025})
            output_folder: carpeta destino (opcional)

        Returns:
            Ruta al PDF generado o None
        """
        self.logger.info("Starting report with params=%s", period_params)

        # Cargar datos usando el loader inyectado
        scrap_df, ventas_df, horas_df = self.loader.load_data()
        if scrap_df is None:
            self.logger.error("No scrap data loaded")
            return None

        # Ejecutar el processor callable. Se espera que devuelva un DataFrame o None
        try:
            result = self.processor(scrap_df, ventas_df, horas_df, **period_params)
        except TypeError:
            # Si el processor requiere firma distinta (ej. solo scrap_df + params), reintentar con scrap_df primero
            result = self.processor(scrap_df, **period_params)

        if result is None:
            self.logger.warning("Processor returned no result for params=%s", period_params)
            return None

        # Ejecutar el analyzer callable (puede ser None)
        contributors = None
        try:
            # Normalize period keys for analyzers: if 'week_number' provided, also
            # offer it as 'week' to support existing analyzer signatures.
            analyzer_params = {k: v for k, v in period_params.items() if k in ('year', 'week', 'month', 'quarter', 'start_date', 'end_date', 'week_number')}
            if 'week_number' in analyzer_params and 'week' not in analyzer_params:
                analyzer_params['week'] = analyzer_params['week_number']
            contributors = self.analyzer(scrap_df, **analyzer_params)
        except Exception:
            # Algunos analyzers esperan firma diferente; silenciar y continuar
            try:
                contributors = self.analyzer(scrap_df)
            except Exception:
                contributors = None

        meta = {
            **period_params,
            "generated_at": datetime.now(timezone.utc),
            "scrap_df": scrap_df,
            "ventas_df": ventas_df,
            "horas_df": horas_df,
        }

        # Generar PDF
        filepath = self.pdf_adapter.generate(result, contributors, meta, output_folder)
        self.logger.info("Report generated: %s", filepath)
        return filepath

    # Compatibilidad: wrapper para reportes anuales si se necesita
    def run_annual_report(self, year: int, output_folder: Optional[str] = None) -> Optional[str]:
        return self.run_report({'year': year}, output_folder)
