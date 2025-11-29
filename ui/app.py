"""
app.py - Interfaz gráfica principal con PySide6
"""

import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QDateEdit,
    QProgressBar, QMessageBox, QFrame, QMenuBar, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon

from config import (
    APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_ICON_PATH,
    WEEK_MONTH_MAPPING_2025
)

# Importar módulos modularizados
from ui.report_thread import ReportThread
from ui.theme_manager import ThemeManager
from ui.dialogs import show_error_dialog, show_log_viewer, show_validation_report, show_backup_manager


class ScrapRateApp(QMainWindow):
    """Aplicación principal para análisis de Scrap Rate con interfaz unificada"""
    
    def __init__(self):
        super().__init__()
        
        # Estado del tema (True = oscuro, False = claro)
        self.is_dark_mode = True
        self.current_thread = None
        
        # Configuración ventana
        self.setWindowTitle(APP_TITLE)
        self.setFixedSize(600, 620)
        
        # Ícono
        self.setup_icon()
        
        # Menu bar
        self.setup_menubar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(15)
        
        # Header con título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Título (centrado)
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        title_label = QLabel("Análisis del Métrico de Scrap")
        title_label.setAlignment(Qt.AlignCenter)
        self.title_label = title_label
        title_container.addWidget(title_label)
        
        subtitle_label = QLabel("Desarrollado por Oscar Teran")
        subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label = subtitle_label
        title_container.addWidget(subtitle_label)
        
        header_layout.addStretch()
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(5)
        
        # ========== BOTONES DE ACCESO RÁPIDO ==========
        quick_actions_container = QFrame()
        quick_actions_layout = QHBoxLayout(quick_actions_container)
        quick_actions_layout.setContentsMargins(0, 0, 0, 0)
        quick_actions_layout.setSpacing(10)
        
        quick_label = QLabel("Acceso Rápido:")
        self.quick_label = quick_label
        quick_actions_layout.addWidget(quick_label)
        
        # Calcular semana y mes actual
        current_date = datetime.now()
        last_week = current_date.isocalendar()[1] - 1
        if last_week < 1:
            last_week = 52
        month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        # Mostrar mes anterior (mes con datos completos)
        last_month_num = current_date.month - 1 if current_date.month > 1 else 12
        last_month_name = month_names[last_month_num - 1]
        
        # Contenedor para botón de semana anterior + label
        week_container = QVBoxLayout()
        week_container.setSpacing(5)
        
        # Botón reporte semana anterior
        this_week_btn = QPushButton("Semana Anterior")
        this_week_btn.setFixedSize(180, 38)
        this_week_btn.setStyleSheet("font-size: 10pt;")
        this_week_btn.setCursor(Qt.PointingHandCursor)
        this_week_btn.clicked.connect(self.generate_last_week_report)
        self.this_week_btn = this_week_btn
        week_container.addWidget(this_week_btn)
        
        # Label con número de semana
        week_number_label = QLabel(f"Semana {last_week}")
        week_number_label.setAlignment(Qt.AlignCenter)
        week_number_label.setStyleSheet("font-size: 9pt; color: #9CA3AF;")
        self.week_number_label = week_number_label
        week_container.addWidget(week_number_label)
        
        quick_actions_layout.addLayout(week_container)
        
        # Contenedor para botón de este mes + label
        month_container = QVBoxLayout()
        month_container.setSpacing(5)
        
        # Botón reporte mes anterior
        this_month_btn = QPushButton("Mes Anterior")
        this_month_btn.setFixedSize(180, 38)
        this_month_btn.setStyleSheet("font-size: 10pt;")
        this_month_btn.setCursor(Qt.PointingHandCursor)
        this_month_btn.clicked.connect(self.generate_this_month_report)
        self.this_month_btn = this_month_btn
        month_container.addWidget(this_month_btn)
        
        # Label con nombre del mes anterior
        month_name_label = QLabel(last_month_name)
        month_name_label.setAlignment(Qt.AlignCenter)
        month_name_label.setStyleSheet("font-size: 9pt; color: #9CA3AF;")
        self.month_name_label = month_name_label
        month_container.addWidget(month_name_label)
        
        quick_actions_layout.addLayout(month_container)
        
        quick_actions_layout.addStretch()
        main_layout.addWidget(quick_actions_container)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.separator = separator
        main_layout.addWidget(separator)
        
        # ========== FORMULARIO UNIFICADO ==========
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 10)
        form_layout.setSpacing(15)
        
        # Año selector
        year_layout = QHBoxLayout()
        year_label = QLabel("📆 Año:")
        self.year_label = year_label
        year_layout.addWidget(year_label)
        year_layout.addStretch()
        
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year, current_year - 5, -1):
            self.year_combo.addItem(str(year))
        self.year_combo.setFixedSize(220, 45)
        year_layout.addWidget(self.year_combo)
        form_layout.addLayout(year_layout)
        
        # Tipo de reporte selector
        type_layout = QHBoxLayout()
        type_label = QLabel("📋 Tipo de Reporte:")
        self.type_label = type_label
        type_layout.addWidget(type_label)
        type_layout.addStretch()
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Semanal", "Mensual", "Trimestral", "Anual", "Personalizado"
        ])
        self.report_type_combo.setFixedSize(220, 45)
        self.report_type_combo.currentTextChanged.connect(self.on_report_type_changed)
        type_layout.addWidget(self.report_type_combo)
        form_layout.addLayout(type_layout)
        
        # ========== CAMPOS DINÁMICOS ==========
        # Contenedor para campos que cambian según el tipo
        self.dynamic_fields_container = QWidget()
        self.dynamic_fields_layout = QVBoxLayout(self.dynamic_fields_container)
        self.dynamic_fields_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_fields_layout.setSpacing(15)
        form_layout.addWidget(self.dynamic_fields_container)
        
        # Inicializar campos específicos
        self.init_dynamic_fields()
        
        main_layout.addWidget(form_container)
        
        # ========== PROGRESO ==========
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_container)
        
        # ========== CHECKBOX COMPARACIÓN ==========
        comparison_container = QHBoxLayout()
        comparison_container.addStretch()
        self.comparison_checkbox = QCheckBox("Incluir comparación con período anterior")
        self.comparison_checkbox.setStyleSheet("font-size: 11pt;")
        self.comparison_checkbox.setChecked(True)  # Marcado por defecto
        comparison_container.addWidget(self.comparison_checkbox)
        comparison_container.addStretch()
        main_layout.addLayout(comparison_container)
        
        # ========== BOTÓN GENERAR ==========
        generate_container = QHBoxLayout()
        generate_container.addStretch()
        self.generate_btn = QPushButton("📄 Generar Reporte")
        self.generate_btn.setFixedSize(300, 50)
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.clicked.connect(self.generate_report)
        generate_container.addWidget(self.generate_btn)
        generate_container.addStretch()
        main_layout.addLayout(generate_container)
        
        main_layout.addStretch()
        
        # Cargar campos del tipo inicial (Semanal)
        self.on_report_type_changed("Semanal")
        
        # Aplicar tema inicial (oscuro)
        ThemeManager.apply_dark_theme(self)
    
    def init_dynamic_fields(self):
        """Inicializa todos los widgets de campos dinámicos"""
        # Campo semana
        self.week_layout = QHBoxLayout()
        self.week_label = QLabel("🗓️ Número de Semana:")
        self.week_layout.addWidget(self.week_label)
        self.week_layout.addStretch()
        self.week_entry = QLineEdit()
        self.week_entry.setPlaceholderText("Ej: 21")
        self.week_entry.setAlignment(Qt.AlignCenter)
        self.week_entry.setFixedSize(220, 45)
        self.week_entry.setStyleSheet("font-size: 10pt; text-align: center;")
        self.week_layout.addWidget(self.week_entry)
        
        # Campo mes
        self.month_layout = QHBoxLayout()
        self.month_label = QLabel("📅 Mes:")
        self.month_layout.addWidget(self.month_label)
        self.month_layout.addStretch()
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        self.month_combo.setFixedSize(220, 45)
        self.month_layout.addWidget(self.month_combo)
        
        # Campo trimestre
        self.quarter_layout = QHBoxLayout()
        self.quarter_label = QLabel("📊 Trimestre:")
        self.quarter_layout.addWidget(self.quarter_label)
        self.quarter_layout.addStretch()
        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems(["Q1", "Q2", "Q3", "Q4"])
        self.quarter_combo.setFixedSize(220, 45)
        self.quarter_layout.addWidget(self.quarter_combo)
        
        # Campos fecha personalizada
        self.custom_start_layout = QHBoxLayout()
        self.custom_start_label = QLabel("📅 Fecha Inicio:")
        self.custom_start_layout.addWidget(self.custom_start_label)
        self.custom_start_layout.addStretch()
        self.custom_start_date = QDateEdit()
        self.custom_start_date.setCalendarPopup(True)
        self.custom_start_date.setDate(QDate.currentDate())
        self.custom_start_date.setFixedSize(220, 45)
        self.custom_start_layout.addWidget(self.custom_start_date)
        
        self.custom_end_layout = QHBoxLayout()
        self.custom_end_label = QLabel("📅 Fecha Fin:")
        self.custom_end_layout.addWidget(self.custom_end_label)
        self.custom_end_layout.addStretch()
        self.custom_end_date = QDateEdit()
        self.custom_end_date.setCalendarPopup(True)
        self.custom_end_date.setDate(QDate.currentDate())
        self.custom_end_date.setFixedSize(220, 45)
        self.custom_end_layout.addWidget(self.custom_end_date)
    
    def clear_dynamic_fields(self):
        """Limpia todos los campos dinámicos del layout"""
        while self.dynamic_fields_layout.count():
            item = self.dynamic_fields_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                # Ocultar widgets del layout sin eliminarlos
                for i in range(item.layout().count()):
                    widget = item.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
    
    def on_report_type_changed(self, report_type):
        """Muestra u oculta campos según el tipo de reporte seleccionado"""
        self.clear_dynamic_fields()
        
        if report_type == "Semanal":
            self.dynamic_fields_layout.addLayout(self.week_layout)
            # Re-añadir widgets al layout
            if self.week_label.parent() is None:
                self.week_layout.addWidget(self.week_label)
                self.week_layout.addWidget(self.week_entry)
                self.week_layout.addStretch()
        
        elif report_type == "Mensual":
            self.dynamic_fields_layout.addLayout(self.month_layout)
            if self.month_label.parent() is None:
                self.month_layout.addWidget(self.month_label)
                self.month_layout.addWidget(self.month_combo)
                self.month_layout.addStretch()
        
        elif report_type == "Trimestral":
            self.dynamic_fields_layout.addLayout(self.quarter_layout)
            if self.quarter_label.parent() is None:
                self.quarter_layout.addWidget(self.quarter_label)
                self.quarter_layout.addWidget(self.quarter_combo)
                self.quarter_layout.addStretch()
        
        elif report_type == "Anual":
            # No necesita campos adicionales
            pass
        
        elif report_type == "Personalizado":
            self.dynamic_fields_layout.addLayout(self.custom_start_layout)
            self.dynamic_fields_layout.addLayout(self.custom_end_layout)
            if self.custom_start_label.parent() is None:
                self.custom_start_layout.addWidget(self.custom_start_label)
                self.custom_start_layout.addWidget(self.custom_start_date)
                self.custom_start_layout.addStretch()
                self.custom_end_layout.addWidget(self.custom_end_label)
                self.custom_end_layout.addWidget(self.custom_end_date)
                self.custom_end_layout.addStretch()
    
    def generate_last_week_report(self):
        """Genera reporte de la semana anterior automáticamente"""
        current_date = datetime.now()
        week_number = current_date.isocalendar()[1] - 1
        if week_number < 1:
            week_number = 52
        year = current_date.year
        
        # Configurar formulario
        self.year_combo.setCurrentText(str(year))
        self.report_type_combo.setCurrentText("Semanal")
        self.week_entry.setText(str(week_number))
        
        # Generar
        self.generate_report()
    
    def generate_this_month_report(self):
        """Genera reporte del mes anterior completo automáticamente"""
        current_date = datetime.now()
        month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        # Usar el mes anterior (datos completos)
        month_number = current_date.month - 1
        year = current_date.year
        
        # Si estamos en enero, usar diciembre del año anterior
        if month_number < 1:
            month_number = 12
            year -= 1
        
        month_name = month_names[month_number - 1]
        
        # Configurar formulario
        self.year_combo.setCurrentText(str(year))
        self.report_type_combo.setCurrentText("Mensual")
        self.month_combo.setCurrentText(month_name)
        
        # Generar
        self.generate_report()
    
    def generate_report(self):
        """Genera el reporte según el tipo y parámetros seleccionados"""
        if self.current_thread and self.current_thread.isRunning():
            QMessageBox.warning(self, "Generación en Progreso", 
                              "Ya hay un reporte generándose. Por favor espera.")
            return
        
        report_type = self.report_type_combo.currentText()
        year = int(self.year_combo.currentText())
        
        kwargs = {}
        
        # Validar y recopilar parámetros según tipo
        if report_type == "Semanal":
            week_text = self.week_entry.text().strip()
            if not week_text:
                QMessageBox.warning(self, "Campo Requerido", "Por favor ingresa el número de semana.")
                return
            try:
                week = int(week_text)
                if week < 1 or week > 53:
                    QMessageBox.warning(self, "Valor Inválido", "El número de semana debe estar entre 1 y 53.")
                    return
                kwargs['week'] = week
            except ValueError:
                QMessageBox.warning(self, "Valor Inválido", "El número de semana debe ser un número.")
                return
        
        elif report_type == "Mensual":
            month_name = self.month_combo.currentText()
            month_names = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            month = month_names.index(month_name) + 1
            kwargs['month'] = month
        
        elif report_type == "Trimestral":
            quarter = self.quarter_combo.currentText()
            kwargs['quarter'] = quarter
        
        elif report_type == "Anual":
            # No necesita parámetros adicionales
            pass
        
        elif report_type == "Personalizado":
            start_date = self.custom_start_date.date().toPython()
            end_date = self.custom_end_date.date().toPython()
            
            if start_date > end_date:
                QMessageBox.warning(self, "Fechas Inválidas", 
                                  "La fecha de inicio debe ser anterior a la fecha de fin.")
                return
            
            kwargs['start_date'] = start_date
            kwargs['end_date'] = end_date
        
        # Agregar parámetro de comparación (solo para Semanal, Mensual y Trimestral)
        if report_type in ["Semanal", "Mensual", "Trimestral"]:
            kwargs['include_comparison'] = self.comparison_checkbox.isChecked()
        
        # Iniciar generación en thread
        self.show_progress("Iniciando generación...")
        self.current_thread = ReportThread(report_type, year, **kwargs)
        self.current_thread.progress_update.connect(self.on_progress_update)
        self.current_thread.progress_percent.connect(self.on_progress_percent)
        self.current_thread.finished_success.connect(self.on_success)
        self.current_thread.finished_error.connect(self.on_error)
        self.current_thread.finished_warning.connect(self.on_warning)
        self.current_thread.finished_exception.connect(self.on_exception)  # Nueva señal
        self.current_thread.start()
    
    def show_progress(self, message):
        """Muestra barra de progreso y deshabilita botón"""
        self.status_label.setText(message)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.generate_btn.setEnabled(False)
        self.this_week_btn.setEnabled(False)
        self.this_month_btn.setEnabled(False)
    
    def hide_progress(self):
        """Oculta barra de progreso y habilita botón"""
        self.status_label.setText("")
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.generate_btn.setEnabled(True)
        self.this_week_btn.setEnabled(True)
        self.this_month_btn.setEnabled(True)
    
    def on_progress_update(self, message):
        """Actualiza mensaje de progreso"""
        self.status_label.setText(message)
    
    def on_progress_percent(self, percent):
        """Actualiza porcentaje de progreso"""
        self.progress_bar.setValue(percent)
    
    def on_success(self, message):
        """Maneja generación exitosa"""
        self.hide_progress()
        QMessageBox.information(self, "Éxito", message)
    
    def on_error(self, message):
        """Maneja error en generación"""
        self.hide_progress()
        QMessageBox.critical(self, "Error", message)
    
    def on_warning(self, message):
        """Maneja advertencia en generación"""
        self.hide_progress()
        QMessageBox.warning(self, "Advertencia", message)
    
    def on_exception(self, exception):
        """Maneja excepciones capturadas durante la generación"""
        self.hide_progress()
        show_error_dialog(exception, self)
    
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            ThemeManager.apply_dark_theme(self)
            self.theme_action.setText("☀️ Modo Claro")
        else:
            ThemeManager.apply_light_theme(self)
            self.theme_action.setText("🌙 Modo Oscuro")
    
    def setup_icon(self):
        """Configura el ícono de la aplicación"""
        try:
            if APP_ICON_PATH:
                self.setWindowIcon(QIcon(APP_ICON_PATH))
        except:
            pass
    
    def setup_menubar(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Ver
        view_menu = menubar.addMenu("Ver")
        
        # Acción Dashboard
        self.dashboard_action = view_menu.addAction("📊 Dashboard")
        self.dashboard_action.triggered.connect(self.show_dashboard)
        self.dashboard_action.setStatusTip("Abre el dashboard con KPIs en tiempo real")
        
        view_menu.addSeparator()
        
        # Menú Datos
        data_menu = menubar.addMenu("Datos")
        
        # Acción recargar datos
        self.reload_action = data_menu.addAction("🔄 Recargar Datos")
        self.reload_action.triggered.connect(self.reload_data_cache)
        self.reload_action.setStatusTip("Fuerza la recarga de datos desde el archivo Excel")
        
        data_menu.addSeparator()
        
        # Acción validar datos
        self.validate_action = data_menu.addAction("✓ Validar Datos")
        self.validate_action.triggered.connect(self.validate_data)
        self.validate_action.setStatusTip("Ejecuta validación completa de calidad de datos")
        
        data_menu.addSeparator()
        
        # Acción gestionar backups
        self.backups_action = data_menu.addAction("💾 Gestionar Backups")
        self.backups_action.triggered.connect(self.manage_backups)
        self.backups_action.setStatusTip("Ver, restaurar y gestionar backups del archivo de datos")
        
        data_menu.addSeparator()
        
        # Acción historial de reportes
        self.history_action = data_menu.addAction("📚 Historial de Reportes")
        self.history_action.triggered.connect(self.show_report_history)
        self.history_action.setStatusTip("Ver y gestionar reportes generados previamente")
        
        # Menú Vista
        view_menu = menubar.addMenu("Vista")
        
        # Acción cambiar tema
        self.theme_action = view_menu.addAction("🌙 Modo Claro")
        self.theme_action.triggered.connect(self.toggle_theme)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        # Acción ver logs
        self.logs_action = help_menu.addAction("📋 Ver Logs")
        self.logs_action.triggered.connect(self.show_logs)
        self.logs_action.setStatusTip("Abre el visor de logs de la aplicación")
    
    def reload_data_cache(self):
        """Limpia el caché y fuerza recarga de datos"""
        from src.processors.data_loader import clear_data_cache
        
        reply = QMessageBox.question(
            self, 
            "Recargar Datos",
            "¿Desea limpiar el caché y recargar los datos del archivo Excel?\n\n"
            "Esto es útil si el archivo fue modificado externamente.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                clear_data_cache()
                QMessageBox.information(
                    self,
                    "Caché Limpiado",
                    "El caché de datos ha sido limpiado exitosamente.\n\n"
                    "Los datos se recargarán en la próxima generación de reporte."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al limpiar caché:\n\n{str(e)}"
                )
    
    def show_logs(self):
        """Abre el visor de logs"""
        try:
            show_log_viewer(self)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el visor de logs:\n\n{str(e)}"
            )
    
    def validate_data(self):
        """Ejecuta validación manual de datos"""
        try:
            from src.processors.data_loader import load_data
            from config import DATA_FILE_PATH
            
            # Mostrar mensaje de progreso
            self.progress_label.setText("Cargando y validando datos...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Modo indeterminado
            
            # Cargar y validar datos
            scrap_df, ventas_df, horas_df, validation_result = load_data(
                DATA_FILE_PATH, 
                force_reload=False,
                validate=True
            )
            
            # Ocultar progreso
            self.progress_bar.setVisible(False)
            self.progress_label.setText("")
            
            # Mostrar resultados
            if validation_result:
                show_validation_report(validation_result, self)
            else:
                QMessageBox.information(
                    self,
                    "Validación Completa",
                    "Los datos fueron validados exitosamente.\n\n"
                    "No se encontraron problemas."
                )
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.progress_label.setText("")
            QMessageBox.critical(
                self,
                "Error",
                f"Error durante la validación:\n\n{str(e)}"
            )
    
    def manage_backups(self):
        """Abre el gestor de backups"""
        try:
            from config import DATA_FILE_PATH
            show_backup_manager(DATA_FILE_PATH, self)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el gestor de backups:\n\n{str(e)}"
            )
    
    def show_report_history(self):
        """Abre el diálogo de historial de reportes"""
        try:
            from ui.dialogs import ReportHistoryDialog
            dialog = ReportHistoryDialog(self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el historial de reportes:\n\n{str(e)}"
            )
    
    def show_dashboard(self):
        """Abre el dashboard de KPIs"""
        try:
            from ui.dialogs import DashboardDialog
            dialog = DashboardDialog(self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el dashboard:\n\n{str(e)}"
            )


def run_app():
    """Ejecuta la aplicación"""
    app = QApplication(sys.argv)
    
    # Configurar estilo global de la aplicación
    app.setStyle("Fusion")
    
    window = ScrapRateApp()
    window.show()
    
    sys.exit(app.exec())

