"""
weekly_tab.py - Pestaña para reportes semanales con PySide6
"""

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
import os

from ui.tabs.base_tab import BaseTab
from ui.report_thread import ReportThread


class WeeklyReportThread(QThread):
    """Thread para generar reporte semanal sin bloquear UI"""
    
    # Signals
    progress_update = Signal(str)
    finished_success = Signal(str)
    finished_error = Signal(str)
    finished_warning = Signal(str)
    
    def __init__(self, root_app, week, year):
        super().__init__()
        self.root_app = root_app
        self.week = week
        self.year = year
    
    def run(self):
        """Ejecuta la generación del PDF en background"""
        try:
            self.progress_update.emit("⌛ Cargando datos...")
            
            service = getattr(self.root_app, 'report_service_weekly', None)
            if service:
                filepath = service.run_report({'week': self.week, 'year': self.year})
                if filepath:
                    self.finished_success.emit(filepath)
                    return
            
            scrap_df, ventas_df, horas_df = load_data()
            if scrap_df is None:
                self.finished_error.emit("No se pudo cargar el archivo.\nVerifique que 'test pandas.xlsx' exista en la carpeta 'data/'")
                return
            
            self.progress_update.emit("⚙️ Procesando datos...")
            result = process_weekly_data(scrap_df, ventas_df, horas_df, self.week, self.year)
            
            if result is None:
                self.finished_warning.emit(f"No se encontraron datos para:\n\nSemana: {self.week}\nAño: {self.year}")
                return
            
            self.progress_update.emit("🔍 Analizando contribuidores...")
            contributors = export_contributors_to_console(scrap_df, self.week, self.year, top_n=10)
            locations = get_weekly_location_contributors(scrap_df, self.week, self.year, top_n=10)
            
            self.progress_update.emit("📄 Generando PDF...")
            filepath = generate_weekly_pdf_report(
                result, contributors, self.week, self.year, scrap_df, locations
            )
            
            if filepath:
                self.finished_success.emit(filepath)
            else:
                self.finished_error.emit("No se pudo generar el PDF")
        
        except Exception as e:
            self.finished_error.emit(f"Ocurrió un error:\n\n{str(e)}")


class WeeklyTab(BaseTab):
    """Pestaña para generación de reportes semanales"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.thread = None
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña semanal"""
        
        # Selector de año
        self.year_combobox = self.create_year_selector(on_change=self.on_year_change)
        
        # Campo de entrada de semana
        week_label = QLabel("Semana:")
        week_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.main_layout.addWidget(week_label)
        
        self.week_entry = QLineEdit()
        self.week_entry.setFixedWidth(220)
        self.week_entry.setFixedHeight(38)
        self.week_entry.setPlaceholderText("Ingrese la semana (1-53)")
        self.week_entry.setAlignment(Qt.AlignCenter)
        
        # Centrar el entry
        entry_layout = QHBoxLayout()
        entry_layout.addStretch()
        entry_layout.addWidget(self.week_entry)
        entry_layout.addStretch()
        self.main_layout.addLayout(entry_layout)
        
        # Barra de progreso
        self.progress_bar, self.status_label = self.create_progress_bar()
        
        # Botón generar PDF
        self.pdf_button = QPushButton("📄 Generar Reporte PDF")
        self.pdf_button.setFixedSize(240, 45)
        self.pdf_button.setCursor(Qt.PointingHandCursor)
        self.pdf_button.clicked.connect(self.start_pdf_generation)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.pdf_button)
        button_layout.addStretch()
        self.main_layout.addLayout(button_layout)
    
    def on_year_change(self, selected_year):
        """Callback cuando cambia el año seleccionado"""
        pass
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un thread separado"""
        try:
            year = int(self.year_combobox.currentText())
            week_str = self.week_entry.text().strip()
            
            if not week_str:
                QMessageBox.critical(self, "Error", "Ingrese una semana válida")
                return
            
            if not week_str.isdigit():
                QMessageBox.critical(self, "Error", "La semana debe ser un número")
                return
            
            week = int(week_str)
            
            if week < 1 or week > 53:
                QMessageBox.critical(self, "Error", "La semana debe estar entre 1 y 53")
                return
            
            if year < 2000 or year > 2100:
                QMessageBox.critical(self, "Error", "Ingrese un año válido")
                return
            
            # Mostrar progreso
            self.show_progress(self.progress_bar, self.status_label, self.pdf_button, "⌛ Procesando...")
            
            # Crear y conectar thread unificado
            self.thread = ReportThread('weekly', year, week=week)
            self.thread.progress_update.connect(self.on_progress_update)
            self.thread.progress_percent.connect(lambda x: None)  # Ignorar porcentaje
            self.thread.finished_success.connect(lambda msg: self.on_success_unified(msg))
            self.thread.finished_error.connect(self.on_error)
            self.thread.finished_warning.connect(self.on_warning)
            self.thread.start()
        
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos")
    
    def on_progress_update(self, message):
        """Actualiza el mensaje de progreso"""
        self.status_label.setText(message)
    
    def on_success_unified(self, message):
        """Maneja la finalización exitosa del thread unificado"""
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.information(self, "Éxito", message)
    
    def on_error(self, message):
        """Maneja errores"""
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.critical(self, "Error", message)
    
    def on_warning(self, message):
        """Maneja advertencias (sin datos)"""
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.warning(self, "Sin datos", message)
