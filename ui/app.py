"""
Interfaz gráfica de usuario con customtkinter
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os

from src.data_processor import load_data, process_weekly_data
from src.report_formatter import export_to_console
from src.pdf_generator import generate_pdf_report
from src.top_contributors import export_contributors_to_console
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_THEME, APP_COLOR_THEME


class ScrapRateApp(ctk.CTk):
    """Aplicación principal para análisis de Scrap Rate"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        
        # Variable para almacenar el último resultado
        self.last_result = None
        self.last_contributors = None
        self.last_week = None
        self.last_year = None
        
        # Configurar el tema
        ctk.set_appearance_mode(APP_THEME)
        ctk.set_default_color_theme(APP_COLOR_THEME)
        
        # Obtener año y semana actual
        current_date = datetime.now()
        self.current_year = current_date.year
        self.current_week = int(current_date.strftime('%U'))
        
        # Crear widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Título
        title_label = ctk.CTkLabel(
            self, 
            text="Reporte Semanal de Scrap Rate",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Frame para los inputs
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Label y Entry para Año
        year_label = ctk.CTkLabel(
            input_frame,
            text="Año:",
            font=ctk.CTkFont(size=14)
        )
        year_label.pack(pady=(20, 5))
        
        self.year_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=f"Año (default: {self.current_year})",
            width=200,
            justify="center"
        )
        self.year_entry.insert(0, str(self.current_year))
        self.year_entry.pack(pady=5)
        
        # Label y Entry para Semana
        week_label = ctk.CTkLabel(
            input_frame,
            text="Semana:",
            font=ctk.CTkFont(size=14)
        )
        week_label.pack(pady=(15, 5))
        
        self.week_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=f"Semana (default: {self.current_week})",
            width=200,
            justify="center"
        )
        self.week_entry.insert(0, str(self.current_week))
        self.week_entry.pack(pady=5)
        
        # Botón para generar reporte en consola
        generate_button = ctk.CTkButton(
            self,
            text="Generar Reporte en Consola",
            command=self.generate_report,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_button.pack(pady=(20, 10))
        
        # Botón para generar PDF
        pdf_button = ctk.CTkButton(
            self,
            text="📄 Generar PDF",
            command=self.generate_pdf,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        pdf_button.pack(pady=10)
        
    def generate_report(self):
        """Genera el reporte con los valores ingresados"""
        try:
            # Obtener valores de los entries
            year = int(self.year_entry.get())
            week = int(self.week_entry.get())
            
            # Validar semana
            if week < 0 or week > 53:
                messagebox.showerror("Error", "La semana debe estar entre 0 y 53")
                return
            
            # Validar año
            if year < 2000 or year > 2100:
                messagebox.showerror("Error", "Ingrese un año válido")
                return
            
            # Cargar datos
            scrap_df, ventas_df, horas_df = load_data()
            
            if scrap_df is None:
                messagebox.showerror(
                    "Error", 
                    "No se pudo cargar el archivo.\nVerifique que 'test pandas.xlsx' exista en la carpeta 'data/'"
                )
                return
            
            # Procesar datos
            result = process_weekly_data(scrap_df, ventas_df, horas_df, week, year)
            
            # Guardar resultado para PDF
            self.last_result = result
            self.last_week = week
            self.last_year = year
            
            # Exportar a consola (deshabilitado)
            export_to_console(result, week, year)
            
            # Generar top contribuidores
            contributors = export_contributors_to_console(scrap_df, week, year, top_n=10)
            self.last_contributors = contributors
            
            if result is not None:
                messagebox.showinfo(
                    "Éxito", 
                    f"✅ Reporte generado exitosamente\n\nSemana: {week}\nAño: {year}"
                )
            else:
                messagebox.showwarning(
                    "Sin datos", 
                    f"⚠️  No se encontraron datos para:\n\nSemana: {week}\nAño: {year}"
                )
                
        except ValueError:
            messagebox.showerror("Error", "❌ Ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Ocurrió un error:\n\n{str(e)}")
    
    def generate_pdf(self):
        """Genera un PDF con el último reporte generado"""
        if self.last_result is None:
            messagebox.showwarning(
                "Advertencia",
                "⚠️  Primero debe generar un reporte en consola"
            )
            return
        
        try:
            filepath = generate_pdf_report(
                self.last_result,
                self.last_contributors,
                self.last_week, 
                self.last_year
            )
            
            if filepath:
                # Abrir la carpeta donde se guardó el PDF
                folder_path = os.path.dirname(filepath)
                
                messagebox.showinfo(
                    "PDF Generado",
                    f"✅ PDF generado exitosamente:\n\n{os.path.basename(filepath)}\n\nUbicación: {folder_path}"
                )
                
                # Opcional: abrir la carpeta automáticamente
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(folder_path)
                    elif os.name == 'posix':  # macOS y Linux
                        os.system(f'open "{folder_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{folder_path}"')
                except:
                    pass  # Si no se puede abrir la carpeta, no pasa nada
            else:
                messagebox.showerror("Error", "❌ No se pudo generar el PDF")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al generar PDF:\n\n{str(e)}")


def run_app():
    """Ejecuta la aplicación"""
    app = ScrapRateApp()
    app.mainloop()