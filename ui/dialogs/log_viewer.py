"""
log_viewer.py - Visor de logs de la aplicación

Diálogo para visualizar y filtrar logs de la aplicación con las siguientes características:
- Visualización de logs en tiempo real
- Filtrado por nivel (DEBUG, INFO, WARNING, ERROR)
- Búsqueda de texto
- Auto-actualización opcional
- Acceso directo a la carpeta de logs
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QLineEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor

from src.utils.logging_config import (
    get_log_file_path, 
    get_log_directory, 
    read_recent_logs
)


class LogViewerDialog(QDialog):
    """Diálogo para visualizar y filtrar logs de la aplicación."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visor de Logs - Metric Scrap")
        self.resize(1000, 600)
        
        # Timer para auto-actualización
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        # Variables de estado
        self.current_filter = "TODOS"
        self.search_text = ""
        
        self.init_ui()
        self.load_logs()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        
        # ========== HEADER CON CONTROLES ==========
        header_layout = QHBoxLayout()
        
        # Etiqueta de título
        title_label = QLabel("📋 Logs de la Aplicación")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Filtro por nivel
        filter_label = QLabel("Filtrar:")
        header_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["TODOS", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        header_layout.addWidget(self.filter_combo)
        
        # Búsqueda
        search_label = QLabel("Buscar:")
        header_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Texto a buscar...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setMinimumWidth(200)
        header_layout.addWidget(self.search_input)
        
        layout.addLayout(header_layout)
        
        # ========== ÁREA DE TEXTO PARA LOGS ==========
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
            }
        """)
        layout.addWidget(self.log_text)
        
        # ========== INFO Y CONTROLES INFERIORES ==========
        bottom_layout = QHBoxLayout()
        
        # Checkbox de auto-actualización
        self.auto_refresh_checkbox = QCheckBox("Auto-actualizar cada 3 seg")
        self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)
        bottom_layout.addWidget(self.auto_refresh_checkbox)
        
        # Etiqueta con ruta del archivo
        self.file_path_label = QLabel()
        self.file_path_label.setStyleSheet("color: gray; font-size: 10px;")
        self.update_file_path_label()
        bottom_layout.addWidget(self.file_path_label)
        
        bottom_layout.addStretch()
        
        # Botón para abrir carpeta de logs
        open_folder_btn = QPushButton("📁 Abrir Carpeta de Logs")
        open_folder_btn.clicked.connect(self.open_logs_folder)
        bottom_layout.addWidget(open_folder_btn)
        
        # Botón para actualizar
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.refresh_logs)
        bottom_layout.addWidget(refresh_btn)
        
        # Botón para cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
    
    def load_logs(self, lines=500):
        """
        Carga los logs en el visor.
        
        Args:
            lines: Número de líneas a cargar (por defecto 500)
        """
        try:
            log_content = read_recent_logs(lines)
            self.apply_filters(log_content)
        except Exception as e:
            self.log_text.setPlainText(f"Error cargando logs: {str(e)}")
    
    def apply_filters(self, content):
        """
        Aplica filtros de nivel y búsqueda al contenido.
        
        Args:
            content: Contenido completo del log
        """
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Filtrar por nivel
            if self.current_filter != "TODOS":
                if f"| {self.current_filter}" not in line:
                    continue
            
            # Filtrar por búsqueda
            if self.search_text and self.search_text.lower() not in line.lower():
                continue
            
            # Aplicar colores según nivel
            formatted_line = self.colorize_line(line)
            filtered_lines.append(formatted_line)
        
        # Mostrar resultado
        self.log_text.setHtml('<br>'.join(filtered_lines))
        
        # Scroll al final
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def colorize_line(self, line):
        """
        Aplica colores HTML según el nivel de log.
        
        Args:
            line: Línea de log
            
        Returns:
            str: Línea con formato HTML
        """
        # Escapar caracteres HTML
        line = line.replace('<', '&lt;').replace('>', '&gt;')
        
        if "| ERROR" in line or "| CRITICAL" in line:
            return f'<span style="color: #f48771;">{line}</span>'
        elif "| WARNING" in line:
            return f'<span style="color: #dcdcaa;">{line}</span>'
        elif "| INFO" in line:
            return f'<span style="color: #4fc1ff;">{line}</span>'
        elif "| DEBUG" in line:
            return f'<span style="color: #b5cea8;">{line}</span>'
        else:
            return f'<span style="color: #d4d4d4;">{line}</span>'
    
    def on_filter_changed(self, filter_text):
        """Maneja cambio en el filtro de nivel."""
        self.current_filter = filter_text
        self.refresh_logs()
    
    def on_search_changed(self, search_text):
        """Maneja cambio en el texto de búsqueda."""
        self.search_text = search_text
        self.refresh_logs()
    
    def refresh_logs(self):
        """Actualiza el contenido de los logs."""
        self.load_logs()
    
    def toggle_auto_refresh(self, state):
        """Activa/desactiva la auto-actualización."""
        if state == Qt.Checked:
            self.refresh_timer.start(3000)  # 3 segundos
        else:
            self.refresh_timer.stop()
    
    def open_logs_folder(self):
        """Abre la carpeta de logs en el explorador de archivos."""
        try:
            log_dir = get_log_directory()
            
            if not os.path.exists(log_dir):
                QMessageBox.warning(
                    self,
                    "Carpeta no encontrada",
                    f"La carpeta de logs no existe:\n{log_dir}"
                )
                return
            
            # Abrir en el explorador según el sistema operativo
            import platform
            if platform.system() == 'Windows':
                os.startfile(log_dir)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{log_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{log_dir}"')
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir la carpeta de logs:\n{str(e)}"
            )
    
    def update_file_path_label(self):
        """Actualiza la etiqueta con la ruta del archivo de log."""
        try:
            log_path = get_log_file_path()
            self.file_path_label.setText(f"Archivo: {log_path}")
        except:
            self.file_path_label.setText("Archivo de log no disponible")
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar el diálogo."""
        self.refresh_timer.stop()
        super().closeEvent(event)


def show_log_viewer(parent=None):
    """
    Muestra el diálogo de visor de logs.
    
    Args:
        parent: Widget padre (opcional)
        
    Returns:
        int: Código de resultado del diálogo
    """
    dialog = LogViewerDialog(parent)
    return dialog.exec()
