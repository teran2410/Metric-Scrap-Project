"""
exceptions.py - Jerarquía de excepciones personalizadas para el proyecto

Proporciona excepciones específicas con mensajes descriptivos y acciones sugeridas
para facilitar el diagnóstico y resolución de problemas.
"""


class MetricScrapError(Exception):
    """
    Clase base para todas las excepciones del proyecto.
    
    Attributes:
        message (str): Mensaje descriptivo del error
        suggested_action (str): Acción sugerida para resolver el problema
        original_error (Exception): Excepción original si existe
    """
    
    def __init__(self, message, suggested_action=None, original_error=None):
        """
        Inicializa la excepción.
        
        Args:
            message (str): Mensaje descriptivo del error
            suggested_action (str, optional): Acción sugerida para el usuario
            original_error (Exception, optional): Excepción original que causó este error
        """
        self.message = message
        self.suggested_action = suggested_action or "Contacte al equipo de soporte técnico."
        self.original_error = original_error
        
        # Construir mensaje completo
        full_message = f"{message}\n\nAcción sugerida: {self.suggested_action}"
        if original_error:
            full_message += f"\n\nError original: {str(original_error)}"
        
        super().__init__(full_message)
    
    def get_user_message(self):
        """Retorna un mensaje formateado para mostrar al usuario"""
        msg = f"❌ {self.message}"
        if self.suggested_action:
            msg += f"\n\n💡 {self.suggested_action}"
        return msg
    
    def get_technical_details(self):
        """Retorna detalles técnicos para logging/debugging"""
        details = f"Error: {self.__class__.__name__}\n"
        details += f"Mensaje: {self.message}\n"
        if self.original_error:
            details += f"Error original: {type(self.original_error).__name__}: {str(self.original_error)}"
        return details


class DataLoadError(MetricScrapError):
    """
    Error al cargar datos desde archivos Excel.
    
    Se lanza cuando hay problemas leyendo el archivo de datos,
    como archivo no encontrado, permisos insuficientes, o formato incorrecto.
    """
    
    def __init__(self, file_path, reason=None, original_error=None):
        """
        Args:
            file_path (str): Ruta del archivo que causó el error
            reason (str, optional): Razón específica del error
            original_error (Exception, optional): Excepción original
        """
        self.file_path = file_path
        
        if reason:
            message = f"No se pudo cargar el archivo de datos:\n{file_path}\n\nRazón: {reason}"
        else:
            message = f"No se pudo cargar el archivo de datos:\n{file_path}"
        
        suggested_action = (
            "Verifique que:\n"
            "• El archivo existe en la ubicación especificada\n"
            "• El archivo no está abierto en otra aplicación\n"
            "• Tiene permisos para leer el archivo\n"
            "• El archivo es un Excel válido (.xlsx)"
        )
        
        super().__init__(message, suggested_action, original_error)


class DataValidationError(MetricScrapError):
    """
    Error de validación de datos.
    
    Se lanza cuando los datos cargados no cumplen con el esquema esperado,
    como columnas faltantes, tipos de datos incorrectos, o valores inválidos.
    """
    
    def __init__(self, validation_issue, details=None, original_error=None):
        """
        Args:
            validation_issue (str): Descripción del problema de validación
            details (list or str, optional): Detalles adicionales (ej: columnas faltantes)
            original_error (Exception, optional): Excepción original
        """
        self.validation_issue = validation_issue
        self.details = details
        
        message = f"Error de validación de datos: {validation_issue}"
        
        if details:
            if isinstance(details, list):
                message += f"\n\nDetalles:\n• " + "\n• ".join(details)
            else:
                message += f"\n\nDetalles: {details}"
        
        suggested_action = (
            "Verifique que:\n"
            "• El archivo Excel tiene la estructura correcta\n"
            "• Las hojas requeridas existen (Scrap, Ventas, Horas)\n"
            "• Las columnas necesarias están presentes\n"
            "• Los datos tienen el formato esperado"
        )
        
        super().__init__(message, suggested_action, original_error)


class ProcessingError(MetricScrapError):
    """
    Error durante el procesamiento de datos.
    
    Se lanza cuando hay problemas al procesar/transformar los datos,
    como cálculos fallidos, conversiones de fecha, o agregaciones.
    """
    
    def __init__(self, operation, reason=None, original_error=None):
        """
        Args:
            operation (str): Operación que estaba ejecutándose
            reason (str, optional): Razón del fallo
            original_error (Exception, optional): Excepción original
        """
        self.operation = operation
        
        message = f"Error procesando datos durante: {operation}"
        if reason:
            message += f"\n\nRazón: {reason}"
        
        suggested_action = (
            "Verifique que:\n"
            "• Los datos tienen el formato esperado\n"
            "• Las fechas están en formato válido\n"
            "• Los valores numéricos son correctos\n"
            "• El rango de fechas seleccionado contiene datos"
        )
        
        super().__init__(message, suggested_action, original_error)


class PDFGenerationError(MetricScrapError):
    """
    Error durante la generación de PDFs.
    
    Se lanza cuando hay problemas creando el documento PDF,
    como errores de escritura, problemas con gráficos, o falta de espacio.
    """
    
    def __init__(self, report_type, reason=None, original_error=None):
        """
        Args:
            report_type (str): Tipo de reporte que se estaba generando
            reason (str, optional): Razón específica del error
            original_error (Exception, optional): Excepción original
        """
        self.report_type = report_type
        
        message = f"Error generando reporte PDF ({report_type})"
        if reason:
            message += f"\n\nRazón: {reason}"
        
        suggested_action = (
            "Verifique que:\n"
            "• Tiene espacio suficiente en disco\n"
            "• La carpeta 'reports/' existe y tiene permisos de escritura\n"
            "• No hay un PDF con el mismo nombre abierto\n"
            "• Los datos procesados son válidos"
        )
        
        super().__init__(message, suggested_action, original_error)


class CacheError(MetricScrapError):
    """
    Error relacionado con el sistema de caché.
    
    Se lanza cuando hay problemas con el caché de datos en memoria.
    """
    
    def __init__(self, operation, reason=None, original_error=None):
        """
        Args:
            operation (str): Operación de caché que falló
            reason (str, optional): Razón del fallo
            original_error (Exception, optional): Excepción original
        """
        self.operation = operation
        
        message = f"Error en sistema de caché: {operation}"
        if reason:
            message += f"\n\nRazón: {reason}"
        
        suggested_action = (
            "Intente:\n"
            "• Usar 'Datos → Recargar Datos' para limpiar el caché\n"
            "• Reiniciar la aplicación\n"
            "• Verificar que el archivo Excel no está corrupto"
        )
        
        super().__init__(message, suggested_action, original_error)


class ConfigurationError(MetricScrapError):
    """
    Error de configuración.
    
    Se lanza cuando hay problemas con archivos de configuración o settings.
    """
    
    def __init__(self, config_item, reason=None, original_error=None):
        """
        Args:
            config_item (str): Elemento de configuración problemático
            reason (str, optional): Razón del problema
            original_error (Exception, optional): Excepción original
        """
        self.config_item = config_item
        
        message = f"Error de configuración: {config_item}"
        if reason:
            message += f"\n\nRazón: {reason}"
        
        suggested_action = (
            "Verifique que:\n"
            "• Los archivos de configuración existen\n"
            "• Los valores de configuración son válidos\n"
            "• No se han modificado archivos críticos del sistema"
        )
        
        super().__init__(message, suggested_action, original_error)
