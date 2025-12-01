"""
launcher_dialog.py - Ventana inicial de selección con precarga de datos
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class DataPreloadThread(QThread):
    """Thread para precargar datos en background"""
    
    finished = Signal(bool)  # True si cargó correctamente, False si error
    progress = Signal(int, str)  # (porcentaje, mensaje)
    
    def run(self):
        """Precarga los datos del Excel"""
        try:
            self.progress.emit(10, "Iniciando carga de datos...")
            
            from src.processors.data_loader import load_data
            
            self.progress.emit(30, "Cargando hoja de Scrap...")
            
            # Cargar datos con force_reload para asegurar datos frescos
            scrap_df, ventas_df, horas_df, status = load_data(
                force_reload=True, 
                validate=False
            )
            
            self.progress.emit(60, "Cargando hoja de Ventas...")
            
            if scrap_df is None or ventas_df is None or horas_df is None:
                logger.error("Error cargando datos: uno o más DataFrames son None")
                self.finished.emit(False)
                return
            
            self.progress.emit(90, "Validando datos cargados...")
            
            logger.info(f"Datos precargados exitosamente:")
            logger.info(f"  - Scrap: {len(scrap_df)} registros")
            logger.info(f"  - Ventas: {len(ventas_df)} registros")
            logger.info(f"  - Horas: {len(horas_df)} registros")
            
            self.progress.emit(100, "Carga completada ✓")
            self.finished.emit(True)
            
        except Exception as e:
            logger.error(f"Error precargando datos: {e}", exc_info=True)
            self.finished.emit(False)


class LauncherDialog(QDialog):
    """Ventana inicial de selección: Dashboard o Generación de PDFs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Metric Scrap Project")
        self.setFixedSize(550, 400)
        self.setModal(True)
        
        # Estado
        self.data_loaded = False
        self.selected_option = None  # "dashboard" o "reports"
        self.preload_thread = None
        
        self._init_ui()
        self._start_preload()
    
    def _init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Título
        title_label = QLabel("Bienvenido al Sistema de\nAnálisis de Scrap")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #1976d2;
            }
        """)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Seleccione una opción para continuar")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666;
            }
        """)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(10)
        
        # Frame de progreso
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(20, 15, 20, 15)
        progress_layout.setSpacing(10)
        self.progress_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        
        self.progress_label = QLabel("Cargando datos...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 12px; color: #333;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #1976d2;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.progress_frame)
        
        layout.addSpacing(10)
        
        # Frame de botones
        self.buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(self.buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)
        
        # Botón Dashboard
        self.dashboard_button = QPushButton("📊 Abrir Dashboard")
        self.dashboard_button.setEnabled(False)
        self.dashboard_button.setMinimumHeight(60)
        self.dashboard_button.setCursor(Qt.PointingHandCursor)
        self.dashboard_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover:enabled {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """)
        self.dashboard_button.clicked.connect(self._on_dashboard_clicked)
        buttons_layout.addWidget(self.dashboard_button)
        
        # Botón Reportes
        self.reports_button = QPushButton("📄 Generar Reportes PDF")
        self.reports_button.setEnabled(False)
        self.reports_button.setMinimumHeight(60)
        self.reports_button.setCursor(Qt.PointingHandCursor)
        self.reports_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #43a047;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover:enabled {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """)
        self.reports_button.clicked.connect(self._on_reports_clicked)
        buttons_layout.addWidget(self.reports_button)
        
        self.buttons_frame.setVisible(False)  # Oculto hasta que carguen datos
        layout.addWidget(self.buttons_frame)
        
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("Desarrollado por Oscar Teran • NavicoGroup")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #999;
            }
        """)
        layout.addWidget(footer_label)
    
    def _start_preload(self):
        """Inicia la precarga de datos en background"""
        logger.info("Iniciando precarga de datos...")
        
        self.preload_thread = DataPreloadThread()
        self.preload_thread.progress.connect(self._on_progress)
        self.preload_thread.finished.connect(self._on_preload_finished)
        self.preload_thread.start()
    
    def _on_progress(self, percent, message):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
    
    def _on_preload_finished(self, success):
        """Callback cuando termina la precarga"""
        if success:
            logger.info("Precarga de datos completada exitosamente")
            self.data_loaded = True
            
            # Ocultar progreso, mostrar botones
            self.progress_frame.setVisible(False)
            self.buttons_frame.setVisible(True)
            
            # Habilitar botones
            self.dashboard_button.setEnabled(True)
            self.reports_button.setEnabled(True)
            
        else:
            logger.error("Error en la precarga de datos")
            self.progress_label.setText("❌ Error cargando datos")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    background-color: white;
                }
                QProgressBar::chunk {
                    background-color: #f44336;
                    border-radius: 4px;
                }
            """)
            
            # Mostrar mensaje de error
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error de Carga",
                "No se pudieron cargar los datos del archivo Excel.\n\n"
                "Verifique que el archivo exista en la ruta configurada y tenga el formato correcto.\n\n"
                "Puede revisar los logs para más detalles."
            )
            
            # Cerrar diálogo
            self.reject()
    
    def _on_dashboard_clicked(self):
        """Usuario seleccionó Dashboard"""
        logger.info("Usuario seleccionó: Dashboard")
        self.selected_option = "dashboard"
        self.accept()
    
    def _on_reports_clicked(self):
        """Usuario seleccionó Generar Reportes"""
        logger.info("Usuario seleccionó: Generar Reportes PDF")
        self.selected_option = "reports"
        self.accept()
    
    def get_selected_option(self):
        """Retorna la opción seleccionada por el usuario"""
        return self.selected_option
