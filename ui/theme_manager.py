"""
theme_manager.py - Gestión de temas claro y oscuro
"""


class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    @staticmethod
    def apply_light_theme(app):
        """Aplica el tema claro"""
        app.title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #1E3A5F;")
        app.subtitle_label.setStyleSheet("font-size: 10pt; font-style: italic; color: #6B7280;")
        app.quick_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.year_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.type_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.status_label.setStyleSheet("font-size: 11pt; color: #6B7280; font-weight: 500;")
        
        # Labels dinámicos
        app.week_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.month_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.quarter_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.custom_start_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        app.custom_end_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #374151;")
        
        app.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F0F4F8, stop:1 #E6EEF5);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60A5FA, stop:1 #3B82F6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563EB, stop:1 #1D4ED8);
            }
            QPushButton:disabled {
                background: #D1D5DB;
                color: #9CA3AF;
            }
            QComboBox {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11pt;
                background-color: white;
                color: #1F2937;
                min-height: 28px;
            }
            QComboBox:hover {
                border: 2px solid #3B82F6;
                background-color: #F9FAFB;
            }
            QComboBox:focus {
                border: 2px solid #2563EB;
                background-color: #EFF6FF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #3B82F6;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1F2937;
                selection-background-color: #DBEAFE;
                selection-color: #1E40AF;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 4px;
            }
            QLineEdit, QDateEdit {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11pt;
                background-color: white;
                color: #1F2937;
                min-height: 28px;
            }
            QLineEdit:hover, QDateEdit:hover {
                border: 2px solid #3B82F6;
                background-color: #F9FAFB;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #2563EB;
                background-color: #EFF6FF;
            }
            QLabel {
                color: #374151;
                background: transparent;
                border: none;
            }
            QFrame[frameShape="4"] {
                background-color: #D1D5DB;
                max-height: 1px;
                min-height: 1px;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #E5E7EB;
                text-align: center;
                font-weight: 600;
                color: #1F2937;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #8B5CF6);
                border-radius: 8px;
            }
        """)
    
    @staticmethod
    def apply_dark_theme(app):
        """Aplica el tema oscuro"""
        app.title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #F9FAFB;")
        app.subtitle_label.setStyleSheet("font-size: 10pt; font-style: italic; color: #9CA3AF;")
        app.quick_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.year_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.type_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.status_label.setStyleSheet("font-size: 11pt; color: #9CA3AF; font-weight: 500;")
        
        # Labels dinámicos
        app.week_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.month_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.quarter_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.custom_start_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        app.custom_end_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #E5E7EB;")
        
        app.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0F172A, stop:1 #1E293B);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60A5FA, stop:1 #3B82F6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563EB, stop:1 #1D4ED8);
            }
            QPushButton:disabled {
                background: #374151;
                color: #6B7280;
            }
            QComboBox {
                border: 2px solid #374151;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11pt;
                background-color: #1F2937;
                color: #F3F4F6;
                min-height: 28px;
            }
            QComboBox:hover {
                border: 2px solid #3B82F6;
                background-color: #374151;
            }
            QComboBox:focus {
                border: 2px solid #60A5FA;
                background-color: #1F2937;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #60A5FA;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #1F2937;
                color: #F3F4F6;
                selection-background-color: #3B82F6;
                selection-color: white;
                border: 2px solid #374151;
                border-radius: 8px;
                padding: 4px;
            }
            QLineEdit, QDateEdit {
                border: 2px solid #374151;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11pt;
                background-color: #1F2937;
                color: #F3F4F6;
                min-height: 28px;
            }
            QLineEdit:hover, QDateEdit:hover {
                border: 2px solid #3B82F6;
                background-color: #374151;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #60A5FA;
                background-color: #1F2937;
            }
            QLabel {
                color: #E5E7EB;
                background: transparent;
                border: none;
            }
            QFrame[frameShape="4"] {
                background-color: #374151;
                max-height: 1px;
                min-height: 1px;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #374151;
                text-align: center;
                font-weight: 600;
                color: #F3F4F6;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #8B5CF6);
                border-radius: 8px;
            }
        """)
