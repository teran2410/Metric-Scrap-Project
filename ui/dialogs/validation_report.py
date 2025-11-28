"""
validation_report.py - Diálogo para mostrar resultados de validación de datos

Muestra un reporte completo de problemas encontrados durante la validación:
- Categorizado por severidad (ERROR, WARNING, INFO)
- Detalles expandibles por problema
- Botones para exportar reporte y continuar/cancelar
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QSplitter, QGroupBox,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from src.utils.data_validator import ValidationResult, Severity
import logging

logger = logging.getLogger(__name__)


class ValidationReportDialog(QDialog):
    """Diálogo para mostrar resultados de validación de datos"""
    
    def __init__(self, validation_result: ValidationResult, parent=None):
        super().__init__(parent)
        self.validation_result = validation_result
        self.user_choice = None  # 'continue' o 'cancel'
        
        self.setWindowTitle("Reporte de Validación de Datos")
        self.resize(900, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # ========== HEADER CON RESUMEN ==========
        header = self._create_header()
        layout.addWidget(header)
        
        # ========== SPLITTER CON LISTA Y DETALLES ==========
        splitter = QSplitter(Qt.Horizontal)
        
        # Lista de problemas
        self.issues_list = self._create_issues_list()
        splitter.addWidget(self.issues_list)
        
        # Panel de detalles
        self.details_panel = self._create_details_panel()
        splitter.addWidget(self.details_panel)
        
        splitter.setSizes([400, 500])
        layout.addWidget(splitter)
        
        # ========== BOTONES DE ACCIÓN ==========
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("📄 Exportar Reporte")
        export_btn.clicked.connect(self.export_report)
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        if self.validation_result.has_errors():
            # Si hay errores críticos, solo botón de cancelar
            cancel_btn = QPushButton("❌ Cancelar Operación")
            cancel_btn.clicked.connect(self.reject)
            cancel_btn.setStyleSheet("background-color: #d32f2f; color: white; padding: 8px;")
            buttons_layout.addWidget(cancel_btn)
        else:
            # Si solo hay warnings o todo OK, permitir continuar
            if self.validation_result.has_warnings():
                cancel_btn = QPushButton("❌ Cancelar")
                cancel_btn.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_btn)
                
                continue_btn = QPushButton("✓ Continuar de Todos Modos")
                continue_btn.clicked.connect(self.accept)
                continue_btn.setStyleSheet("background-color: #388e3c; color: white; padding: 8px;")
                buttons_layout.addWidget(continue_btn)
            else:
                ok_btn = QPushButton("✓ Aceptar")
                ok_btn.clicked.connect(self.accept)
                ok_btn.setStyleSheet("background-color: #388e3c; color: white; padding: 8px;")
                buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_header(self):
        """Crea el header con resumen de validación"""
        group = QGroupBox("Resumen de Validación")
        layout = QVBoxLayout(group)
        
        # Ícono y mensaje principal
        header_layout = QHBoxLayout()
        
        if self.validation_result.has_errors():
            icon_label = QLabel("❌")
            icon_label.setStyleSheet("font-size: 32px;")
            status_text = "Validación Fallida - Se encontraron errores críticos"
            status_color = "#d32f2f"
        elif self.validation_result.has_warnings():
            icon_label = QLabel("⚠️")
            icon_label.setStyleSheet("font-size: 32px;")
            status_text = "Validación con Advertencias - Revise los problemas encontrados"
            status_color = "#f57c00"
        else:
            icon_label = QLabel("✓")
            icon_label.setStyleSheet("font-size: 32px; color: #4caf50;")
            status_text = "Validación Exitosa - No se encontraron problemas críticos"
            status_color = "#4caf50"
        
        header_layout.addWidget(icon_label)
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {status_color};")
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Contadores
        summary_label = QLabel(
            f"Total de problemas: {len(self.validation_result.issues)} | "
            f"Errores: {self.validation_result.total_errors} | "
            f"Advertencias: {self.validation_result.total_warnings} | "
            f"Info: {self.validation_result.total_infos}"
        )
        summary_label.setStyleSheet("font-size: 11px; color: gray;")
        layout.addWidget(summary_label)
        
        return group
    
    def _create_issues_list(self):
        """Crea la lista de problemas encontrados"""
        group = QGroupBox("Problemas Encontrados")
        layout = QVBoxLayout(group)
        
        list_widget = QListWidget()
        list_widget.itemClicked.connect(self.on_issue_selected)
        
        # Agregar problemas agrupados por severidad
        for severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]:
            filtered_issues = [i for i in self.validation_result.issues if i.severity == severity]
            
            if not filtered_issues:
                continue
            
            # Header de severidad
            header_item = QListWidgetItem(f"\n{severity.value} ({len(filtered_issues)})")
            header_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            if severity == Severity.ERROR:
                header_item.setBackground(QColor("#ffebee"))
                header_item.setForeground(QColor("#c62828"))
            elif severity == Severity.WARNING:
                header_item.setBackground(QColor("#fff3e0"))
                header_item.setForeground(QColor("#e65100"))
            else:
                header_item.setBackground(QColor("#e3f2fd"))
                header_item.setForeground(QColor("#1565c0"))
            
            header_item.setFlags(Qt.NoItemFlags)  # No seleccionable
            list_widget.addItem(header_item)
            
            # Problemas de esta severidad
            for issue in filtered_issues:
                item_text = f"  • {issue.category}: {issue.message}"
                if issue.sheet_name:
                    item_text += f" ({issue.sheet_name})"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, issue)  # Guardar issue completo
                list_widget.addItem(item)
        
        if not self.validation_result.issues:
            no_issues_item = QListWidgetItem("✓ No se encontraron problemas")
            no_issues_item.setForeground(QColor("#4caf50"))
            no_issues_item.setFlags(Qt.NoItemFlags)
            list_widget.addItem(no_issues_item)
        
        layout.addWidget(list_widget)
        return group
    
    def _create_details_panel(self):
        """Crea el panel de detalles del problema seleccionado"""
        group = QGroupBox("Detalles del Problema")
        layout = QVBoxLayout(group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Consolas", 9))
        self.details_text.setPlainText("Seleccione un problema de la lista para ver detalles...")
        
        layout.addWidget(self.details_text)
        return group
    
    def on_issue_selected(self, item: QListWidgetItem):
        """Maneja la selección de un problema en la lista"""
        issue = item.data(Qt.UserRole)
        
        if issue is None:  # Headers no tienen data
            return
        
        # Formatear detalles
        details = f"Severidad: {issue.severity.value}\n"
        details += f"Categoría: {issue.category}\n"
        details += f"Hoja: {issue.sheet_name}\n\n"
        details += f"Mensaje:\n{issue.message}\n\n"
        details += f"Detalles:\n{issue.details}\n"
        
        if issue.affected_rows > 0:
            details += f"\nRegistros afectados: {issue.affected_rows}\n"
        
        # Agregar recomendaciones según el tipo de problema
        recommendations = self._get_recommendations(issue)
        if recommendations:
            details += f"\nRecomendaciones:\n{recommendations}"
        
        self.details_text.setPlainText(details)
    
    def _get_recommendations(self, issue) -> str:
        """Obtiene recomendaciones basadas en el tipo de problema"""
        recommendations = {
            "Columnas Faltantes": 
                "• Verifique que el archivo Excel tenga la estructura correcta\n"
                "• Las columnas deben tener exactamente los nombres esperados\n"
                "• Revise si hay espacios extra en los nombres de columnas",
            
            "Fechas Inválidas":
                "• Verifique el formato de las fechas en Excel\n"
                "• Use formato de fecha estándar (dd/mm/yyyy o mm/dd/yyyy)\n"
                "• Evite texto mezclado con fechas",
            
            "Valores No Numéricos":
                "• Elimine texto o caracteres especiales de las celdas numéricas\n"
                "• Asegúrese de que las columnas numéricas solo contengan números\n"
                "• Revise celdas con errores (#N/A, #DIV/0, etc.)",
            
            "Valores Negativos":
                "• Verifique si los valores negativos son esperados\n"
                "• Algunos valores negativos pueden ser normales (devoluciones, ajustes)\n"
                "• Corrija valores que sean claramente errores",
            
            "Registros Duplicados":
                "• Determine si los duplicados son intencionales o errores\n"
                "• Elimine registros duplicados si son errores de captura\n"
                "• Mantenga duplicados si representan múltiples transacciones válidas",
            
            "Valores Atípicos":
                "• Verifique valores extremadamente altos o bajos\n"
                "• Confirme que no sean errores de captura de datos\n"
                "• Valores atípicos válidos pueden mantenerse",
            
            "Fechas Futuras":
                "• Corrija fechas que estén en el futuro\n"
                "• Verifique si hay errores en año, mes o día\n"
                "• Fechas futuras pueden causar problemas en reportes",
        }
        
        return recommendations.get(issue.category, "")
    
    def export_report(self):
        """Exporta el reporte de validación a archivo de texto"""
        try:
            from datetime import datetime
            
            filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = f"reports/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("REPORTE DE VALIDACIÓN DE DATOS\n")
                f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(self.validation_result.get_summary() + "\n\n")
                
                for severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]:
                    filtered = [i for i in self.validation_result.issues if i.severity == severity]
                    if not filtered:
                        continue
                    
                    f.write(f"\n{severity.value} ({len(filtered)}):\n")
                    f.write("-" * 80 + "\n")
                    
                    for issue in filtered:
                        f.write(f"\n• {issue.category}\n")
                        f.write(f"  Hoja: {issue.sheet_name}\n")
                        f.write(f"  Mensaje: {issue.message}\n")
                        f.write(f"  Detalles: {issue.details}\n")
                        if issue.affected_rows > 0:
                            f.write(f"  Registros afectados: {issue.affected_rows}\n")
            
            QMessageBox.information(
                self,
                "Reporte Exportado",
                f"El reporte se guardó exitosamente en:\n{filepath}"
            )
            
            logger.info(f"Reporte de validación exportado a: {filepath}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo exportar el reporte:\n{str(e)}"
            )
            logger.error(f"Error exportando reporte: {e}")


def show_validation_report(validation_result: ValidationResult, parent=None) -> bool:
    """
    Muestra el diálogo de reporte de validación.
    
    Args:
        validation_result: Resultado de la validación
        parent: Widget padre (opcional)
        
    Returns:
        bool: True si el usuario eligió continuar, False si canceló
    """
    dialog = ValidationReportDialog(validation_result, parent)
    result = dialog.exec()
    return result == QDialog.Accepted
