"""
base_tab.py - Clase base para las pestañas con PySide6
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, 
    QProgressBar, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime


class BaseTab(QWidget):
    """Clase base para las pestañas de la aplicación"""
    
    def __init__(self, parent=None):
        """
        Inicializa la pestaña base
        
        Args:
            parent: Widget padre (la ventana principal)
        """
        super().__init__(parent)
        self.root_app = parent
        self.current_year = datetime.now().year
        # Use ISO week number for consistency with processors (1-53)
        try:
            self.current_week = int(datetime.now().isocalendar()[1])
        except Exception:
            self.current_week = int(datetime.now().strftime('%U'))
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(30, 25, 30, 25)
        self.main_layout.setSpacing(15)
    
    def create_year_selector(self, on_change=None):
        """
        Crea un selector de año reutilizable
        
        Args:
            on_change: Función callback cuando cambia el año
            
        Returns:
            QComboBox: ComboBox del año
        """
        year_label = QLabel("Año:")
        year_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.main_layout.addWidget(year_label)
        
        year_combo = QComboBox()
        year_combo.setFixedWidth(220)
        year_combo.setFixedHeight(38)
        years_list = [str(year) for year in range(2023, self.current_year + 1)]
        year_combo.addItems(years_list)
        year_combo.setCurrentText(str(self.current_year))
        
        if on_change:
            year_combo.currentTextChanged.connect(on_change)
        
        # Centrar el combo
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()
        combo_layout.addWidget(year_combo)
        combo_layout.addStretch()
        self.main_layout.addLayout(combo_layout)
        
        return year_combo
    
    def create_progress_bar(self):
        """
        Crea una barra de progreso reutilizable
        
        Returns:
            tuple: (progress_bar, status_label)
        """
        status_label = QLabel("")
        status_label.setStyleSheet("font-size: 11pt; color: #7A7A7A; font-weight: 500;")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.hide()
        
        progress_bar = QProgressBar()
        progress_bar.setFixedWidth(280)
        progress_bar.setFixedHeight(8)
        progress_bar.setTextVisible(False)
        progress_bar.hide()
        
        # Layouts centrados
        label_layout = QHBoxLayout()
        label_layout.addStretch()
        label_layout.addWidget(status_label)
        label_layout.addStretch()
        
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(progress_bar)
        progress_layout.addStretch()
        
        self.main_layout.addLayout(label_layout)
        self.main_layout.addLayout(progress_layout)
        
        return progress_bar, status_label
    
    def show_progress(self, progress_bar, status_label, button, message):
        """
        Muestra la barra de progreso
        
        Args:
            progress_bar: Barra de progreso
            status_label: Label de estado
            button: Botón a deshabilitar
            message (str): Mensaje a mostrar
        """
        status_label.setText(message)
        status_label.show()
        progress_bar.setRange(0, 0)  # Modo indeterminado
        progress_bar.show()
        button.setEnabled(False)
    
    def hide_progress(self, progress_bar, status_label, button):
        """
        Oculta la barra de progreso
        
        Args:
            progress_bar: Barra de progreso
            status_label: Label de estado
            button: Botón a habilitar
        """
        progress_bar.hide()
        status_label.hide()
        button.setEnabled(True)

