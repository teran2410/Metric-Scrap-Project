"""
history_dialog.py - Diálogo para visualizar y gestionar el historial de reportes
"""

import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QGroupBox, QTextEdit, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from src.utils.report_history import get_report_history_manager, ReportEntry


class ReportHistoryDialog(QDialog):
    """Diálogo para gestionar el historial de reportes generados"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = get_report_history_manager()
        self.init_ui()
        self.load_reports()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("📚 Historial de Reportes Generados")
        self.setMinimumSize(1000, 600)
        
        layout = QVBoxLayout()
        
        # ========== PANEL DE ESTADÍSTICAS ==========
        stats_group = QGroupBox("📊 Estadísticas")
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 10pt; padding: 10px;")
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # ========== FILTROS ==========
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filtrar por tipo:")
        filter_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Todos",
            "Semanal",
            "Mensual",
            "Trimestral",
            "Anual",
            "Personalizado"
        ])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        # Botón limpiar reportes faltantes
        cleanup_btn = QPushButton("🧹 Limpiar Faltantes")
        cleanup_btn.setToolTip("Elimina del historial los reportes cuyos archivos ya no existen")
        cleanup_btn.clicked.connect(self.cleanup_missing)
        filter_layout.addWidget(cleanup_btn)
        
        layout.addLayout(filter_layout)
        
        # ========== TABLA DE REPORTES ==========
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tipo", "Periodo", "Fecha Generación", "Tamaño", "Estado", "Ruta"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.open_report)
        
        layout.addWidget(self.table)
        
        # ========== PANEL DE DETALLES ==========
        details_group = QGroupBox("ℹ️ Detalles del Reporte Seleccionado")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(80)
        self.details_text.setStyleSheet("background-color: #f5f5f5; color: #000000; font-family: Consolas; font-size: 9pt;")
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # ========== BOTONES DE ACCIÓN ==========
        buttons_layout = QHBoxLayout()
        
        open_btn = QPushButton("📄 Abrir Reporte")
        open_btn.clicked.connect(self.open_report)
        buttons_layout.addWidget(open_btn)
        
        delete_btn = QPushButton("🗑️ Eliminar del Historial")
        delete_btn.clicked.connect(self.delete_from_history)
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_reports)
        buttons_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Conectar selección de tabla a detalles
        self.table.itemSelectionChanged.connect(self.show_details)
    
    def load_reports(self):
        """Carga los reportes en la tabla"""
        self.table.setRowCount(0)
        
        filter_type = self.filter_combo.currentText()
        if filter_type == "Todos":
            filter_type = None
        
        reports = self.manager.get_all_reports(filter_type=filter_type)
        
        self.table.setRowCount(len(reports))
        
        for row, entry in enumerate(reports):
            # Tipo
            type_item = QTableWidgetItem(entry.report_type)
            self.table.setItem(row, 0, type_item)
            
            # Periodo
            period_item = QTableWidgetItem(entry.period)
            self.table.setItem(row, 1, period_item)
            
            # Fecha generación
            from datetime import datetime
            try:
                gen_date = datetime.fromisoformat(entry.generated_date)
                date_str = gen_date.strftime('%d/%m/%Y %H:%M')
            except:
                date_str = entry.generated_date
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 2, date_item)
            
            # Tamaño
            size_mb = entry.get_size_mb()
            size_item = QTableWidgetItem(f"{size_mb:.2f} MB")
            self.table.setItem(row, 3, size_item)
            
            # Estado
            exists = entry.exists()
            status_item = QTableWidgetItem("✓ Existe" if exists else "✗ Faltante")
            if not exists:
                status_item.setForeground(QColor("#c62828"))
            else:
                status_item.setForeground(QColor("#2e7d32"))
            self.table.setItem(row, 4, status_item)
            
            # Ruta
            path_item = QTableWidgetItem(entry.filepath)
            self.table.setItem(row, 5, path_item)
        
        # Actualizar estadísticas
        self.update_statistics()
    
    def apply_filter(self):
        """Aplica el filtro seleccionado"""
        self.load_reports()
    
    def update_statistics(self):
        """Actualiza el panel de estadísticas"""
        stats = self.manager.get_statistics()
        
        by_type_str = ", ".join([f"{k}: {v}" for k, v in stats['by_type'].items()])
        
        stats_text = f"""
        <b>Total de reportes:</b> {stats['total']} | 
        <b>Existentes:</b> {stats['existing']} | 
        <b>Faltantes:</b> {stats['missing']} | 
        <b>Espacio total:</b> {stats['total_size_mb']:.2f} MB<br>
        <b>Por tipo:</b> {by_type_str}
        """
        
        self.stats_label.setText(stats_text)
    
    def show_details(self):
        """Muestra detalles del reporte seleccionado"""
        selected = self.table.selectedItems()
        if not selected:
            self.details_text.clear()
            return
        
        row = self.table.currentRow()
        
        tipo = self.table.item(row, 0).text()
        periodo = self.table.item(row, 1).text()
        fecha = self.table.item(row, 2).text()
        tamano = self.table.item(row, 3).text()
        estado = self.table.item(row, 4).text()
        ruta = self.table.item(row, 5).text()
        
        details = f"""Tipo: {tipo}
Periodo: {periodo}
Fecha de Generación: {fecha}
Tamaño: {tamano}
Estado: {estado}
Ruta Completa: {ruta}"""
        
        self.details_text.setText(details)
    
    def open_report(self):
        """Abre el reporte seleccionado con la aplicación predeterminada"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sin Selección", "Por favor selecciona un reporte.")
            return
        
        row = self.table.currentRow()
        filepath = self.table.item(row, 5).text()
        
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self,
                "Archivo No Encontrado",
                f"El archivo ya no existe:\n{filepath}"
            )
            return
        
        try:
            os.startfile(filepath)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el archivo:\n{str(e)}"
            )
    
    def delete_from_history(self):
        """Elimina el reporte seleccionado del historial (no elimina el archivo)"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Sin Selección", "Por favor selecciona un reporte.")
            return
        
        row = self.table.currentRow()
        filepath = self.table.item(row, 5).text()
        periodo = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Eliminar del historial el reporte?\n\n{periodo}\n\nNOTA: El archivo PDF no será eliminado, solo se quitará del historial.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.manager.delete_report(filepath)
            self.load_reports()
            QMessageBox.information(self, "Eliminado", "Reporte eliminado del historial.")
    
    def cleanup_missing(self):
        """Limpia entradas de archivos que ya no existen"""
        reply = QMessageBox.question(
            self,
            "Confirmar Limpieza",
            "¿Eliminar del historial todos los reportes cuyos archivos ya no existen?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            removed = self.manager.cleanup_missing()
            self.load_reports()
            QMessageBox.information(
                self,
                "Limpieza Completada",
                f"Se eliminaron {removed} entradas del historial."
            )
