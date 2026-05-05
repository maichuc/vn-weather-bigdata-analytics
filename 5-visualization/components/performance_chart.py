import plotly.express as px
from plotly.graph_objects import Figure

def create_performance_figure(mr_time, spark_time):
    data = [
        {"Công nghệ": "MapReduce", "Thời gian (giây)": mr_time},
        {"Công nghệ": "Apache Spark", "Thời gian (giây)": spark_time},
    ]

    fig = px.bar(
        data, x="Thời gian (giây)", y="Công nghệ",
        orientation="h", text="Thời gian (giây)", color="Công nghệ",
        color_discrete_map={"MapReduce": "#0284c7", "Apache Spark": "#38bdf8"}
    )

    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0f2fe"),
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(14, 165, 233, 0.1)"),
        yaxis=dict(showgrid=False)
    )
    return fig
