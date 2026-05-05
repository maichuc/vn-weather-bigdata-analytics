#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TẦNG 5: VISUALIZATION LAYER – Main Layout with Rain Chart
File: layouts/main_layout.py
=============================================================================
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

COLORS = {
    "bg_primary":    "#030b14",
    "bg_card":       "#0d213b",
    "accent":        "#38bdf8",
    "text_primary":  "#e0f2fe",
    "text_secondary":"#bae6fd",
    "text_muted":    "#7dd3fc",
    "border":        "rgba(14, 165, 233, 0.25)",
}

CARD_STYLE = {
    "background": COLORS["bg_card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "16px",
    "padding": "20px",
    "boxShadow": "0 4px 15px rgba(0,0,0,0.3)"
}

TAB_STYLE = {
    "padding": "15px",
    "backgroundColor": "transparent",
    "color": COLORS["text_muted"],
    "border": "none",
    "fontWeight": "600",
    "fontSize": "1.1rem"
}

TAB_SELECTED_STYLE = {
    "padding": "15px",
    "backgroundColor": "transparent",
    "color": COLORS["accent"],
    "borderBottom": f"3px solid {COLORS['accent']}",
    "fontWeight": "700",
    "fontSize": "1.1rem"
}

def _metric_card(label, icon, value_id, subtitle, accent_color=None):
    accent = accent_color or COLORS["accent"]
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.Span(icon, className="me-2", style={"fontSize": "1.2rem"}),
                    html.Span(label.upper(), style={"fontSize": "0.75rem", "color": COLORS["text_muted"], "fontWeight": "600", "letterSpacing": "1px"}),
                ], className="mb-2"),
                html.Div("—", id=value_id, style={"fontSize": "1.8rem", "fontWeight": "700", "color": accent}),
                html.Div(subtitle, style={"fontSize": "0.7rem", "color": COLORS["text_muted"]}),
            ]),
            style=CARD_STYLE,
            className="h-100",
        ),
        xs=6, md=3,
    )

def create_layout():
    return html.Div(
        id="root",
        children=[
            dcc.Interval(id="interval-refresh", interval=30_000, n_intervals=0),
            
            # Header
            html.Header(
                dbc.Container(
                    dbc.Row([
                        dbc.Col(html.H1("HỆ THỐNG PHÂN TÍCH THỜI TIẾT VIỆT NAM", style={"color": COLORS["text_primary"], "fontSize": "1.4rem", "margin": "0", "fontWeight": "800"}), width=8),
                        dbc.Col(html.Div("Lab 10 · Big Data Pipeline", style={"color": COLORS["text_muted"], "textAlign": "right", "fontSize": "0.9rem"}), width=4),
                    ], align="center"),
                    fluid=True, className="px-4 py-3"
                ),
                style={"background": COLORS["bg_primary"], "borderBottom": f"1px solid {COLORS['border']}", "position": "sticky", "top": "0", "zIndex": "1000"}
            ),

            dbc.Container([
                html.Div(id="alert-container", className="mt-3"),
                
                # Tiêu đề & Cập nhật
                html.Div([
                    html.Div([
                        html.H2("Bảng Điều Khiển Khí Tượng", style={"color": COLORS["accent"], "marginTop": "20px", "fontWeight": "700", "display": "inline-block"}),
                        html.Div(id="last-updated-time", style={"fontSize": "0.85rem", "color": COLORS["text_muted"], "fontStyle": "italic", "display": "inline-block", "marginLeft": "20px"}),
                    ]),
                    html.P("Phân tích dữ liệu thời gian thực xử lý qua Spark & MapReduce Cluster.", style={"color": COLORS["text_secondary"]}),
                ], className="mb-2"),

                # Tabs Navigation
                dbc.Tabs([
                    # TAB 1: THỜI TIẾT
                    dbc.Tab(label="DỰ BÁO THỜI TIẾT", tab_id="tab-weather", children=[
                        html.Div([
                            # Chỉ số tổng quan
                            dbc.Row([
                                _metric_card("Nhiệt độ TB", "🌡️", "metric-avg-temp", "Trung bình toàn quốc"),
                                _metric_card("Mưa lớn nhất", "🌧️", "metric-max-rain", "Lượng mưa cao nhất"),
                                _metric_card("Tỉnh nóng nhất", "🔥", "metric-max-temp", "Nhiệt độ cao nhất"),
                                _metric_card("Tỉnh lạnh nhất", "❄️", "metric-min-temp", "Nhiệt độ thấp nhất"),
                            ], className="mt-4 mb-4 g-3"),

                            # Heatmap
                            dbc.Row([
                                dbc.Col(dbc.Card(dbc.CardBody([
                                    html.H5([html.I(className="bi bi-map me-2"), "Bản đồ Nhiệt độ Toàn quốc"], className="card-title mb-3", style={"color": COLORS["text_primary"]}),
                                    dcc.Graph(id="weather-heatmap", style={"height": "550px"}, config={'displayModeBar': False})
                                ]), style=CARD_STYLE), width=12),
                            ], className="mb-4 g-3"),

                            # Charts Row 1
                            dbc.Row([
                                dbc.Col(dbc.Card(dbc.CardBody([
                                    html.H5("Top 10 Tỉnh Nóng Nhất", className="card-title"),
                                    dcc.Graph(id="top-hot-chart", style={"height": "350px"})
                                ]), style=CARD_STYLE), md=6),
                                dbc.Col(dbc.Card(dbc.CardBody([
                                    html.H5("Top 10 Tỉnh Mưa Nhiều (1h)", className="card-title"),
                                    dcc.Graph(id="top-rain-chart", style={"height": "350px"})
                                ]), style=CARD_STYLE), md=6),
                            ], className="mb-4 g-3"),

                            # Charts Row 2
                            dbc.Row([
                                dbc.Col(dbc.Card(dbc.CardBody([
                                    html.H5("Tình trạng Thời tiết Toàn quốc", className="card-title"),
                                    dcc.Graph(id="weather-desc-chart", style={"height": "350px"})
                                ]), style=CARD_STYLE), md=12),
                            ], className="mb-4 g-3"),

                            # Table
                            dbc.Row([
                                dbc.Col(dbc.Card(dbc.CardBody([
                                    html.H5("Danh Sách Chi Tiết 63 Tỉnh Thành", className="card-title"),
                                    html.Div(id="weather-table-container", className="mt-3")
                                ]), style=CARD_STYLE), width=12),
                            ], className="mb-4")
                        ])
                    ], tab_style={"marginLeft": "0"}, label_style=TAB_STYLE, active_label_style=TAB_SELECTED_STYLE),

                    # TAB 2: HIỆU NĂNG
                    dbc.Tab(label="HIỆU NĂNG HỆ THỐNG", tab_id="tab-performance", children=[
                        html.Div([
                            html.H3("Phân tích Hiệu năng Big Data", style={"color": COLORS["accent"], "marginTop": "30px", "marginBottom": "20px"}),
                            
                            dbc.Row([
                                dbc.Col(dbc.Card(dbc.CardBody([
                                    html.H5([html.I(className="bi bi-cpu me-2"), "So sánh Thời gian Xử lý"], className="card-title mb-4"),
                                    dcc.Graph(id="performance-graph", style={"height": "500px"}),
                                    html.Div([
                                        html.P([
                                            html.Strong("Apache Spark: "), "Xử lý dữ liệu dạng bảng với cơ chế In-memory đạt hiệu năng cực cao."
                                        ], className="mt-4", style={"color": COLORS["text_secondary"]}),
                                        html.P([
                                            html.Strong("Hadoop MapReduce: "), "Xử lý theo từng lô trên ổ đĩa, có độ trễ lớn hơn."
                                        ], style={"color": COLORS["text_secondary"]}),
                                    ], className="px-3")
                                ]), style=CARD_STYLE), lg=8),
                                
                                dbc.Col([
                                    dbc.Card(dbc.CardBody([
                                        html.H5("Thông số Hệ thống", className="card-title mb-3"),
                                        html.Ul([
                                            html.Li("Storage: HDFS Cluster"),
                                            html.Li("Cluster Manager: YARN"),
                                            html.Li("Processing: Spark 3.2"),
                                            html.Li("API: FastAPI + httpx"),
                                            html.Li("Visualization: Plotly Dash")
                                        ], style={"color": COLORS["text_muted"], "lineHeight": "2"})
                                    ]), style=CARD_STYLE, className="mb-3"),
                                    
                                    dbc.Card(dbc.CardBody([
                                        html.H5("Trạng thái Pipeline", className="card-title mb-3"),
                                        html.Div([
                                            html.Div([html.I(className="bi bi-check-circle-fill text-success me-2"), "Dữ liệu: Active"]),
                                            html.Div([html.I(className="bi bi-check-circle-fill text-success me-2"), "Xử lý: Ready"]),
                                            html.Div([html.I(className="bi bi-check-circle-fill text-success me-2"), "Cổng Serving: Online"]),
                                        ], style={"color": COLORS["text_secondary"], "lineHeight": "2"})
                                    ]), style=CARD_STYLE)
                                ], lg=4)
                            ], className="g-3")
                        ])
                    ], label_style=TAB_STYLE, active_label_style=TAB_SELECTED_STYLE),
                ], id="dashboard-tabs", active_tab="tab-weather", className="mt-3")

            ], fluid=True, className="px-4 pb-5")
        ],
        style={"backgroundColor": COLORS["bg_primary"], "minHeight": "100vh", "fontFamily": "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"}
    )
