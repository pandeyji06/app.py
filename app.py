import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME / GLOBAL CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13161f !important;
    border-right: 1px solid #1f2330;
}
[data-testid="stSidebar"] * {
    color: #c9ccd8 !important;
}
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e8eaf0 !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }

/* ── Dashboard Header ── */
.dash-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #1f2330;
}
.dash-title {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #ffffff;
    line-height: 1;
}
.dash-subtitle {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.35rem;
    font-weight: 400;
    font-family: 'DM Mono', monospace;
}
.dash-badge {
    background: #1a2a1a;
    border: 1px solid #2d4a2d;
    color: #4ade80;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    letter-spacing: 0.05em;
}

/* ── Section Labels ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 1rem;
    font-family: 'DM Mono', monospace;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2.5rem;
}
.kpi-card {
    background: #13161f;
    border: 1px solid #1f2330;
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #2d3348; }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 12px 12px 0 0;
}
.kpi-card.accent-green::before  { background: linear-gradient(90deg, #22c55e, #4ade80); }
.kpi-card.accent-blue::before   { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-card.accent-violet::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.kpi-card.accent-amber::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }

.kpi-icon {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
    display: block;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.4rem;
    font-family: 'DM Mono', monospace;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #f9fafb;
    line-height: 1;
}
.kpi-delta {
    font-size: 0.75rem;
    color: #4ade80;
    margin-top: 0.5rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
}

/* ── Chart Containers ── */
.chart-card {
    background: #13161f;
    border: 1px solid #1f2330;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}
.chart-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e8eaf0;
    margin-bottom: 0.2rem;
}
.chart-desc {
    font-size: 0.75rem;
    color: #6b7280;
    margin-bottom: 1.25rem;
    font-family: 'DM Mono', monospace;
}

/* ── Sidebar Widgets ── */
.sidebar-section {
    background: #1a1d28;
    border: 1px solid #252838;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── PLOTLY TEMPLATE ────────────────────────────────────────────────────────────
PLOT_BG   = "#13161f"
PAPER_BG  = "#13161f"
GRID_CLR  = "#1a1d28"
TICK_CLR  = "#4b5563"
TEXT_CLR  = "#9ca3af"
LINE_MAIN = "#60a5fa"
LINE_FORE = "#4ade80"
BAR_CLR   = "#8b5cf6"


def base_layout(title="", height=340):
    return dict(
        height=height,
        title=dict(text=title, font=dict(size=14)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="DM Sans, sans-serif", color=TEXT_CLR),
        margin=dict(l=10, r=10, t=10, b=40),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=11, color=TICK_CLR),
            linecolor="#1f2330",
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_CLR, zeroline=False,
            tickfont=dict(size=11, color=TICK_CLR),
            linecolor="#1f2330",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", font=dict(size=12, color=TEXT_CLR),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1f2330", bordercolor="#2d3348",
            font=dict(family="DM Mono, monospace", size=12, color="#e8eaf0"),
        ),
    )


# ── SAMPLE DATA GENERATOR (fallback) ──────────────────────────────────────────
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", "2024-03-31", freq="D")
    trend = np.linspace(800, 1400, len(dates))
    seasonal = 200 * np.sin(np.linspace(0, 4 * np.pi, len(dates)))
    noise = np.random.normal(0, 80, len(dates))
    sales = pd.DataFrame({
        "Date": dates,
        "TotalPrice": np.clip(trend + seasonal + noise, 50, None).round(2),
    })

    forecast_dates = pd.date_range("2024-04-01", "2024-06-30", freq="D")
    ft = np.linspace(1400, 1650, len(forecast_dates))
    fs = 180 * np.sin(np.linspace(0, np.pi, len(forecast_dates)))
    fn = np.random.normal(0, 50, len(forecast_dates))
    forecast = pd.DataFrame({
        "Date": forecast_dates,
        "Predicted_Sales": np.clip(ft + fs + fn, 50, None).round(2),
    })
    return sales, forecast


# ── DATA LOADER ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        sales = pd.read_csv("sales_data.csv", parse_dates=["Date"])
        forecast = pd.read_csv("forecast_data.csv", parse_dates=["Date"])
        return sales, forecast, False
    except FileNotFoundError:
        sales, forecast = generate_sample_data()
        return sales, forecast, True


sales_df, forecast_df, using_sample = load_data()
sales_df.sort_values("Date", inplace=True)
forecast_df.sort_values("Date", inplace=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")

    min_date = sales_df["Date"].min().date()
    max_date = sales_df["Date"].max().date()

    st.markdown("**📅 Date Range**")
    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    with col_b:
        end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

    st.markdown("---")
    st.markdown("**📊 Chart Options**")
    show_ma = st.toggle("Show 7-Day Moving Average", value=True)
    show_forecast = st.toggle("Show Forecast Overlay", value=True)

    st.markdown("---")
    if using_sample:
        st.info("⚡ Demo mode — using generated sample data.\n\nPlace `sales_data.csv` & `forecast_data.csv` in the app directory to load your own data.", icon="ℹ️")

# ── FILTER DATA ────────────────────────────────────────────────────────────────
mask = (sales_df["Date"].dt.date >= start_date) & (sales_df["Date"].dt.date <= end_date)
filtered = sales_df[mask].copy()
# Focus on last 90 days for better visualization
filtered = filtered.tail(90)

# ── KPIs ───────────────────────────────────────────────────────────────────────
total_rev   = filtered["TotalPrice"].sum()
avg_daily   = filtered["TotalPrice"].mean()
max_sales   = filtered["TotalPrice"].max()
min_sales   = filtered["TotalPrice"].min()
days_count  = filtered["Date"].nunique()


def fmt(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:.2f}"


# ── DASHBOARD HEADER ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Sales Intelligence</div>
    <div class="dash-subtitle">Revenue & Forecast Analytics · {start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}</div>
  </div>
  <div class="dash-badge">● LIVE DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

# ── KPI SECTION ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Key Performance Indicators</div>', unsafe_allow_html=True)

kpi_html = f"""
<div class="kpi-grid">
  <div class="kpi-card accent-green">
    <span class="kpi-icon">💰</span>
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value">{fmt(total_rev)}</div>
    <div class="kpi-delta">↑ across {days_count} days</div>
  </div>
  <div class="kpi-card accent-blue">
    <span class="kpi-icon">📊</span>
    <div class="kpi-label">Avg Daily Sales</div>
    <div class="kpi-value">{fmt(avg_daily)}</div>
    <div class="kpi-delta">per trading day</div>
  </div>
  <div class="kpi-card accent-violet">
    <span class="kpi-icon">🚀</span>
    <div class="kpi-label">Peak Day</div>
    <div class="kpi-value">{fmt(max_sales)}</div>
    <div class="kpi-delta">highest single day</div>
  </div>
  <div class="kpi-card accent-amber">
    <span class="kpi-icon">📉</span>
    <div class="kpi-label">Lowest Day</div>
    <div class="kpi-value">{fmt(min_sales)}</div>
    <div class="kpi-delta">minimum recorded</div>
  </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)
st.markdown("""
- Sales show high volatility indicating inconsistent demand patterns  
- Peak sales reach above $3,000 while low days drop below $100  
- Forecast suggests moderate recovery in upcoming days  
- Tuesday and Thursday drive the highest average revenue  
- Weekends show slightly lower performance compared to weekdays  

👉 Focus: Stabilizing demand and maximizing peak-day performance
""")

# ── CHART 1 – Historical Sales Trend ──────────────────────────────────────────
st.markdown('<div class="section-label">Trend Analysis</div>', unsafe_allow_html=True)

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Historical Sales Trend</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Daily revenue performance over selected period</div>', unsafe_allow_html=True)

fig1 = go.Figure()

# Area fill
fig1.add_trace(go.Scatter(
    x=filtered["Date"], y=filtered["TotalPrice"],
    fill="tozeroy",
    fillcolor="rgba(96, 165, 250, 0.06)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=False, hoverinfo="skip",
))

# Main line
fig1.add_trace(go.Scatter(
    x=filtered["Date"], y=filtered["TotalPrice"],
    mode="lines", name="Daily Sales",
    line=dict(color=LINE_MAIN, width=1.8),
    hovertemplate="<b>%{x|%b %d, %Y}</b><br>Sales: $%{y:,.0f}<extra></extra>",
))


# Moving average
if show_ma and len(filtered) >= 7:
    ma7 = filtered["TotalPrice"].rolling(7, center=True).mean()
    fig1.add_trace(go.Scatter(
        x=filtered["Date"], y=ma7,
        mode="lines", name="7-Day MA",
        line=dict(color="#f59e0b", width=2, dash="dot"),
        hovertemplate="7-Day MA: $%{y:,.0f}<extra></extra>",
    ))

layout1 = base_layout(height=320)
layout1["yaxis"]["tickprefix"] = "$"
layout1["yaxis"]["tickformat"] = ",.0f"
fig1.update_layout(**layout1)
st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# ── CHART 2 & 3 side by side ──────────────────────────────────────────────────
col1, col2 = st.columns([3, 2], gap="medium")

# Chart 2 – Actual vs Forecast
with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Actual vs Forecast Sales</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Historical actuals bridged with model predictions</div>', unsafe_allow_html=True)

    fig2 = go.Figure()

    # Historical (area)
    fig2.add_trace(go.Scatter(
        x=filtered["Date"], y=filtered["TotalPrice"],
        fill="tozeroy",
        fillcolor="rgba(96,165,250,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))
    fig2.add_trace(go.Scatter(
        x=filtered["Date"], y=filtered["TotalPrice"],
        mode="lines", name="Actual",
        line=dict(color=LINE_MAIN, width=1.8),
        hovertemplate="<b>%{x|%b %d}</b><br>Actual: $%{y:,.0f}<extra></extra>",
    ))
    fig2.add_vrect(
    x0=forecast_df["Date"].min(),
    x1=forecast_df["Date"].max(),
    fillcolor="#22c55e",
    opacity=0.15,   # 👈 increase from 0.08
    line_width=0,
)

    # Forecast
    if show_forecast:
        fig2.add_trace(go.Scatter(
            x=forecast_df["Date"], y=forecast_df["Predicted_Sales"],
            fill="tozeroy",
            fillcolor="rgba(74,222,128,0.06)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ))
        fig2.add_trace(go.Scatter(
            x=forecast_df["Date"], y=forecast_df["Predicted_Sales"],
            mode="lines", name="Forecast",
            line=dict(color=LINE_FORE, width=2, dash="dash"),
            hovertemplate="<b>%{x|%b %d}</b><br>Forecast: $%{y:,.0f}<extra></extra>",
        ))

        # Bridge connector
        if not filtered.empty:
            bridge_x = [filtered["Date"].iloc[-1], forecast_df["Date"].iloc[0]]
            bridge_y = [filtered["TotalPrice"].iloc[-1], forecast_df["Predicted_Sales"].iloc[0]]
            fig2.add_trace(go.Scatter(
                x=bridge_x, y=bridge_y,
                mode="lines", showlegend=False,
                line=dict(color="#4b5563", width=1.5, dash="dot"),
                hoverinfo="skip",
            ))

    layout2 = base_layout(height=320)
    layout2["yaxis"]["tickprefix"] = "$"
    layout2["yaxis"]["tickformat"] = ",.0f"
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# Chart 3 – Avg Sales by Weekday
with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Avg Sales by Weekday</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Which days drive the most revenue</div>', unsafe_allow_html=True)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_short  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    filtered["Weekday"] = pd.Categorical(
        filtered["Date"].dt.day_name(), categories=day_order, ordered=True
    )
    weekday_avg = filtered.groupby("Weekday", observed=True)["TotalPrice"].mean().reindex(day_order)

    # Color gradient: highlight the max bar
    max_day = weekday_avg.idxmax()
    bar_colors = [
        "#a78bfa" if d == max_day else "#3d2f6e"
        for d in weekday_avg.index
    ]

    fig3 = go.Figure(go.Bar(
        x=day_short,
        y=weekday_avg.values,
        marker=dict(
            color=bar_colors,
            line=dict(width=0),
            cornerradius=6,
        ),
        hovertemplate="<b>%{x}</b><br>Avg: $%{y:,.0f}<extra></extra>",
    ))

    layout3 = base_layout(height=320)
    layout3["yaxis"]["tickprefix"] = "$"
    layout3["yaxis"]["tickformat"] = ",.0f"
    layout3["xaxis"]["showgrid"] = False
    layout3["yaxis"]["showgrid"] = True
    layout3["bargap"] = 0.35
    fig3.update_layout(**layout3)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    margin-top: 2.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid #1f2330;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
  <span style="font-size:0.72rem; color:#4b5563; font-family:'DM Mono',monospace;">
    Sales Intelligence Dashboard · Built with Streamlit & Plotly
  </span>
  <span style="font-size:0.72rem; color:#4b5563; font-family:'DM Mono',monospace;">
    v1.0.0
  </span>
</div>
""", unsafe_allow_html=True)