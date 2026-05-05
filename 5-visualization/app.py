#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TẦNG 5: VISUALIZATION LAYER – Plotly Dash Dashboard (Support Rain)
File: app.py
=============================================================================
"""

import logging
from datetime import datetime
import dash
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output
from components.performance_chart import create_performance_figure
from layouts.main_layout import create_layout

import os
API_BASE_URL = os.getenv("FASTAPI_URL", "http://fastapi:4000")

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG, 
        dbc.icons.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
    ],
    suppress_callback_exceptions=True,
    title="Dự báo & Phân tích Thời tiết Việt Nam",
)

server = app.server
app.layout = create_layout()

WEATHER_TRANSLATIONS = {
    "clear sky": "Trời trong xanh",
    "few clouds": "Ít mây",
    "scattered clouds": "Mây thưa",
    "broken clouds": "Mây rải rác",
    "overcast clouds": "Mây u ám",
    "light rain": "Mưa nhỏ",
    "moderate rain": "Mưa vừa",
    "heavy intensity rain": "Mưa lớn",
    "thunderstorm": "Có dông",
    "mist": "Sương mù nhẹ",
    "fog": "Sương mù",
}

def translate_description(desc):
    if not desc or pd.isna(desc): return "N/A"
    return WEATHER_TRANSLATIONS.get(desc.lower(), desc.capitalize())

def create_top_hot_figure(df):
    if df.empty: return go.Figure().update_layout(template="plotly_dark")
    top_10 = df.sort_values("temp", ascending=False).head(10)
    fig = px.bar(
        top_10, x="temp", y="province", orientation='h',
        color="temp", color_continuous_scale="Reds",
        labels={"temp": "Nhiệt độ (°C)", "province": "Tỉnh thành"}
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0f2fe"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )
    return fig

def create_top_rain_figure(df):
    if df.empty or "rain_1h" not in df.columns: 
        return go.Figure().update_layout(template="plotly_dark")
    top_10 = df.sort_values("rain_1h", ascending=False).head(10)
    fig = px.bar(
        top_10, x="rain_1h", y="province", orientation='h',
        color="rain_1h", color_continuous_scale="Blues",
        labels={"rain_1h": "Lượng mưa (mm)", "province": "Tỉnh thành"}
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0f2fe"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )
    return fig

def create_weather_pie(df):
    if df.empty or "description" not in df.columns: 
        return go.Figure().update_layout(template="plotly_dark")
    counts = df["description"].value_counts().reset_index()
    counts.columns = ["description", "count"]
    
    fig = px.pie(
        counts, values="count", names="description",
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0f2fe"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

@callback(
    Output("metric-avg-temp", "children"),
    Output("metric-max-rain", "children"),
    Output("metric-max-temp", "children"),
    Output("metric-min-temp", "children"),
    Output("weather-heatmap", "figure"),
    Output("performance-graph", "figure"),
    Output("top-hot-chart", "figure"),
    Output("top-rain-chart", "figure"),
    Output("weather-desc-chart", "figure"),
    Output("weather-table-container", "children"),
    Output("last-updated-time", "children"),
    Output("alert-container", "children"),
    Input("interval-refresh", "n_intervals"),
)
def update_dashboard(n):
    try:
        # 1. Fetch Summary
        summary_res = requests.get(f"{API_BASE_URL}/api/weather/summary", timeout=5).json()
        s_data = summary_res["data"]
        
        # 2. Fetch Details
        details_res = requests.get(f"{API_BASE_URL}/api/weather/latest", timeout=5).json()
        d_list = details_res.get("data", [])
        
        if not d_list:
            raise ValueError("Không có dữ liệu chi tiết từ API.")
            
        df = pd.DataFrame(d_list)

        # Việt hóa mô tả
        df["description"] = df["description"].apply(translate_description)

        # Metrics
        avg_temp = f"{s_data['avg_temp']}°C"
        max_rain = f"{s_data.get('max_rain_val', 0.0)} mm ({s_data.get('max_rain_province', 'N/A')})"
        max_temp = f"{s_data['max_temp_val']}°C ({s_data['max_temp_province']})"
        min_temp = f"{s_data['min_temp_val']}°C ({s_data['min_temp_province']})"

        # Heatmap
        heatmap_fig = px.scatter_mapbox(
            df, lat="lat", lon="lon", color="temp", size=[15]*len(df),
            center=dict(lat=16.4, lon=106.6), zoom=4.8,
            mapbox_style="carto-darkmatter",
            color_continuous_scale="RdYlBu_r",
            hover_name="province",
            labels={"temp": "Nhiệt độ (°C)"}
        )
        heatmap_fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0f2fe")
        )

        perf_fig = create_performance_figure(s_data.get('mapreduce_time', 0), s_data.get('spark_time', 0))
        
        top_hot_fig = create_top_hot_figure(df)
        top_rain_fig = create_top_rain_figure(df)
        weather_pie_fig = create_weather_pie(df)

        # Table
        df_display = df[["province", "temp", "humidity", "rain_1h", "description", "timestamp"]].copy()
        df_display.columns = ["Tỉnh thành", "Nhiệt độ (°C)", "Độ ẩm (%)", "Mưa (mm)", "Mô tả", "Thời điểm"]
        
        table = dbc.Table.from_dataframe(
            df_display, 
            striped=True, bordered=True, hover=True, responsive=True,
            style={"color": "#e0f2fe", "fontSize": "0.85rem"}
        )

        updated_time = f"Cập nhật lúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"

        return avg_temp, max_rain, max_temp, min_temp, heatmap_fig, perf_fig, top_hot_fig, top_rain_fig, weather_pie_fig, table, updated_time, ""

    except Exception as e:
        print(f"Lỗi Dashboard: {e}")
        empty_fig = go.Figure().update_layout(template="plotly_dark")
        return "—", "—", "—", "—", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Đang tải...", "", ""

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=3000)
