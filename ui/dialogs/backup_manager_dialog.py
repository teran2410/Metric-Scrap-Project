"""
backup_manager_dialog.py - Diálogo para gestionar backups de archivos de datos

Permite visualizar, restaurar y eliminar backups:
- Lista de backups con fecha, tamaño y antigüedad
- Restauración con confirmación
- Eliminación de backups individuales
- Estadísticas de uso de espacio
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QMessageBox,
    QGroupBox, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.utils.backup_manager import get_backup_manager, BackupInfo
import logging

logger = logging.getLogger(__name__)


class BackupManagerDialog(QDialog):
    """Diálogo para gestionar backups de archivos"""
    
    def __init__(self, data_file_path: str, parent=None):
        super().__init__(parent)
        self.data_file_path = data_file_path
        self.backup_manager = get_backup_manager()
        self.selected_backup = None
        
        self.setWindowTitle("Gestor de Backups")
        self.resize(800, 600)
        
        self.init_ui()
        self.load_backups()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # ========== HEADER ==========
        header = QLabel("📦 Gestor de Backups de Datos")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # ========== ESTADÍSTICAS ==========
        stats_group = self._create_statistics_panel()
        layout.addWidget(stats_group)
        
        # ========== LISTA DE BACKUPS ==========
        backups_group = QGroupBox("Backups Disponibles")
        backups_layout = QVBoxLayout(backups_group)
        
        self.backups_list = QListWidget()
        self.backups_list.itemClicked.connect(self.on_backup_selected)
        self.backups_list.itemDoubleClicked.connect(self.restore_backup)
        backups_layout.addWidget(self.backups_list)
        
        layout.addWidget(backups_group)
        
        # ========== DETALLES DEL BACKUP ==========
        details_group = QGroupBox("Detalles del Backup Seleccionado")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        self.details_text.setPlainText("Seleccione un backup para ver detalles...")
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # ========== BOTONES DE ACCIÓN ==========
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton("➕ Crear Backup Ahora")
        create_btn.clicked.connect(self.create_backup_now)
        buttons_layout.addWidget(create_btn)
        
        buttons_layout.addStretch()
        
        self.delete_btn = QPushButton("🗑️ Eliminar")
        self.delete_btn.clicked.connect(self.delete_backup)
        self.delete_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_btn)
        
        self.restore_btn = QPushButton("↩️ Restaurar")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.restore_btn.setEnabled(False)
        self.restore_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 8px;")
        buttons_layout.addWidget(self.restore_btn)
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_backups)
        buttons_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_statistics_panel(self):
        """Crea el panel de estadísticas"""
        group = QGroupBox("Estadísticas")
        layout = QHBoxLayout(group)
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.stats_label)
        
        return group
    
    def load_backups(self):
        """Carga la lista de backups disponibles"""
        self.backups_list.clear()
        
        # Obtener nombre del archivo
        filename = os.path.basename(self.data_file_path)
        
        # Cargar backups
        backups = self.backup_manager.list_backups(filename)
        
        if not backups:
            no_backups_item = QListWidgetItem("No hay backups disponibles")
            no_backups_item.setFlags(Qt.NoItemFlags)
            self.backups_list.addItem(no_backups_item)
        else:
            for backup in backups:
                item_text = (
                    f"📁 {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"{backup.size_mb:.2f} MB | "
                    f"{backup.age_str}"
                )
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, backup)  # Guardar objeto BackupInfo
                self.backups_list.addItem(item)
        
        # Actualizar estadísticas
        self._update_statistics()
    
    def _update_statistics(self):
        """Actualiza el panel de estadísticas"""
        stats = self.backup_manager.get_backup_statistics()
        
        if stats["total_backups"] == 0:
            self.stats_label.setText("No hay backups disponibles")
            return
        
        stats_text = (
            f"Total de backups: {stats['total_backups']} | "
            f"Espacio usado: {stats['total_size_mb']:.2f} MB | "
            f"Más reciente: {stats['newest_backup'].strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.stats_label.setText(stats_text)
    
    def on_backup_selected(self, item: QListWidgetItem):
        """Maneja la selección de un backup"""
        backup = item.data(Qt.UserRole)
        
        if backup is None:
            return
        
        self.selected_backup = backup
        
        # Actualizar detalles
        details = f"Nombre: {backup.filename}\n"
        details += f"Ruta: {backup.filepath}\n"
        details += f"Fecha: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        details += f"Tamaño: {backup.size_mb:.2f} MB ({backup.size_bytes:,} bytes)\n"
        details += f"Antigüedad: {backup.age_str}"
        
        self.details_text.setPlainText(details)
        
        # Habilitar botones
        self.restore_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
    
    def create_backup_now(self):
        """Crea un backup manual inmediato"""
        reply = QMessageBox.question(
            self,
            "Crear Backup",
            f"¿Desea crear un backup del archivo actual?\n\n{self.data_file_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Usar manual=True para indicar que es un backup manual
                result = self.backup_manager.create_backup(self.data_file_path, force=True, manual=True)
                
                # Si se alcanzó el límite
                if isinstance(result, tuple) and result[1] == "limit_reached":
                    limit_reply = QMessageBox.warning(
                        self,
                        "⚠️ Límite de Backups Alcanzado",
                        f"Ya existen {self.backup_manager.max_backups} backups (máximo permitido).\n\n"
                        f"Si continúa, se eliminará el backup más antiguo.\n\n"
                        f"¿Desea proceder?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    # Si confirma, crear sin manual=True para que aplique la limpieza automática
                    if limit_reply == QMessageBox.Yes:
                        backup_path = self.backup_manager.create_backup(self.data_file_path, force=True, manual=False)
                    else:
                        return  # Usuario canceló
                else:
                    backup_path = result
                
                if backup_path:
                    QMessageBox.information(
                        self,
                        "Backup Creado",
                        f"El backup se creó exitosamente:\n\n{backup_path}"
                    )
                    self.load_backups()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "No se pudo crear el backup. Revise los logs para más detalles."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error creando backup:\n\n{str(e)}"
                )
                logger.error(f"Error en create_backup_now: {e}", exc_info=True)
    
    def restore_backup(self):
        """Restaura el backup seleccionado"""
        if not self.selected_backup:
            QMessageBox.warning(self, "Aviso", "Seleccione un backup para restaurar")
            return
        
        # Confirmación con advertencia
        reply = QMessageBox.warning(
            self,
            "⚠️ Confirmar Restauración",
            f"¿Está seguro de restaurar este backup?\n\n"
            f"Fecha: {self.selected_backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Tamaño: {self.selected_backup.size_mb:.2f} MB\n\n"
            f"ADVERTENCIA: El archivo actual será reemplazado.\n"
            f"Se creará un backup de seguridad del archivo actual antes de restaurar.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.backup_manager.restore_backup(
                    self.selected_backup.filepath,
                    self.data_file_path
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Restauración Exitosa",
                        f"El backup se restauró correctamente.\n\n"
                        f"Se creó un backup de seguridad del archivo anterior.\n\n"
                        f"Por favor, recargue los datos en la aplicación."
                    )
                    self.accept()  # Cerrar diálogo
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "No se pudo restaurar el backup. Revise los logs para más detalles."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error restaurando backup:\n\n{str(e)}"
                )
                logger.error(f"Error en restore_backup: {e}", exc_info=True)
    
    def delete_backup(self):
        """Elimina el backup seleccionado"""
        if not self.selected_backup:
            QMessageBox.warning(self, "Aviso", "Seleccione un backup para eliminar")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar este backup?\n\n"
            f"Fecha: {self.selected_backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Tamaño: {self.selected_backup.size_mb:.2f} MB\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.backup_manager.delete_backup(self.selected_backup.filepath)
                
                if success:
                    QMessageBox.information(
                        self,
                        "Backup Eliminado",
                        "El backup se eliminó correctamente."
                    )
                    self.selected_backup = None
                    self.restore_btn.setEnabled(False)
                    self.delete_btn.setEnabled(False)
                    self.load_backups()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "No se pudo eliminar el backup."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error eliminando backup:\n\n{str(e)}"
                )
                logger.error(f"Error en delete_backup: {e}", exc_info=True)


def show_backup_manager(data_file_path: str, parent=None) -> int:
    """
    Muestra el diálogo de gestión de backups.
    
    Args:
        data_file_path: Ruta del archivo de datos
        parent: Widget padre (opcional)
        
    Returns:
        int: Código de resultado del diálogo
    """
    dialog = BackupManagerDialog(data_file_path, parent)
    return dialog.exec()
