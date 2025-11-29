"""
period_kpi_calculator.py - Cálculo de KPIs por diferentes periodos
Extiende kpi_calculator.py para soportar mes, trimestre, año y rangos personalizados
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from config import TARGET_WEEK_RATES, TARGET_RATES, get_week_number_vectorized
from src.analysis.kpi_calculator import DashboardKPIs, WeeklyKPI, get_top_contributors_summary

logger = logging.getLogger(__name__)


def calculate_period_kpis(scrap_df: pd.DataFrame,
                          ventas_df: pd.DataFrame,
                          horas_df: pd.DataFrame,
                          period_config: Dict) -> Optional[DashboardKPIs]:
    """
    Calcula KPIs para cualquier tipo de periodo
    
    Args:
        scrap_df: DataFrame con datos de scrap
        ventas_df: DataFrame con datos de ventas
        horas_df: DataFrame con datos de horas
        period_config: Dict con configuración del periodo
            Ejemplos:
            - {"type": "last_week"}
            - {"type": "week", "week": 47, "year": 2025}
            - {"type": "month", "month": 11, "year": 2025}
            - {"type": "quarter", "quarter": 4, "year": 2025}
            - {"type": "year", "year": 2025}
            - {"type": "custom", "start_date": date, "end_date": date}
    
    Returns:
        DashboardKPIs o None si no hay datos
    """
    try:
        period_type = period_config.get("type")
        
        if period_type == "last_week" or period_type == "week":
            return _calculate_week_kpis(scrap_df, ventas_df, horas_df, period_config)
        elif period_type == "month":
            return _calculate_month_kpis(scrap_df, ventas_df, horas_df, period_config)
        elif period_type == "quarter":
            return _calculate_quarter_kpis(scrap_df, ventas_df, horas_df, period_config)
        elif period_type == "year":
            return _calculate_year_kpis(scrap_df, ventas_df, horas_df, period_config)
        elif period_type == "custom":
            return _calculate_custom_kpis(scrap_df, ventas_df, horas_df, period_config)
        else:
            logger.error(f"Tipo de periodo no soportado: {period_type}")
            return None
            
    except Exception as e:
        logger.error(f"Error calculando KPIs de periodo: {e}", exc_info=True)
        return None


def _calculate_week_kpis(scrap_df: pd.DataFrame,
                         ventas_df: pd.DataFrame,
                         horas_df: pd.DataFrame,
                         period_config: Dict) -> Optional[DashboardKPIs]:
    """Calcula KPIs para una semana (usa la función existente)"""
    from src.analysis.kpi_calculator import calculate_dashboard_kpis, find_last_week_with_data
    
    if period_config.get("type") == "last_week":
        # Usar función existente
        return calculate_dashboard_kpis(scrap_df, ventas_df, horas_df)
    else:
        # Semana específica
        week = period_config["week"]
        year = period_config["year"]
        
        # Similar a calculate_dashboard_kpis pero para semana específica
        from src.analysis.kpi_calculator import calculate_weekly_kpi, get_historical_trend, generate_alerts
        
        current_kpi = calculate_weekly_kpi(scrap_df, ventas_df, horas_df, week, year)
        
        if not current_kpi:
            logger.warning(f"No hay datos para la semana {week}/{year}")
            return None
        
        # KPI de semana anterior
        prev_week = week - 1 if week > 1 else 52
        prev_year = year if week > 1 else year - 1
        prev_kpi = calculate_weekly_kpi(scrap_df, ventas_df, horas_df, prev_week, prev_year)
        
        # Calcular cambio y dirección
        prev_week_rate = prev_kpi.scrap_rate if prev_kpi else None
        rate_change_pct = None
        scrap_change_pct = None
        hours_change_pct = None
        trend_direction = "neutral"
        
        if prev_kpi:
            if prev_week_rate and prev_week_rate > 0:
                rate_change_pct = ((current_kpi.scrap_rate - prev_week_rate) / prev_week_rate) * 100
                if rate_change_pct < -2:
                    trend_direction = "improving"
                elif rate_change_pct > 2:
                    trend_direction = "deteriorating"
            
            if prev_kpi.total_scrap > 0:
                scrap_change_pct = ((current_kpi.total_scrap - prev_kpi.total_scrap) / prev_kpi.total_scrap) * 100
            
            if prev_kpi.total_hours > 0:
                hours_change_pct = ((current_kpi.total_hours - prev_kpi.total_hours) / prev_kpi.total_hours) * 100
        
        # Calcular total de ventas
        ventas_df_copy = ventas_df.copy()
        ventas_df_copy['Create Date'] = pd.to_datetime(ventas_df_copy['Create Date'])
        ventas_df_copy['Week'] = get_week_number_vectorized(ventas_df_copy['Create Date'], year=year)
        ventas_df_copy['Year'] = ventas_df_copy['Create Date'].dt.year
        ventas_week = ventas_df_copy[(ventas_df_copy['Week'] == week) & (ventas_df_copy['Year'] == year)]
        total_sales = ventas_week['Total Posted'].sum() if not ventas_week.empty and 'Total Posted' in ventas_week.columns else 0.0
        
        # Top contributors
        top_contributors = get_top_contributors_summary(scrap_df, week, year, top_n=3)
        
        # Tendencia histórica
        historical = get_historical_trend(scrap_df, ventas_df, horas_df, week, year, weeks_back=4)
        
        # Alertas
        alerts = generate_alerts(current_kpi, historical)
        
        return DashboardKPIs(
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


def _calculate_month_kpis(scrap_df: pd.DataFrame,
                          ventas_df: pd.DataFrame,
                          horas_df: pd.DataFrame,
                          period_config: Dict) -> Optional[DashboardKPIs]:
    """Calcula KPIs para un mes completo"""
    try:
        month = period_config["month"]
        year = period_config["year"]
        
        logger.info(f"Calculando KPIs para mes {month}/{year}")
        
        # Preparar DataFrames
        scrap_df = scrap_df.copy()
        ventas_df = ventas_df.copy()
        horas_df = horas_df.copy()
        
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
        
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Filtrar por mes
        scrap_month = scrap_df[(scrap_df['Create Date'].dt.month == month) & (scrap_df['Create Date'].dt.year == year)]
        ventas_month = ventas_df[(ventas_df['Create Date'].dt.month == month) & (ventas_df['Create Date'].dt.year == year)]
        horas_month = horas_df[(horas_df['Trans Date'].dt.month == month) & (horas_df['Trans Date'].dt.year == year)]
        
        if scrap_month.empty and horas_month.empty:
            logger.warning(f"No hay datos para el mes {month}/{year}")
            return None
        
        # Calcular totales
        total_scrap = scrap_month['Total Posted'].sum()
        total_hours = horas_month['Actual Hours'].sum()
        total_sales = ventas_month['Total Posted'].sum() if not ventas_month.empty else 0.0
        scrap_rate = total_scrap / total_hours if total_hours > 0 else 0
        
        # Target del mes (promedio de las semanas del mes)
        target_rate = TARGET_RATES.get(month, 0.50)
        variance_pct = ((scrap_rate - target_rate) / target_rate * 100) if target_rate > 0 else 0
        meets_target = scrap_rate <= target_rate
        
        # Mes anterior
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        
        scrap_prev = scrap_df[(scrap_df['Create Date'].dt.month == prev_month) & (scrap_df['Create Date'].dt.year == prev_year)]
        horas_prev = horas_df[(horas_df['Trans Date'].dt.month == prev_month) & (horas_df['Trans Date'].dt.year == prev_year)]
        ventas_prev = ventas_df[(ventas_df['Create Date'].dt.month == prev_month) & (ventas_df['Create Date'].dt.year == prev_year)]
        
        prev_total_scrap = scrap_prev['Total Posted'].sum()
        prev_total_hours = horas_prev['Actual Hours'].sum()
        prev_scrap_rate = prev_total_scrap / prev_total_hours if prev_total_hours > 0 else 0
        
        # Calcular cambios
        rate_change_pct = None
        scrap_change_pct = None
        hours_change_pct = None
        trend_direction = "neutral"
        
        if prev_scrap_rate > 0:
            rate_change_pct = ((scrap_rate - prev_scrap_rate) / prev_scrap_rate) * 100
            if rate_change_pct < -2:
                trend_direction = "improving"
            elif rate_change_pct > 2:
                trend_direction = "deteriorating"
        
        if prev_total_scrap > 0:
            scrap_change_pct = ((total_scrap - prev_total_scrap) / prev_total_scrap) * 100
        
        if prev_total_hours > 0:
            hours_change_pct = ((total_hours - prev_total_hours) / prev_total_hours) * 100
        
        # Top contributors del mes
        if not scrap_month.empty:
            contributors = scrap_month.groupby('Item', as_index=False).agg({
                'Description': 'first',
                'Total Posted': 'sum'
            })
            contributors = contributors.sort_values('Total Posted', ascending=False).head(3)
            
            total_scrap_month = scrap_month['Total Posted'].sum()
            top_contributors = []
            for _, row in contributors.iterrows():
                pct = (row['Total Posted'] / total_scrap_month * 100) if total_scrap_month > 0 else 0
                top_contributors.append({
                    'item': row['Item'],
                    'description': row['Description'][:30] + '...' if len(row['Description']) > 30 else row['Description'],
                    'amount': row['Total Posted'],
                    'percentage': pct
                })
        else:
            top_contributors = []
        
        # Tendencia histórica (últimos 6 meses)
        historical = []
        for i in range(5, -1, -1):
            hist_month = month - i
            hist_year = year
            while hist_month < 1:
                hist_month += 12
                hist_year -= 1
            
            hist_scrap = scrap_df[(scrap_df['Create Date'].dt.month == hist_month) & (scrap_df['Create Date'].dt.year == hist_year)]
            hist_horas = horas_df[(horas_df['Trans Date'].dt.month == hist_month) & (horas_df['Trans Date'].dt.year == hist_year)]
            
            if not hist_scrap.empty or not hist_horas.empty:
                hist_total_scrap = hist_scrap['Total Posted'].sum()
                hist_total_hours = hist_horas['Actual Hours'].sum()
                hist_rate = hist_total_scrap / hist_total_hours if hist_total_hours > 0 else 0
                hist_target = TARGET_RATES.get(hist_month, 0.50)
                
                historical.append(WeeklyKPI(
                    week=hist_month,  # Usamos month como week para compatibilidad
                    year=hist_year,
                    scrap_rate=hist_rate,
                    total_scrap=hist_total_scrap,
                    total_hours=hist_total_hours,
                    target_rate=hist_target,
                    meets_target=hist_rate <= hist_target,
                    variance_pct=((hist_rate - hist_target) / hist_target * 100) if hist_target > 0 else 0
                ))
        
        # Alertas básicas
        alerts = []
        if not meets_target:
            severity = "critical" if variance_pct > 20 else "warning"
            alerts.append({
                'severity': severity,
                'title': 'Fuera de Target',
                'message': f'Scrap rate {variance_pct:+.1f}% sobre target ({target_rate:.2f})'
            })
        
        return DashboardKPIs(
            current_week=month,  # Usamos month como week
            current_year=year,
            current_scrap_rate=scrap_rate,
            current_total_scrap=total_scrap,
            current_total_hours=total_hours,
            current_target=target_rate,
            meets_target=meets_target,
            variance_pct=variance_pct,
            previous_week_rate=prev_scrap_rate,
            rate_change_pct=rate_change_pct,
            trend_direction=trend_direction,
            scrap_change_pct=scrap_change_pct,
            hours_change_pct=hours_change_pct,
            total_sales=total_sales,
            top_contributors=top_contributors,
            historical_weeks=historical,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error calculando KPIs de mes: {e}", exc_info=True)
        return None


def _calculate_quarter_kpis(scrap_df: pd.DataFrame,
                            ventas_df: pd.DataFrame,
                            horas_df: pd.DataFrame,
                            period_config: Dict) -> Optional[DashboardKPIs]:
    """Calcula KPIs para un trimestre"""
    try:
        quarter = period_config["quarter"]
        year = period_config["year"]
        
        # Meses del trimestre
        quarter_months = {
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }
        months = quarter_months[quarter]
        
        logger.info(f"Calculando KPIs para Q{quarter}/{year}")
        
        # Preparar DataFrames
        scrap_df = scrap_df.copy()
        ventas_df = ventas_df.copy()
        horas_df = horas_df.copy()
        
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
        
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Filtrar por trimestre
        scrap_quarter = scrap_df[(scrap_df['Create Date'].dt.month.isin(months)) & (scrap_df['Create Date'].dt.year == year)]
        ventas_quarter = ventas_df[(ventas_df['Create Date'].dt.month.isin(months)) & (ventas_df['Create Date'].dt.year == year)]
        horas_quarter = horas_df[(horas_df['Trans Date'].dt.month.isin(months)) & (horas_df['Trans Date'].dt.year == year)]
        
        if scrap_quarter.empty and horas_quarter.empty:
            logger.warning(f"No hay datos para Q{quarter}/{year}")
            return None
        
        # Calcular totales
        total_scrap = scrap_quarter['Total Posted'].sum()
        total_hours = horas_quarter['Actual Hours'].sum()
        total_sales = ventas_quarter['Total Posted'].sum() if not ventas_quarter.empty else 0.0
        scrap_rate = total_scrap / total_hours if total_hours > 0 else 0
        
        # Target del trimestre (promedio de los meses)
        target_rate = sum(TARGET_RATES.get(m, 0.50) for m in months) / 3
        variance_pct = ((scrap_rate - target_rate) / target_rate * 100) if target_rate > 0 else 0
        meets_target = scrap_rate <= target_rate
        
        # Trimestre anterior
        prev_quarter = quarter - 1 if quarter > 1 else 4
        prev_year = year if quarter > 1 else year - 1
        prev_months = quarter_months[prev_quarter]
        
        scrap_prev = scrap_df[(scrap_df['Create Date'].dt.month.isin(prev_months)) & (scrap_df['Create Date'].dt.year == prev_year)]
        horas_prev = horas_df[(horas_df['Trans Date'].dt.month.isin(prev_months)) & (horas_df['Trans Date'].dt.year == prev_year)]
        
        prev_total_scrap = scrap_prev['Total Posted'].sum()
        prev_total_hours = horas_prev['Actual Hours'].sum()
        prev_scrap_rate = prev_total_scrap / prev_total_hours if prev_total_hours > 0 else 0
        
        # Calcular cambios
        rate_change_pct = ((scrap_rate - prev_scrap_rate) / prev_scrap_rate * 100) if prev_scrap_rate > 0 else None
        scrap_change_pct = ((total_scrap - prev_total_scrap) / prev_total_scrap * 100) if prev_total_scrap > 0 else None
        hours_change_pct = ((total_hours - prev_total_hours) / prev_total_hours * 100) if prev_total_hours > 0 else None
        
        trend_direction = "neutral"
        if rate_change_pct:
            if rate_change_pct < -2:
                trend_direction = "improving"
            elif rate_change_pct > 2:
                trend_direction = "deteriorating"
        
        # Top contributors
        if not scrap_quarter.empty:
            contributors = scrap_quarter.groupby('Item', as_index=False).agg({
                'Description': 'first',
                'Total Posted': 'sum'
            })
            contributors = contributors.sort_values('Total Posted', ascending=False).head(3)
            
            total_scrap_q = scrap_quarter['Total Posted'].sum()
            top_contributors = []
            for _, row in contributors.iterrows():
                pct = (row['Total Posted'] / total_scrap_q * 100) if total_scrap_q > 0 else 0
                top_contributors.append({
                    'item': row['Item'],
                    'description': row['Description'][:30] + '...' if len(row['Description']) > 30 else row['Description'],
                    'amount': row['Total Posted'],
                    'percentage': pct
                })
        else:
            top_contributors = []
        
        # Tendencia histórica (últimos 4 trimestres)
        historical = []
        for i in range(3, -1, -1):
            hist_q = quarter - i
            hist_year = year
            while hist_q < 1:
                hist_q += 4
                hist_year -= 1
            
            hist_months = quarter_months[hist_q]
            hist_scrap = scrap_df[(scrap_df['Create Date'].dt.month.isin(hist_months)) & (scrap_df['Create Date'].dt.year == hist_year)]
            hist_horas = horas_df[(horas_df['Trans Date'].dt.month.isin(hist_months)) & (horas_df['Trans Date'].dt.year == hist_year)]
            
            if not hist_scrap.empty or not hist_horas.empty:
                hist_total_scrap = hist_scrap['Total Posted'].sum()
                hist_total_hours = hist_horas['Actual Hours'].sum()
                hist_rate = hist_total_scrap / hist_total_hours if hist_total_hours > 0 else 0
                hist_target = sum(TARGET_RATES.get(m, 0.50) for m in hist_months) / 3
                
                historical.append(WeeklyKPI(
                    week=hist_q,
                    year=hist_year,
                    scrap_rate=hist_rate,
                    total_scrap=hist_total_scrap,
                    total_hours=hist_total_hours,
                    target_rate=hist_target,
                    meets_target=hist_rate <= hist_target,
                    variance_pct=((hist_rate - hist_target) / hist_target * 100) if hist_target > 0 else 0
                ))
        
        # Alertas
        alerts = []
        if not meets_target:
            severity = "critical" if variance_pct > 20 else "warning"
            alerts.append({
                'severity': severity,
                'title': 'Fuera de Target',
                'message': f'Scrap rate {variance_pct:+.1f}% sobre target ({target_rate:.2f})'
            })
        
        return DashboardKPIs(
            current_week=quarter,
            current_year=year,
            current_scrap_rate=scrap_rate,
            current_total_scrap=total_scrap,
            current_total_hours=total_hours,
            current_target=target_rate,
            meets_target=meets_target,
            variance_pct=variance_pct,
            previous_week_rate=prev_scrap_rate,
            rate_change_pct=rate_change_pct,
            trend_direction=trend_direction,
            scrap_change_pct=scrap_change_pct,
            hours_change_pct=hours_change_pct,
            total_sales=total_sales,
            top_contributors=top_contributors,
            historical_weeks=historical,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error calculando KPIs de trimestre: {e}", exc_info=True)
        return None


def _calculate_year_kpis(scrap_df: pd.DataFrame,
                        ventas_df: pd.DataFrame,
                        horas_df: pd.DataFrame,
                        period_config: Dict) -> Optional[DashboardKPIs]:
    """Calcula KPIs para un año completo"""
    try:
        year = period_config["year"]
        
        logger.info(f"Calculando KPIs para año {year}")
        
        # Preparar DataFrames
        scrap_df = scrap_df.copy()
        ventas_df = ventas_df.copy()
        horas_df = horas_df.copy()
        
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
        
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Filtrar por año
        scrap_year = scrap_df[scrap_df['Create Date'].dt.year == year]
        ventas_year = ventas_df[ventas_df['Create Date'].dt.year == year]
        horas_year = horas_df[horas_df['Trans Date'].dt.year == year]
        
        if scrap_year.empty and horas_year.empty:
            logger.warning(f"No hay datos para el año {year}")
            return None
        
        # Calcular totales
        total_scrap = scrap_year['Total Posted'].sum()
        total_hours = horas_year['Actual Hours'].sum()
        total_sales = ventas_year['Total Posted'].sum() if not ventas_year.empty else 0.0
        scrap_rate = total_scrap / total_hours if total_hours > 0 else 0
        
        # Target del año (promedio anual = 0.50)
        target_rate = 0.50
        variance_pct = ((scrap_rate - target_rate) / target_rate * 100) if target_rate > 0 else 0
        meets_target = scrap_rate <= target_rate
        
        # Año anterior
        prev_year = year - 1
        scrap_prev = scrap_df[scrap_df['Create Date'].dt.year == prev_year]
        horas_prev = horas_df[horas_df['Trans Date'].dt.year == prev_year]
        
        prev_total_scrap = scrap_prev['Total Posted'].sum()
        prev_total_hours = horas_prev['Actual Hours'].sum()
        prev_scrap_rate = prev_total_scrap / prev_total_hours if prev_total_hours > 0 else 0
        
        # Calcular cambios
        rate_change_pct = ((scrap_rate - prev_scrap_rate) / prev_scrap_rate * 100) if prev_scrap_rate > 0 else None
        scrap_change_pct = ((total_scrap - prev_total_scrap) / prev_total_scrap * 100) if prev_total_scrap > 0 else None
        hours_change_pct = ((total_hours - prev_total_hours) / prev_total_hours * 100) if prev_total_hours > 0 else None
        
        trend_direction = "neutral"
        if rate_change_pct:
            if rate_change_pct < -2:
                trend_direction = "improving"
            elif rate_change_pct > 2:
                trend_direction = "deteriorating"
        
        # Top contributors del año
        if not scrap_year.empty:
            contributors = scrap_year.groupby('Item', as_index=False).agg({
                'Description': 'first',
                'Total Posted': 'sum'
            })
            contributors = contributors.sort_values('Total Posted', ascending=False).head(3)
            
            total_scrap_y = scrap_year['Total Posted'].sum()
            top_contributors = []
            for _, row in contributors.iterrows():
                pct = (row['Total Posted'] / total_scrap_y * 100) if total_scrap_y > 0 else 0
                top_contributors.append({
                    'item': row['Item'],
                    'description': row['Description'][:30] + '...' if len(row['Description']) > 30 else row['Description'],
                    'amount': row['Total Posted'],
                    'percentage': pct
                })
        else:
            top_contributors = []
        
        # Tendencia histórica (últimos 3 años)
        historical = []
        for i in range(2, -1, -1):
            hist_year = year - i
            
            hist_scrap = scrap_df[scrap_df['Create Date'].dt.year == hist_year]
            hist_horas = horas_df[horas_df['Trans Date'].dt.year == hist_year]
            
            if not hist_scrap.empty or not hist_horas.empty:
                hist_total_scrap = hist_scrap['Total Posted'].sum()
                hist_total_hours = hist_horas['Actual Hours'].sum()
                hist_rate = hist_total_scrap / hist_total_hours if hist_total_hours > 0 else 0
                
                historical.append(WeeklyKPI(
                    week=1,  # Dummy value
                    year=hist_year,
                    scrap_rate=hist_rate,
                    total_scrap=hist_total_scrap,
                    total_hours=hist_total_hours,
                    target_rate=0.50,
                    meets_target=hist_rate <= 0.50,
                    variance_pct=((hist_rate - 0.50) / 0.50 * 100)
                ))
        
        # Alertas
        alerts = []
        if not meets_target:
            severity = "critical" if variance_pct > 20 else "warning"
            alerts.append({
                'severity': severity,
                'title': 'Fuera de Target',
                'message': f'Scrap rate {variance_pct:+.1f}% sobre target anual ({target_rate:.2f})'
            })
        
        return DashboardKPIs(
            current_week=1,  # Dummy value
            current_year=year,
            current_scrap_rate=scrap_rate,
            current_total_scrap=total_scrap,
            current_total_hours=total_hours,
            current_target=target_rate,
            meets_target=meets_target,
            variance_pct=variance_pct,
            previous_week_rate=prev_scrap_rate,
            rate_change_pct=rate_change_pct,
            trend_direction=trend_direction,
            scrap_change_pct=scrap_change_pct,
            hours_change_pct=hours_change_pct,
            total_sales=total_sales,
            top_contributors=top_contributors,
            historical_weeks=historical,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error calculando KPIs de año: {e}", exc_info=True)
        return None


def _calculate_custom_kpis(scrap_df: pd.DataFrame,
                          ventas_df: pd.DataFrame,
                          horas_df: pd.DataFrame,
                          period_config: Dict) -> Optional[DashboardKPIs]:
    """Calcula KPIs para un rango personalizado"""
    try:
        start_date = pd.to_datetime(period_config["start_date"])
        end_date = pd.to_datetime(period_config["end_date"])
        
        logger.info(f"Calculando KPIs para rango {start_date.date()} a {end_date.date()}")
        
        # Preparar DataFrames
        scrap_df = scrap_df.copy()
        ventas_df = ventas_df.copy()
        horas_df = horas_df.copy()
        
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        ventas_df['Create Date'] = pd.to_datetime(ventas_df['Create Date'])
        horas_df['Trans Date'] = pd.to_datetime(horas_df['Trans Date'])
        
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Filtrar por rango
        scrap_range = scrap_df[(scrap_df['Create Date'] >= start_date) & (scrap_df['Create Date'] <= end_date)]
        ventas_range = ventas_df[(ventas_df['Create Date'] >= start_date) & (ventas_df['Create Date'] <= end_date)]
        horas_range = horas_df[(horas_df['Trans Date'] >= start_date) & (horas_df['Trans Date'] <= end_date)]
        
        if scrap_range.empty and horas_range.empty:
            logger.warning(f"No hay datos para el rango seleccionado")
            return None
        
        # Calcular totales
        total_scrap = scrap_range['Total Posted'].sum()
        total_hours = horas_range['Actual Hours'].sum()
        total_sales = ventas_range['Total Posted'].sum() if not ventas_range.empty else 0.0
        scrap_rate = total_scrap / total_hours if total_hours > 0 else 0
        
        # Target genérico
        target_rate = 0.50
        variance_pct = ((scrap_rate - target_rate) / target_rate * 100) if target_rate > 0 else 0
        meets_target = scrap_rate <= target_rate
        
        # Periodo anterior (mismo tamaño)
        days_diff = (end_date - start_date).days
        prev_start = start_date - timedelta(days=days_diff + 1)
        prev_end = start_date - timedelta(days=1)
        
        scrap_prev = scrap_df[(scrap_df['Create Date'] >= prev_start) & (scrap_df['Create Date'] <= prev_end)]
        horas_prev = horas_df[(horas_df['Trans Date'] >= prev_start) & (horas_df['Trans Date'] <= prev_end)]
        
        prev_total_scrap = scrap_prev['Total Posted'].sum()
        prev_total_hours = horas_prev['Actual Hours'].sum()
        prev_scrap_rate = prev_total_scrap / prev_total_hours if prev_total_hours > 0 else 0
        
        # Calcular cambios
        rate_change_pct = ((scrap_rate - prev_scrap_rate) / prev_scrap_rate * 100) if prev_scrap_rate > 0 else None
        scrap_change_pct = ((total_scrap - prev_total_scrap) / prev_total_scrap * 100) if prev_total_scrap > 0 else None
        hours_change_pct = ((total_hours - prev_total_hours) / prev_total_hours * 100) if prev_total_hours > 0 else None
        
        trend_direction = "neutral"
        if rate_change_pct:
            if rate_change_pct < -2:
                trend_direction = "improving"
            elif rate_change_pct > 2:
                trend_direction = "deteriorating"
        
        # Top contributors
        if not scrap_range.empty:
            contributors = scrap_range.groupby('Item', as_index=False).agg({
                'Description': 'first',
                'Total Posted': 'sum'
            })
            contributors = contributors.sort_values('Total Posted', ascending=False).head(3)
            
            total_scrap_r = scrap_range['Total Posted'].sum()
            top_contributors = []
            for _, row in contributors.iterrows():
                pct = (row['Total Posted'] / total_scrap_r * 100) if total_scrap_r > 0 else 0
                top_contributors.append({
                    'item': row['Item'],
                    'description': row['Description'][:30] + '...' if len(row['Description']) > 30 else row['Description'],
                    'amount': row['Total Posted'],
                    'percentage': pct
                })
        else:
            top_contributors = []
        
        # Tendencia histórica (dividir rango en segmentos)
        historical = []
        num_segments = min(6, days_diff // 7 + 1)  # Máximo 6 segmentos
        segment_days = days_diff // num_segments if num_segments > 0 else days_diff
        
        for i in range(num_segments):
            seg_start = start_date + timedelta(days=i * segment_days)
            seg_end = seg_start + timedelta(days=segment_days - 1)
            if seg_end > end_date:
                seg_end = end_date
            
            seg_scrap = scrap_df[(scrap_df['Create Date'] >= seg_start) & (scrap_df['Create Date'] <= seg_end)]
            seg_horas = horas_df[(horas_df['Trans Date'] >= seg_start) & (horas_df['Trans Date'] <= seg_end)]
            
            if not seg_scrap.empty or not seg_horas.empty:
                seg_total_scrap = seg_scrap['Total Posted'].sum()
                seg_total_hours = seg_horas['Actual Hours'].sum()
                seg_rate = seg_total_scrap / seg_total_hours if seg_total_hours > 0 else 0
                
                historical.append(WeeklyKPI(
                    week=i + 1,
                    year=seg_start.year,
                    scrap_rate=seg_rate,
                    total_scrap=seg_total_scrap,
                    total_hours=seg_total_hours,
                    target_rate=0.50,
                    meets_target=seg_rate <= 0.50,
                    variance_pct=((seg_rate - 0.50) / 0.50 * 100)
                ))
        
        # Alertas
        alerts = []
        if not meets_target:
            severity = "critical" if variance_pct > 20 else "warning"
            alerts.append({
                'severity': severity,
                'title': 'Fuera de Target',
                'message': f'Scrap rate {variance_pct:+.1f}% sobre target ({target_rate:.2f})'
            })
        
        return DashboardKPIs(
            current_week=1,  # Dummy
            current_year=end_date.year,
            current_scrap_rate=scrap_rate,
            current_total_scrap=total_scrap,
            current_total_hours=total_hours,
            current_target=target_rate,
            meets_target=meets_target,
            variance_pct=variance_pct,
            previous_week_rate=prev_scrap_rate,
            rate_change_pct=rate_change_pct,
            trend_direction=trend_direction,
            scrap_change_pct=scrap_change_pct,
            hours_change_pct=hours_change_pct,
            total_sales=total_sales,
            top_contributors=top_contributors,
            historical_weeks=historical,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error calculando KPIs personalizados: {e}", exc_info=True)
        return None


def get_period_label(period_config: Dict) -> str:
    """Genera un label descriptivo para el periodo seleccionado"""
    period_type = period_config.get("type")
    
    if period_type == "last_week":
        return "Última Semana con Datos"
    elif period_type == "week":
        return f"Semana {period_config['week']}/{period_config['year']}"
    elif period_type == "month":
        month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return f"{month_names[period_config['month']-1]} {period_config['year']}"
    elif period_type == "quarter":
        return f"Q{period_config['quarter']} {period_config['year']}"
    elif period_type == "year":
        return f"Año {period_config['year']}"
    elif period_type == "custom":
        start = period_config['start_date']
        end = period_config['end_date']
        return f"{start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}"
    else:
        return "Periodo Desconocido"


def get_top_items_for_period(scrap_df: pd.DataFrame, 
                             period_config: Dict, 
                             top_n: int = 10) -> List[Dict]:
    """
    Obtiene los top N items por scrap para un periodo dado
    
    Args:
        scrap_df: DataFrame con datos de scrap
        period_config: Configuración del periodo
        top_n: Número de items a retornar
        
    Returns:
        Lista de diccionarios con item, description, amount
    """
    try:
        scrap_df = scrap_df.copy()
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Filtrar según el periodo
        filtered_df = _filter_by_period(scrap_df, period_config, 'Create Date')
        
        if filtered_df.empty:
            return []
        
        # Agrupar por Item
        items = filtered_df.groupby('Item', as_index=False).agg({
            'Description': 'first',
            'Total Posted': 'sum'
        })
        
        # Ordenar y tomar top N
        items = items.sort_values('Total Posted', ascending=False).head(top_n)
        
        result = []
        for _, row in items.iterrows():
            result.append({
                'item': row['Item'],
                'description': row['Description'][:25] + '...' if len(row['Description']) > 25 else row['Description'],
                'amount': row['Total Posted']
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo top items: {e}")
        return []


def get_top_locations_for_period(scrap_df: pd.DataFrame, 
                                 period_config: Dict, 
                                 top_n: int = 10) -> List[Dict]:
    """
    Obtiene las top N locations (celdas) por scrap para un periodo dado
    
    Args:
        scrap_df: DataFrame con datos de scrap
        period_config: Configuración del periodo
        top_n: Número de locations a retornar
        
    Returns:
        Lista de diccionarios con location, amount
    """
    try:
        scrap_df = scrap_df.copy()
        scrap_df['Create Date'] = pd.to_datetime(scrap_df['Create Date'])
        scrap_df['Total Posted'] = abs(scrap_df['Total Posted'])
        
        # Filtrar según el periodo
        filtered_df = _filter_by_period(scrap_df, period_config, 'Create Date')
        
        if filtered_df.empty:
            return []
        
        # Agrupar por Location
        locations = filtered_df.groupby('Location', as_index=False).agg({
            'Total Posted': 'sum'
        })
        
        # Ordenar y tomar top N
        locations = locations.sort_values('Total Posted', ascending=False).head(top_n)
        
        result = []
        for _, row in locations.iterrows():
            result.append({
                'location': row['Location'],
                'amount': row['Total Posted']
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo top locations: {e}")
        return []


def _filter_by_period(df: pd.DataFrame, period_config: Dict, date_column: str) -> pd.DataFrame:
    """
    Filtra un DataFrame según la configuración de periodo
    
    Args:
        df: DataFrame a filtrar
        period_config: Configuración del periodo
        date_column: Nombre de la columna de fecha
        
    Returns:
        DataFrame filtrado
    """
    period_type = period_config.get("type")
    
    if period_type == "last_week" or period_type == "week":
        week = period_config.get("week")
        year = period_config.get("year")
        
        if not week or not year:
            # Para last_week, buscar la última con datos
            from src.analysis.kpi_calculator import find_last_week_with_data
            # Crear dfs dummy para horas
            result = find_last_week_with_data(df, df, weeks_back=8)
            if result:
                week, year = result
            else:
                return pd.DataFrame()
        
        df['Week'] = get_week_number_vectorized(df[date_column], year=year)
        df['Year'] = df[date_column].dt.year
        return df[(df['Week'] == week) & (df['Year'] == year)]
        
    elif period_type == "month":
        month = period_config["month"]
        year = period_config["year"]
        return df[(df[date_column].dt.month == month) & (df[date_column].dt.year == year)]
        
    elif period_type == "quarter":
        quarter = period_config["quarter"]
        year = period_config["year"]
        quarter_months = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
        months = quarter_months[quarter]
        return df[(df[date_column].dt.month.isin(months)) & (df[date_column].dt.year == year)]
        
    elif period_type == "year":
        year = period_config["year"]
        return df[df[date_column].dt.year == year]
        
    elif period_type == "custom":
        start_date = pd.to_datetime(period_config["start_date"])
        end_date = pd.to_datetime(period_config["end_date"])
        return df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    
    return df
