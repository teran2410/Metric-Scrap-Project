"""
period_comparison.py - Módulo para comparación de periodos

Calcula métricas del periodo anterior y compara con el periodo actual:
- Scrap rate anterior vs actual
- Total scrap anterior vs actual
- Horas producción anterior vs actual
- Porcentajes de cambio e indicadores visuales
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

from config import get_week_number_vectorized

logger = logging.getLogger(__name__)


@dataclass
class PeriodComparison:
    """Resultado de la comparación entre dos periodos"""
    # Periodo actual
    current_scrap_rate: float
    current_total_scrap: float
    current_total_hours: float
    
    # Periodo anterior
    previous_scrap_rate: float
    previous_total_scrap: float
    previous_total_hours: float
    
    # Cambios
    rate_change_pct: float  # Porcentaje de cambio en scrap rate
    scrap_change_abs: float  # Cambio absoluto en scrap ($)
    scrap_change_pct: float  # Porcentaje de cambio en scrap
    hours_change_pct: float  # Porcentaje de cambio en horas
    
    # Metadata
    period_label: str  # Ej: "Semana 20/2025"
    previous_label: str  # Ej: "Semana 19/2025"
    
    def is_improvement(self) -> bool:
        """Retorna True si el scrap rate mejoró (disminuyó)"""
        return self.rate_change_pct < 0
    
    def get_rate_indicator(self) -> str:
        """Retorna indicador visual para el cambio de rate"""
        if abs(self.rate_change_pct) < 1:  # Cambio menor a 1%
            return "→"
        return "↓" if self.is_improvement() else "↑"
    
    def get_scrap_indicator(self) -> str:
        """Retorna indicador visual para el cambio de scrap total"""
        if abs(self.scrap_change_pct) < 1:
            return "→"
        return "↓" if self.scrap_change_abs < 0 else "↑"


def compare_weekly_periods(scrap_df: pd.DataFrame, ventas_df: pd.DataFrame, 
                          horas_df: pd.DataFrame, week: int, year: int) -> Optional[PeriodComparison]:
    """
    Compara la semana actual con la semana anterior.
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        week: Número de semana actual
        year: Año actual
        
    Returns:
        PeriodComparison o None si no hay datos del periodo anterior
    """
    logger.info(f"Comparando semana {week}/{year} con semana anterior...")
    
    # Preparar DataFrames
    scrap_df = scrap_df.copy()
    ventas_df = ventas_df.copy()
    horas_df = horas_df.copy()
    
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    # Agregar semanas
    scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    horas_df['Week'] = get_week_number_vectorized(horas_df['Trans Date'], year=year)
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Calcular métricas semana actual
    current_scrap = scrap_df[(scrap_df['Week'] == week) & (scrap_df['Year'] == year)]
    current_horas = horas_df[(horas_df['Week'] == week) & (horas_df['Year'] == year)]
    
    # Usar valores absolutos para evitar confusión con negativos
    current_total_scrap = abs(current_scrap['Total Posted'].sum())
    current_total_hours = current_horas['Actual Hours'].sum()
    current_scrap_rate = current_total_scrap / current_total_hours if current_total_hours > 0 else 0
    
    # Calcular semana anterior
    previous_week = week - 1
    previous_year = year
    
    if previous_week < 1:  # Si es semana 1, ir al año anterior
        previous_week = 52
        previous_year = year - 1
    
    previous_scrap = scrap_df[(scrap_df['Week'] == previous_week) & (scrap_df['Year'] == previous_year)]
    previous_horas = horas_df[(horas_df['Week'] == previous_week) & (horas_df['Year'] == previous_year)]
    
    if len(previous_scrap) == 0 or len(previous_horas) == 0:
        logger.warning(f"No hay datos para la semana anterior {previous_week}/{previous_year}")
        return None
    
    # Usar valores absolutos para evitar confusión con negativos
    previous_total_scrap = abs(previous_scrap['Total Posted'].sum())
    previous_total_hours = previous_horas['Actual Hours'].sum()
    previous_scrap_rate = previous_total_scrap / previous_total_hours if previous_total_hours > 0 else 0
    
    # Calcular cambios (ahora todo es positivo, más = peor)
    rate_change_pct = ((current_scrap_rate - previous_scrap_rate) / previous_scrap_rate * 100) if previous_scrap_rate > 0 else 0
    scrap_change_abs = current_total_scrap - previous_total_scrap
    scrap_change_pct = ((current_total_scrap - previous_total_scrap) / previous_total_scrap * 100) if previous_total_scrap > 0 else 0
    hours_change_pct = ((current_total_hours - previous_total_hours) / previous_total_hours * 100) if previous_total_hours > 0 else 0
    
    comparison = PeriodComparison(
        current_scrap_rate=current_scrap_rate,
        current_total_scrap=current_total_scrap,
        current_total_hours=current_total_hours,
        previous_scrap_rate=previous_scrap_rate,
        previous_total_scrap=previous_total_scrap,
        previous_total_hours=previous_total_hours,
        rate_change_pct=rate_change_pct,
        scrap_change_abs=scrap_change_abs,
        scrap_change_pct=scrap_change_pct,
        hours_change_pct=hours_change_pct,
        period_label=f"Semana {week}/{year}",
        previous_label=f"Semana {previous_week}/{previous_year}"
    )
    
    logger.info(f"✓ Comparación calculada: Rate {current_scrap_rate:.2%} vs {previous_scrap_rate:.2%} ({rate_change_pct:+.1f}%)")
    
    return comparison


def compare_monthly_periods(scrap_df: pd.DataFrame, ventas_df: pd.DataFrame,
                           horas_df: pd.DataFrame, month: int, year: int) -> Optional[PeriodComparison]:
    """
    Compara el mes actual con el mes anterior.
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        month: Número de mes actual (1-12)
        year: Año actual
        
    Returns:
        PeriodComparison o None si no hay datos del periodo anterior
    """
    logger.info(f"Comparando mes {month}/{year} con mes anterior...")
    
    # Preparar DataFrames
    scrap_df = scrap_df.copy()
    horas_df = horas_df.copy()
    
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    # Convertir scrap a positivo usando valor absoluto
    scrap_df['Total Posted'] = scrap_df['Total Posted'].abs()
    
    scrap_df['Month'] = scrap_df['Create Date'].dt.month
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    horas_df['Month'] = horas_df['Trans Date'].dt.month
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Calcular métricas mes actual
    current_scrap = scrap_df[(scrap_df['Month'] == month) & (scrap_df['Year'] == year)]
    current_horas = horas_df[(horas_df['Month'] == month) & (horas_df['Year'] == year)]
    
    # Usar valores absolutos para evitar confusión con negativos
    current_total_scrap = abs(current_scrap['Total Posted'].sum())
    current_total_hours = current_horas['Actual Hours'].sum()
    current_scrap_rate = current_total_scrap / current_total_hours if current_total_hours > 0 else 0
    
    # Calcular mes anterior
    previous_month = month - 1
    previous_year = year
    
    if previous_month < 1:
        previous_month = 12
        previous_year = year - 1
    
    previous_scrap = scrap_df[(scrap_df['Month'] == previous_month) & (scrap_df['Year'] == previous_year)]
    previous_horas = horas_df[(horas_df['Month'] == previous_month) & (horas_df['Year'] == previous_year)]
    
    if len(previous_scrap) == 0 or len(previous_horas) == 0:
        logger.warning(f"No hay datos para el mes anterior {previous_month}/{previous_year}")
        return None
    
    # Usar valores absolutos para evitar confusión con negativos
    previous_total_scrap = abs(previous_scrap['Total Posted'].sum())
    previous_total_hours = previous_horas['Actual Hours'].sum()
    previous_scrap_rate = previous_total_scrap / previous_total_hours if previous_total_hours > 0 else 0
    
    # Calcular cambios (ahora todo es positivo, más = peor)
    rate_change_pct = ((current_scrap_rate - previous_scrap_rate) / previous_scrap_rate * 100) if previous_scrap_rate > 0 else 0
    scrap_change_abs = current_total_scrap - previous_total_scrap
    scrap_change_pct = ((current_total_scrap - previous_total_scrap) / previous_total_scrap * 100) if previous_total_scrap > 0 else 0
    hours_change_pct = ((current_total_hours - previous_total_hours) / previous_total_hours * 100) if previous_total_hours > 0 else 0
    
    # Nombres de meses
    month_names = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    comparison = PeriodComparison(
        current_scrap_rate=current_scrap_rate,
        current_total_scrap=current_total_scrap,
        current_total_hours=current_total_hours,
        previous_scrap_rate=previous_scrap_rate,
        previous_total_scrap=previous_total_scrap,
        previous_total_hours=previous_total_hours,
        rate_change_pct=rate_change_pct,
        scrap_change_abs=scrap_change_abs,
        scrap_change_pct=scrap_change_pct,
        hours_change_pct=hours_change_pct,
        period_label=f"{month_names[month]} {year}",
        previous_label=f"{month_names[previous_month]} {previous_year}"
    )
    
    logger.info(f"✓ Comparación calculada: Rate {current_scrap_rate:.2%} vs {previous_scrap_rate:.2%} ({rate_change_pct:+.1f}%)")
    
    return comparison


def compare_quarterly_periods(scrap_df: pd.DataFrame, ventas_df: pd.DataFrame,
                             horas_df: pd.DataFrame, quarter: int, year: int) -> Optional[PeriodComparison]:
    """
    Compara el trimestre actual con el trimestre anterior.
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        quarter: Número de trimestre actual (1-4)
        year: Año actual
        
    Returns:
        PeriodComparison o None si no hay datos del periodo anterior
    """
    logger.info(f"Comparando Q{quarter}/{year} con trimestre anterior...")
    
    # Preparar DataFrames
    scrap_df = scrap_df.copy()
    horas_df = horas_df.copy()
    
    scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
    horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
    
    scrap_df['Total Posted'] = scrap_df['Total Posted'] * -1
    
    scrap_df['Quarter'] = scrap_df['Create Date'].dt.quarter
    scrap_df['Year'] = scrap_df['Create Date'].dt.year
    horas_df['Quarter'] = horas_df['Trans Date'].dt.quarter
    horas_df['Year'] = horas_df['Trans Date'].dt.year
    
    # Calcular métricas trimestre actual
    current_scrap = scrap_df[(scrap_df['Quarter'] == quarter) & (scrap_df['Year'] == year)]
    current_horas = horas_df[(horas_df['Quarter'] == quarter) & (horas_df['Year'] == year)]
    
    # Usar valores absolutos para evitar confusión con negativos
    current_total_scrap = abs(current_scrap['Total Posted'].sum())
    current_total_hours = current_horas['Actual Hours'].sum()
    current_scrap_rate = current_total_scrap / current_total_hours if current_total_hours > 0 else 0
    
    # Calcular trimestre anterior
    previous_quarter = quarter - 1
    previous_year = year
    
    if previous_quarter < 1:
        previous_quarter = 4
        previous_year = year - 1
    
    previous_scrap = scrap_df[(scrap_df['Quarter'] == previous_quarter) & (scrap_df['Year'] == previous_year)]
    previous_horas = horas_df[(horas_df['Quarter'] == previous_quarter) & (horas_df['Year'] == previous_year)]
    
    if len(previous_scrap) == 0 or len(previous_horas) == 0:
        logger.warning(f"No hay datos para el trimestre anterior Q{previous_quarter}/{previous_year}")
        return None
    
    # Usar valores absolutos para evitar confusión con negativos
    previous_total_scrap = abs(previous_scrap['Total Posted'].sum())
    previous_total_hours = previous_horas['Actual Hours'].sum()
    previous_scrap_rate = previous_total_scrap / previous_total_hours if previous_total_hours > 0 else 0
    
    # Calcular cambios (ahora todo es positivo, más = peor)
    rate_change_pct = ((current_scrap_rate - previous_scrap_rate) / previous_scrap_rate * 100) if previous_scrap_rate > 0 else 0
    scrap_change_abs = current_total_scrap - previous_total_scrap
    scrap_change_pct = ((current_total_scrap - previous_total_scrap) / previous_total_scrap * 100) if previous_total_scrap > 0 else 0
    hours_change_pct = ((current_total_hours - previous_total_hours) / previous_total_hours * 100) if previous_total_hours > 0 else 0
    
    comparison = PeriodComparison(
        current_scrap_rate=current_scrap_rate,
        current_total_scrap=current_total_scrap,
        current_total_hours=current_total_hours,
        previous_scrap_rate=previous_scrap_rate,
        previous_total_scrap=previous_total_scrap,
        previous_total_hours=previous_total_hours,
        rate_change_pct=rate_change_pct,
        scrap_change_abs=scrap_change_abs,
        scrap_change_pct=scrap_change_pct,
        hours_change_pct=hours_change_pct,
        period_label=f"Q{quarter} {year}",
        previous_label=f"Q{previous_quarter} {previous_year}"
    )
    
    logger.info(f"✓ Comparación calculada: Rate {current_scrap_rate:.2%} vs {previous_scrap_rate:.2%} ({rate_change_pct:+.1f}%)")
    
    return comparison
