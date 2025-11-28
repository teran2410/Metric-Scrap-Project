"""
custom_tab.py - Pestaña para reportes personalizados con PySide6
"""

from PySide6.QtWidgets import (
    QLabel, QDateEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import QDate, Qt
from datetime import datetime

from ui.tabs.base_tab import BaseTab
from ui.report_thread import ReportThread


class CustomReportThread(QThread):
    """Thread para generar reporte personalizado sin bloquear UI"""
    
    progress_update = Signal(str)
    finished_success = Signal(str)
    finished_error = Signal(str)
    finished_warning = Signal(str)
    
    def __init__(self, root_app, start_date, end_date):
        super().__init__()
        self.root_app = root_app
        self.start_date = start_date
        self.end_date = end_date
    
    def run(self):
        """Ejecuta la generación del PDF en background"""
        try:
            self.progress_update.emit("⌛ Cargando datos...")
            
            service = getattr(self.root_app, 'report_service_custom', None)
            if service:
                filepath = service.run_report({
                    'start_date': self.start_date.strftime('%Y-%m-%d'),
                    'end_date': self.end_date.strftime('%Y-%m-%d')
                })
                if filepath:
                    self.finished_success.emit(filepath)
                    return
            
            scrap_df, ventas_df, horas_df = load_data()
            if scrap_df is None:
                self.finished_error.emit("No se pudo cargar el archivo.\nVerifique que 'test pandas.xlsx' exista en la carpeta 'data/'")
                return
            
            self.progress_update.emit("⚙️ Procesando datos...")
            result = process_custom_data(scrap_df, ventas_df, horas_df, self.start_date, self.end_date)
            
            if result is None:
                self.finished_warning.emit(f"No se encontraron datos para el período:\n{self.start_date.strftime('%Y-%m-%d')} a {self.end_date.strftime('%Y-%m-%d')}")
                return
            
            self.progress_update.emit("🔍 Analizando contribuidores...")
            contributors = get_custom_contributors(scrap_df, self.start_date, self.end_date, top_n=10)
            
            self.progress_update.emit("📄 Generando PDF...")
            # Nota: create_custom_report espera (data_df, contributors_df, reasons_df, start_date, end_date, output_path)
            # Asumiendo que result tiene la información necesaria y contributors es el DataFrame
            filepath = create_custom_report(result, contributors, contributors, self.start_date, self.end_date, None)
            
            if filepath:
                self.finished_success.emit(filepath)
            else:
                self.finished_error.emit("No se pudo generar el PDF")
        
        except Exception as e:
            self.finished_error.emit(f"Ocurrió un error:\n\n{str(e)}")


class CustomTab(BaseTab):
    """Pestaña para generación de reportes personalizados por rango de fechas"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.thread = None
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña personalizada"""
        
        # Fecha inicio
        start_label = QLabel("📅 Fecha Inicio:")
        start_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.main_layout.addWidget(start_label)
        
        self.start_date = QDateEdit()
        self.start_date.setFixedWidth(220)
        self.start_date.setFixedHeight(38)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        
        start_layout = QHBoxLayout()
        start_layout.addStretch()
        start_layout.addWidget(self.start_date)
        start_layout.addStretch()
        self.main_layout.addLayout(start_layout)
        
        # Fecha fin
        end_label = QLabel("📅 Fecha Fin:")
        end_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.main_layout.addWidget(end_label)
        
        self.end_date = QDateEdit()
        self.end_date.setFixedWidth(220)
        self.end_date.setFixedHeight(38)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())
        
        end_layout = QHBoxLayout()
        end_layout.addStretch()
        end_layout.addWidget(self.end_date)
        end_layout.addStretch()
        self.main_layout.addLayout(end_layout)
        
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
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un thread separado"""
        try:
            # Convertir QDate a datetime
            start_qdate = self.start_date.date()
            end_qdate = self.end_date.date()
            
            start_dt = datetime(start_qdate.year(), start_qdate.month(), start_qdate.day())
            end_dt = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day())
            
            # Validaciones
            if start_dt > end_dt:
                QMessageBox.critical(self, "Error", "La fecha de inicio debe ser anterior a la fecha de fin")
                return
            
            if end_dt > datetime.now():
                QMessageBox.critical(self, "Error", "La fecha de fin no puede ser futura")
                return
            
            self.show_progress(self.progress_bar, self.status_label, self.pdf_button, "⌛ Procesando...")
            
            self.thread = ReportThread('custom', start_dt.year, start_date=start_dt, end_date=end_dt)
            self.thread.progress_update.connect(self.on_progress_update)
            self.thread.progress_percent.connect(lambda x: None)
            self.thread.finished_success.connect(lambda msg: self.on_success_unified(msg))
            self.thread.finished_error.connect(self.on_error)
            self.thread.finished_warning.connect(self.on_warning)
            self.thread.start()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar generación:\n\n{str(e)}")
    
    def on_progress_update(self, message):
        self.status_label.setText(message)
    
    def on_success_unified(self, message):
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.information(self, "Éxito", message)
    
    def on_error(self, message):
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.critical(self, "Error", message)
    
    def on_warning(self, message):
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.warning(self, "Sin datos", message)
