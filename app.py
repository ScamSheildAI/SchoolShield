
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
# PREMIUM SCHOOLSHIELD — CYBER COMMAND CENTRE DESIGN
# ============================================================

st.markdown("""
<style>
:root {
    --ss-bg: #070B16;
    --ss-panel: #101B30;
    --ss-panel2: #14233B;
    --ss-line: rgba(112, 177, 220, .22);
    --ss-cyan: #67E8F9;
    --ss-blue: #3B82F6;
    --ss-purple: #8B5CF6;
    --ss-text: #F3F7FF;
    --ss-muted: #A8B8D0;
}
.stApp {
    background:
        radial-gradient(ellipse at 8% 4%, rgba(6,182,212,.19), transparent 30%),
        radial-gradient(ellipse at 92% 12%, rgba(124,58,237,.20), transparent 32%),
        radial-gradient(ellipse at 50% 100%, rgba(37,99,235,.10), transparent 38%),
        var(--ss-bg);
    color: var(--ss-text);
}
.block-container { max-width: 1420px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101B30 0%, #080F1E 100%);
    border-right: 1px solid var(--ss-line);
}
h1, h2, h3 { color: var(--ss-text) !important; font-weight: 800 !important; letter-spacing: -.035em; }
h1 { text-shadow: 0 0 30px rgba(103,232,249,.18); }
p, label, li, .stMarkdown { color: #D1DCEE; }
[data-testid="stCaptionContainer"], .stCaption { color: var(--ss-muted) !important; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(20,35,59,.96), rgba(10,20,37,.96));
    border: 1px solid var(--ss-line); border-radius: 18px; padding: 18px 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,.20);
}
div[data-testid="stMetricLabel"] { color: var(--ss-muted) !important; }
div[data-testid="stMetricValue"] { color: var(--ss-cyan) !important; font-weight: 850; }
div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stExpander"] {
    background: linear-gradient(145deg, rgba(17,31,53,.94), rgba(9,18,34,.96));
    border: 1px solid var(--ss-line) !important; border-radius: 20px;
    box-shadow: 0 14px 34px rgba(0,0,0,.20);
}
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
    background: linear-gradient(105deg, #0891B2, #2563EB 58%, #7C3AED);
    color: white !important; border: 1px solid rgba(103,232,249,.25);
    border-radius: 12px; min-height: 46px; font-weight: 800;
    box-shadow: 0 7px 22px rgba(37,99,235,.22); transition: .2s ease;
}
.stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {
    border-color: var(--ss-cyan); box-shadow: 0 0 24px rgba(34,211,238,.25);
    transform: translateY(-2px);
}
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
    background: #0C172A !important; color: var(--ss-text) !important;
    -webkit-text-fill-color: var(--ss-text) !important;
    border: 1px solid #354D6C !important; border-radius: 13px !important;
    caret-color: var(--ss-cyan) !important;
}
div[data-testid="stTextArea"] textarea:focus, div[data-testid="stTextInput"] input:focus {
    border-color: var(--ss-cyan) !important;
    box-shadow: 0 0 0 2px rgba(34,211,238,.14) !important;
}
div[data-baseweb="select"] > div {
    background: #12213A; border-color: #354D6C; border-radius: 12px; color: white;
}
div[role="radiogroup"] {
    display:flex; flex-wrap:wrap; gap:8px; padding:11px;
    background:rgba(15,28,49,.92); border:1px solid var(--ss-line);
    border-radius:16px; margin:8px 0 22px;
}
div[role="radiogroup"] label {
    background:#172A45; border:1px solid #344C6D; border-radius:11px;
    padding:8px 14px; margin:0 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background:linear-gradient(110deg,#075985,#1D4ED8,#6D28D9);
    border-color:var(--ss-cyan);
}
