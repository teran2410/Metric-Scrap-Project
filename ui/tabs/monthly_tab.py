"""
monthly_tab.py - Pestaña para reportes mensuales con PySide6
"""

from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from datetime import datetime
import os

from ui.tabs.base_tab import BaseTab
from ui.report_thread import ReportThread
from config import MONTHS_NUM_TO_ES


class MonthlyTab(BaseTab):
    """Pestaña para generación de reportes mensuales"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_month = datetime.now().month
        self.thread = None
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de la pestaña mensual"""
        
        # Selector de año
        self.year_combobox = self.create_year_selector(on_change=self.on_year_change)
        
        # Selector de mes
        month_label = QLabel("Mes:")
        month_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.main_layout.addWidget(month_label)
        
        self.month_combobox = QComboBox()
        self.month_combobox.setFixedWidth(220)
        self.month_combobox.setFixedHeight(38)
        
        # Centrar el combo
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()
        combo_layout.addWidget(self.month_combobox)
        combo_layout.addStretch()
        self.main_layout.addLayout(combo_layout)
        
        # Actualizar meses disponibles
        self.update_months_for_year(self.current_year)
        
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
        self.update_months_for_year(int(selected_year))
    
    def update_months_for_year(self, year):
        """Actualiza los meses disponibles según el año"""
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        if year < current_year:
            max_month = 12
        elif year == current_year:
            max_month = current_month
        else:
            max_month = 0
        
        months_list = [f"{month:02d} - {MONTHS_NUM_TO_ES[month]}" for month in range(1, max_month + 1)]
        self.month_combobox.clear()
        self.month_combobox.addItems(months_list)
        
        if months_list:
            self.month_combobox.setCurrentText(f"{max_month:02d} - {MONTHS_NUM_TO_ES[max_month]}")
    
    def start_pdf_generation(self):
        """Inicia la generación del PDF en un thread separado"""
        try:
            year = int(self.year_combobox.currentText())
            month_str = self.month_combobox.currentText()
            
            if not month_str:
                QMessageBox.critical(self, "Error", "Seleccione un mes válido")
                return
            
            month = int(month_str.split(" - ")[0])
            
            # Validaciones
            if month < 1 or month > 12:
                QMessageBox.critical(self, "Error", "El mes debe estar entre 1 y 12")
                return
            
            if year < 2000 or year > 2100:
                QMessageBox.critical(self, "Error", "Ingrese un año válido")
                return
            
            # Mostrar progreso
            self.show_progress(self.progress_bar, self.status_label, self.pdf_button, "⌛ Procesando...")
            
            # Crear y conectar thread unificado
            self.thread = ReportThread('monthly', year, month=month)
            self.thread.progress_update.connect(self.on_progress_update)
            self.thread.progress_percent.connect(lambda x: None)
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
