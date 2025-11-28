"""
data_validator.py - Sistema avanzado de validación de datos

Valida la calidad e integridad de los datos cargados desde Excel:
- Estructura de columnas
- Tipos de datos
- Rangos válidos
- Valores nulos/negativos
- Duplicados
- Anomalías estadísticas
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Niveles de severidad para problemas de validación"""
    ERROR = "ERROR"      # Problema crítico que impide el procesamiento
    WARNING = "WARNING"  # Problema que puede afectar resultados
    INFO = "INFO"        # Observación informativa


@dataclass
class ValidationIssue:
    """Representa un problema encontrado durante la validación"""
    severity: Severity
    category: str
    message: str
    details: str
    affected_rows: int = 0
    sheet_name: str = ""
    
    def __str__(self):
        return f"[{self.severity.value}] {self.category}: {self.message}"


class ValidationResult:
    """Resultado completo de validación con todos los problemas encontrados"""
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.passed = True
        self.total_errors = 0
        self.total_warnings = 0
        self.total_infos = 0
    
    def add_issue(self, issue: ValidationIssue):
        """Agrega un problema al reporte de validación"""
        self.issues.append(issue)
        
        # Log cada problema individual
        logger.debug(f"[{issue.severity.value}] {issue.sheet_name} - {issue.category}: {issue.message}")
        
        if issue.severity == Severity.ERROR:
            self.passed = False
            self.total_errors += 1
            logger.error(f"❌ {issue.category}: {issue.message} ({issue.sheet_name})")
        elif issue.severity == Severity.WARNING:
            self.total_warnings += 1
            logger.warning(f"⚠️ {issue.category}: {issue.message} ({issue.sheet_name})")
        elif issue.severity == Severity.INFO:
            self.total_infos += 1
            logger.info(f"ℹ️ {issue.category}: {issue.message} ({issue.sheet_name})")
    
    def has_errors(self) -> bool:
        """Verifica si hay errores críticos"""
        return self.total_errors > 0
    
    def has_warnings(self) -> bool:
        """Verifica si hay advertencias"""
        return self.total_warnings > 0
    
    def get_summary(self) -> str:
        """Obtiene resumen de la validación"""
        if not self.issues:
            return "✓ Validación exitosa - No se encontraron problemas"
        
        summary = f"Validación completada con {len(self.issues)} problemas:\n"
        summary += f"  • Errores: {self.total_errors}\n"
        summary += f"  • Advertencias: {self.total_warnings}\n"
        summary += f"  • Info: {self.total_infos}"
        return summary


class DataValidator:
    """Validador avanzado para datos de Scrap, Ventas y Horas"""
    
    def __init__(self):
        self.result = ValidationResult()
    
    def validate_all(self, scrap_df: pd.DataFrame, ventas_df: pd.DataFrame, 
                     horas_df: pd.DataFrame) -> ValidationResult:
        """
        Ejecuta todas las validaciones en los 3 DataFrames.
        
        Args:
            scrap_df: DataFrame con datos de scrap
            ventas_df: DataFrame con datos de ventas
            horas_df: DataFrame con datos de horas
            
        Returns:
            ValidationResult con todos los problemas encontrados
        """
        logger.info("=== Iniciando validación completa de datos ===")
        
        # Validar cada hoja
        self._validate_scrap(scrap_df)
        self._validate_ventas(ventas_df)
        self._validate_horas(horas_df)
        
        # Validaciones cruzadas
        self._validate_date_consistency(scrap_df, ventas_df, horas_df)
        
        logger.info(self.result.get_summary())
        return self.result
    
    def _validate_scrap(self, df: pd.DataFrame):
        """Valida datos de Scrap"""
        sheet_name = "Scrap"
        logger.debug(f"Validando hoja {sheet_name}...")
        
        # Validar columnas requeridas
        required_cols = ['Create Date', 'Total Posted', 'Item', 'Description', 'Location', 'Quantity']
        self._check_required_columns(df, required_cols, sheet_name)
        
        if df.empty:
            self.result.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="Datos Vacíos",
                message=f"La hoja {sheet_name} está vacía",
                details="No se encontraron registros en la hoja de Scrap",
                sheet_name=sheet_name
            ))
            return
        
        # Validar tipos de datos
        self._check_date_column(df, 'Create Date', sheet_name)
        self._check_numeric_column(df, 'Total Posted', sheet_name)
        self._check_numeric_column(df, 'Quantity', sheet_name, allow_negative=True)
        
        # Validar valores nulos
        self._check_nulls(df, ['Item', 'Location'], sheet_name)
        
        # Validar rangos de fechas
        self._check_date_range(df, 'Create Date', sheet_name)
        
        # Detectar valores extremos
        self._check_outliers(df, 'Total Posted', sheet_name, "Scrap")
        
        # Validar duplicados
        self._check_duplicates(df, ['Create Date', 'Item', 'Location'], sheet_name)
    
    def _validate_ventas(self, df: pd.DataFrame):
        """Valida datos de Ventas"""
        sheet_name = "Ventas"
        logger.debug(f"Validando hoja {sheet_name}...")
        
        required_cols = ['Create Date', 'Total Posted']
        self._check_required_columns(df, required_cols, sheet_name)
        
        if df.empty:
            self.result.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="Datos Vacíos",
                message=f"La hoja {sheet_name} está vacía",
                details="No se encontraron registros en la hoja de Ventas",
                sheet_name=sheet_name
            ))
            return
        
        self._check_date_column(df, 'Create Date', sheet_name)
        self._check_numeric_column(df, 'Total Posted', sheet_name)
        self._check_date_range(df, 'Create Date', sheet_name)
        self._check_outliers(df, 'Total Posted', sheet_name, "Ventas")
        
        # Validar que no haya ventas negativas
        if 'Total Posted' in df.columns:
            negative_count = (pd.to_numeric(df['Total Posted'], errors='coerce') < 0).sum()
            if negative_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Valores Negativos",
                    message=f"Se encontraron {negative_count} ventas con valores negativos",
                    details="Las ventas deberían ser valores positivos. Valores negativos pueden indicar devoluciones o errores.",
                    affected_rows=negative_count,
                    sheet_name=sheet_name
                ))
    
    def _validate_horas(self, df: pd.DataFrame):
        """Valida datos de Horas"""
        sheet_name = "Horas"
        logger.debug(f"Validando hoja {sheet_name}...")
        
        required_cols = ['Trans Date', 'Actual Hours']
        self._check_required_columns(df, required_cols, sheet_name)
        
        if df.empty:
            self.result.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="Datos Vacíos",
                message=f"La hoja {sheet_name} está vacía",
                details="No se encontraron registros en la hoja de Horas",
                sheet_name=sheet_name
            ))
            return
        
        self._check_date_column(df, 'Trans Date', sheet_name)
        self._check_numeric_column(df, 'Actual Hours', sheet_name)
        self._check_date_range(df, 'Trans Date', sheet_name)
        
        # Validar que horas sean razonables (0-24 por registro típicamente)
        if 'Actual Hours' in df.columns:
            hours_numeric = pd.to_numeric(df['Actual Hours'], errors='coerce')
            negative_count = (hours_numeric < 0).sum()
            excessive_count = (hours_numeric > 24).sum()
            
            if negative_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="Valores Negativos",
                    message=f"Se encontraron {negative_count} registros con horas negativas",
                    details="Las horas trabajadas no pueden ser negativas. Esto indica un error en los datos.",
                    affected_rows=negative_count,
                    sheet_name=sheet_name
                ))
            
            if excessive_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Valores Inusuales",
                    message=f"Se encontraron {excessive_count} registros con más de 24 horas",
                    details="Algunos registros tienen más de 24 horas. Esto podría ser normal (acumulado) o un error.",
                    affected_rows=excessive_count,
                    sheet_name=sheet_name
                ))
    
    def _check_required_columns(self, df: pd.DataFrame, required: List[str], sheet_name: str):
        """Verifica que existan todas las columnas requeridas"""
        missing = [col for col in required if col not in df.columns]
        if missing:
            self.result.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="Columnas Faltantes",
                message=f"Faltan columnas requeridas en {sheet_name}",
                details=f"Columnas faltantes: {', '.join(missing)}",
                sheet_name=sheet_name
            ))
    
    def _check_date_column(self, df: pd.DataFrame, col_name: str, sheet_name: str):
        """Valida que una columna contenga fechas válidas"""
        if col_name not in df.columns:
            return
        
        try:
            date_series = pd.to_datetime(df[col_name], errors='coerce')
            null_count = date_series.isna().sum()
            
            if null_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Fechas Inválidas",
                    message=f"Se encontraron {null_count} fechas inválidas en '{col_name}'",
                    details=f"Algunos registros en {sheet_name} tienen fechas que no se pueden interpretar.",
                    affected_rows=null_count,
                    sheet_name=sheet_name
                ))
        except Exception as e:
            self.result.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="Error de Formato",
                message=f"Error procesando columna de fecha '{col_name}'",
                details=str(e),
                sheet_name=sheet_name
            ))
    
    def _check_numeric_column(self, df: pd.DataFrame, col_name: str, sheet_name: str, 
                             allow_negative: bool = False):
        """Valida que una columna contenga valores numéricos"""
        if col_name not in df.columns:
            return
        
        numeric_series = pd.to_numeric(df[col_name], errors='coerce')
        null_count = numeric_series.isna().sum()
        
        if null_count > 0:
            self.result.add_issue(ValidationIssue(
                severity=Severity.WARNING,
                category="Valores No Numéricos",
                message=f"Se encontraron {null_count} valores no numéricos en '{col_name}'",
                details=f"Algunos registros no se pueden convertir a números en {sheet_name}.",
                affected_rows=null_count,
                sheet_name=sheet_name
            ))
        
        if not allow_negative:
            negative_count = (numeric_series < 0).sum()
            if negative_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Valores Negativos",
                    message=f"Se encontraron {negative_count} valores negativos en '{col_name}'",
                    details=f"Valores negativos detectados en {sheet_name}. Verifique si son esperados.",
                    affected_rows=negative_count,
                    sheet_name=sheet_name
                ))
    
    def _check_nulls(self, df: pd.DataFrame, columns: List[str], sheet_name: str):
        """Verifica valores nulos en columnas críticas"""
        for col in columns:
            if col not in df.columns:
                continue
            
            null_count = df[col].isna().sum()
            if null_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Valores Nulos",
                    message=f"Se encontraron {null_count} valores nulos en '{col}'",
                    details=f"Registros con datos faltantes en {sheet_name}.",
                    affected_rows=null_count,
                    sheet_name=sheet_name
                ))
    
    def _check_date_range(self, df: pd.DataFrame, col_name: str, sheet_name: str):
        """Valida que las fechas estén en un rango razonable"""
        if col_name not in df.columns:
            return
        
        try:
            date_series = pd.to_datetime(df[col_name], errors='coerce')
            valid_dates = date_series.dropna()
            
            if len(valid_dates) == 0:
                return
            
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            today = pd.Timestamp.now()
            
            # Fechas futuras
            future_count = (valid_dates > today).sum()
            if future_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Fechas Futuras",
                    message=f"Se encontraron {future_count} fechas futuras en '{col_name}'",
                    details=f"Rango: {min_date.date()} a {max_date.date()}. Hay fechas posteriores a hoy.",
                    affected_rows=future_count,
                    sheet_name=sheet_name
                ))
            
            # Fechas muy antiguas (más de 5 años)
            five_years_ago = today - pd.Timedelta(days=365*5)
            old_count = (valid_dates < five_years_ago).sum()
            if old_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.INFO,
                    category="Fechas Antiguas",
                    message=f"Se encontraron {old_count} fechas de hace más de 5 años",
                    details=f"Fecha más antigua: {min_date.date()}. Esto podría ser normal si tiene datos históricos.",
                    affected_rows=old_count,
                    sheet_name=sheet_name
                ))
        except Exception as e:
            logger.error(f"Error validando rango de fechas: {e}")
    
    def _check_outliers(self, df: pd.DataFrame, col_name: str, sheet_name: str, data_type: str):
        """Detecta valores atípicos estadísticamente"""
        if col_name not in df.columns:
            return
        
        try:
            numeric_series = pd.to_numeric(df[col_name], errors='coerce').dropna()
            
            if len(numeric_series) < 10:  # No suficientes datos para análisis estadístico
                return
            
            Q1 = numeric_series.quantile(0.25)
            Q3 = numeric_series.quantile(0.75)
            IQR = Q3 - Q1
            
            # Outliers usando método IQR
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = numeric_series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
            
            if len(outliers) > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.INFO,
                    category="Valores Atípicos",
                    message=f"Se detectaron {len(outliers)} valores atípicos en {data_type}",
                    details=f"Valores fuera del rango esperado [{lower_bound:.2f}, {upper_bound:.2f}]. "
                           f"Rango observado: [{outliers.min():.2f}, {outliers.max():.2f}]",
                    affected_rows=len(outliers),
                    sheet_name=sheet_name
                ))
        except Exception as e:
            logger.error(f"Error detectando outliers: {e}")
    
    def _check_duplicates(self, df: pd.DataFrame, columns: List[str], sheet_name: str):
        """Detecta registros duplicados"""
        if not all(col in df.columns for col in columns):
            return
        
        try:
            duplicates = df[df.duplicated(subset=columns, keep=False)]
            dup_count = len(duplicates)
            
            if dup_count > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="Registros Duplicados",
                    message=f"Se encontraron {dup_count} registros potencialmente duplicados",
                    details=f"Duplicados basados en: {', '.join(columns)}. Esto podría ser intencional o un error.",
                    affected_rows=dup_count,
                    sheet_name=sheet_name
                ))
        except Exception as e:
            logger.error(f"Error detectando duplicados: {e}")
    
    def _validate_date_consistency(self, scrap_df: pd.DataFrame, ventas_df: pd.DataFrame, 
                                   horas_df: pd.DataFrame):
        """Valida consistencia de fechas entre las 3 hojas"""
        logger.debug("Validando consistencia de fechas entre hojas...")
        
        try:
            # Obtener rangos de fechas
            scrap_dates = pd.to_datetime(scrap_df['Create Date'], errors='coerce').dropna()
            ventas_dates = pd.to_datetime(ventas_df['Create Date'], errors='coerce').dropna()
            horas_dates = pd.to_datetime(horas_df['Trans Date'], errors='coerce').dropna()
            
            if len(scrap_dates) == 0 or len(ventas_dates) == 0 or len(horas_dates) == 0:
                return
            
            # Comparar rangos
            scrap_range = (scrap_dates.min(), scrap_dates.max())
            ventas_range = (ventas_dates.min(), ventas_dates.max())
            horas_range = (horas_dates.min(), horas_dates.max())
            
            # Verificar solapamiento significativo
            overall_min = min(scrap_range[0], ventas_range[0], horas_range[0])
            overall_max = max(scrap_range[1], ventas_range[1], horas_range[1])
            
            date_range_days = (overall_max - overall_min).days
            
            if date_range_days > 0:
                self.result.add_issue(ValidationIssue(
                    severity=Severity.INFO,
                    category="Información de Fechas",
                    message=f"Rango de datos: {date_range_days} días",
                    details=f"Desde {overall_min.date()} hasta {overall_max.date()}. "
                           f"Scrap: {len(scrap_dates)} registros, "
                           f"Ventas: {len(ventas_dates)} registros, "
                           f"Horas: {len(horas_dates)} registros"
                ))
        except Exception as e:
            logger.error(f"Error validando consistencia de fechas: {e}")


def validate_data(scrap_df: pd.DataFrame, ventas_df: pd.DataFrame, 
                  horas_df: pd.DataFrame) -> ValidationResult:
    """
    Función conveniente para validar datos.
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        
    Returns:
        ValidationResult con todos los problemas encontrados
    """
    validator = DataValidator()
    return validator.validate_all(scrap_df, ventas_df, horas_df)
