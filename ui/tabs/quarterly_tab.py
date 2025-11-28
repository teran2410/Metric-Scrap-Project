"""
quarterly_tab.py - Pestaña para reportes trimestrales con PySide6
"""

from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from datetime import datetime

from ui.tabs.base_tab import BaseTab
from ui.report_thread import ReportThread


class QuarterlyTab(BaseTab):
    """Pestaña para generación de reportes trimestrales"""
    
    QUARTERS = {
        1: "Q1 - Enero a Marzo",
        2: "Q2 - Abril a Junio",
        3: "Q3 - Julio a Septiembre",
        4: "Q4 - Octubre a Diciembre"
    }
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_quarter = (datetime.now().month - 1) // 3 + 1
        self.thread = None
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña trimestral"""
        
        self.year_combobox = self.create_year_selector(on_change=self.on_year_change)
        
        quarter_label = QLabel("Trimestre:")
        quarter_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.main_layout.addWidget(quarter_label)
        
        self.quarter_combobox = QComboBox()
        self.quarter_combobox.setFixedWidth(220)
        self.quarter_combobox.setFixedHeight(38)
        
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()
        combo_layout.addWidget(self.quarter_combobox)
        combo_layout.addStretch()
        self.main_layout.addLayout(combo_layout)
        
        self.update_quarters_for_year(self.current_year)
        
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
    
    def on_year_change(self, selected_year):
        self.update_quarters_for_year(int(selected_year))
    
    def update_quarters_for_year(self, year):
        """Actualiza los trimestres disponibles según el año"""
        current_date = datetime.now()
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1
        
        if year < current_year:
            max_quarter = 4
        elif year == current_year:
            max_quarter = current_quarter
        else:
            max_quarter = 0
        
        quarters_list = [f"{q} - {self.QUARTERS[q].split(' - ')[1]}" for q in range(1, max_quarter + 1)]
        self.quarter_combobox.clear()
        self.quarter_combobox.addItems(quarters_list)
        
        if quarters_list:
            self.quarter_combobox.setCurrentText(f"{max_quarter} - {self.QUARTERS[max_quarter].split(' - ')[1]}")
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un thread separado"""
        try:
            year = int(self.year_combobox.currentText())
            quarter_str = self.quarter_combobox.currentText()
            
            if not quarter_str:
                QMessageBox.critical(self, "Error", "Seleccione un trimestre válido")
                return
            
            quarter = int(quarter_str.split(" - ")[0])
            
            if quarter < 1 or quarter > 4:
                QMessageBox.critical(self, "Error", "El trimestre debe estar entre 1 y 4")
                return
            
            if year < 2000 or year > 2100:
                QMessageBox.critical(self, "Error", "Ingrese un año válido")
                return
            
            self.show_progress(self.progress_bar, self.status_label, self.pdf_button, "⌛ Procesando...")
            
            self.thread = ReportThread('quarterly', year, quarter=quarter)
            self.thread.progress_update.connect(self.on_progress_update)
            self.thread.progress_percent.connect(lambda x: None)  # Ignorar porcentaje
            self.thread.finished_success.connect(self.on_success)
            self.thread.finished_error.connect(self.on_error)
            self.thread.finished_warning.connect(self.on_warning)
            self.thread.start()
        
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos")
    
    def on_progress_update(self, message):
        self.status_label.setText(message)
    
    def on_success(self, filepath):
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.information(self, "Éxito", f"El archivo [{os.path.basename(filepath)}]\n\n se ha generado exitosamente.")
        
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                import subprocess
                opener = 'open' if os.uname().sysname == 'Darwin' else 'xdg-open'
                subprocess.run([opener, filepath])
        except:
            pass
    
    def on_error(self, message):
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.critical(self, "Error", message)
    
    def on_warning(self, message):
        self.hide_progress(self.progress_bar, self.status_label, self.pdf_button)
        QMessageBox.warning(self, "Sin datos", message)
