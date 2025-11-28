"""
report_thread.py - Thread worker para generación de reportes en background
"""

import os
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

# Para custom reports
try:
    from src.processors.custom_processor import process_custom_data
    from src.analysis.custom_contributors import get_custom_contributors
    from src.pdf.generators.custom import create_custom_report
except ImportError:
    process_custom_data = None
    get_custom_contributors = None
    create_custom_report = None


class ReportThread(QThread):
    """Thread worker para generar reportes en background"""
    progress_update = Signal(str)
    progress_percent = Signal(int)
    finished_success = Signal(str)
    finished_error = Signal(str)
    finished_warning = Signal(str)
    
    def __init__(self, report_type, year, **kwargs):
        super().__init__()
        self.report_type = report_type
        self.year = year
        self.kwargs = kwargs
    
    def run(self):
        try:
            self.progress_percent.emit(10)
            self.progress_update.emit("Cargando datos...")
            result = load_data()
            
            # load_data retorna una tupla (scrap_df, ventas_df, horas_df)
            # Verificar si el primer elemento es None para saber si falló
            if result[0] is None:
                self.finished_error.emit("No se pudieron cargar los datos del archivo Excel.")
                return
            
            scrap_df, ventas_df, horas_df = result
            
            if scrap_df is None:
                self.finished_error.emit("No se pudieron cargar los datos de Scrap.")
                return
            
            if scrap_df.empty:
                self.finished_error.emit("Los datos de Scrap están vacíos.")
                return
            
            self.progress_percent.emit(30)
            
            if self.report_type == "Semanal":
                self._generate_weekly(scrap_df, ventas_df, horas_df)
            elif self.report_type == "Mensual":
                self._generate_monthly(scrap_df, ventas_df, horas_df)
            elif self.report_type == "Trimestral":
                self._generate_quarterly(scrap_df, ventas_df, horas_df)
            elif self.report_type == "Anual":
                self._generate_annual(scrap_df, ventas_df, horas_df)
            elif self.report_type == "Personalizado":
                self._generate_custom(scrap_df, ventas_df, horas_df)
                
        except Exception as e:
            self.finished_error.emit(f"Error: {str(e)}")
    
    def _generate_weekly(self, scrap_df, ventas_df, horas_df):
        week = self.kwargs.get('week')
        self.progress_update.emit(f"Procesando datos semana {week}...")
        self.progress_percent.emit(50)
        
        weekly_data = process_weekly_data(scrap_df, ventas_df, horas_df, week, self.year)
        contributors = get_weekly_contributors(scrap_df, week, self.year)
        
        self.progress_percent.emit(70)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_weekly_pdf_report(weekly_data, contributors, week, self.year)
        
        self.progress_percent.emit(100)
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte de Semana {week} generado exitosamente.")
    
    def _generate_monthly(self, scrap_df, ventas_df, horas_df):
        month = self.kwargs.get('month')
        self.progress_update.emit(f"Procesando datos de {month}...")
        self.progress_percent.emit(40)
        
        monthly_data = process_monthly_data(scrap_df, ventas_df, horas_df, month, self.year)
        
        self.progress_percent.emit(60)
        self.progress_update.emit("Analizando contribuidores...")
        contributors = get_monthly_contributors(scrap_df, month, self.year)
        locations = get_monthly_location_contributors(scrap_df, month, self.year)
        
        self.progress_percent.emit(80)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_monthly_pdf_report(monthly_data, contributors, month, self.year, 
                                               scrap_df=scrap_df, locations_df=locations)
        
        self.progress_percent.emit(100)
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte de {month} generado exitosamente.")
    
    def _generate_quarterly(self, scrap_df, ventas_df, horas_df):
        quarter_raw = self.kwargs.get('quarter')
        
        # Convertir "Q1" a 1, "Q2" a 2, etc.
        if isinstance(quarter_raw, str) and quarter_raw.startswith('Q'):
            quarter = int(quarter_raw[1:])
        else:
            quarter = int(quarter_raw)
        
        self.progress_update.emit(f"Procesando datos del trimestre Q{quarter}...")
        self.progress_percent.emit(50)
        
        quarterly_data = process_quarterly_data(scrap_df, ventas_df, horas_df, quarter, self.year)
        contributors = get_quarterly_contributors(scrap_df, quarter, self.year)
        
        self.progress_percent.emit(70)
        self.progress_update.emit("Generando PDF...")
        filepath = generate_quarterly_pdf_report(quarterly_data, contributors, quarter, self.year, scrap_df=scrap_df)
        
        self.progress_percent.emit(100)
        
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
        
        # Abrir PDF automáticamente
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        
        self.finished_success.emit(f"Reporte Anual {self.year} generado exitosamente.")
    
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
