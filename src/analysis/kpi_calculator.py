"""
kpi_calculator.py - Cálculo de KPIs para Dashboard
Calcula métricas clave de scrap rate para visualización en tiempo real
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from config import TARGET_WEEK_RATES, get_week_number_vectorized

logger = logging.getLogger(__name__)


@dataclass
class WeeklyKPI:
    """Estructura para almacenar KPIs de una semana"""
    week: int
    year: int
    scrap_rate: float
    total_scrap: float
    total_hours: float
    target_rate: float
    meets_target: bool
    variance_pct: float  # Diferencia porcentual vs target
    

@dataclass
class DashboardKPIs:
    """Estructura completa de KPIs para el dashboard"""
    # Semana actual
    current_week: int
    current_year: int
    current_scrap_rate: float
    current_total_scrap: float
    current_total_hours: float
    current_target: float
    meets_target: bool
    variance_pct: float
    
    # Comparación
    previous_week_rate: Optional[float] = None
    rate_change_pct: Optional[float] = None
    trend_direction: str = "neutral"  # "improving", "deteriorating", "neutral"
    scrap_change_pct: Optional[float] = None  # % cambio en scrap vs periodo anterior
    hours_change_pct: Optional[float] = None  # % cambio en horas vs periodo anterior
    total_sales: Optional[float] = None  # Total de ventas del periodo
    period_label: str = "semana"  # "semana", "mes", "trimestre", "año", "periodo"
    
    # Top contributors
    top_contributors: List[Dict] = None
    
    # Tendencia histórica (últimas 4 semanas)
    historical_weeks: List[WeeklyKPI] = None
    
    # Alertas
    alerts: List[Dict] = None
    
    def __post_init__(self):
        if self.top_contributors is None:
            self.top_contributors = []
        if self.historical_weeks is None:
            self.historical_weeks = []
        if self.alerts is None:
            self.alerts = []


def get_current_week_info() -> Tuple[int, int]:
    """
    Obtiene la semana y año actuales según calendario fiscal
    
    Returns:
        Tuple[int, int]: (week_number, year)
    """
    today = pd.Timestamp.now()
    week = get_week_number_vectorized(pd.Series([today]), year=today.year).iloc[0]
    return int(week), today.year


def find_last_week_with_data(scrap_df: pd.DataFrame, 
                              horas_df: pd.DataFrame,
                              weeks_back: int = 8) -> Optional[Tuple[int, int]]:
    """
    Encuentra la última semana que tiene datos disponibles
    
    Args:
        scrap_df: DataFrame con datos de scrap
        horas_df: DataFrame con datos de horas
        weeks_back: Número máximo de semanas hacia atrás a buscar
        
    Returns:
        Tuple[int, int]: (week, year) o None si no hay datos
    """
    try:
        current_week, current_year = get_current_week_info()
        
        # Buscar hacia atrás desde la semana actual
        for i in range(weeks_back):
            week = current_week - i
            year = current_year
            
            # Manejar rollover de año
            if week < 1:
                week += 52
                year -= 1
            
            # Verificar si hay datos para esta semana
            scrap_df_copy = scrap_df.copy()
            horas_df_copy = horas_df.copy()
            
            scrap_df_copy['Create Date'] = pd.to_datetime(scrap_df_copy['Create Date'])
            horas_df_copy['Trans Date'] = pd.to_datetime(horas_df_copy['Trans Date'])
            
            scrap_df_copy['Week'] = get_week_number_vectorized(scrap_df_copy['Create Date'], year=year)
            scrap_df_copy['Year'] = scrap_df_copy['Create Date'].dt.year
            horas_df_copy['Week'] = get_week_number_vectorized(horas_df_copy['Trans Date'], year=year)
            horas_df_copy['Year'] = horas_df_copy['Trans Date'].dt.year
            
            scrap_week = scrap_df_copy[(scrap_df_copy['Week'] == week) & (scrap_df_copy['Year'] == year)]
            horas_week = horas_df_copy[(horas_df_copy['Week'] == week) & (horas_df_copy['Year'] == year)]
            
            if not scrap_week.empty or not horas_week.empty:
                logger.info(f"Última semana con datos encontrada: {week}/{year}")
                return week, year
        
        logger.warning(f"No se encontraron datos en las últimas {weeks_back} semanas")
        return None
        
    except Exception as e:
        logger.error(f"Error buscando última semana con datos: {e}")
        return None


def calculate_weekly_kpi(scrap_df: pd.DataFrame, 
                         ventas_df: pd.DataFrame, 
                         horas_df: pd.DataFrame,
                         week: int, 
                         year: int,
                         prev_week_kpi: Optional['WeeklyKPI'] = None) -> Optional[WeeklyKPI]:
    """
    Calcula los KPIs de una semana específica
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        week: Número de semana
        year: Año
        prev_week_kpi: KPI de la semana anterior para comparaciones
        
    Returns:
        WeeklyKPI o None si no hay datos
    """
    try:
        # Convertir fechas
        scrap_df = scrap_df.copy()
        horas_df = horas_df.copy()
        ventas_df = ventas_df.copy()
        
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
        
        # Asegurar valores positivos
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Agregar semana y año
        scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
        scrap_df['Year'] = scrap_df['Create Date'].dt.year
        horas_df['Week'] = get_week_number_vectorized(horas_df['Trans Date'], year=year)
        horas_df['Year'] = horas_df['Trans Date'].dt.year
        ventas_df['Week'] = get_week_number_vectorized(ventas_df['Create Date'], year=year)
        ventas_df['Year'] = ventas_df['Create Date'].dt.year
        
        # Filtrar por semana
        scrap_week = scrap_df[(scrap_df['Week'] == week) & (scrap_df['Year'] == year)]
        horas_week = horas_df[(horas_df['Week'] == week) & (horas_df['Year'] == year)]
        ventas_week = ventas_df[(ventas_df['Week'] == week) & (ventas_df['Year'] == year)]
        
        if scrap_week.empty and horas_week.empty:
            return None
        
        # Calcular totales
        total_scrap = scrap_week['Total Posted'].sum()
        total_hours = horas_week['Actual Hours'].sum()
        total_sales = ventas_week['Total Posted'].sum() if not ventas_week.empty else 0.0
        
        # Calcular rate
        scrap_rate = total_scrap / total_hours if total_hours > 0 else 0
        
        # Obtener target
        target_rate = TARGET_WEEK_RATES.get(week, 0.50)
        
        # Calcular varianza
        variance_pct = ((scrap_rate - target_rate) / target_rate * 100) if target_rate > 0 else 0
        meets_target = scrap_rate <= target_rate
        
        return WeeklyKPI(
            week=week,
            year=year,
            scrap_rate=scrap_rate,
            total_scrap=total_scrap,
            total_hours=total_hours,
            target_rate=target_rate,
            meets_target=meets_target,
            variance_pct=variance_pct
        )
        
    except Exception as e:
        logger.error(f"Error calculando KPI para semana {week}/{year}: {e}")
        return None


def get_top_contributors_summary(scrap_df: pd.DataFrame, 
                                  week: int, 
                                  year: int, 
                                  top_n: int = 3) -> List[Dict]:
    """
    Obtiene resumen de los principales contribuidores de scrap
    
    Args:
        scrap_df: DataFrame con datos de scrap
        week: Número de semana
        year: Año
        top_n: Número de top contributors a retornar
        
    Returns:
        Lista de diccionarios con item, monto y porcentaje
    """
    try:
        scrap_df = scrap_df.copy()
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Agregar semana
        scrap_df['Week'] = get_week_number_vectorized(scrap_df['Create Date'], year=year)
        scrap_df['Year'] = scrap_df['Create Date'].dt.year
        
        # Filtrar por semana
        scrap_week = scrap_df[(scrap_df['Week'] == week) & (scrap_df['Year'] == year)]
        
        if scrap_week.empty:
            return []
        
        # Agrupar por item
        contributors = scrap_week.groupby('Item', as_index=False).agg({
            'Description': 'first',
            'Total Posted': 'sum'
        })
        
        # Ordenar por monto
        contributors = contributors.sort_values('Total Posted', ascending=False)
        contributors = contributors.head(top_n)
        
        # Calcular porcentaje del total
        total_scrap = scrap_week['Total Posted'].sum()
        
        result = []
        for _, row in contributors.iterrows():
            pct = (row['Total Posted'] / total_scrap * 100) if total_scrap > 0 else 0
            result.append({
                'item': row['Item'],
                'description': row['Description'][:30] + '...' if len(row['Description']) > 30 else row['Description'],
                'amount': row['Total Posted'],
                'percentage': pct
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo top contributors: {e}")
        return []


def get_historical_trend(scrap_df: pd.DataFrame,
                         ventas_df: pd.DataFrame,
                         horas_df: pd.DataFrame,
                         current_week: int,
                         current_year: int,
                         weeks_back: int = 4) -> List[WeeklyKPI]:
    """
    Obtiene tendencia histórica de las últimas N semanas desde una semana específica
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        current_week: Semana de referencia (última con datos)
        current_year: Año de referencia
        weeks_back: Número de semanas hacia atrás (incluyendo actual)
        
    Returns:
        Lista de WeeklyKPI ordenados del más antiguo al más reciente
    """
    try:
        historical = []
        
        # Calcular KPIs de las últimas N semanas desde la semana de referencia
        for i in range(weeks_back - 1, -1, -1):
            week = current_week - i
            year = current_year
            
            # Manejar rollover de año
            if week < 1:
                week += 52
                year -= 1
            
            kpi = calculate_weekly_kpi(scrap_df, ventas_df, horas_df, week, year)
            if kpi:
                historical.append(kpi)
        
        return historical
        
    except Exception as e:
        logger.error(f"Error obteniendo tendencia histórica: {e}")
        return []


def generate_alerts(kpi: WeeklyKPI, 
                    historical: List[WeeklyKPI]) -> List[Dict]:
    """
    Genera alertas basadas en los KPIs actuales e históricos
    
    Args:
        kpi: KPI de la semana actual
        historical: Lista de KPIs históricos
        
    Returns:
        Lista de diccionarios con alertas
    """
    alerts = []
    
    try:
        # Alerta 1: Excede target
        if not kpi.meets_target:
            severity = "critical" if kpi.variance_pct > 20 else "warning"
            alerts.append({
                'severity': severity,
                'title': 'Fuera de Target',
                'message': f'Scrap rate {kpi.variance_pct:+.1f}% sobre target ({kpi.target_rate:.2%})'
            })
        
        # Alerta 2: Tendencia creciente (si hay datos históricos)
        if len(historical) >= 3:
            recent_rates = [h.scrap_rate for h in historical[-3:]]
            if all(recent_rates[i] < recent_rates[i+1] for i in range(len(recent_rates)-1)):
                alerts.append({
                    'severity': 'warning',
                    'title': 'Tendencia Creciente',
                    'message': 'El scrap rate ha aumentado consistentemente en las últimas 3 semanas'
                })
        
        # Alerta 3: Aumento súbito (>25% vs semana anterior)
        if len(historical) >= 2:
            prev_rate = historical[-2].scrap_rate
            current_rate = historical[-1].scrap_rate
            if prev_rate > 0:
                change_pct = ((current_rate - prev_rate) / prev_rate) * 100
                if change_pct > 25:
                    alerts.append({
                        'severity': 'critical',
                        'title': 'Aumento Súbito',
                        'message': f'Scrap rate aumentó {change_pct:.1f}% vs semana anterior'
                    })
        
        # Alerta 4: Mejora sostenida (cumple target 3+ semanas)
        if len(historical) >= 3:
            if all(h.meets_target for h in historical[-3:]):
                alerts.append({
                    'severity': 'info',
                    'title': 'Mejora Sostenida',
                    'message': 'Cumpliendo target consistentemente por 3+ semanas'
                })
        
    except Exception as e:
        logger.error(f"Error generando alertas: {e}")
    
    return alerts


def calculate_dashboard_kpis(scrap_df: pd.DataFrame,
                             ventas_df: pd.DataFrame,
                             horas_df: pd.DataFrame) -> Optional[DashboardKPIs]:
    """
    Calcula todos los KPIs necesarios para el dashboard
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        
    Returns:
        DashboardKPIs o None si no hay datos
    """
    try:
        logger.info("=== Calculando KPIs para Dashboard ===")
        
        # Buscar la última semana con datos disponibles
        last_week_info = find_last_week_with_data(scrap_df, horas_df, weeks_back=8)
        
        if not last_week_info:
            logger.error("No se encontraron datos en las últimas 8 semanas")
            return None
        
        current_week, current_year = last_week_info
        logger.info(f"Usando semana con datos: {current_week}/{current_year}")
        
        # KPI de semana actual (última con datos)
        current_kpi = calculate_weekly_kpi(scrap_df, ventas_df, horas_df, current_week, current_year)
        
        if not current_kpi:
            logger.warning("No hay datos para la semana actual")
            return None
        
        # KPI de semana anterior
        prev_week = current_week - 1 if current_week > 1 else 52
        prev_year = current_year if current_week > 1 else current_year - 1
        prev_kpi = calculate_weekly_kpi(scrap_df, ventas_df, horas_df, prev_week, prev_year)
        
        # Calcular cambio y dirección
        prev_week_rate = prev_kpi.scrap_rate if prev_kpi else None
        rate_change_pct = None
        scrap_change_pct = None
        hours_change_pct = None
        trend_direction = "neutral"
        
        if prev_kpi:
            # Cambio en rate
            if prev_week_rate and prev_week_rate > 0:
                rate_change_pct = ((current_kpi.scrap_rate - prev_week_rate) / prev_week_rate) * 100
                if rate_change_pct < -2:
                    trend_direction = "improving"
                elif rate_change_pct > 2:
                    trend_direction = "deteriorating"
            
            # Cambio en scrap total
            if prev_kpi.total_scrap > 0:
                scrap_change_pct = ((current_kpi.total_scrap - prev_kpi.total_scrap) / prev_kpi.total_scrap) * 100
            
            # Cambio en horas
            if prev_kpi.total_hours > 0:
                hours_change_pct = ((current_kpi.total_hours - prev_kpi.total_hours) / prev_kpi.total_hours) * 100
        
        # Calcular total de ventas de la semana actual
        ventas_df_copy = ventas_df.copy()
        ventas_df_copy['Create Date'] = pd.to_datetime(ventas_df_copy['Create Date'])
        ventas_df_copy['Week'] = get_week_number_vectorized(ventas_df_copy['Create Date'], year=current_year)
        ventas_df_copy['Year'] = ventas_df_copy['Create Date'].dt.year
        ventas_week = ventas_df_copy[(ventas_df_copy['Week'] == current_week) & (ventas_df_copy['Year'] == current_year)]
        total_sales = ventas_week['Total Posted'].sum() if not ventas_week.empty and 'Total Posted' in ventas_week.columns else 0.0
        
        # Top contributors
        top_contributors = get_top_contributors_summary(scrap_df, current_week, current_year, top_n=3)
        
        # Tendencia histórica (últimas 4 semanas desde la semana de referencia)
        historical = get_historical_trend(scrap_df, ventas_df, horas_df, current_week, current_year, weeks_back=4)
        
        # Generar alertas
        alerts = generate_alerts(current_kpi, historical)
        
        # Construir objeto de KPIs
        dashboard_kpis = DashboardKPIs(
            current_week=current_kpi.week,
            current_year=current_kpi.year,
            current_scrap_rate=current_kpi.scrap_rate,
            current_total_scrap=current_kpi.total_scrap,
            current_total_hours=current_kpi.total_hours,
            current_target=current_kpi.target_rate,
            meets_target=current_kpi.meets_target,
            variance_pct=current_kpi.variance_pct,
            previous_week_rate=prev_week_rate,
            rate_change_pct=rate_change_pct,
            trend_direction=trend_direction,
            scrap_change_pct=scrap_change_pct,
            hours_change_pct=hours_change_pct,
            total_sales=total_sales,
            top_contributors=top_contributors,
            historical_weeks=historical,
            alerts=alerts
        )
        
        logger.info(f"KPIs calculados exitosamente. Rate actual: {current_kpi.scrap_rate:.2%}")
        return dashboard_kpis
        
    except Exception as e:
        logger.error(f"Error calculando KPIs del dashboard: {e}", exc_info=True)
        return None
