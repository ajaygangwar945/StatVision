import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

# ==============================================================================
# Asset Paths & Page Configuration
# ==============================================================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(APP_DIR, "assets", "logo.svg")

# Safely read and base64-encode the logo SVG
b64_svg = ""
if os.path.exists(LOGO_PATH):
    try:
        with open(LOGO_PATH, "r", encoding="utf-8") as f:
            svg_text = f.read()
            b64_svg = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
    except Exception:
        b64_svg = ""

# Single unified logo asset used everywhere (browser favicon, hero header, and sidebar)
favicon = LOGO_PATH if os.path.exists(LOGO_PATH) else "📊"

st.set_page_config(
    page_title="StatVision",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# Theme State Initialization & Dynamic Resolution
# ==============================================================================
if "theme_mode" not in st.session_state or st.session_state["theme_mode"] not in ["Light ☀️", "Dark 🌙"]:
    st.session_state["theme_mode"] = "Light ☀️"

current_theme = st.session_state["theme_mode"]

# Generate theme-specific CSS variables & Plotly color palettes
if current_theme == "Dark 🌙":
    active_theme_css = """
    :root, [data-theme="dark"], [data-theme="light"], html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        --background-color: #0e1117 !important;
        --secondary-background-color: #161b26 !important;
        --text-color: #f8fafc !important;
        --primary-color: #3b82f6 !important;
        --card-bg: #1e2433 !important;
        --card-border: #334155 !important;
        --muted-text: #94a3b8 !important;
        --pill-bg: rgba(59, 130, 246, 0.16) !important;
        --pill-border: rgba(59, 130, 246, 0.35) !important;
        --shadow-color: rgba(0, 0, 0, 0.45) !important;
        color-scheme: dark !important;
        background-color: #161b26 !important;
        color: #f8fafc !important;
    }
    .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #161b26 !important;
        color: #f8fafc !important;
    }
    header[data-testid="stHeader"] {
        background-color: #0e1117 !important;
        border-bottom: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        border-right: 1px solid #334155 !important;
    }
    """
    plotly_font_color = "#f8fafc"
    plotly_grid_color = "rgba(255, 255, 255, 0.1)"
    plotly_template = "plotly_dark"
    plotly_streamlit_theme = None
    js_theme_attr = "dark"
elif current_theme == "Light ☀️":
    active_theme_css = """
    :root, [data-theme="dark"], [data-theme="light"], html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        --background-color: #ffffff !important;
        --secondary-background-color: #f8fafc !important;
        --text-color: #0f172a !important;
        --primary-color: #2563eb !important;
        --card-bg: #ffffff !important;
        --card-border: #e2e8f0 !important;
        --muted-text: #475569 !important;
        --pill-bg: #eff6ff !important;
        --pill-border: #bfdbfe !important;
        --shadow-color: rgba(0, 0, 0, 0.04) !important;
        color-scheme: light !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    """
    plotly_font_color = "#0f172a"
    plotly_grid_color = "rgba(0, 0, 0, 0.06)"
    plotly_template = "plotly_white"
    plotly_streamlit_theme = "streamlit"
    js_theme_attr = "light"
else:  # System ⚙️
    active_theme_css = """
    :root {
        --background-color: #ffffff;
        --secondary-background-color: #f8fafc;
        --text-color: #0f172a;
        --primary-color: #2563eb;
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --muted-text: #475569;
        --pill-bg: #eff6ff;
        --pill-border: #bfdbfe;
        --shadow-color: rgba(0, 0, 0, 0.04);
        color-scheme: light;
    }
    @media (prefers-color-scheme: dark) {
        :root, html, body, .stApp, [data-testid="stAppViewContainer"], .main {
            --background-color: #0e1117 !important;
            --secondary-background-color: #161b26 !important;
            --text-color: #f8fafc !important;
            --primary-color: #3b82f6 !important;
            --card-bg: #1e2433 !important;
            --card-border: #334155 !important;
            --muted-text: #94a3b8 !important;
            --pill-bg: rgba(59, 130, 246, 0.16) !important;
            --pill-border: rgba(59, 130, 246, 0.35) !important;
            --shadow-color: rgba(0, 0, 0, 0.45) !important;
            color-scheme: dark !important;
            background-color: #161b26 !important;
            color: #f8fafc !important;
        }
        .stApp, [data-testid="stAppViewContainer"], .main {
            background-color: #161b26 !important;
            color: #f8fafc !important;
        }
        header[data-testid="stHeader"] {
            background-color: #0e1117 !important;
            border-bottom: 1px solid #334155 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #0e1117 !important;
            border-right: 1px solid #334155 !important;
        }
    }
    """
    plotly_font_color = "#0f172a"
    plotly_grid_color = "rgba(0, 0, 0, 0.06)"
    plotly_template = "plotly_white"
    plotly_streamlit_theme = "streamlit"
    js_theme_attr = "system"

# Synchronize parent document attribute
components.html(f"""
<script>
    (function() {{
        const parentDoc = window.parent.document;
        const mode = "{js_theme_attr}";
        function applyDocTheme() {{
            try {{
                let targetTheme = mode;
                if (mode === "system") {{
                    targetTheme = (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
                }}
                if (parentDoc.documentElement.getAttribute('data-theme') !== targetTheme) {{
                    parentDoc.documentElement.setAttribute('data-theme', targetTheme);
                }}
            }} catch (e) {{}}
        }}
        applyDocTheme();
        setInterval(applyDocTheme, 400);
    }})();
</script>
""", height=0, width=0)

# Dynamic Active Theme Tokens
st.markdown(f"<style>{active_theme_css}</style>", unsafe_allow_html=True)

# ==============================================================================
# Master Responsive Styling & Appearance Controller
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* =========================================================================
       Appearance Mode Segmented Control (Sidebar: Light & Dark)
       ========================================================================= */
    div[data-testid="stRadio"] {
        margin: 0 0 1rem 0 !important;
        width: 100% !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 4px !important;
        background-color: var(--secondary-background-color) !important;
        padding: 4px !important;
        border-radius: 10px !important;
        border: 1px solid var(--card-border) !important;
        box-shadow: inset 0 1px 2px var(--shadow-color) !important;
        width: 100% !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
        flex: 1 1 0 !important;
        margin: 0 !important;
        padding: 7px 10px !important;
        border-radius: 7px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        position: relative !important;
    }
    /* Hide the radio dot safely */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: var(--muted-text) !important;
        margin: 0 !important;
        white-space: nowrap !important;
        text-align: center !important;
        letter-spacing: -0.01em !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover:not(:has(input:checked)) {
        background-color: var(--card-bg) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover:not(:has(input:checked)) [data-testid="stMarkdownContainer"] p {
        color: var(--text-color) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Top Navbar/Header Clean & Fully Visible (No Square Borders) */
    header[data-testid="stHeader"] {
        background-color: var(--background-color) !important;
        border-bottom: 1px solid var(--card-border) !important;
        box-shadow: 0 1px 3px var(--shadow-color) !important;
    }
    header[data-testid="stHeader"] * {
        color: var(--text-color) !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* Header Navbar & Toolbar: 100% Visible & Elegant */
    .eyeqlp53,
    .st-emotion-cache-1b2ybts,
    .ex0cdmw0,
    header [data-testid="stToolbar"],
    [data-testid="stToolbar"],
    [data-testid="stActionToolbar"],
    div[data-testid="stToolbar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background: transparent !important;
        border: none !important;
    }

    /* Header Buttons & Text: Visible with No Button Border Box */
    .eyeqlp53 button,
    .st-emotion-cache-1b2ybts button,
    .ex0cdmw0 button,
    button.ef3psqc5,
    button.ef3psqc6,
    .st-emotion-cache-o7ec7j,
    .st-emotion-cache-1m4tft7,
    button[kind="header"],
    button[aria-label="Menu"],
    button[aria-label="Options"],
    header button,
    [data-testid="stHeader"] button,
    #MainMenu,
    #MainMenu button,
    [data-testid="stBaseButton-header"],
    [data-testid="baseButton-header"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        color: var(--text-color) !important;
        background: transparent !important;
        background-color: transparent !important;
        border: 0px none transparent !important;
        border-width: 0px !important;
        border-style: none !important;
        border-color: transparent !important;
        outline: none !important;
        outline-width: 0px !important;
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        visibility: visible !important;
    }

    .eyeqlp53 button:hover,
    .eyeqlp53 button:focus,
    .st-emotion-cache-1b2ybts button:hover,
    .st-emotion-cache-1b2ybts button:focus,
    button.ef3psqc5:hover,
    button.ef3psqc5:focus,
    .st-emotion-cache-o7ec7j:hover,
    .st-emotion-cache-o7ec7j:focus,
    button[kind="header"]:hover,
    button[kind="header"]:focus,
    button[aria-label="Menu"]:hover,
    button[aria-label="Menu"]:focus,
    header button:hover,
    header button:focus {
        border: 0px none transparent !important;
        outline: none !important;
        box-shadow: none !important;
        background: rgba(125, 125, 125, 0.12) !important;
        border-radius: 6px !important;
    }

    /* STRICTLY ELIMINATE THE SQUARE BORDER FROM SVG:
       Material Icon SVGs contain a bounding box path <path fill="none" d="M0 0h24v24H0V0z">.
       Setting stroke on the SVG causes that box to stroke into a square border.
       We set stroke: none and hide any path with fill="none". */
    header button svg,
    button[kind="header"] svg,
    button[aria-label="Menu"] svg,
    button[data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        fill: var(--text-color) !important;
        stroke: none !important;
    }

    header button svg path,
    button[kind="header"] svg path,
    button[aria-label="Menu"] svg path {
        stroke: none !important;
    }

    header button svg path[fill="none"],
    button[kind="header"] svg path[fill="none"],
    button[aria-label="Menu"] svg path[fill="none"] {
        display: none !important;
        stroke: none !important;
    }

    /* Dynamic Canvas (Adapts to Light / Dark / Custom) */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--secondary-background-color) !important;
        background-image: none !important;
        color: var(--text-color) !important;
    }

    /* Sidebar Dynamic Theme */
    section[data-testid="stSidebar"] {
        background-color: var(--background-color) !important;
        border-right: 1px solid var(--card-border) !important;
        box-shadow: 1px 0 3px var(--shadow-color) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-color) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: var(--muted-text) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: var(--card-border) !important;
    }

    /* Universal Form & Widget Label Visibility */
    label, .stWidgetLabel, .stWidgetLabel p, .stWidgetLabel span {
        color: var(--text-color) !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    /* Sliders: Dynamic Accent Thumb, Clear Values */
    div[data-testid="stSlider"] {
        background-color: transparent !important;
    }
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] label * {
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--primary-color) !important;
        border: 2px solid var(--background-color) !important;
        box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4) !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"],
    div[data-testid="stSlider"] div[data-baseweb="slider"] div[style*="background-color: #ff4b4b"] {
        background-color: var(--primary-color) !important;
    }
    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        font-family: 'Fira Code', monospace !important;
        background: transparent !important;
    }
    div[data-testid="stSliderTickBarMin"],
    div[data-testid="stSliderTickBarMax"],
    div[data-testid="stTickBar"] span,
    div[data-testid="stSlider"] [data-testid="stTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
        color: var(--muted-text) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        font-family: 'Fira Code', monospace !important;
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Selectbox Dropdowns */
    div[data-baseweb="select"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px var(--shadow-color) !important;
    }
    div[data-baseweb="select"] * {
        color: var(--text-color) !important;
        background-color: var(--card-bg) !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: var(--pill-bg) !important;
        color: var(--primary-color) !important;
    }

    /* File Uploader Dropzone */
    div[data-testid="stFileUploader"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    div[data-testid="stFileUploader"] section,
    div[data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--card-bg) !important;
        border: 2px dashed var(--pill-border) !important;
        border-radius: 10px !important;
        padding: 1.2rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stFileUploader"] section:hover,
    [data-testid="stFileUploaderDropzone"]:hover {
        background-color: var(--pill-bg) !important;
        border-color: var(--primary-color) !important;
    }
    div[data-testid="stFileUploader"] section * {
        color: var(--text-color) !important;
        background-color: transparent !important;
    }
    div[data-testid="stFileUploader"] section span {
        color: var(--text-color) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stFileUploader"] section small {
        color: var(--muted-text) !important;
        font-size: 0.8rem !important;
    }
    div[data-testid="stFileUploader"] section svg {
        fill: var(--primary-color) !important;
        color: var(--primary-color) !important;
    }
    div[data-testid="stFileUploader"] section button {
        background-color: var(--pill-bg) !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--pill-border) !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 0.35rem 0.85rem !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stFileUploader"] section button:hover {
        border-color: var(--primary-color) !important;
    }

    /* Navigation Tabs */
    button[data-baseweb="tab"] {
        color: var(--muted-text) !important;
        font-weight: 600 !important;
        background-color: transparent !important;
        padding: 0.5rem 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--primary-color) !important;
    }

    /* Accordion Expanders */
    div[data-testid="stExpander"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px var(--shadow-color) !important;
    }
    div[data-testid="stExpander"] details summary {
        color: var(--text-color) !important;
        font-weight: 600 !important;
        background-color: var(--card-bg) !important;
    }
    div[data-testid="stExpander"] details summary svg {
        fill: var(--text-color) !important;
    }

    /* =========================================================================
       Checkbox Elements & Tick Mark High-Contrast Visibility
       ========================================================================= */
    div[data-testid="stCheckbox"],
    label[data-baseweb="checkbox"] {
        background-color: transparent !important;
        cursor: pointer !important;
    }

    /* Checkbox Label Text & Wrapper: Strictly Transparent, Never Highlighted */
    div[data-testid="stCheckbox"] label > div,
    div[data-testid="stCheckbox"] input + div,
    div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"],
    div[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"],
    div[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p,
    label[data-baseweb="checkbox"] [data-testid="stMarkdownContainer"],
    label[data-baseweb="checkbox"] [data-testid="stMarkdownContainer"] p,
    label[data-baseweb="checkbox"] p {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text-color) !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }

    /* Checkbox Square Box (span) - Unchecked State */
    div[data-testid="stCheckbox"] label:has(input:not(:checked)) > span:first-child,
    label[data-baseweb="checkbox"]:has(input:not(:checked)) > span:first-child {
        background-color: var(--card-bg, #ffffff) !important;
        border: 1.5px solid var(--muted-text, #94a3b8) !important;
        border-radius: 4px !important;
        background-image: none !important;
        transition: all 0.15s ease !important;
    }

    /* Checkbox Square Box (span) - Checked State */
    div[data-testid="stCheckbox"] label:has(input:checked) > span:first-child,
    label[data-baseweb="checkbox"]:has(input:checked) > span:first-child {
        background-color: var(--primary-color, #2563eb) !important;
        border: 1.5px solid var(--primary-color, #2563eb) !important;
        border-radius: 4px !important;
        background-image: url("data:image/svg+xml,%3Csvg%20width%3D%2217%22%20height%3D%2213%22%20viewBox%3D%220%200%2017%2013%22%20fill%3D%22none%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M6.50002%2012.6L0.400024%206.60002L2.60002%204.40002L6.50002%208.40002L13.9%200.900024L16.1%203.10002L6.50002%2012.6Z%22%20fill%3D%22%23ffffff%22%2F%3E%3C%2Fsvg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 11px 11px !important;
        transition: all 0.15s ease !important;
    }

    /* Hover effect on checkbox box */
    div[data-testid="stCheckbox"] label:hover > span:first-child,
    label[data-baseweb="checkbox"]:hover > span:first-child {
        border-color: var(--primary-color, #2563eb) !important;
    }

    /* Fallback support for direct SVG checkmarks */
    label[data-baseweb="checkbox"] svg,
    div[data-testid="stCheckbox"] svg {
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        fill: #ffffff !important;
        color: #ffffff !important;
        stroke: #ffffff !important;
    }
    label[data-baseweb="checkbox"] svg path,
    div[data-testid="stCheckbox"] svg path {
        fill: #ffffff !important;
        color: #ffffff !important;
        stroke: #ffffff !important;
        stroke-width: 0.8px !important;
    }

    /* Tables & DataFrames */
    div[data-testid="stDataFrame"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stDataFrame"] * {
        color: var(--text-color) !important;
    }

    /* Modal Dialogs */
    div[role="dialog"] {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
    }
    div[role="dialog"] * {
        color: var(--text-color) !important;
    }

    /* Typography */
    h1, h2, h3, h4, .math-header {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-color) !important;
        letter-spacing: -0.02em;
    }
    p, span {
        color: var(--text-color);
    }
    code, .math-code {
        font-family: 'Fira Code', monospace !important;
    }

    /* Hero Branding Card */
    .hero-container {
        text-align: center;
        padding: 1.6rem 1.2rem 1.7rem 1.2rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--card-border);
        background: var(--card-bg);
        border-radius: 16px;
        box-shadow: 0 1px 4px var(--shadow-color);
    }
    .hero-brand {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.9rem;
        margin-bottom: 0.3rem;
    }
    .hero-logo-img {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28);
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--text-color);
        letter-spacing: -0.03em;
        line-height: 1;
        font-family: 'Space Grotesk', sans-serif;
    }
    .hero-title span {
        color: var(--primary-color);
    }
    .hero-subtitle {
        color: var(--muted-text);
        font-size: 1.05rem;
        font-weight: 400;
        max-width: 620px;
        margin: 0.4rem auto 0.8rem auto;
        line-height: 1.5;
        text-align: center;
    }
    .math-pill-row {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .math-pill {
        font-family: 'Fira Code', monospace;
        background: var(--pill-bg) !important;
        border: 1px solid var(--pill-border) !important;
        color: var(--primary-color) !important;
        font-size: 0.82rem !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px var(--shadow-color) !important;
    }

    /* Section Headers */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-color);
        margin: 2.2rem 0 1rem 0;
        padding: 0.45rem 0.85rem;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-left: 4px solid var(--primary-color);
        border-radius: 6px;
        box-shadow: 0 1px 3px var(--shadow-color);
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-idx {
        font-family: 'Fira Code', monospace;
        font-size: 0.82rem;
        color: var(--primary-color);
        background: var(--pill-bg);
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        border: 1px solid var(--pill-border);
        font-weight: 600;
    }

    /* Metric Cards */
    .metric-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 10px;
        padding: 1.2rem 1rem;
        text-align: center;
        position: relative;
        box-shadow: 0 1px 3px var(--shadow-color);
        transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary-color);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.2);
    }
    .metric-sym {
        position: absolute;
        top: 0.5rem;
        right: 0.7rem;
        font-family: 'Fira Code', monospace;
        font-size: 0.85rem;
        color: var(--muted-text);
        font-weight: 600;
    }
    .metric-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--primary-color);
        line-height: 1.2;
    }
    .metric-lbl {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--muted-text);
        margin-top: 0.2rem;
    }

    /* Insight Alert Boxes */
    .insight-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-left: 4px solid var(--primary-color);
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.92rem;
        color: var(--text-color);
        display: flex;
        align-items: center;
        gap: 0.8rem;
        box-shadow: 0 1px 2px var(--shadow-color);
    }
    .insight-pill {
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        white-space: nowrap;
    }
    .pill-warning {
        background-color: rgba(245, 158, 11, 0.16);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .pill-info {
        background-color: var(--pill-bg);
        color: var(--primary-color);
        border: 1px solid var(--pill-border);
    }
    .pill-danger {
        background-color: rgba(239, 68, 68, 0.16);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .pill-success {
        background-color: rgba(16, 185, 129, 0.16);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    /* Action Buttons */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        border: 1px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.4rem !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35) !important;
    }

    /* Math Formula Callout */
    .formula-callout {
        background-color: var(--card-bg);
        border: 1px solid var(--pill-border);
        border-left: 4px solid var(--primary-color);
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-top: 0.6rem;
        font-family: 'Fira Code', monospace;
        color: var(--primary-color);
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 1px 2px var(--shadow-color);
        overflow-x: auto;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch;
    }

    /* =========================================================================
       Comprehensive Responsive Design System (Mobile, Tablet & Desktop)
       ========================================================================= */

    /* Fluid Base Container */
    .main .block-container {
        max-width: 1360px;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        transition: padding 0.2s ease;
    }

    /* Responsive Grid for Section 1 Topology Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.85rem;
        margin-bottom: 1.5rem;
        width: 100%;
    }

    /* Responsive Grid for Landing State Cards */
    .landing-card-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        width: 100%;
    }

    /* Checkbox Desktop Alignment in Form Columns */
    div[data-testid="stColumn"] div[data-testid="stCheckbox"] {
        margin-top: 1.85rem;
    }

    /* =========================================================================
       TABLET BREAKPOINT: <= 1024px (iPads, Surface, Landscape Tablets)
       ========================================================================= */
    @media (max-width: 1024px) {
        .main .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 4rem !important;
        }

        .metrics-grid {
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 0.75rem !important;
        }

        .hero-title {
            font-size: 2.2rem !important;
        }

        .hero-subtitle {
            font-size: 0.98rem !important;
        }

        .metric-val {
            font-size: 1.85rem !important;
        }

        /* 4-column blocks wrap to clean 2x2 grid on tablet */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.85rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: calc(50% - 0.5rem) !important;
            flex: 1 1 calc(50% - 0.5rem) !important;
        }
        div[data-testid="stColumn"] div[data-testid="stCheckbox"] {
            margin-top: 0.5rem !important;
        }

        .landing-card-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 1rem !important;
        }
    }

    /* =========================================================================
       MOBILE & PHABLET BREAKPOINT: <= 768px (Phones, Small Tablets, Portrait)
       ========================================================================= */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 3.5rem !important;
            padding-bottom: 3.5rem !important;
        }

        .hero-container {
            padding: 1.25rem 0.85rem !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
        }

        .hero-brand {
            gap: 0.65rem !important;
        }

        .hero-logo-img {
            width: 42px !important;
            height: 42px !important;
            border-radius: 10px !important;
        }

        .hero-title {
            font-size: 1.9rem !important;
        }

        .hero-subtitle {
            font-size: 0.9rem !important;
            margin: 0.3rem auto 0.65rem auto !important;
            line-height: 1.45 !important;
            text-align: center !important;
        }

        .math-pill-row {
            gap: 0.4rem !important;
            justify-content: center !important;
        }

        .math-pill {
            font-size: 0.74rem !important;
            padding: 0.2rem 0.6rem !important;
        }

        .section-header {
            font-size: 1.1rem !important;
            padding: 0.4rem 0.65rem !important;
            margin: 1.6rem 0 0.85rem 0 !important;
            flex-wrap: wrap !important;
        }

        .section-idx {
            font-size: 0.75rem !important;
            padding: 0.12rem 0.45rem !important;
        }

        .metrics-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 0.65rem !important;
        }

        .metric-card {
            padding: 0.95rem 0.75rem !important;
            border-radius: 8px !important;
        }

        .metric-val {
            font-size: 1.6rem !important;
        }

        .metric-sym {
            font-size: 0.75rem !important;
            top: 0.4rem !important;
            right: 0.5rem !important;
        }

        .metric-lbl {
            font-size: 0.78rem !important;
        }

        /* Univariate & Tab side-by-side charts stack cleanly on mobile */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.75rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }

        /* Tabs horizontal smooth touch scroll on mobile */
        div[data-baseweb="tab-list"],
        div[role="tablist"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            scrollbar-width: thin !important;
            -webkit-overflow-scrolling: touch !important;
            padding-bottom: 4px !important;
        }
        div[data-baseweb="tab-list"] button,
        div[role="tablist"] button {
            white-space: nowrap !important;
            padding: 0.4rem 0.75rem !important;
            font-size: 0.85rem !important;
        }

        .insight-card {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 0.4rem !important;
            padding: 0.75rem 0.85rem !important;
            font-size: 0.88rem !important;
        }

        .formula-callout {
            font-size: 0.8rem !important;
            padding: 0.6rem 0.8rem !important;
        }

        .landing-card-grid {
            grid-template-columns: 1fr !important;
            gap: 0.85rem !important;
        }

        /* Full-width touch tap targets for mobile action buttons */
        .stButton > button,
        div[data-testid="stDownloadButton"] > button {
            width: 100% !important;
            padding: 0.65rem 1rem !important;
            font-size: 0.95rem !important;
            text-align: center !important;
        }

        /* Scale Plotly modebar so it does not overlap chart titles */
        .js-plotly-plot .plotly .modebar {
            transform: scale(0.8) !important;
            transform-origin: top right !important;
        }
    }

    /* =========================================================================
       NARROW MOBILE BREAKPOINT: <= 420px (Compact Smartphones)
       ========================================================================= */
    @media (max-width: 420px) {
        .main .block-container {
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-top: 3rem !important;
        }

        .hero-title {
            font-size: 1.65rem !important;
        }

        .hero-subtitle {
            font-size: 0.84rem !important;
        }

        .metrics-grid {
            grid-template-columns: 1fr !important;
            gap: 0.55rem !important;
        }

        .metric-val {
            font-size: 1.5rem !important;
        }

        .section-header {
            font-size: 0.98rem !important;
            padding: 0.35rem 0.5rem !important;
        }

        .math-pill {
            font-size: 0.7rem !important;
            padding: 0.18rem 0.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# Cohesive Dynamic Plotly Theme (Transparent Canvas, Adapts to Light & Dark)
PLOTLY_THEME = dict(
    template=plotly_template,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', size=12, color=plotly_font_color),
    title=dict(font=dict(size=14, family='Space Grotesk, sans-serif', color=plotly_font_color)),
    margin=dict(l=35, r=20, t=45, b=40)
)
MATH_PALETTE = ["#2563eb", "#0284c7", "#0d9488", "#7c3aed", "#d97706", "#dc2626"]

# ==============================================================================
# Header with Safe Base64 SVG Logo
# ==============================================================================
logo_img_tag = f'<img src="data:image/svg+xml;base64,{b64_svg}" class="hero-logo-img" alt="StatVision Logo" />' if b64_svg else '📊'

st.markdown(f"""
<div class="hero-container">
    <div class="hero-brand">
        {logo_img_tag}
        <div class="hero-title">Stat<span>Vision</span></div>
    </div>
    <div class="hero-subtitle">
        Mathematical Exploratory Data Analysis & Quantitative Intelligence Engine
    </div>
    <div class="math-pill-row">
        <span class="math-pill">Matrix: N &times; p</span>
        <span class="math-pill">Mean: &mu; = E[X]</span>
        <span class="math-pill">Std Dev: &sigma;</span>
        <span class="math-pill">Pearson: r &isin; [-1, 1]</span>
        <span class="math-pill">Quantiles: Q1, Q2, Q3</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# Sidebar Controls & File Ingestion
# ==============================================================================
with st.sidebar:
    sidebar_logo_img = f'<img src="data:image/svg+xml;base64,{b64_svg}" style="width: 38px; height: 38px; border-radius: 8px; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.22);" alt="Logo" />' if b64_svg else '📊'
    sidebar_brand = f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.9rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--card-border);">
        {sidebar_logo_img}
        <span style="font-size: 1.35rem; font-weight: 700; color: var(--text-color); letter-spacing: -0.02em; font-family: 'Space Grotesk', sans-serif;">Stat<span style="color: var(--primary-color);">Vision</span></span>
    </div>
    """
    st.markdown(sidebar_brand, unsafe_allow_html=True)
    
    # In-App Appearance Mode Switcher (Sidebar: Light & Dark)
    st.markdown("<p style='font-size: 0.76rem; font-weight: 700; color: var(--muted-text); margin: 0 0 0.35rem 0; text-transform: uppercase; letter-spacing: 0.08em;'>Appearance Mode</p>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Appearance Mode",
        options=["Light ☀️", "Dark 🌙"],
        index=0 if current_theme == "Light ☀️" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="theme_mode"
    )
    st.markdown("<div style='margin-bottom: 0.85rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("### Controls")
    chart_height = st.slider("Chart Height (px)", min_value=320, max_value=600, value=380, step=20)
    max_categories = st.slider("Max Categories in Charts", min_value=5, max_value=20, value=10)
    corr_threshold = st.slider("Correlation Sensitivity (|r|)", min_value=0.5, max_value=0.95, value=0.75, step=0.05)
    
    st.markdown("---")
    st.markdown("### Data Ingestion")
    uploaded_file = st.file_uploader("Upload CSV Matrix", type=["csv"], help="Upload any standard CSV file to analyze")
    
    use_sample = False
    if uploaded_file is None:
        st.markdown("<p style='text-align: center; color: var(--muted-text); font-size: 0.85rem; margin: 0.5rem 0;'>— or load benchmark sample —</p>", unsafe_allow_html=True)
        sample_choice = st.selectbox("Benchmark Dataset", [
            "None",
            "Iris Morphometrics (p=4, N=150)",
            "Hospitality Economics (p=6, N=244)"
        ])
        if sample_choice != "None":
            use_sample = True
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: var(--muted-text); font-size: 0.85rem; font-weight: 500;'>• StatVision •</div>", unsafe_allow_html=True)

# ==============================================================================
# Data Loading
# ==============================================================================
@st.cache_data
def load_sample_data(name):
    if "Iris" in name:
        return px.data.iris()
    elif "Hospitality" in name or "Tips" in name:
        return px.data.tips()
    return None

df = None
dataset_name = ""

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        dataset_name = uploaded_file.name
    except Exception as e:
        st.error(f"Could not read the uploaded CSV matrix: {e}")
        st.stop()
elif use_sample:
    df = load_sample_data(sample_choice)
    dataset_name = sample_choice

# ==============================================================================
# Empty Landing State
# ==============================================================================
if df is None:
    st.markdown("""
    <div style="max-width: 850px; margin: 2rem auto;">
        <div class="landing-card-grid">
            <div class="metric-card" style="padding: 1.8rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-color); margin-bottom: 0.3rem;">1. Ingest Matrix</div>
                <div style="font-size: 0.88rem; color: var(--muted-text); line-height: 1.5;">Drop any tabular dataset or CSV into the sidebar.</div>
            </div>
            <div class="metric-card" style="padding: 1.8rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📐</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-color); margin-bottom: 0.3rem;">2. Compute Moments</div>
                <div style="font-size: 0.88rem; color: var(--muted-text); line-height: 1.5;">Automatic computation of Mean &mu;, Variance &sigma;&sup2;, and Pearson correlation r.</div>
            </div>
            <div class="metric-card" style="padding: 1.8rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-color); margin-bottom: 0.3rem;">3. Graph & Regress</div>
                <div style="font-size: 0.88rem; color: var(--muted-text); line-height: 1.5;">Explore probability histograms, correlation heatmaps, and OLS regression lines.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Upload your CSV matrix from the sidebar or choose a benchmark dataset to begin.")
    st.stop()

# ==============================================================================
# Column Identification
# ==============================================================================
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
total_rows, total_cols = df.shape
total_nulls = int(df.isnull().sum().sum())

# ==============================================================================
# § 1: Dataset Topology & Dimensions
# ==============================================================================
st.markdown('''
<div class="section-header">
    <span class="section-idx">&sect; 1</span>
    <span>Dataset Topology & Dimensions</span>
</div>
''', unsafe_allow_html=True)

metrics_items = [
    ("N", f"{total_rows:,}", "Observations (Rows)"),
    ("p", f"{total_cols:,}", "Dimensions (Cols)"),
    ("&real;", f"{len(num_cols)}", "Numeric Features"),
    ("S", f"{len(cat_cols)}", "Categorical Factors"),
    ("&empty;", f"{total_nulls:,}", "Missing Values")
]
cards_html = "".join([
    f'''<div class="metric-card">
        <span class="metric-sym">{sym}</span>
        <div class="metric-val">{val}</div>
        <div class="metric-lbl">{label}</div>
    </div>'''
    for sym, val, label in metrics_items
])
st.markdown(f'<div class="metrics-grid">{cards_html}</div>', unsafe_allow_html=True)

# ==============================================================================
# § 2: Mathematical Summary & Moments
# ==============================================================================
st.markdown('''
<div class="section-header">
    <span class="section-idx">&sect; 2</span>
    <span>Mathematical Summary & Moments</span>
</div>
''', unsafe_allow_html=True)

with st.expander("View Sample Vectors (First 20 Rows)", expanded=False):
    st.dataframe(df.head(20), use_container_width=True)

if num_cols:
    with st.expander("Moments & Five-Number Summary Table (&mu;, &sigma;, Q)", expanded=True):
        summary_table = df[num_cols].describe().T
        summary_table["std_error"] = summary_table["std"] / np.sqrt(summary_table["count"])
        
        summary_table = summary_table[[
            "count", "mean", "std", "std_error", "min", "25%", "50%", "75%", "max"
        ]].rename(columns={
            "count": "Sample n",
            "mean": "Mean μ",
            "std": "Std Dev σ",
            "std_error": "Std Error SE",
            "min": "Min (x₀)",
            "25%": "Q₁ (25%)",
            "50%": "Median Q₂",
            "75%": "Q₃ (75%)",
            "max": "Max (xₙ)"
        }).round(3)
        st.dataframe(summary_table, use_container_width=True)

# ==============================================================================
# § 3: Statistical Inferences & Diagnostics
# ==============================================================================
st.markdown('''
<div class="section-header">
    <span class="section-idx">&sect; 3</span>
    <span>Statistical Inferences & Diagnostics</span>
</div>
''', unsafe_allow_html=True)

insights = []

# Missing values check
if total_nulls > 0:
    null_summary = df.isnull().sum()[df.isnull().sum() > 0]
    detail = ", ".join([f"<b>{col}</b> ({cnt})" for col, cnt in null_summary.items()])
    insights.append((
        "pill-danger",
        "NULL ~ &empty;",
        f"Missing values detected in vectors: {detail} (Total {total_nulls} null entries)."
    ))

# Skewness check
if num_cols:
    for col in num_cols:
        skew_val = df[col].skew()
        if abs(skew_val) > 1.0:
            dir_text = "right-skewed (positive tail)" if skew_val > 0 else "left-skewed (negative tail)"
            insights.append((
                "pill-warning",
                "SKEW ~ &gamma;1",
                f"Feature <b>{col}</b> is {dir_text} (skewness = {skew_val:.2f}). Consider a logarithmic transform."
            ))

# Correlation check
if len(num_cols) >= 2:
    corr_matrix = df[num_cols].corr()
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            r = corr_matrix.iloc[i, j]
            if abs(r) >= corr_threshold:
                rel_type = "positive" if r > 0 else "negative"
                insights.append((
                    "pill-info",
                    "CORR ~ r",
                    f"Strong {rel_type} linear dependence between <b>{num_cols[i]}</b> and <b>{num_cols[j]}</b> (r = {r:.2f} &ge; {corr_threshold:.2f})."
                ))

if not insights:
    insights.append((
        "pill-success",
        "CONVERGED",
        "Empirical sample matrix verified: No abnormal skewness, excessive collinearity, or missing values."
    ))

for pill_class, pill_text, message in insights:
    st.markdown(f"""
    <div class="insight-card">
        <span class="insight-pill {pill_class}">{pill_text}</span>
        <div>{message}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# § 4: Empirical Distributions & Probability Density
# ==============================================================================
if num_cols:
    st.markdown('''
    <div class="section-header">
        <span class="section-idx">&sect; 4</span>
        <span>Empirical Distributions & Central Tendency [ P(X) ]</span>
    </div>
    ''', unsafe_allow_html=True)
    
    tabs = st.tabs([f"P({col})" for col in num_cols])
    for tab, col in zip(tabs, num_cols):
        with tab:
            left_col, right_col = st.columns(2)
            mean_val = float(df[col].mean())
            median_val = float(df[col].median())
            
            with left_col:
                fig_hist = px.histogram(
                    df, x=col, nbins=30,
                    title=f"Probability Frequency Histogram — {col}",
                    color_discrete_sequence=["#2563eb"],
                    opacity=0.88
                )
                fig_hist.update_layout(**PLOTLY_THEME, height=chart_height)
                fig_hist.update_xaxes(title_text=col)
                fig_hist.update_yaxes(title_text="Count")
                fig_hist.add_vline(x=mean_val, line_dash="dash", line_color="#d97706",
                                   annotation_text=f"Mean μ: {mean_val:.2f}", annotation_position="top left",
                                   annotation_font=dict(color="#d97706", size=11, family="Fira Code, monospace"))
                fig_hist.add_vline(x=median_val, line_dash="dot", line_color="#059669",
                                   annotation_text=f"Median Q₂: {median_val:.2f}", annotation_position="top right",
                                   annotation_font=dict(color="#059669", size=11, family="Fira Code, monospace"))
                st.plotly_chart(fig_hist, use_container_width=True, theme=plotly_streamlit_theme)
            
            with right_col:
                fig_box = px.box(
                    df, y=col, points="all",
                    title=f"Quantile Outlier Boxplot — {col}",
                    color_discrete_sequence=["#0284c7"]
                )
                fig_box.update_layout(**PLOTLY_THEME, height=chart_height)
                fig_box.update_yaxes(title_text=col)
                st.plotly_chart(fig_box, use_container_width=True, theme=plotly_streamlit_theme)

# ==============================================================================
# § 5: Correlation Matrix & Collinearity Topology
# ==============================================================================
if len(num_cols) >= 2:
    st.markdown('''
    <div class="section-header">
        <span class="section-idx">&sect; 5</span>
        <span>Correlation Matrix Topology [ r &isin; [-1, 1] ]</span>
    </div>
    ''', unsafe_allow_html=True)
    
    corr_df = df[num_cols].corr().round(2)
    
    fig_corr = px.imshow(
        corr_df,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1.0, zmax=1.0,
        title="Pearson Correlation Matrix (r)",
        aspect="auto"
    )
    fig_corr.update_traces(
        textfont=dict(family="Fira Code, monospace", size=13)
    )
    fig_corr.update_layout(**PLOTLY_THEME, height=chart_height)
    fig_corr.update_xaxes(tickfont=dict(family="Fira Code, monospace", size=12))
    fig_corr.update_yaxes(tickfont=dict(family="Fira Code, monospace", size=12))
    fig_corr.update_coloraxes(colorbar_tickfont=dict(family="Fira Code, monospace", size=11))
    st.plotly_chart(fig_corr, use_container_width=True, theme=plotly_streamlit_theme)

# ==============================================================================
# § 6: Bivariate Geometry & Linear Regression
# ==============================================================================
if len(num_cols) >= 2:
    st.markdown('''
    <div class="section-header">
        <span class="section-idx">&sect; 6</span>
        <span>Bivariate Geometry & Linear Regression [ ŷ = mx + b ]</span>
    </div>
    ''', unsafe_allow_html=True)
    
    s1, s2, s3, s4 = st.columns([1.2, 1.2, 1.2, 1])
    with s1:
        x_col = st.selectbox("Predictor Feature (X)", num_cols, index=0)
    with s2:
        y_col = st.selectbox("Response Feature (Y)", num_cols, index=min(1, len(num_cols) - 1))
    with s3:
        color_col = st.selectbox("Decomposition (Color)", ["None"] + cat_cols + num_cols)
    with s4:
        show_trend = st.checkbox("Fit OLS Line (y = mx + b)", value=True)
    
    valid_data = df[[x_col, y_col]].dropna()
    trend_info = ""
    slope, intercept, r_val, r2_score = None, None, None, None
    if show_trend and len(valid_data) > 1:
        try:
            slope, intercept = np.polyfit(valid_data[x_col], valid_data[y_col], 1)
            r_val = np.corrcoef(valid_data[x_col], valid_data[y_col])[0, 1]
            r2_score = r_val ** 2
            trend_info = f"OLS Model: ŷ = {slope:.3f}x + ({intercept:.3f}) | Pearson r = {r_val:.3f} | R² = {r2_score:.3f}"
        except Exception:
            show_trend = False

    fig_scatter = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=None if color_col == "None" else color_col,
        title=f"Bivariate Scatter: {x_col} vs {y_col}",
        color_discrete_sequence=MATH_PALETTE
    )
    if show_trend and slope is not None:
        x_pts = np.linspace(valid_data[x_col].min(), valid_data[x_col].max(), 100)
        y_pts = slope * x_pts + intercept
        fig_scatter.add_trace(
            go.Scatter(
                x=x_pts,
                y=y_pts,
                mode="lines",
                name=f"OLS: ŷ={slope:.2f}x+{intercept:.2f}",
                line=dict(color="#dc2626", width=2.5, dash="dash")
            )
        )
    fig_scatter.update_layout(**PLOTLY_THEME, height=chart_height)
    fig_scatter.update_xaxes(title_text=x_col)
    fig_scatter.update_yaxes(title_text=y_col)
    st.plotly_chart(fig_scatter, use_container_width=True, theme=plotly_streamlit_theme)
    
    if trend_info:
        st.markdown(f'<div class="formula-callout"><b>Linear Fit:</b> <code>{trend_info}</code></div>', unsafe_allow_html=True)

# ==============================================================================
# § 7: Categorical Factor Projections
# ==============================================================================
if cat_cols and num_cols:
    st.markdown('''
    <div class="section-header">
        <span class="section-idx">&sect; 7</span>
        <span>Categorical Factor Projections [ E[Y | C = c] ]</span>
    </div>
    ''', unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns(3)
    with b1:
        group_col = st.selectbox("Factor Group (C)", cat_cols)
    with b2:
        val_col = st.selectbox("Metric Feature (Y)", num_cols)
    with b3:
        calc_type = st.selectbox("Aggregation Operator", ["Mean μ", "Median Q₂", "Sum ∑", "Std Dev σ"])
    
    calc_map = {
        "Mean μ": "mean",
        "Median Q₂": "median",
        "Sum ∑": "sum",
        "Std Dev σ": "std"
    }
    agg_type = calc_map[calc_type]
    
    grouped = df.groupby(group_col)[val_col].agg(agg_type).reset_index()
    grouped = grouped.sort_values(by=val_col, ascending=False).head(max_categories)
    
    fig_bar = px.bar(
        grouped,
        x=group_col,
        y=val_col,
        title=f"{calc_type} of {val_col} partitioned by {group_col}",
        color=val_col,
        color_continuous_scale="Blues"
    )
    fig_bar.update_layout(**PLOTLY_THEME, height=chart_height)
    fig_bar.update_xaxes(title_text=group_col)
    fig_bar.update_yaxes(title_text=val_col)
    fig_bar.update_coloraxes(colorbar_tickfont=dict(family="Fira Code, monospace", size=11))
    st.plotly_chart(fig_bar, use_container_width=True, theme=plotly_streamlit_theme)

# ==============================================================================
# § 8: Export Quantitative Metrics
# ==============================================================================
st.markdown('''
<div class="section-header">
    <span class="section-idx">&sect; 8</span>
    <span>Export Quantitative Summary Metrics</span>
</div>
''', unsafe_allow_html=True)

if num_cols:
    export_df = df[num_cols].describe().round(3).to_csv().encode("utf-8")
    st.download_button(
        label="Download Mathematical Moments (CSV)",
        data=export_df,
        file_name="statvision_moments.csv",
        mime="text/csv"
    )
