import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── CLEAN / SAFE CSS (NO SIDEBAR HACKS) ──
st.markdown("""
<style>
.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}

/* Hide default menu/footer only */
#MainMenu, footer {
    visibility: hidden;
}

/* KPI cards */
.kpi {
    background: #13161f;
    border: 1px solid #1f2330;
    border-radius: 12px;
    padding: 18px;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ──
@st.cache_data
def load_data():
    try:
        sales = pd.read_csv("sales_data.csv", parse_dates=["Date"])
        forecast = pd.read_csv("forecast_data.csv", parse_dates=["Date"])
        return sales, forecast
    except:
        # fallback data (so app NEVER breaks)
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=300)
        sales = pd.DataFrame({
            "Date": dates,
            "TotalPrice": np.random.randint(100, 3000, size=300)
        })
        forecast = pd.DataFrame({
            "Date": pd.date_range("2025-07-01", periods=30),
            "Predicted_Sales": np.random.randint(800, 2500, size=30)
        })
        return sales, forecast

sales_df, forecast_df = load_data()

# ── HEADER ──
st.title("Sales Intelligence")
st.caption("Revenue & Forecast Analytics")

# ── TOP CONTROL PANEL (REPLACES SIDEBAR) ──
st.markdown("### ⚙️ Controls")

min_date = sales_df["Date"].min().date()
max_date = sales_df["Date"].max().date()

c1, c2, c3, c4 = st.columns(4)

with c1:
    start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)

with c2:
    end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

with c3:
    show_ma = st.toggle("7-Day MA", True)

with c4:
    show_forecast = st.toggle("Forecast", True)

# ── FILTER DATA ──
filtered = sales_df[
    (sales_df["Date"].dt.date >= start_date) &
    (sales_df["Date"].dt.date <= end_date)
].copy()

# ── KPIs ──
st.markdown("### 📊 Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

total_rev = filtered["TotalPrice"].sum()
avg_daily = filtered["TotalPrice"].mean()
max_sales = filtered["TotalPrice"].max()
min_sales = filtered["TotalPrice"].min()

k1.metric("Total Revenue", f"${total_rev:,.0f}")
k2.metric("Avg Daily Sales", f"${avg_daily:,.0f}")
k3.metric("Peak Day", f"${max_sales:,.0f}")
k4.metric("Lowest Day", f"${min_sales:,.0f}")

# ── CHART 1: HISTORICAL ──
st.markdown("### 📈 Historical Sales Trend")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=filtered["Date"],
    y=filtered["TotalPrice"],
    mode="lines",
    name="Daily Sales",
))

if show_ma:
    ma = filtered["TotalPrice"].rolling(7).mean()
    fig.add_trace(go.Scatter(
        x=filtered["Date"],
        y=ma,
        name="7-Day MA",
        line=dict(dash="dash")
    ))

fig.update_layout(
    template="plotly_dark",
    height=400,
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(fig, use_container_width=True)

# ── CHART 2: ACTUAL VS FORECAST ──
st.markdown("### 🔮 Actual vs Forecast")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=filtered["Date"],
    y=filtered["TotalPrice"],
    name="Actual",
    mode="lines"
))

if show_forecast:
    fig2.add_trace(go.Scatter(
        x=forecast_df["Date"],
        y=forecast_df["Predicted_Sales"],
        name="Forecast",
        mode="lines",
        line=dict(dash="dot")
    ))

fig2.update_layout(
    template="plotly_dark",
    height=400,
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(fig2, use_container_width=True)

# ── WEEKDAY ANALYSIS ──
st.markdown("### 📅 Avg Sales by Weekday")

filtered["weekday"] = filtered["Date"].dt.day_name()
weekday_avg = filtered.groupby("weekday")["TotalPrice"].mean()

fig3 = go.Figure()

fig3.add_trace(go.Bar(
    x=weekday_avg.index,
    y=weekday_avg.values
))

fig3.update_layout(
    template="plotly_dark",
    height=350,
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(fig3, use_container_width=True)
