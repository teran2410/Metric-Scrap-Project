"""
report_thread.py - Thread worker para generación de reportes en background
"""

import os
import logging
from PySide6.QtCore import QThread, Signal

from src.processors.data_loader import load_data
from src.processors.weekly_processor import process_weekly_data
from src.processors.monthly_processor import process_monthly_data
from src.processors.quarterly_processor import process_quarterly_data
from src.processors.annual_processor import process_annual_data

from src.analysis.weekly_contributors import get_weekly_contributors
from src.analysis.monthly_contributors import get_monthly_contributors, get_monthly_location_contributors
from src.analysis.quarterly_contributors import get_quarterly_contributors
from src.analysis.annual_contributors import get_annual_contributors

# New PDF generators (refactored architecture)
from src.pdf.generators.weekly import generate_weekly_pdf_report
from src.pdf.generators.monthly import generate_monthly_pdf_report
from src.pdf.generators.quarterly import generate_quarterly_pdf_report
from src.pdf.generators.annual import generate_annual_pdf_report

# Period comparison
from src.analysis.period_comparison import compare_weekly_periods, compare_monthly_periods, compare_quarterly_periods

# Para custom reports
try:
    from src.processors.custom_processor import process_custom_data
    from src.analysis.custom_contributors import get_custom_contributors
    from src.pdf.generators.custom import create_custom_report
except ImportError:
    process_custom_data = None
    get_custom_contributors = None
    create_custom_report = None

from src.utils.exceptions import MetricScrapError
from src.utils.report_history import get_report_history_manager
from config import MONTHS_NUM_TO_ES

logger = logging.getLogger(__name__)


class ReportThread(QThread):
    """Thread worker para generar reportes en background"""
    progress_update = Signal(str)
    progress_percent = Signal(int)
    finished_success = Signal(str)
    finished_error = Signal(str)
    finished_warning = Signal(str)
    finished_exception = Signal(object)  # Nueva señal para excepciones completas
    
    def __init__(self, report_type, year, **kwargs):
        super().__init__()
        self.report_type = report_type
        self.year = year
        self.kwargs = kwargs
    
    def run(self):
        try:
            self.progress_percent.emit(10)
            self.progress_update.emit("Cargando datos...")
            
            scrap_df, ventas_df, horas_df, validation_result = load_data()
            
            if scrap_df.empty:
                self.finished_warning.emit("Los datos de Scrap están vacíos.")
                return
            
            self.progress_percent.emit(30)
            
            if self.report_type in ("Semanal", "weekly"):
                self._generate_weekly(scrap_df, ventas_df, horas_df)
            elif self.report_type in ("Mensual", "monthly"):
                self._generate_monthly(scrap_df, ventas_df, horas_df)
            elif self.report_type in ("Trimestral", "quarterly"):
                self._generate_quarterly(scrap_df, ventas_df, horas_df)
            elif self.report_type in ("Anual", "annual"):
                self._generate_annual(scrap_df, ventas_df, horas_df)
            elif self.report_type == "Personalizado":
                self._generate_custom(scrap_df, ventas_df, horas_df)
                
        except MetricScrapError as e:
            # Capturar excepciones personalizadas y enviarlas completas a la UI
            logger.error(f"Error en generación de reporte: {e.get_technical_details()}", exc_info=True)
            self.finished_exception.emit(e)
        except Exception as e:
            # Capturar cualquier otro error inesperado
            logger.error(f"Error inesperado en ReportThread: {str(e)}", exc_info=True)
            self.finished_exception.emit(e)
    
    def _generate_weekly(self, scrap_df, ventas_df, horas_df):
        week = self.kwargs.get('week')
        include_comparison = self.kwargs.get('include_comparison', False)
        
        self.progress_update.emit(f"Procesando datos semana {week}...")
        self.progress_percent.emit(50)
        
        weekly_data = process_weekly_data(scrap_df, ventas_df, horas_df, week, self.year)
        contributors = get_weekly_contributors(scrap_df, week, self.year)
        
        # Generar comparación si se solicitó
        comparison = None
        if include_comparison:
            self.progress_update.emit("Comparando con semana anterior...")
            comparison = compare_weekly_periods(scrap_df, ventas_df, horas_df, week, self.year)
            if comparison:
                logger.info(f"Comparación generada: {comparison.period_label} vs {comparison.previous_label}")
            else:
                logger.warning("No hay datos suficientes para comparar con semana anterior")
        
        self.progress_percent.emit(70)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_weekly_pdf_report(weekly_data, contributors, week, self.year, 
                                             scrap_df=scrap_df, locations_df=None, comparison=comparison)
        
        self.progress_percent.emit(100)
        
        # Registrar en historial
        if filepath and os.path.exists(filepath):
            history_manager = get_report_history_manager()
            history_manager.add_report(filepath, "Semanal", f"Semana {week}/{self.year}")
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte de Semana {week} generado exitosamente.")
    
    def _generate_monthly(self, scrap_df, ventas_df, horas_df):
        month = self.kwargs.get('month')
        include_comparison = self.kwargs.get('include_comparison', False)
        
        # Convertir número de mes a nombre en español
        month_name = MONTHS_NUM_TO_ES.get(month, f"Mes {month}")
        
        self.progress_update.emit(f"Procesando datos de {month_name}...")
        self.progress_percent.emit(40)
        
        monthly_data = process_monthly_data(scrap_df, ventas_df, horas_df, month, self.year)
        
        if monthly_data is None or monthly_data.empty:
            raise MetricScrapError(f"No se encontraron datos para {month_name} {self.year}")
        
        self.progress_percent.emit(60)
        self.progress_update.emit("Analizando contribuidores...")
        contributors = get_monthly_contributors(scrap_df, month, self.year)
        locations = get_monthly_location_contributors(scrap_df, month, self.year)
        
        # Generar comparación si se solicitó
        comparison = None
        if include_comparison:
            self.progress_update.emit("Comparando con mes anterior...")
            comparison = compare_monthly_periods(scrap_df, ventas_df, horas_df, month, self.year)
            if comparison:
                logger.info(f"Comparación generada: {comparison.period_label} vs {comparison.previous_label}")
            else:
                logger.warning("No hay datos suficientes para comparar con mes anterior")
        
        self.progress_percent.emit(80)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_monthly_pdf_report(monthly_data, contributors, month, self.year, 
                                               scrap_df=scrap_df, locations_df=locations, comparison=comparison)
        
        self.progress_percent.emit(100)
        
        # Registrar en historial
        if filepath and os.path.exists(filepath):
            history_manager = get_report_history_manager()
            history_manager.add_report(filepath, "Mensual", f"{month_name} {self.year}")
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte de {month_name} generado exitosamente.")
    
    def _generate_quarterly(self, scrap_df, ventas_df, horas_df):
        quarter_raw = self.kwargs.get('quarter')
        include_comparison = self.kwargs.get('include_comparison', False)
        
        # Convertir "Q1" a 1, "Q2" a 2, etc.
        if isinstance(quarter_raw, str) and quarter_raw.startswith('Q'):
            quarter = int(quarter_raw[1:])
        else:
            quarter = int(quarter_raw)
        
        self.progress_update.emit(f"Procesando datos del trimestre Q{quarter}...")
        self.progress_percent.emit(50)
        
        quarterly_data = process_quarterly_data(scrap_df, ventas_df, horas_df, quarter, self.year)
        contributors = get_quarterly_contributors(scrap_df, quarter, self.year)
        
        # Generar comparación si se solicitó
        comparison = None
        if include_comparison:
            self.progress_update.emit("Comparando con trimestre anterior...")
            comparison = compare_quarterly_periods(scrap_df, ventas_df, horas_df, quarter, self.year)
            if comparison:
                logger.info(f"Comparación generada: {comparison.period_label} vs {comparison.previous_label}")
            else:
                logger.warning("No hay datos suficientes para comparar con trimestre anterior")
        
        self.progress_percent.emit(70)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_quarterly_pdf_report(quarterly_data, contributors, quarter, self.year, 
                                                scrap_df=scrap_df, comparison=comparison)
        
        self.progress_percent.emit(100)
        
        # Registrar en historial
        if filepath and os.path.exists(filepath):
            history_manager = get_report_history_manager()
            history_manager.add_report(filepath, "Trimestral", f"Q{quarter} {self.year}")
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte de Q{quarter} generado exitosamente.")
    
    def _generate_annual(self, scrap_df, ventas_df, horas_df):
        self.progress_update.emit(f"Procesando datos del año {self.year}...")
        self.progress_percent.emit(50)
        
        annual_data = process_annual_data(scrap_df, ventas_df, horas_df, self.year)
        contributors = get_annual_contributors(scrap_df, self.year)
        
        self.progress_percent.emit(70)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_annual_pdf_report(annual_data, contributors, self.year, scrap_df, ventas_df, horas_df)
        
        self.progress_percent.emit(100)
        
        # Registrar en historial
        if filepath and os.path.exists(filepath):
            history_manager = get_report_history_manager()
            history_manager.add_report(filepath, "Anual", f"Año {self.year}")
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte anual {self.year} generado exitosamente.")
    
    def _generate_custom(self, scrap_df, ventas_df, horas_df):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        self.progress_update.emit(f"Procesando datos personalizados...")
        self.progress_percent.emit(50)
        
        custom_data = process_custom_data(scrap_df, ventas_df, horas_df, start_date, end_date)
        contributors = get_custom_contributors(scrap_df, start_date, end_date)
        
        self.progress_percent.emit(70)
        self.progress_update.emit("Generando PDF...")
        filepath = create_custom_report(custom_data, contributors, start_date, end_date)
        
        self.progress_percent.emit(100)
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit("Reporte personalizado generado exitosamente.")
