#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TẦNG 5: VISUALIZATION LAYER – Top URLs Horizontal Bar Chart
File: components/topurl_chart.py
Mục đích: Tạo Plotly figure cho Horizontal Bar Chart Top 10 URLs.
          Dữ liệu đến từ FastAPI → phân tích bởi PySpark + ghi vào Hive.
=============================================================================
"""

from typing import Any

import plotly.graph_objects as go  # type: ignore

# -----------------------------------------------------------------------
# Design tokens
# -----------------------------------------------------------------------
BG_COLOR = "rgba(0,0,0,0)"
PAPER_COLOR = "rgba(0,0,0,0)"
TEXT_COLOR = "#c4a882"
GRID_COLOR = "rgba(196, 130, 45, 0.1)"
FONT_FAMILY = "Inter, system-ui, sans-serif"

# Gradient màu từ vàng gold → nâu brown (top → bottom)
BAR_COLORS_TOP10 = [
    "#f59e0b",   # 1st – Gold tươi nhất
    "#eca012",
    "#e39a1a",
    "#d99320",
    "#cf8d28",
    "#c58730",
    "#bb8138",
    "#b17b40",
    "#a77548",
    "#c4822d",   # 10th – Brown
]


def create_top_urls_figure(data: list[dict[str, Any]]) -> go.Figure:
    """
    Tạo Plotly Horizontal Bar Chart cho Top 10 URLs.

    Args:
        data: Danh sách dict với keys: url, request_count, unique_visitors, avg_response_size
              (sorted by request_count DESC)

    Returns:
        go.Figure: Plotly figure object cho dcc.Graph
    """
    if not data:
        return _empty_figure("Chưa có dữ liệu Top URLs\n(Đang chờ PySpark/Hive hoàn thành...)")

    # Chuẩn hóa và đảo ngược thứ tự (plotly bar chart: bottom = first item)
    # Đảo để item cao nhất hiện ở trên cùng
    items = list(reversed(data))

    urls: list[str] = []
    counts: list[int] = []
    visitors: list[int] = []
    avg_sizes: list[int] = []
    hover_texts: list[str] = []
    bar_colors: list[str] = []

    reversed_colors = list(reversed(BAR_COLORS_TOP10))

    for idx, item in enumerate(items):
        # Hỗ trợ cả dict và object attribute
        url = item.get("url") if isinstance(item, dict) else item.url
        count = item.get("request_count") if isinstance(item, dict) else item.request_count
        visitors_n = item.get("unique_visitors") if isinstance(item, dict) else item.unique_visitors
        avg_size = item.get("avg_response_size") if isinstance(item, dict) else item.avg_response_size

        # Rút ngắn URL cho trục Y
        short_url = url[:30] + "…" if len(url) > 30 else url

        urls.append(short_url)
        counts.append(count)
        visitors.append(visitors_n)
        avg_sizes.append(avg_size)
        bar_colors.append(
            reversed_colors[idx] if idx < len(reversed_colors) else "#c4822d"
        )
        hover_texts.append(
            f"<b>{url}</b><br>"
            f"Requests: <b>{count:,}</b><br>"
            f"Unique Visitors: <b>{visitors_n:,}</b><br>"
            f"Avg Response Size: <b>{_fmt_bytes(avg_size)}</b>"
        )

    fig = go.Figure(
        data=[
            go.Bar(
                y=urls,
                x=counts,
                orientation="h",              # Horizontal bar chart
                marker=dict(
                    color=bar_colors,
                    line=dict(color="rgba(0,0,0,0.2)", width=0.5),
                    # Opacity gradient: top bar sáng hơn
                    opacity=0.92,
                ),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_texts,
                # Hiển thị số ngay bên phải thanh bar
                text=[_fmt(c) for c in counts],
                textposition="outside",
                textfont=dict(color=TEXT_COLOR, size=11),
                cliponaxis=False,
            )
        ]
    )

    # Thêm đường dọc trung bình
    avg_count = sum(counts) / len(counts) if counts else 0
    fig.add_vline(
        x=avg_count,
        line_dash="dot",
        line_color="rgba(245, 158, 11, 0.4)",
        line_width=1.5,
        annotation_text=f"Avg: {_fmt(int(avg_count))}",
        annotation_position="top right",
        annotation_font=dict(color="#f59e0b", size=10),
    )

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=10, r=80, t=10, b=30),
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=11),
        # Trục X
        xaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickfont=dict(color=TEXT_COLOR, size=10),
            tickformat=",",              # Format dấu phân cách nghìn
        ),
        # Trục Y (URL labels)
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            tickfont=dict(color=TEXT_COLOR, size=11, family="monospace"),
        ),
        bargap=0.25,
        hoverlabel=dict(
            bgcolor="#221709",
            bordercolor="rgba(196,130,45,0.4)",
            font=dict(color="#f5dcb8", size=12),
        ),
        # Không cần legend (single trace)
        showlegend=False,
    )

    return fig


def _empty_figure(message: str) -> go.Figure:
    """Figure rỗng khi chưa có data."""
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
    """Format số lớn."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def _fmt_bytes(num: int) -> str:
    """Format bytes."""
    if num >= 1_048_576:
        return f"{num/1_048_576:.1f} MB"
    if num >= 1_024:
        return f"{num/1_024:.1f} KB"
    return f"{num} B"
