
import re
import hmac
import streamlit as st
import pandas as pd
import json


st.set_page_config(
    page_title="SchoolShield",
    page_icon="🛡️",
    layout="wide"
)

# ============================================================
# PREMIUM SCHOOLSHIELD DESIGN
# ============================================================

st.markdown("""
<style>
/* Main background */
.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #172554 0%, transparent 42%),
        radial-gradient(ellipse at 90% 10%, #312e81 0%, transparent 35%),
        #080D1B;
    color: #F8FAFC;
}

/* Main content */
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111B32, #0B1222);
    border-right: 1px solid #263653;
}

/* Typography */
h1 {
    color: #F8FAFC !important;
    font-weight: 800 !important;
    letter-spacing: -1.2px;
}
h2, h3 {
    color: #E2E8F0 !important;
    font-weight: 700 !important;
}
p, label, li, .stMarkdown {
    color: #CBD5E1;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #17243D, #101A2E);
    border: 1px solid #304362;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,.20);
}
div[data-testid="stMetricLabel"] {
    color: #9FB4D0 !important;
}
div[data-testid="stMetricValue"] {
    color: #67E8F9 !important;
    font-weight: 800;
}

/* Cards and expanders */
div[data-testid="stExpander"] {
    background: #111D32;
    border: 1px solid #304362;
    border-radius: 15px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px;
    border-color: #304362;
}

/* Buttons */
.stButton button, .stDownloadButton button,
.stFormSubmitButton button {
    background: linear-gradient(110deg, #2563EB, #7C3AED);
    color: white !important;
    border: 0;
    border-radius: 11px;
    min-height: 44px;
    font-weight: 700;
    transition: all .2s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
    border: 1px solid #67E8F9;
