#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TẦNG 5: VISUALIZATION LAYER – Status Code Donut Chart
File: components/status_chart.py
Mục đích: Tạo Plotly figure cho Donut Pie Chart phân phối HTTP Status Code.
          Dữ liệu đến từ FastAPI → xử lý bởi MapReduce + PySpark.
=============================================================================
"""

from typing import Any

import plotly.graph_objects as go  # type: ignore

# -----------------------------------------------------------------------
# Design tokens (đồng bộ với main_layout.py và custom.css)
# -----------------------------------------------------------------------
BG_COLOR = "rgba(0,0,0,0)"           # Transparent – dùng CSS background của card
PAPER_COLOR = "rgba(0,0,0,0)"
TEXT_COLOR = "#c4a882"
GRID_COLOR = "rgba(196, 130, 45, 0.1)"
FONT_FAMILY = "Inter, system-ui, sans-serif"

# Bảng màu theo nhóm status code
STATUS_COLOR_MAP = {
    # 2xx Success – xanh lá
    200: "#22c55e",
    201: "#16a34a",
    204: "#15803d",
    # 3xx Redirect – xanh dương
    301: "#3b82f6",
    302: "#2563eb",
    304: "#1d4ed8",
    # 4xx Client Error – vàng/cam
    400: "#f59e0b",
    401: "#d97706",
    403: "#b45309",
    404: "#ef4444",
    429: "#dc2626",
    # 5xx Server Error – đỏ
    500: "#dc2626",
    502: "#b91c1c",
    503: "#991b1b",
}

FALLBACK_COLORS = [
    "#f59e0b", "#c4822d", "#d97706", "#e4a14a",
    "#22c55e", "#3b82f6", "#ef4444", "#a855f7",
]


def get_status_color(status_code: int) -> str:
    """Lấy màu theo status code, fallback theo index."""
    return STATUS_COLOR_MAP.get(status_code, FALLBACK_COLORS[status_code % len(FALLBACK_COLORS)])


def create_status_code_figure(data: list[dict[str, Any]]) -> go.Figure:
    """
    Tạo Plotly Donut Pie Chart cho HTTP Status Code distribution.

    Args:
        data: Danh sách dict với keys: status_code, count, percentage, description
              (có thể là list[StatusCodeRecord] đã serialize hoặc raw dict từ API)

    Returns:
        go.Figure: Plotly figure object cho dcc.Graph
    """
    if not data:
        return _empty_figure("Chưa có dữ liệu Status Code\n(Đang chờ Spark pipeline hoàn thành...)")

    # Chuẩn hóa data (dict hoặc Pydantic model)
    labels: list[str] = []
    values: list[int] = []
    colors: list[str] = []
    hover_texts: list[str] = []

    for item in data:
        # Hỗ trợ cả dict và object có attribute
        sc = item.get("status_code") if isinstance(item, dict) else item.status_code
        count = item.get("count") if isinstance(item, dict) else item.count
        pct = item.get("percentage") if isinstance(item, dict) else item.percentage
        desc = item.get("description") if isinstance(item, dict) else item.description

        labels.append(f"HTTP {sc}")
        values.append(count)
        colors.append(get_status_color(sc))
        hover_texts.append(
            f"<b>HTTP {sc}</b><br>"
            f"{desc}<br>"
            f"Số lượng: <b>{count:,}</b><br>"
            f"Tỷ lệ: <b>{pct:.1f}%</b>"
        )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.52,                  # Donut style
                marker=dict(
                    colors=colors,
                    line=dict(color="#0f0a04", width=2),  # Đường viền dark giữa các slice
                ),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_texts,
                textposition="outside",
                textinfo="label+percent",
                textfont=dict(
                    color=TEXT_COLOR,
                    size=11,
                    family=FONT_FAMILY,
                ),
                pull=[0.03 if i == 0 else 0 for i in range(len(labels))],  # Nổi bật slice đầu
                sort=False,                  # Giữ nguyên thứ tự (đã sort theo count)
                rotation=90,
            )
        ]
    )

    # Chú thích ở giữa Donut
    total = sum(values)
    fig.add_annotation(
        text=f"<b>{_fmt(total)}</b><br><span style='font-size:10px'>requests</span>",
        x=0.5, y=0.5,
        font=dict(size=18, color="#f5dcb8", family="'Playfair Display', Georgia, serif"),
        showarrow=False,
        align="center",
    )

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR),
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            font=dict(size=11, color=TEXT_COLOR),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(196,130,45,0.2)",
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#221709",
            bordercolor="rgba(196,130,45,0.4)",
            font=dict(color="#f5dcb8", size=12),
        ),
    )

    return fig


def _empty_figure(message: str) -> go.Figure:
    """Figure rỗng hiển thị khi chưa có data."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(color="#8a7258", size=14, family=FONT_FAMILY),
        align="center",
    )
    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def _fmt(num: int) -> str:
    """Format số: 15420 → '15.4K'."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)
