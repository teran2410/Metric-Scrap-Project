"""
error_dialog.py - Dialog mejorado para mostrar errores con detalles técnicos

Proporciona una interfaz clara para mostrar errores al usuario con:
- Mensaje principal legible
- Detalles técnicos expandibles
- Stack trace completo
- Botón para copiar detalles al portapapeles
"""

import traceback
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from src.utils.exceptions import MetricScrapError


class ErrorDialog(QDialog):
    """Dialog personalizado para mostrar errores con detalles técnicos"""
    
    def __init__(self, error, parent=None):
        """
        Inicializa el dialog de error.
        
        Args:
            error (Exception): Excepción a mostrar
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        self.error = error
        self.setWindowTitle("Error")
        self.setMinimumWidth(500)
        self.setMinimumHeight(250)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== ÍCONO Y TÍTULO ==========
        header_layout = QHBoxLayout()
        
        # Ícono de error
        icon_label = QLabel("❌")
        icon_font = QFont()
        icon_font.setPointSize(32)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel("Ha ocurrido un error")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # ========== MENSAJE PRINCIPAL ==========
        message = self._get_user_message()
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 11pt; padding: 10px;")
        layout.addWidget(message_label)
        
        # ========== DETALLES TÉCNICOS (EXPANDIBLE) ==========
        self.details_visible = False
        
        # Botón para mostrar/ocultar detalles
        self.details_btn = QPushButton("▶ Mostrar detalles técnicos")
        self.details_btn.clicked.connect(self.toggle_details)
        self.details_btn.setStyleSheet("text-align: left; padding: 8px;")
        layout.addWidget(self.details_btn)
        
        # Área de texto para detalles
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Courier New", 9))
        self.details_text.setPlainText(self._get_technical_details())
        self.details_text.setMinimumHeight(200)
        self.details_text.hide()
        layout.addWidget(self.details_text)
        
        # ========== BOTONES DE ACCIÓN ==========
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Botón copiar (inicialmente oculto)
        self.copy_btn = QPushButton("📋 Copiar detalles")
        self.copy_btn.clicked.connect(self.copy_details)
        self.copy_btn.hide()
        buttons_layout.addWidget(self.copy_btn)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(100)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _get_user_message(self):
        """Obtiene el mensaje formateado para el usuario"""
        if isinstance(self.error, MetricScrapError):
            return self.error.get_user_message()
        else:
            return f"❌ {str(self.error)}\n\n💡 Intente nuevamente o contacte al soporte técnico."
    
    def _get_technical_details(self):
        """Obtiene los detalles técnicos del error"""
        details = []
        
        # Tipo de error
        details.append(f"Tipo de Error: {type(self.error).__name__}")
        details.append("")
        
        # Mensaje
        details.append(f"Mensaje: {str(self.error)}")
        details.append("")
        
        # Detalles específicos si es MetricScrapError
        if isinstance(self.error, MetricScrapError):
            details.append("=== Detalles Específicos ===")
            details.append(self.error.get_technical_details())
            details.append("")
        
        # Stack trace
        details.append("=== Stack Trace ===")
        tb_lines = traceback.format_exception(type(self.error), self.error, self.error.__traceback__)
        details.extend(tb_lines)
        
        return "\n".join(details)
    
    def toggle_details(self):
        """Muestra u oculta los detalles técnicos"""
        self.details_visible = not self.details_visible
        
        if self.details_visible:
            self.details_text.show()
            self.copy_btn.show()
            self.details_btn.setText("▼ Ocultar detalles técnicos")
            self.setMinimumHeight(500)
        else:
            self.details_text.hide()
            self.copy_btn.hide()
            self.details_btn.setText("▶ Mostrar detalles técnicos")
            self.setMinimumHeight(250)
    
    def copy_details(self):
        """Copia los detalles técnicos al portapapeles"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.details_text.toPlainText())
        
        # Cambiar texto del botón temporalmente
        original_text = self.copy_btn.text()
        self.copy_btn.setText("✓ Copiado!")
        self.copy_btn.setEnabled(False)
        
        # Restaurar después de 1.5 segundos
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self._restore_copy_button(original_text))
    
    def _restore_copy_button(self, original_text):
        """Restaura el botón de copiar a su estado original"""
        self.copy_btn.setText(original_text)
        self.copy_btn.setEnabled(True)


def show_error_dialog(error, parent=None):
    """
    Función de conveniencia para mostrar un error en un dialog.
    
    Args:
        error (Exception): Error a mostrar
        parent (QWidget, optional): Widget padre
    
    Returns:
        int: Código de resultado del dialog
    """
    dialog = ErrorDialog(error, parent)
    return dialog.exec()
