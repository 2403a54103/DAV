import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import chardet

# ==========================================
# PAGE CONFIG & CLEAN LAYOUT STYLING
# ==========================================
st.set_page_config(page_title="Weather Trends Dashboard", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #e6f2ff !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 0rem !important; padding-left: 0rem !important; padding-right: 0rem !important; }
    [data-testid="stSidebar"] { background-color: #f2f6fa !important; }
    h1, h2, h3 { color: #08306B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LOAD CSV FILE
# ==========================================
file_name = "weather_trends.csv"

if not os.path.exists(file_name):
    st.error("❌ CSV file not found! Please place 'weather_trends.csv' in the same directory.")
    st.stop()

with open(file_name, "rb") as f:
    enc = chardet.detect(f.read())["encoding"] or "utf-8"

df = pd.read_csv(file_name, encoding=enc)

df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]

mapping = {
    "year": "Year", "month": "Month", "region": "Region",
    "temperature": "Temperature", "rainfall": "Rainfall", "humidity": "Humidity"
}
for c in df.columns:
    if c.lower() in mapping:
        df.rename(columns={c: mapping[c.lower()]}, inplace=True)

df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")
df["Region"] = df["Region"].astype(str).str.strip()
for c in ["Temperature", "Rainfall", "Humidity"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ==========================================
# HEADER BAR
# ==========================================
st.markdown("""
    <div style="
        background: linear-gradient(90deg, #00b4db, #0083b0);
        padding: 16px 0;
        text-align: center;
        color: white;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        margin-bottom: 0;
    ">
        <h1 style="margin:0;font-size:28px;">🌦 Weather Trends Dashboard</h1>
        <p style="margin:4px 0 0 0;font-size:16px;">
            📊 Analyze Temperature, Rainfall & Humidity patterns across regions over the years.
        </p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("⚙️ Visualization Controls")

years = sorted(df["Year"].dropna().unique())
regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
metrics_available = ["Temperature", "Rainfall", "Humidity"]

year_sel = st.sidebar.selectbox("Select Year", years, index=0)
region_sel = st.sidebar.selectbox("Select Region", regions, index=0)
metrics_sel = st.sidebar.multiselect("Select Metrics", metrics_available, default=["Temperature"])

chart_type = st.sidebar.selectbox("Chart Type", ["Line", "Bar", "Area", "Scatter", "Pie", "Heatmap"])
show_total = st.sidebar.checkbox("🌍 Show Entire Dataset")
generate = st.sidebar.button("🚀 Generate Visualization")

# ==========================================
# FILTER DATA FOR VISUALIZATION
# ==========================================
df_filtered = df[df["Year"] == year_sel]
if region_sel != "All":
    df_filtered = df_filtered[df_filtered["Region"] == region_sel]

# ==========================================
# SHOW ENTIRE DATASET
# ==========================================
if show_total:
    st.markdown("---")
    st.markdown("### 🌐 Complete Dataset Overview")
    st.dataframe(df, use_container_width=True)

# ==========================================
# VISUALIZATION SECTION
# ==========================================
if generate:

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Temperature (°C)", f"{df_filtered['Temperature'].mean():.2f}")
    col2.metric("Avg Rainfall (mm)", f"{df_filtered['Rainfall'].mean():.2f}")
    col3.metric("Avg Humidity (%)", f"{df_filtered['Humidity'].mean():.2f}")

    st.markdown("---")

    for metric in metrics_sel:
        st.markdown(f"### 📈 {chart_type} Chart — {metric} ({year_sel})")

        fig = None
        if chart_type == "Line":
            fig = px.line(df_filtered.sort_values("Month"), x="Month", y=metric, color="Region", markers=True)
        elif chart_type == "Bar":
            fig = px.bar(df_filtered, x="Region", y=metric, color="Region", barmode="group")
        elif chart_type == "Area":
            fig = px.area(df_filtered.sort_values("Month"), x="Month", y=metric, color="Region")
        elif chart_type == "Scatter":
            fig = px.scatter(df_filtered, x="Month", y=metric, size=metric, color="Region", hover_name="Region")
        elif chart_type == "Pie":
            avg = df_filtered.groupby("Region")[[metric]].mean().reset_index()
            fig = px.pie(avg, names="Region", values=metric)
        elif chart_type == "Heatmap":
            corr = df_filtered.select_dtypes(include="number").corr()
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
            fig = None

        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # INSIGHTS
    # ==========================================
    st.markdown("### 🔍 Insights")

    t_avg = df_filtered["Temperature"].mean()
    r_avg = df_filtered["Rainfall"].mean()
    h_avg = df_filtered["Humidity"].mean()

    insights = []
    if t_avg > 30:
        insights.append("🔥 High temperature this year — possible heatwave effects.")
    else:
        insights.append("🌤 Temperatures are within normal seasonal range.")
    if r_avg > 100:
        insights.append("🌧 Heavy rainfall patterns observed.")
    else:
        insights.append("☀ Low/Moderate rainfall this year.")
    if h_avg > 60:
        insights.append("💧 High humidity levels detected across regions.")
    else:
        insights.append("🌬 Humidity levels remain comfortable.")

    st.markdown(
        f"<div style='background:#DCEEFB;padding:12px;border-radius:10px;'>{'<br>'.join(insights)}</div>",
        unsafe_allow_html=True
    )
