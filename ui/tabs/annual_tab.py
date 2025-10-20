"""
anual_tab.py - Pestaña para reportes anuales
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import threading

from ui.tabs.base_tab import BaseTab
from src.processors.data_loader import load_data
from src.processors.annual_processor import process_annual_data
from src.pdf_annual_generator import generate_annual_pdf_report
from src.analysis.annual_contributors import export_annual_contributors_to_console

class AnnualTab(BaseTab):
    """Pestaña para generación de reportes anuales"""

    def __init__(self, parent_frame, root_app):
        """
        Inicializa la pestaña anual
        Args:
            parent_frame: Frame padre
            root_app: Referencia a la aplicación principal
        """
        super().__init__(parent_frame)
        self.root_app = root_app
        self.current_year = datetime.now().year
        self.create_content()

    def create_content(self):
        """Crea el contenido de la pestaña anual"""
        # Selector de año
        self.year_combobox = self.create_year_selector()

        # Barra de progreso
        self.progress_bar, self.status_label = self.create_progress_bar()

        # Botón generar PDF
        self.pdf_button = ctk.CTkButton(
            self.frame,
            text="Generar Reporte PDF",
            command=self.start_pdf_generation,
            width=250,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2F6690",
            hover_color="#9DB4C0"
        )
        self.pdf_button.pack(pady=20)

    def start_pdf_generation(self):
        """Inicia la generación del PDF en un hilo separado"""
        thread = threading.Thread(target=self.generate_pdf, daemon=True)
        thread.start()

    def generate_pdf(self):
        """Genera el PDF anual con todos los datos"""
        try:
            # Obtener año
            year = int(self.year_combobox.get())
            if year < 2000 or year > 2100:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese un año válido"))
                return

            # Paso 1: Cargar datos
            self.root_app.after(0, lambda: self.show_progress(
                self.progress_bar, self.status_label, self.pdf_button, "⌛ Cargando datos..."
            ))
            scrap_df, ventas_df, horas_df = load_data()
            if scrap_df is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showerror(
                    "Error",
                    "No se pudo cargar el archivo.\nVerifique que 'test pandas.xlsx' exista en la carpeta 'data/'"
                ))
                return

            # Paso 2: Procesar datos
            self.root_app.after(0, lambda: self.status_label.configure(text="⚙️ Procesando datos..."))

            service = getattr(self.root_app, 'report_service_annual', None)
            if service:
                filepath = service.run_report({'year': year})
                if filepath:
                    self.root_app.after(0, lambda: self.hide_progress(
                        self.progress_bar, self.status_label, self.pdf_button
                    ))
                    self.root_app.after(0, lambda: messagebox.showinfo(
                        "Éxito",
                        f"El archivo [{os.path.basename(filepath)}]\n\n se ha generado exitosamente."
                    ))
                    try:
                        if os.name == 'nt':
                            os.startfile(filepath)
                        elif os.name == 'posix':
                            os.system(f'open "{filepath}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{filepath}"')
                    except:
                        pass
                    return
                else:
                    result = None
            else:
                result = process_annual_data(scrap_df, ventas_df, horas_df, year)

            if result is None:
                self.root_app.after(0, lambda: self.hide_progress(
                    self.progress_bar, self.status_label, self.pdf_button
                ))
                self.root_app.after(0, lambda: messagebox.showwarning(
                    "Sin datos",
                    f"No se encontraron datos para:\n\nAño: {year}"
                ))
                return

            # Paso 3: Analizar contribuidores
            self.root_app.after(0, lambda: self.status_label.configure(text="🔍 Analizando contribuidores..."))
            contributors = export_annual_contributors_to_console(scrap_df, year, top_n=10)

            # Paso 4: Generar PDF
            self.root_app.after(0, lambda: self.status_label.configure(text="📄 Generando PDF..."))
            filepath = generate_annual_pdf_report(
                result,
                contributors,
                year,
                scrap_df,
                ventas_df,
                horas_df
            )

            # Ocultar progreso
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))

            # Mostrar mensaje de éxito o error
            if filepath:
                folder_path = os.path.dirname(filepath)
                self.root_app.after(0, lambda: messagebox.showinfo(
                    "Éxito",
                    f"El archivo [{os.path.basename(filepath)}]\n\n se ha generado exitosamente."
                ))
                # Abrir PDF
                try:
                    if os.name == 'nt':
                        os.startfile(filepath)
                    elif os.name == 'posix':
                        os.system(f'open "{filepath}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{filepath}"')
                except:
                    pass
            else:
                self.root_app.after(0, lambda: messagebox.showerror("Error", "No se pudo generar el PDF"))

        except ValueError:
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            self.root_app.after(0, lambda: messagebox.showerror("Error", "Ingrese valores numéricos válidos"))
        except Exception as e:
            self.root_app.after(0, lambda: self.hide_progress(
                self.progress_bar, self.status_label, self.pdf_button
            ))
            error_msg = str(e)
            self.root_app.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Ocurrió un error:\n\n{msg}"))
