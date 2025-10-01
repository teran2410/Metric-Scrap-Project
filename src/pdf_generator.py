"""
Módulo para la generación de reportes en PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tempfile
import os


def create_weekly_chart(df, target_rate, output_path="weekly_chart.png"):
    """
    Genera la gráfica semanal de scrap rate
    """
    days = df['Day'].tolist()[:-1]  # quitar fila de Totales
    rates = df['Rate'].tolist()[:-1]

    fig, ax = plt.subplots(figsize=(8,4))
    bars = ax.bar(days, rates, color="green")

    # Resaltar si está arriba del target
    for bar, val in zip(bars, rates):
        if val > target_rate:
            bar.set_color("gray")
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.01,
                f"{val:.2f}", ha="center", fontsize=9)

    ax.axhline(target_rate, color="navy", linewidth=2)
    ax.set_title(f"Weekly Scrap Rate (Target={target_rate})")
    ax.set_ylabel("Rate")
    plt.tight_layout()
    fig.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def create_pareto_chart(df_items, output_path="pareto.png"):
    """
    Genera un gráfico de Pareto para los Top 10 ítems de scrap
    """
    # Ordenar y calcular % acumulado
    df_sorted = df_items.sort_values(by="Scrap", ascending=False).head(10).copy()
    df_sorted["Cumulative %"] = df_sorted["Scrap"].cumsum() / df_sorted["Scrap"].sum() * 100

    fig, ax1 = plt.subplots(figsize=(8,4))

    # Barras
    bars = ax1.bar(df_sorted["Item"], df_sorted["Scrap"], color="skyblue", label="Total Scrap")
    ax1.set_ylabel("Total Scrap")
    ax1.tick_params(axis="x", rotation=45)

    # Línea de % acumulado
    ax2 = ax1.twinx()
    ax2.plot(df_sorted["Item"], df_sorted["Cumulative %"], color="navy", marker="o", label="%")
    ax2.set_ylabel("Cumulative %")
    ax2.set_ylim(0, 110)

    # Etiquetas
    for i, v in enumerate(df_sorted["Scrap"]):
        ax1.text(i, v + (v*0.01), f"{v/1000:.1f}k", ha="center", fontsize=8)
    for i, v in enumerate(df_sorted["Cumulative %"]):
        ax2.text(i, v + 2, f"{v:.1f}%", ha="center", fontsize=7, color="navy")

    plt.title("TOP 10 SCRAP BY ITEMS")
    fig.tight_layout()
    fig.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    return df_sorted


def generate_pdf(report_df, items_df, output_file="reporte.pdf"):
    """
    Genera el PDF con tabla, gráfica semanal y pareto chart
    """
    styles = getSampleStyleSheet()
    elements = []

    doc = SimpleDocTemplate(output_file, pagesize=landscape(letter))

    # ===== Página 1: Tabla semanal =====
    elements.append(Paragraph("Weekly Scrap Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Convertir DataFrame a tabla ReportLab
    data = [report_df.columns.tolist()] + report_df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.gray),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(table)
    elements.append(PageBreak())

    # ===== Página 2: Gráfica semanal =====
    tmp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    create_weekly_chart(report_df, report_df["Target Rate"].iloc[0], tmp_chart.name)
    elements.append(Paragraph("Weekly Scrap Rate Chart", styles['Title']))
    elements.append(Image(tmp_chart.name, width=500, height=250))
    elements.append(PageBreak())

    # ===== Página 3: Top 10 Pareto =====
    tmp_pareto = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    df_top10 = create_pareto_chart(items_df, tmp_pareto.name)

    elements.append(Paragraph("Top Contributors - Pareto Analysis", styles['Title']))
    elements.append(Image(tmp_pareto.name, width=500, height=250))
    elements.append(Spacer(1, 12))

    # Tabla del Top 10 con % acumulado
    data_items = [df_top10.columns.tolist()] + df_top10.values.tolist()
    table_items = Table(data_items)
    table_items.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.gray),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(table_items)

    # Construir PDF
    doc.build(elements)

    # Borrar imágenes temporales
    os.unlink(tmp_chart.name)
    os.unlink(tmp_pareto.name)
