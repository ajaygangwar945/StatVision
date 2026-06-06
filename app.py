import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import io

# ── Page Config ─────────────────────────────────────────
st.set_page_config(
    page_title="StatVision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f1117; }

    .hero-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #3a3a5c;
        border-radius: 12px; padding: 1.2rem;
        text-align: center; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-value {
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .metric-label { color: #aaa; font-size: 0.85rem; margin-top: 0.2rem; }

    .section-header {
        font-size: 1.4rem; font-weight: 600; color: #e0e0e0;
        border-left: 4px solid #667eea;
        padding-left: 0.8rem; margin: 1.5rem 0 1rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #667eea44;
        border-radius: 10px; padding: 1rem 1.2rem;
        margin: 0.5rem 0; color: #ccc; font-size: 0.95rem;
    }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 2px dashed #667eea;
        border-radius: 16px; padding: 2rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem 2rem; font-weight: 600;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,17,23,0.8)',
    font=dict(color='#e0e0e0', family='Inter'),
    xaxis=dict(gridcolor='#2a2a3e', linecolor='#3a3a5c'),
    yaxis=dict(gridcolor='#2a2a3e', linecolor='#3a3a5c'),
)
COLORS = px.colors.qualitative.Vivid

# ── Header ───────────────────────────────────────────────
st.markdown('<div class="hero-title">📊 CSV Analyzer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload any CSV — get instant stats, insights & beautiful charts</div>', unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    chart_height = st.slider("Chart Height (px)", 300, 700, 420, 20)
    max_categories = st.slider("Max categories in bar charts", 5, 20, 10)
    st.markdown("---")
    st.markdown("### 📁 Upload CSV")
    uploaded_file = st.file_uploader("", type=["csv"])
    st.markdown("---")
    st.caption("Built with Streamlit + Plotly")

# ── Main ─────────────────────────────────────────────────
if uploaded_file is None:
    # Landing state
    col1, col2, col3 = st.columns(3)
    for col, icon, title, desc in [
        (col1, "📤", "Upload", "Drop any CSV file"),
        (col2, "🔍", "Analyze", "Auto stats & insights"),
        (col3, "📈", "Visualize", "Interactive charts"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:2.5rem">{icon}</div>
                <div style="font-size:1.1rem;font-weight:600;color:#e0e0e0;margin:0.5rem 0">{title}</div>
                <div style="color:#888;font-size:0.9rem">{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.info("👈 Upload a CSV file from the sidebar to get started.")
    st.stop()

# ── Load Data ────────────────────────────────────────────
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

num_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()

# ── Top Metrics ──────────────────────────────────────────
st.markdown('<div class="section-header">📋 Dataset Overview</div>', unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
for col, val, label in [
    (m1, df.shape[0], "Rows"),
    (m2, df.shape[1], "Columns"),
    (m3, len(num_cols), "Numeric Cols"),
    (m4, len(cat_cols), "Text Cols"),
    (m5, int(df.isnull().sum().sum()), "Missing Values"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

# ── Data Preview ─────────────────────────────────────────
with st.expander("🔎 Preview Data", expanded=False):
    st.dataframe(df.head(20), use_container_width=True)

# ── Summary Stats ────────────────────────────────────────
if num_cols:
    with st.expander("📐 Summary Statistics", expanded=False):
        st.dataframe(df[num_cols].describe().round(3), use_container_width=True)

# ── Auto Insights ────────────────────────────────────────
st.markdown('<div class="section-header">💡 Auto Insights</div>', unsafe_allow_html=True)
insights = []
if df.isnull().sum().sum() > 0:
    insights.append(f"⚠️ {int(df.isnull().sum().sum())} missing values found across {int((df.isnull().sum()>0).sum())} columns.")
if num_cols:
    for c in num_cols:
        skew = df[c].skew()
        if abs(skew) > 1:
            insights.append(f"📐 **{c}** is {'right' if skew>0 else 'left'}-skewed (skewness: {skew:.2f}) — consider log transform.")
    corr = df[num_cols].corr()
    for i in range(len(num_cols)):
        for j in range(i+1, len(num_cols)):
            v = corr.iloc[i,j]
            if abs(v) > 0.75:
                insights.append(f"🔗 **{num_cols[i]}** & **{num_cols[j]}** are strongly correlated ({v:.2f}).")
if not insights:
    insights.append("✅ No obvious data issues detected. Looks clean!")
for ins in insights:
    st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)

# ── Charts ───────────────────────────────────────────────
if num_cols:
    st.markdown('<div class="section-header">📊 Distributions</div>', unsafe_allow_html=True)
    tab_cols = st.tabs([f"📈 {c}" for c in num_cols])
    for tab, col in zip(tab_cols, num_cols):
        with tab:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}",
                                   color_discrete_sequence=["#667eea"])
                fig.update_layout(**PLOTLY_THEME, height=chart_height)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.box(df, y=col, title=f"Box Plot — {col}",
                              color_discrete_sequence=["#f093fb"])
                fig2.update_layout(**PLOTLY_THEME, height=chart_height)
                st.plotly_chart(fig2, use_container_width=True)

if len(num_cols) >= 2:
    st.markdown('<div class="section-header">🔥 Correlation Heatmap</div>', unsafe_allow_html=True)
    corr_matrix = df[num_cols].corr().round(2)
    fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu_r",
                    title="Feature Correlation Matrix", aspect="auto")
    fig.update_layout(**PLOTLY_THEME, height=chart_height)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">🔵 Scatter Plot Explorer</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    x_col = sc1.selectbox("X axis", num_cols, index=0)
    y_col = sc2.selectbox("Y axis", num_cols, index=min(1, len(num_cols)-1))
    color_col = sc3.selectbox("Color by", ["None"] + cat_cols + num_cols)
    fig = px.scatter(df, x=x_col, y=y_col,
                     color=None if color_col == "None" else color_col,
                     title=f"{x_col} vs {y_col}",
                     color_continuous_scale="Viridis",
                     color_discrete_sequence=COLORS)
    fig.update_layout(**PLOTLY_THEME, height=chart_height)
    st.plotly_chart(fig, use_container_width=True)

if cat_cols and num_cols:
    st.markdown('<div class="section-header">📊 Category Analysis</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    cat_sel = b1.selectbox("Group by", cat_cols)
    num_sel = b2.selectbox("Metric", num_cols)
    grouped = df.groupby(cat_sel)[num_sel].mean().nlargest(max_categories).reset_index()
    fig = px.bar(grouped, x=cat_sel, y=num_sel,
                 title=f"Avg {num_sel} by {cat_sel}",
                 color=num_sel, color_continuous_scale="Viridis")
    fig.update_layout(**PLOTLY_THEME, height=chart_height)
    st.plotly_chart(fig, use_container_width=True)

# ── Download ─────────────────────────────────────────────
st.markdown('<div class="section-header">⬇️ Export</div>', unsafe_allow_html=True)
csv_out = df.describe().round(3).to_csv().encode("utf-8")
st.download_button("📥 Download Summary Stats as CSV", csv_out, "summary_stats.csv", "text/csv")
