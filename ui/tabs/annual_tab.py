"""
annual_tab.py - Pestaña para reportes anuales con PySide6
"""

from PySide6.QtWidgets import QPushButton, QMessageBox, QHBoxLayout
from PySide6.QtCore import Qt

from ui.tabs.base_tab import BaseTab
from ui.report_thread import ReportThread


class AnnualTab(BaseTab):
    """Pestaña para generación de reportes anuales"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.thread = None
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña anual"""
        
        self.year_combobox = self.create_year_selector()
        
        self.progress_bar, self.status_label = self.create_progress_bar()
        
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
            year = int(self.year_combobox.currentText())
            
            if year < 2000 or year > 2100:
                QMessageBox.critical(self, "Error", "Ingrese un año válido")
                return
            
            self.show_progress(self.progress_bar, self.status_label, self.pdf_button, "⌛ Procesando...")
            
            self.thread = ReportThread('annual', year)
            self.thread.progress_update.connect(self.on_progress_update)
            self.thread.progress_percent.connect(lambda x: None)
            self.thread.finished_success.connect(lambda msg: self.on_success_unified(msg))
            self.thread.finished_error.connect(self.on_error)
            self.thread.finished_warning.connect(self.on_warning)
            self.thread.start()
        
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos")
    
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
