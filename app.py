```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────
# GLOBAL STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>

/* App Background */
.stApp {
    background-color: #0d1117;
    color: #f8fafc;
    font-family: 'Segoe UI', sans-serif;
}

/* Remove Streamlit Branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Main Title */
.main-title {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.2rem;
}

/* Subtitle */
.sub-text {
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #131a24, #0f1722);
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 1.5rem;
    box-shadow: 0 0 20px rgba(0,0,0,0.25);
    transition: 0.3s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    border-color: #38bdf8;
}

.kpi-title {
    color: #94a3b8;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.4rem;
}

.kpi-value {
    color: white;
    font-size: 2.2rem;
    font-weight: 800;
    margin-top: 0.4rem;
}

.kpi-desc {
    color: #4ade80;
    font-size: 0.9rem;
    margin-top: 0.4rem;
    font-weight: 600;
}

/* Control Panel */
.control-box {
    background: #131a24;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 2rem;
}

/* Section Heading */
.section-title {
    color: white;
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

/* Insight Box */
.insight-box {
    background: linear-gradient(145deg, #14202f, #101827);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #38bdf8;
    border-radius: 16px;
    padding: 1.2rem;
    margin-top: 1rem;
    margin-bottom: 2rem;
}

.insight-title {
    color: #38bdf8;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.7rem;
}

.insight-text {
    color: #cbd5e1;
    line-height: 1.7;
    font-size: 0.95rem;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        sales_df = pd.read_csv("sales_data.csv")
        forecast_df = pd.read_csv("forecast_data.csv")

        sales_df["Date"] = pd.to_datetime(sales_df["Date"])
        forecast_df["Date"] = pd.to_datetime(forecast_df["Date"])

        return sales_df, forecast_df

    except:
        np.random.seed(42)

        dates = pd.date_range(start="2023-01-01", periods=600)
        sales = np.random.randint(100, 3500, size=600)

        sales_df = pd.DataFrame({
            "Date": dates,
            "TotalPrice": sales
        })

        forecast_dates = pd.date_range(start=dates[-1], periods=30)
        forecast_sales = np.random.randint(900, 3000, size=30)

        forecast_df = pd.DataFrame({
            "Date": forecast_dates,
            "Predicted_Sales": forecast_sales
        })

        return sales_df, forecast_df


sales_df, forecast_df = load_data()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Sales Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">Revenue & Forecast Analytics Dashboard · Streamlit + Plotly</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# CONTROL PANEL
# ─────────────────────────────────────────────
st.markdown('<div class="control-box">', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

min_date = sales_df["Date"].min().date()
max_date = sales_df["Date"].max().date()

with c1:
    start_date = st.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

with c2:
    end_date = st.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

with c3:
    show_ma = st.toggle("7-Day Moving Average", value=True)

with c4:
    show_forecast = st.toggle("Forecast Overlay", value=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
filtered = sales_df[
    (sales_df["Date"].dt.date >= start_date) &
    (sales_df["Date"].dt.date <= end_date)
].copy()

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_rev = filtered["TotalPrice"].sum()
avg_daily = filtered["TotalPrice"].mean()
max_sales = filtered["TotalPrice"].max()
min_sales = filtered["TotalPrice"].min()

# ─────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:1.5rem;">💰</div>
        <div class="kpi-title">TOTAL REVENUE</div>
        <div class="kpi-value">${total_rev:,.0f}</div>
        <div class="kpi-desc">Across selected date range</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:1.5rem;">📊</div>
        <div class="kpi-title">AVG DAILY SALES</div>
        <div class="kpi-value">${avg_daily:,.0f}</div>
        <div class="kpi-desc">Average daily performance</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:1.5rem;">🚀</div>
        <div class="kpi-title">PEAK SALES DAY</div>
        <div class="kpi-value">${max_sales:,.0f}</div>
        <div class="kpi-desc">Highest recorded sales</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="font-size:1.5rem;">📉</div>
        <div class="kpi-title">LOWEST SALES DAY</div>
        <div class="kpi-value">${min_sales:,.0f}</div>
        <div class="kpi-desc">Minimum recorded sales</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INSIGHT BOX
# ─────────────────────────────────────────────
st.markdown("""
<div class="insight-box">
    <div class="insight-title">📌 Dashboard Insights</div>
    <div class="insight-text">
        • Sales patterns show moderate volatility across the selected timeline.<br>
        • Peak revenue days significantly outperform average daily revenue.<br>
        • Forecast model suggests continued demand stability in upcoming periods.<br>
        • Interactive controls allow dynamic analysis across custom date ranges.
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HISTORICAL SALES TREND
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Historical Sales Trend</div>', unsafe_allow_html=True)

fig = go.Figure()

# Area Glow
fig.add_trace(go.Scatter(
    x=filtered["Date"],
    y=filtered["TotalPrice"],
    fill='tozeroy',
    fillcolor='rgba(56,189,248,0.10)',
    line=dict(color='rgba(0,0,0,0)'),
    hoverinfo='skip',
    showlegend=False
))

# Main Sales Line
fig.add_trace(go.Scatter(
    x=filtered["Date"],
    y=filtered["TotalPrice"],
    mode='lines',
    name='Daily Sales',
    line=dict(color='#60a5fa', width=2.5)
))

# Moving Average
if show_ma:
    ma = filtered["TotalPrice"].rolling(7).mean()

    fig.add_trace(go.Scatter(
        x=filtered["Date"],
        y=ma,
        mode='lines',
        name='7-Day MA',
        line=dict(color='#f59e0b', width=2, dash='dot')
    ))

fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#0d1117',
    plot_bgcolor='#131a24',
    font=dict(color='white'),
    height=500,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    )
)

st.plotly_chart(fig, width='stretch')

# ─────────────────────────────────────────────
# FORECAST SECTION
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🔮 Actual vs Forecast</div>', unsafe_allow_html=True)

fig2 = go.Figure()

# Actual
fig2.add_trace(go.Scatter(
    x=filtered["Date"],
    y=filtered["TotalPrice"],
    mode='lines',
    name='Actual Sales',
    line=dict(color='#60a5fa', width=2)
))

# Forecast Overlay
if show_forecast:

    fig2.add_vrect(
        x0=forecast_df["Date"].min(),
        x1=forecast_df["Date"].max(),
        fillcolor='#22c55e',
        opacity=0.08,
        line_width=0
    )

    fig2.add_trace(go.Scatter(
        x=forecast_df["Date"],
        y=forecast_df["Predicted_Sales"],
        mode='lines',
        name='Forecast',
        line=dict(color='#4ade80', width=3, dash='dash')
    ))

fig2.update_layout(
    template='plotly_dark',
    paper_bgcolor='#0d1117',
    plot_bgcolor='#131a24',
    font=dict(color='white'),
    height=500,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig2, width='stretch')

# ─────────────────────────────────────────────
# WEEKDAY ANALYSIS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Average Sales by Weekday</div>', unsafe_allow_html=True)

filtered["weekday"] = filtered["Date"].dt.day_name()

weekday_order = [
    'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday', 'Sunday'
]

weekday_avg = (
    filtered.groupby('weekday')['TotalPrice']
    .mean()
    .reindex(weekday_order)
)

fig3 = go.Figure()

fig3.add_trace(go.Bar(
    x=weekday_avg.index,
    y=weekday_avg.values,
    marker=dict(
        color=weekday_avg.values,
        colorscale='Blues'
    ),
    text=[f'${v:,.0f}' for v in weekday_avg.values],
    textposition='outside'
))

fig3.update_layout(
    template='plotly_dark',
    paper_bgcolor='#0d1117',
    plot_bgcolor='#131a24',
    font=dict(color='white'),
    height=450,
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=False
)

st.plotly_chart(fig3, width='stretch')

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<br>
<hr style='border:1px solid #1f2937;'>
<div style='text-align:center; color:#64748b; padding-bottom:20px;'>
Sales Intelligence Dashboard · Built with Streamlit & Plotly · v2.0
</div>
""", unsafe_allow_html=True)