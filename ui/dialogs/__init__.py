"""
ui/dialogs/__init__.py - Módulo de dialogs personalizados
"""

from .error_dialog import ErrorDialog, show_error_dialog
from .log_viewer import LogViewerDialog, show_log_viewer
from .validation_report import ValidationReportDialog, show_validation_report
from .backup_manager_dialog import BackupManagerDialog, show_backup_manager
from .history_dialog import ReportHistoryDialog
from .dashboard_dialog import DashboardDialog
from .launcher_dialog import LauncherDialog

__all__ = [
    'ErrorDialog', 
    'show_error_dialog',
    'LogViewerDialog',
    'show_log_viewer',
    'ValidationReportDialog',
    'show_validation_report',
    'BackupManagerDialog',
    'show_backup_manager',
    'ReportHistoryDialog',
    'DashboardDialog',
    'LauncherDialog'
]
