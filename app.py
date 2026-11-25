
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
# CINEMATIC SCHOOLSHIELD INTRO — FIRST VISIT IN EACH SESSION
# ============================================================
if "schoolshield_intro_complete" not in st.session_state:
    st.session_state.schoolshield_intro_complete = False

if not st.session_state.schoolshield_intro_complete:
    st.markdown("""
    <style>
    .ss-intro-wrap {
        min-height: 76vh; display:flex; flex-direction:column;
        align-items:center; justify-content:center; overflow:hidden;
        text-align:center; position:relative; padding:35px 12px 20px;
        background: radial-gradient(ellipse at 50% 48%, rgba(0,190,255,.13), transparent 42%),
                    radial-gradient(ellipse at 50% 100%, rgba(15,55,110,.16), transparent 55%);
        border:1px solid rgba(80,190,255,.16); border-radius:26px;
    }
    .ss-scene { width:min(760px, 96%); height:245px; position:relative; display:flex;
        align-items:center; justify-content:center; }
    .ss-scam {
        position:absolute; left:3%; top:83px; width:190px; padding:17px 13px;
        border:1px solid rgba(255,75,75,.85); border-radius:15px;
        background:linear-gradient(145deg,rgba(85,12,22,.96),rgba(25,7,15,.98));
        color:#ffdada; font:800 15px/1.4 Arial,sans-serif; letter-spacing:1px;
        box-shadow:0 0 28px rgba(255,35,65,.26);
        animation:ss-scam-in 2.15s cubic-bezier(.2,.8,.2,1) forwards;
    }
    .ss-scam small {display:block;color:#ff737d;font-size:10px;letter-spacing:2px;margin-bottom:6px;}
    .ss-shield {
        position:absolute; right:5%; top:58px; width:135px; height:155px;
        display:flex;align-items:center;justify-content:center;font-size:86px;
        filter:drop-shadow(0 0 18px rgba(0,210,255,.7));
        animation:ss-shield-in 2.15s cubic-bezier(.2,.8,.2,1) forwards;
    }
    .ss-impact {
        position:absolute; left:50%; top:50%; width:18px;height:18px;border-radius:50%;
        transform:translate(-50%,-50%); opacity:0;
        background:#e7fcff; box-shadow:0 0 18px 8px #00d9ff,0 0 55px 24px rgba(0,160,255,.8);
        animation:ss-impact 1.2s ease-out 1.65s forwards;
    }
    .ss-logo {
        position:absolute; left:50%; top:50%; transform:translate(-50%,-50%) scale(.25);
        opacity:0; white-space:nowrap; color:#e9fbff; font:950 clamp(25px,5vw,48px)/1 Arial,sans-serif;
        letter-spacing:3px; text-shadow:0 0 12px #00d9ff,0 0 34px rgba(0,150,255,.8);
        animation:ss-logo 1.1s cubic-bezier(.15,.85,.2,1) 2.35s forwards;
    }
    .ss-tagline { opacity:0; margin-top:3px; color:#9feeff; font:700 12px Arial,sans-serif;
        letter-spacing:3px; animation:ss-tag 1s ease 3.15s forwards; }
    .ss-intro-kicker {color:#7ddfff;font:800 10px Arial,sans-serif;letter-spacing:4px;margin-bottom:12px;}
    .ss-intro-sub {color:#aabed1;font:14px Arial,sans-serif;margin-top:17px;}
    @keyframes ss-scam-in {0%{transform:translateX(-360px) rotate(-8deg);opacity:0}65%{transform:translateX(115px) rotate(2deg);opacity:1}100%{transform:translateX(145px) scale(.72);opacity:0}}
    @keyframes ss-shield-in {0%{transform:translateX(360px) scale(.65);opacity:0}65%{transform:translateX(-110px) scale(1.08);opacity:1}100%{transform:translateX(-135px) scale(.7);opacity:0}}
    @keyframes ss-impact {0%{opacity:0;transform:translate(-50%,-50%) scale(.2)}35%{opacity:1;transform:translate(-50%,-50%) scale(3.8)}100%{opacity:0;transform:translate(-50%,-50%) scale(8)}}
    @keyframes ss-logo {0%{opacity:0;transform:translate(-50%,-50%) scale(.25);letter-spacing:12px}70%{opacity:1;transform:translate(-50%,-50%) scale(1.08)}100%{opacity:1;transform:translate(-50%,-50%) scale(1);letter-spacing:3px}}
    @keyframes ss-tag {to{opacity:1}}
    @media(max-width:600px){.ss-scene{height:215px}.ss-scam{width:145px;font-size:12px}.ss-shield{font-size:65px}.ss-intro-wrap{min-height:70vh}}
    @media(prefers-reduced-motion:reduce){.ss-scam,.ss-shield,.ss-impact,.ss-logo,.ss-tagline{animation:none;opacity:1;transform:none}.ss-impact{display:none}}
    </style>
    <div class="ss-intro-wrap">
      <div class="ss-intro-kicker">DIGITAL THREATS. ONE STRONG DEFENCE.</div>
      <div class="ss-scene">
        <div class="ss-scam"><small>⚠ THREAT DETECTED</small>SCAM MESSAGE<br/>ACCESS REQUEST</div>
        <div class="ss-shield">🛡️</div>
        <div class="ss-impact"></div>
        <div class="ss-logo">SCHOOLSHIELD</div>
      </div>
      <div class="ss-tagline">ONE PLATFORM. THREE LAYERS OF PROTECTION.</div>
      <div class="ss-intro-sub">Phishing Guardian&nbsp; • &nbsp;Cyberbullying Guardian&nbsp; • &nbsp;Privacy Guardian</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.4, 1])
    with center:
        if st.button("ENTER SCHOOLSHIELD  →", use_container_width=True, key="enter_schoolshield_intro"):
            st.session_state.schoolshield_intro_complete = True
            st.rerun()
    st.stop()

# ============================================================
# PREMIUM SCHOOLSHIELD — CYBER COMMAND CENTRE DESIGN
# ============================================================

st.markdown("""
<style>
:root {
    --ss-bg: #04030A;
    --ss-panel: #090611;
    --ss-panel2: #0D0819;
    --ss-line: rgba(167, 139, 250, .24);
    --ss-violet: #8B70D6;
    --ss-purple: #6036A8;
    --ss-cyan: #67E8F9;
    --ss-blue: #60A5FA;
    --ss-text: #F7F4FF;
    --ss-muted: #B7AECF;
}
.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, rgba(66,24,122,.22), transparent 34%),
        radial-gradient(ellipse at 88% 8%, rgba(30,58,138,.13), transparent 32%),
        radial-gradient(ellipse at 52% 100%, rgba(6,100,120,.07), transparent 40%),
        #04030A;
    color: var(--ss-text);
}
.block-container { max-width: 1480px; padding-top: 1.35rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0719 0%, #05040B 100%);
    border-right: 1px solid rgba(167,139,250,.24);
}
[data-testid="stSidebar"] * { color: #EDE9FE; }
h1, h2, h3 { color: var(--ss-text) !important; font-weight: 850 !important; letter-spacing: -.035em; }
h1 { text-shadow: 0 0 32px rgba(167,139,250,.30); }
p, label, li, .stMarkdown { color: #DCD5EF; }
[data-testid="stCaptionContainer"], .stCaption { color: var(--ss-muted) !important; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(17,10,32,.96), rgba(7,5,15,.98));
    border: 1px solid rgba(167,139,250,.28); border-radius: 19px; padding: 18px 20px;
    box-shadow: 0 12px 34px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.035);
}
div[data-testid="stMetricLabel"] { color: #BDB2D8 !important; }
div[data-testid="stMetricValue"] { color: var(--ss-cyan) !important; font-weight: 900; text-shadow: 0 0 18px rgba(103,232,249,.22); }
div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stExpander"] {
    background: linear-gradient(145deg, rgba(15,9,27,.96), rgba(6,5,13,.98));
    border: 1px solid rgba(167,139,250,.24) !important; border-radius: 20px;
    box-shadow: 0 14px 36px rgba(0,0,0,.25);
}
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
    background: linear-gradient(105deg, #32105F 0%, #482080 48%, #07566B 100%);
    color: #fff !important; border: 1px solid rgba(196,181,253,.42);
    border-radius: 13px; min-height: 46px; font-weight: 850;
    box-shadow: 0 7px 26px rgba(66,24,122,.22); transition: .2s ease;
}
.stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {
    border-color: var(--ss-cyan); box-shadow: 0 0 28px rgba(139,92,246,.42), 0 0 18px rgba(34,211,238,.18);
    transform: translateY(-2px);
}
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
    background: #090611 !important; color: var(--ss-text) !important;
    -webkit-text-fill-color: var(--ss-text) !important;
    border: 1px solid #302344 !important; border-radius: 14px !important;
    caret-color: var(--ss-cyan) !important;
}
div[data-testid="stTextArea"] textarea:focus, div[data-testid="stTextInput"] input:focus {
    border-color: var(--ss-violet) !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,.17), 0 0 22px rgba(139,92,246,.15) !important;
}
div[data-baseweb="select"] > div {
    background: #0D0819; border-color: #302344; border-radius: 12px; color: white;
}
div[role="radiogroup"] {
    display:flex; flex-wrap:wrap; gap:8px; padding:11px;
    background:rgba(9,5,18,.97); border:1px solid rgba(167,139,250,.25);
    border-radius:16px; margin:8px 0 22px;
}
div[role="radiogroup"] label {
    background:#100A1D; border:1px solid #302044; border-radius:11px;
    padding:8px 14px; margin:0 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background:linear-gradient(110deg,#32105F,#37308A,#07566B);
    border-color:var(--ss-cyan); box-shadow:0 0 18px rgba(139,92,246,.24);
}
[data-testid="stImage"] img {
    border-radius:19px; border:1px solid rgba(167,139,250,.30);
    box-shadow:0 12px 34px rgba(0,0,0,.25);
}
div[data-testid="stAlert"] { border-radius:15px; }
div[data-testid="stDataFrame"] { border:1px solid rgba(167,139,250,.25); border-radius:15px; overflow:hidden; }
.stMarkdown a { color:var(--ss-cyan) !important; }
hr { border-color:rgba(167,139,250,.20); }
.guardian-tile {
    backdrop-filter: blur(16px);
    background: linear-gradient(150deg, rgba(20,10,38,.88), rgba(6,4,13,.98) 76%) !important;
    border: 1px solid rgba(167,139,250,.42) !important;
    box-shadow: 0 15px 40px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.05) !important;
}
.guardian-tile:after { opacity:.72 !important; }
.guardian-symbol { box-shadow:0 0 30px var(--tile-glow), inset 0 0 18px rgba(255,255,255,.04) !important; }
@media(max-width:768px) {
    .block-container { padding:1rem .9rem 2rem; }
    h1 { font-size:2rem !important; }
    div[data-testid="stMetric"] { padding:13px; }
}

/* Premium Guardian showcase cards */
.guardian-showcase {
    min-height: 205px;
    padding: 22px 20px;
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(20,12,38,.96), rgba(7,6,15,.98));
    border: 1px solid rgba(139,112,214,.34);
    box-shadow: 0 16px 38px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.045);
    transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    position: relative;
    overflow: hidden;
}
.guardian-showcase:hover {
    transform: translateY(-4px);
    border-color: rgba(103,232,249,.65);
    box-shadow: 0 18px 42px rgba(0,0,0,.38), 0 0 25px rgba(96,165,250,.10);
}
.guardian-showcase:before {
    content: "";
    position: absolute;
    width: 130px; height: 130px;
    right: -45px; top: -55px;
    border-radius: 50%;
    background: rgba(96,70,160,.16);
    filter: blur(5px);
}
.guardian-showcase .symbol {
    font-size: 30px; margin-bottom: 12px;
    filter: drop-shadow(0 0 12px rgba(103,232,249,.24));
}
.guardian-showcase .eyebrow {
    color: #8FEAF5; font-size: 10px; font-weight: 900;
    letter-spacing: 1.8px; margin-bottom: 7px;
}
.guardian-showcase .name {
    color: #F7F4FF; font-size: 18px; font-weight: 850;
    margin-bottom: 8px;
}
.guardian-showcase .desc {
    color: #BEB5D2; font-size: 13px; line-height: 1.55;
}



/* ========================================================
   SCHOOLSHIELD INTERACTIVE MOTION + CURSOR GLOW SYSTEM
   ======================================================== */
@keyframes ss-page-arrive {
    from { opacity: 0; transform: translateY(13px); filter: blur(3px); }
    to   { opacity: 1; transform: translateY(0); filter: blur(0); }
}
@keyframes ss-circuit-drift {
    0% { background-position: 0 0, 0 0; opacity: .22; }
    50% { opacity: .42; }
    100% { background-position: 54px 54px, -54px 54px; opacity: .22; }
}
@keyframes ss-soft-scan {
    0% { transform: translateX(-110%); opacity: 0; }
    15% { opacity: .45; }
    85% { opacity: .35; }
    100% { transform: translateX(110%); opacity: 0; }
}
/* Subtle animated circuit-grid atmosphere; never intercepts clicks. */
.stApp::before {
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
      linear-gradient(rgba(103,232,249,.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(103,232,249,.035) 1px, transparent 1px);
    background-size: 54px 54px;
    mask-image: linear-gradient(to bottom, black, transparent 82%);
    animation: ss-circuit-drift 18s linear infinite;
}
.stApp > header, [data-testid="stSidebar"], .main, [data-testid="stAppViewContainer"] > .main {
    position: relative; z-index: 1;
}
/* Bring the main content in gently on each Streamlit page change. */
[data-testid="stMainBlockContainer"] > div {
    animation: ss-page-arrive .48s cubic-bezier(.2,.75,.25,1) both;
}
/* Interactive surfaces: lift + cyan edge glow on hover. */
div[data-testid="stMetric"],
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stExpander"],
.guardian-showcase, .guardian-tile,
[data-testid="stImage"] img {
    transition: transform .24s ease, border-color .24s ease,
                box-shadow .24s ease, filter .24s ease, background-color .24s ease;
}
div[data-testid="stMetric"]:hover,
div[data-testid="stVerticalBlockBorderWrapper"]:hover,
div[data-testid="stExpander"]:hover,
.guardian-showcase:hover, .guardian-tile:hover {
    transform: translateY(-4px);
    border-color: rgba(103,232,249,.78) !important;
    box-shadow: 0 15px 38px rgba(0,0,0,.34),
                0 0 0 1px rgba(103,232,249,.13),
                0 0 27px rgba(34,211,238,.16) !important;
}
[data-testid="stImage"] img:hover {
    transform: scale(1.018);
    border-color: rgba(103,232,249,.72);
    box-shadow: 0 0 26px rgba(34,211,238,.20);
}
/* Buttons get a brighter edge and a restrained glow. */
.stButton button, .stDownloadButton button, .stFormSubmitButton button,
[data-testid="stLinkButton"] a {
    position: relative; overflow: hidden;
    transition: transform .2s ease, box-shadow .2s ease,
                border-color .2s ease, filter .2s ease !important;
}
.stButton button:hover, .stDownloadButton button:hover,
.stFormSubmitButton button:hover, [data-testid="stLinkButton"] a:hover {
    transform: translateY(-3px) scale(1.012) !important;
    border-color: #67E8F9 !important;
    filter: brightness(1.16);
    box-shadow: 0 0 0 1px rgba(103,232,249,.2),
                0 0 25px rgba(34,211,238,.28),
                0 10px 26px rgba(0,0,0,.24) !important;
}
.stButton button:active, .stDownloadButton button:active,
.stFormSubmitButton button:active { transform: translateY(0) scale(.985) !important; }
/* Navigation options glow and slide slightly when hovered. */
div[role="radiogroup"] label {
    cursor: pointer;
    transition: transform .2s ease, border-color .2s ease,
                box-shadow .2s ease, background .2s ease !important;
}
div[role="radiogroup"] label:hover {
    transform: translateY(-2px);
    border-color: rgba(103,232,249,.85) !important;
    box-shadow: 0 0 19px rgba(34,211,238,.19);
}
div[role="radiogroup"] label:has(input:checked) {
    box-shadow: 0 0 0 1px rgba(103,232,249,.18),
                0 0 22px rgba(34,211,238,.22) !important;
}
/* Inputs glow on focus; links brighten on hover. */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input {
    transition: border-color .2s ease, box-shadow .2s ease, background .2s ease !important;
}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-baseweb="select"] > div:focus-within {
    border-color: #67E8F9 !important;
    box-shadow: 0 0 0 2px rgba(103,232,249,.16),
                0 0 23px rgba(34,211,238,.19) !important;
}
.stMarkdown a { transition: color .18s ease, text-shadow .18s ease; }
.stMarkdown a:hover { color: #B8F7FF !important; text-shadow: 0 0 12px rgba(103,232,249,.65); }
/* Focus indicators also work for keyboard navigation. */
button:focus-visible, a:focus-visible, input:focus-visible,
textarea:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid #67E8F9 !important;
    outline-offset: 3px !important;
}
/* Avoid motion for visitors who request reduced animation. */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
    }
}


/* ========================================================
   COMPATIBILITY OVERRIDES — STREAMLIT HOVER + TRANSITIONS
   These selectors cover current Streamlit layouts as well
   as custom guardian cards.
   ======================================================== */

/* Animate the actual Streamlit content area after reruns. */
[data-testid="stAppViewContainer"] section.main .block-container,
section.main .block-container,
[data-testid="stMainBlockContainer"] {
    animation: ss-page-arrive .65s ease-out both !important;
}

/* Common Streamlit card/container surfaces. */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stMetric"],
[data-testid="stExpander"],
[data-testid="stAlert"],
[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"],
[data-testid="stImage"],
.guardian-showcase,
.guardian-tile {
    transition:
        transform .28s cubic-bezier(.2,.75,.25,1),
        box-shadow .28s ease,
        border-color .28s ease,
        filter .28s ease !important;
}

/* Hovering columns makes dashboard tiles visibly respond too. */
[data-testid="stHorizontalBlock"] [data-testid="column"] [data-testid="stVerticalBlockBorderWrapper"]:hover,
[data-testid="stVerticalBlockBorderWrapper"]:hover,
[data-testid="stMetric"]:hover,
[data-testid="stExpander"]:hover,
[data-testid="stAlert"]:hover,
.guardian-showcase:hover,
.guardian-tile:hover {
    transform: translateY(-5px) !important;
    border-color: rgba(103,232,249,.95) !important;
    box-shadow:
        0 14px 36px rgba(0,0,0,.38),
        0 0 0 1px rgba(103,232,249,.22),
        0 0 30px rgba(34,211,238,.27) !important;
    filter: brightness(1.08);
}

/* Streamlit buttons: make the hover state unmistakable. */
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"],
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    transition: all .22s ease !important;
}
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-secondary"]:hover,
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-3px) scale(1.025) !important;
    border-color: #67E8F9 !important;
    box-shadow: 0 0 0 1px rgba(103,232,249,.25),
                0 0 28px rgba(34,211,238,.38) !important;
    filter: brightness(1.2) !important;
}

/* Tabs and radio navigation highlight on pointer hover. */
button[data-baseweb="tab"],
div[role="radiogroup"] label {
    transition: all .22s ease !important;
}
button[data-baseweb="tab"]:hover,
div[role="radiogroup"] label:hover {
    color: #B8F7FF !important;
    border-color: #67E8F9 !important;
    box-shadow: 0 0 20px rgba(34,211,238,.28) !important;
}

/* Text fields glow on focus, with smooth transitions. */
textarea, input, [data-baseweb="select"] > div {
    transition: box-shadow .22s ease, border-color .22s ease !important;
}
textarea:focus, input:focus,
[data-baseweb="select"] > div:focus-within {
    border-color: #67E8F9 !important;
    box-shadow: 0 0 0 2px rgba(103,232,249,.22),
                0 0 25px rgba(34,211,238,.24) !important;
}

/* A slow ambient scan line across the main app content. */
section.main .block-container {
    position: relative;
}
section.main .block-container::after {
    content: "";
    position: absolute;
    pointer-events: none;
    top: 0;
    left: 0;
    width: 35%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(103,232,249,.55), transparent);
    filter: blur(1px);
    animation: ss-soft-scan 8s ease-in-out infinite;
    opacity: .35;
}

@media (prefers-reduced-motion: reduce) {
    section.main .block-container,
    [data-testid="stMainBlockContainer"] {
        animation: none !important;
    }
    section.main .block-container::after {
        animation: none !important;
        display: none !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER
# ============================================================

def matches(pattern, text):
    return re.search(pattern, text, re.IGNORECASE) is not None



def contains_any(text, phrases):
    """Unicode-safe phrase matching for Telugu, Hindi and Russian."""
    lowered = text.casefold()
    return any(phrase.casefold() in lowered for phrase in phrases)


# ============================================================
# PHISHING GUARDIAN
# ============================================================


def detect_phishing(message):
    text = message.lower()
    reasons = []

    # --------------------------------------------------------
    # 1. CONTEXT DETECTION
    # --------------------------------------------------------

    educational_context = matches(
        r"\b(our lesson|computer lesson|teacher explained|"
        r"teacher taught|class discussed|we discussed|"
        r"we are learning|textbook explains|worksheet asks|"
        r"school presentation|educational message|"
        r"studying examples|writing an essay|"
        r"learning about|the chapter explains|"
        r"our teacher|class presentation)\b",
        text
    )

    protective_context = matches(
        r"\b(never share|do not share|don't share|"
        r"should not share|should never share|"
        r"must not share|never reveal|do not reveal|"
        r"don't reveal|keep your password private|"
        r"protect your password|protect your account|"
        r"keep your details private|"
        r"should be kept secret)\b",
        text
    )

    active_request_after_warning = matches(
        r"\b(asks?|tells?|demands?|requests?|instructs?)\b.{0,80}\b(share|send|reveal|provide|give|submit|enter|type)\b",
        text
    )
    protective_only = protective_context and not active_request_after_warning

    # --------------------------------------------------------
    # 2. DIRECT SENSITIVE INFORMATION REQUESTS
    # --------------------------------------------------------

    sensitive_request = (
        matches(
            r"\b(share|send|tell|reveal|provide|give|"
            r"submit|enter|type|reply with)\b"
            r".{0,60}"
            r"\b(otp|verification code|password|passcode|"
            r"login details|bank details)\b",
            text
        )
        or
        matches(
            r"\b(otp|verification code|password|passcode|"
            r"login details|bank details)\b"
            r".{0,60}"
            r"\b(share|send|tell|reveal|provide|give|"
            r"submit|enter|type)\b",
            text
        )
    )

    if sensitive_request and not protective_only:
        reasons.append(
            "Requests sensitive verification or login information"
        )

    # --------------------------------------------------------
    # 3. PAYMENT SCAMS
    # --------------------------------------------------------

    payment_pressure = (
        matches(
            r"\b(pay|payment|fee|charge|transfer|send money)\b",
            text
        )
        and
        matches(
            r"\b(prize|reward|parcel|scholarship|refund|"
            r"lottery|unlock|release|claim|gift)\b",
            text
        )
    )

    if payment_pressure:
        reasons.append(
            "Links a payment request with an unexpected benefit"
        )

    # --------------------------------------------------------
    # 3B. ADDITIONAL HIGH-RISK REQUESTS
    # --------------------------------------------------------

    credential_or_private_request = (
        matches(
            r"\b(reveal|provide|send|share|confirm|confirmed|requests?|submit|enter)\b.{0,65}"
            r"\b(digits sent to your phone|banking information|private details|"
            r"account credentials|login credentials|personal details|"
            r"security code|code sent to your phone)\b",
            text
        )
        or matches(
            r"\b(password|passcode|credentials|banking information|private details)\b"
            r".{0,55}\b(confirm|confirmed|send|share|provide|enter|reveal)\b",
            text
        )
    )
    if credential_or_private_request:
        reasons.append("Requests private account or personal information")

    money_pressure = (
        matches(r"\b(send funds|transfer money|move my savings|another transfer|pay first|pay a fee)\b", text)
        and matches(r"\b(caller|stranger|unknown|unexpected|protect|prize|contest|parcel|refund|reward|account|payment)\b", text)
    )
    if money_pressure:
        reasons.append("Pressures the recipient to make an unexpected payment or transfer")

    risky_app_request = (
        matches(r"\b(install|download)\b.{0,45}\b(unknown|unfamiliar|unverified)\b.{0,30}\b(app|application)\b", text)
        and matches(r"\b(restore|unlock|recover|account|access)\b", text)
    )
    if risky_app_request:
        reasons.append("Requests installation of an unverified app to solve an account issue")

    # --------------------------------------------------------
    # 4. ACCOUNT THREATS
    # --------------------------------------------------------

    account_threat = (
        matches(
            r"\b(account|school account|profile|access)\b",
            text
        )
        and
        matches(
            r"\b(blocked|suspended|closed|locked|disabled|"
            r"deactivated|termination)\b",
            text
        )
        and
        matches(
            r"\b(urgent|immediately|today|act now|"
            r"within 24 hours|right away|before tonight)\b",
            text
        )
    )

    if account_threat:
        reasons.append(
            "Uses an account restriction threat with urgency"
        )

    # --------------------------------------------------------
    # 5. DECEPTIVE VERIFICATION
    # --------------------------------------------------------

    verification_request = (
        matches(
            r"\b(account|school account|profile|login|access)\b",
            text
        )
        and
        matches(
            r"\b(verify|verification|confirm|restore|"
            r"recover|unlock|reactivate)\b",
            text
        )
        and
        matches(
            r"\b(link|website|page|details|information|"
            r"identity|password|otp)\b|https?://|www\.",
            text
        )
    )

    if verification_request:
        reasons.append(
            "Connects account verification with a request for action"
        )

    # --------------------------------------------------------
    # 6. SUSPICIOUS LINKS
    # --------------------------------------------------------

    link_action = (
        matches(
            r"\b(click|tap|open|visit)\b.{0,50}"
            r"\b(link|website|page)\b",
            text
        )
        or matches(r"https?://|www\.", text)
    )

    suspicious_link_context = (
        link_action
        and matches(
            r"\b(urgent|verify|verification|password|"
            r"otp|reward|prize|blocked|suspended|"
            r"unlock|restore|payment)\b",
            text
        )
    )

    if suspicious_link_context:
        reasons.append(
            "Contains a link connected with suspicious activity"
        )

    # --------------------------------------------------------
    # 7. ORGANISATION IMPERSONATION
    # --------------------------------------------------------

    impersonation_request = (
        matches(
            r"\b(bank|delivery|parcel|school account|"
            r"support team|security team|administrator)\b",
            text
        )
        and
        matches(
            r"\b(demand|demands|asking|asks|request|"
            r"requests|send|provide|reveal|confirm)\b",
            text
        )
        and
        matches(
            r"\b(password|otp|verification code|"
            r"bank details|login details|payment)\b",
            text
        )
    )

    if impersonation_request and not protective_context:
        reasons.append(
            "Uses an organisation identity to request sensitive information"
        )

    # --------------------------------------------------------
    # 8. TELUGU, HINDI AND RUSSIAN PHISHING PATTERNS
    # --------------------------------------------------------
    # The interface and all explanations remain in English.
    # These are phrase-based rules, not full translation or AI understanding.

    multi_sensitive_terms = [
        "ఓటీపీ", "otp", "పాస్‌వర్డ్", "పాస్వర్డ్", "రహస్య కోడ్",
        "ओटीपी", "पासवर्ड", "सत्यापन कोड", "गुप्त कोड",
        "одноразовый пароль", "пароль", "код подтверждения"
    ]
    multi_request_terms = [
        "పంపండి", "చెప్పండి", "పంచుకోండి", "నమోదు చేయండి", "ఇవ్వండి",
        "भेजें", "बताएं", "साझा करें", "दर्ज करें", "दीजिए",
        "отправьте", "сообщите", "поделитесь", "введите", "предоставьте"
    ]
    multi_urgent_terms = [
        "వెంటనే", "తక్షణమే", "ఈరోజే", "ఇప్పుడే",
        "तुरंत", "अभी", "आज ही", "शीघ्र",
        "срочно", "немедленно", "сегодня", "прямо сейчас"
    ]
    multi_account_terms = [
        "ఖాతా", "అకౌంట్", "खाता", "аккаунт", "учётная запись"
    ]
    multi_block_terms = [
        "బ్లాక్", "నిలిపివేయబడుతుంది", "మూసివేయబడుతుంది",
        "बंद", "ब्लॉक", "निलंबित", "заблокирован", "закрыт", "приостановлен"
    ]
    multi_payment_terms = [
        "చెల్లింపు", "డబ్బు పంపండి", "ఫీజు", "బహుమతి",
        "भुगतान", "पैसे भेजें", "शुल्क", "इनाम",
        "оплата", "переведите деньги", "платёж", "награда", "приз"
    ]
    multi_link_terms = [
        "లింక్", "క్లిక్ చేయండి", "లింక్ తెరవండి",
        "लिंक", "क्लिक करें", "ссылка", "перейдите по ссылке"
    ]
    multi_verify_terms = [
        "ధృవీకరించండి", "నిర్ధారించండి", "వెరిఫై",
        "सत्यापित करें", "पुष्टि करें", "проверьте", "подтвердите"
    ]

    multi_sensitive_request = (
        contains_any(text, multi_sensitive_terms)
        and contains_any(text, multi_request_terms)
    )
    multi_account_threat = (
        contains_any(text, multi_account_terms)
        and contains_any(text, multi_block_terms)
        and contains_any(text, multi_urgent_terms)
    )
    multi_payment_scam = (
        contains_any(text, multi_payment_terms)
        and contains_any(text, [
            "బహుమతి", "బహుమానం", "రివార్డ్", "విడుదల",
            "इनाम", "पुरस्कार", "रिवॉर्ड", "जारी",
            "награда", "приз", "вознаграждение", "получить"
        ])
    )
    multi_verification_link = (
        contains_any(text, multi_verify_terms)
        and (
            contains_any(text, multi_link_terms)
            or contains_any(text, multi_account_terms)
        )
    )

    if multi_sensitive_request and not contains_any(text, [
        "పంచుకోవద్దు", "పంపవద్దు", "చెప్పకండి",
        "साझा न करें", "मत भेजें", "कभी न बताएं",
        "не сообщайте", "не отправляйте", "не делитесь"
    ]):
        reasons.append("Requests sensitive verification or login information")

    if multi_account_threat:
        reasons.append("Uses an account restriction threat with urgency")

    if multi_payment_scam:
        reasons.append("Links a payment request with an unexpected benefit")

    if multi_verification_link:
        reasons.append("Connects account verification with a request for action")

    # --------------------------------------------------------
    # 8. CONTEXT-AWARE DECISION
    # --------------------------------------------------------

    # Protective educational messages should not be flagged
    # merely because they mention passwords, OTPs or scams.
    # Do not let an educational introduction automatically hide a real request.
    # Protective wording suppresses the sensitive-request rule only when the
    # message is genuinely warning people not to disclose information.

    # Additional context patterns catch common variants that do not use
    # the exact words "OTP" or "password".
    extra_account_threat = (
        matches(r"\b(account|school account|account access)\b", text)
        and matches(r"\b(close|closed|disappear|lose access|lost access)\b", text)
        and matches(r"\b(today|tonight|immediately|urgent|act now|respond)\b", text)
    )
    extra_sensitive_request = (
        matches(r"\b(reveal|send|provide|confirm|give|share|demands?|asks?)\b.{0,75}\b(code|digits|details|credentials|identity|password|banking information)\b", text)
        and matches(r"\b(phone|account|parcel|delivery|caller|stranger|unknown|unexpected|reward|unlock|setup|school|link)\b", text)
    )
    extra_reward_scam = (
        matches(r"\b(pay|fee|payment|transfer|send money|send funds)\b", text)
        and matches(r"\b(prize|contest|won|reward|gift|refund|parcel|scholarship)\b", text)
    )
    if extra_account_threat:
        reasons.append("Threatens account access to pressure a quick response")
    if extra_sensitive_request:
        reasons.append("Requests a code, identity detail or account information")
    if extra_reward_scam:
        reasons.append("Connects an unexpected benefit with a payment request")

    # A message with no meaningful warning signs is not flagged.
    # Two or more independent warning signs increase concern.
    suspicious = (
        (sensitive_request and not protective_only)
        or payment_pressure
        or credential_or_private_request
        or money_pressure
        or risky_app_request
        or extra_account_threat
        or extra_sensitive_request
        or extra_reward_scam
        or account_threat
        or verification_request
        or suspicious_link_context
        or (impersonation_request and not protective_only)
        or multi_sensitive_request
        or multi_account_threat
        or multi_payment_scam
        or multi_verification_link
        or len(reasons) >= 2
    )

    return suspicious, reasons

# ============================================================
# CYBERBULLYING GUARDIAN
# ============================================================

def detect_bullying(message):
    text = message.lower()
    reasons = []

    educational_context = matches(
        r"\b(lesson explains|teacher asked us|essay about|poster says|"
        r"worksheet asks|we are learning|we discussed|studying examples|"
        r"story includes|textbook explains|reported an|"
        r"discussed why|learning how to|class discussed)\b",
        text
    )

    patterns = [
        (r"\b(you are|you're|such a|what a)\s+(stupid|idiot|loser|worthless|ugly|dumb|pathetic)\b",
         "Contains insulting language directed at someone"),
        (r"\b(nobody likes you|everyone hates you|you have no friends|nobody wants you)\b",
         "Contains hurtful personal remarks"),
        (r"\b(i will hurt you|i will beat you|you will regret this)\b",
         "Contains threatening language"),
        (r"\b(go away|you don't belong here|you should not be here)\b",
         "Contains exclusionary language"),
        (r"\b(i hate you|i hate him|i hate her|you shut up)\b",
         "Contains hostile language"),
        (r"\b(spreading|spread|sharing)\s+(rumours|rumors|false stories)\b",
         "Mentions spreading rumours"),
        (r"\b(make fun of|mock|humiliate|embarrass)\b",
         "Mentions mocking or humiliating someone"),
        (r"\b(leave me out|exclude me|excluding me|leave me behind|not include me)\b",
         "Describes deliberate exclusion"),
        (r"\b(deliberately|repeatedly|keeps|keep|constantly)\b.{0,65}\b(ignore|mock|exclude|insult|target|embarrass|humiliate)\b",
         "Describes repeated targeted behaviour"),
        (r"\b(tell|telling|tells|pressure|pressuring)\b.{0,50}\b(others|everyone|friends)\b.{0,40}\b(ignore|avoid|exclude|not talk|not sit)\b",
         "Describes encouraging others to exclude someone"),
        (r"\b(separate group|group chat)\b.{0,60}\b(mock|make fun|target|embarrass|insult)\b",
         "Describes group-based targeting"),
        (r"\b(share|post|send)\b.{0,50}\b(embarrassing|private|unwanted)\b.{0,40}\b(picture|photo|story|message|comment)\b",
         "May involve sharing embarrassing content"),
        (r"\b(after i asked them to stop|asked them to stop|told them to stop)\b",
         "Indicates unwanted behaviour continued after being asked to stop"),
        (r"\b(turn my friends against me|stop being friends with me)\b",
         "Describes attempts to damage friendships"),
        (r"\b(laugh whenever i speak|laugh at my mistakes|laugh at me)\b",
         "Describes repeated humiliation"),
        (r"\b(group chat)\b.{0,65}\b(silent|ignore|exclude|leave me out)\b",
         "Describes exclusion in a group chat"),
        (r"\b(keeps|repeatedly|constantly)\b.{0,55}\b(sharing|posting|sending)\b.{0,45}\b(embarrassing|unkind|insulting|cruel)\b",
         "Describes repeated sharing of hurtful content"),
        (r"\b(tell|tells|telling|pressure|pressures)\b.{0,45}\b(everyone|others|friends)\b.{0,45}\b(not to|to)\s+(sit|work|talk|include|ignore|avoid)\b",
         "Describes encouraging others to exclude someone"),
        (r"\b(keeps|repeatedly|constantly)\b.{0,60}\b(send|sends|sending|post|posts|posting)\b.{0,45}\b(unwanted|insulting|cruel|unkind)\b",
         "Describes repeated unwanted or insulting messages"),
        (r"\b(classmates|they|someone)\b.{0,45}\b(laugh|laughs|laughing)\b.{0,45}\b(whenever i speak|at my mistakes|at me)\b",
         "Describes repeated humiliation"),
        (r"\b(share|shares|sharing|post|posts|posting)\b.{0,45}\b(embarrassing pictures|embarrassing photos|cruel comments|unkind comments)\b",
         "May involve sharing embarrassing or hurtful content"),
        (r"\b(repeatedly|keeps|constantly)\b.{0,45}\b(target|targets|targeting)\b.{0,45}\b(cruel comments|unkind messages|online)\b",
         "Describes repeated online targeting"),
        (r"\b(keep telling me|keeps telling me)\b.{0,45}\b(nobody wants me|not wanted|no one wants me)\b",
         "Contains repeated hurtful personal remarks")
    ]

    for pattern, reason in patterns:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    extra_bullying_patterns = [
        (r"\b(group chat)\b.{0,65}\b(silent|ignore|exclude)\b.{0,35}\b(join|me|i)\b", "Describes exclusion in a group chat"),
        (r"\b(someone|they|classmates)\b.{0,70}\b(keeps|repeatedly|constantly)\b.{0,60}\b(sharing|posting|sending)\b.{0,50}\b(embarrassing|unkind|insulting|cruel)\b", "Describes repeated sharing of hurtful content"),
        (r"\b(tell|tells|telling|pressure|pressures)\b.{0,45}\b(everyone|others|friends)\b.{0,45}\b(not to sit|not to work|ignore|avoid|exclude)\b", "Describes encouraging others to exclude someone"),
        (r"\b(someone|they|classmate)\b.{0,60}\b(repeatedly|keeps|constantly)\b.{0,60}\b(insulting messages|unkind comments|cruel comments|targeting)\b", "Describes repeated online targeting"),
        (r"\b(classmates|they|someone)\b.{0,45}\b(laugh|laughs|laughing)\b.{0,45}\b(whenever i speak|at my mistakes|at me)\b", "Describes repeated humiliation"),
        (r"\b(share|shares|sharing|post|posts|posting)\b.{0,45}\b(embarrassing pictures|embarrassing photos|cruel comments|unkind comments)\b", "May involve sharing embarrassing or hurtful content"),
        (r"\b(keep telling me|keeps telling me)\b.{0,45}\b(nobody wants me|not wanted|no one wants me)\b", "Contains repeated hurtful personal remarks"),
        (r"\b(someone|they)\b.{0,55}\b(keeps making|repeatedly makes)\b.{0,45}\b(joke out of my mistakes|jokes about me)\b", "Describes repeated humiliation")
    ]
    for pattern, reason in extra_bullying_patterns:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    targeted_social_patterns = [
        (r"\b(someone|they|a person)\b.{0,55}\b(encourages|encourage|tells|tell|pressures)\b.{0,55}\b(others|everyone|friends)\b.{0,55}\b(ignore me|not include me|not be included|not sit with me|not work with me)\b", "Describes encouraging others to exclude someone"),
        (r"\b(my classmates|classmates|they)\b.{0,45}\b(laugh|laughs|laughing)\b.{0,45}\b(whenever i speak|whenever i try to speak|when i speak|at my mistakes)\b", "Describes repeated humiliation"),
        (r"\b(someone|they)\b.{0,45}\b(keeps|keep|repeatedly)\b.{0,45}\b(making a joke out of my mistakes|joking about my mistakes)\b", "Describes repeated humiliation")
    ]
    for pattern, reason in targeted_social_patterns:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    # Telugu, Hindi and Russian phrase rules. Results are always English.
    multilingual_bullying = [
        (["మూర్ఖుడు", "వెధవ", "నీచుడు", "అందరూ నిన్ను ద్వేషిస్తారు",
          "నీకు స్నేహితులు లేరు", "నిన్ను కొడతాను"],
         "Contains insulting or threatening language"),
        (["बेवकूफ", "मूर्ख", "घटिया", "सब तुमसे नफरत करते हैं",
          "तुम्हारा कोई दोस्त नहीं", "मैं तुम्हें मारूंगा", "दूर रहो"],
         "Contains insulting or threatening language"),
        (["дурак", "идиот", "никому ты не нравишься",
          "у тебя нет друзей", "я тебя побью", "заткнись", "ненавижу тебя"],
         "Contains insulting or threatening language"),
        (["నిన్ను గ్రూప్‌లో చేర్చము", "నిన్ను దూరంగా ఉంచుతున్నారు",
          "నీ గురించి తప్పుడు మాటలు", "నిన్ను అవమానిస్తున్నారు"],
         "Describes exclusion or repeated humiliation"),
        (["तुम्हें समूह में शामिल नहीं करेंगे", "तुम्हें बाहर रखेंगे",
          "तुम्हारा मज़ाक उड़ाते हैं", "तुम्हें अपमानित करते हैं"],
         "Describes exclusion or repeated humiliation"),
        (["तебя не возьмут в группу", "тебя исключают",
          "над тобой смеются", "тебя унижают"],
         "Describes exclusion or repeated humiliation")
    ]

    for phrases, reason in multilingual_bullying:
        if contains_any(text, phrases) and reason not in reasons:
            reasons.append(reason)

    direct_attack = matches(
        r"\b(you are\s+(?:such an?\s+)?|you're\s+(?:such an?\s+)?|such an?\s+|what an?\s+)(stupid|idiot|loser|worthless|ugly|dumb|pathetic)\b|"
        r"\b(nobody likes you|everyone hates you|you have no friends|"
        r"i will hurt you|i will beat you|you will regret this|you shut up|"
        r"you don't belong here|you should not be here)\b",
        text
    )

    # Educational/reporting sentences can mention hurtful words without
    # targeting the reader. Keep the warning if the text also describes
    # ongoing or first-person targeted behaviour.
    reported_or_educational = educational_context or matches(
        r"\b(reported|reporting|quoted|quote|character says|word means|"
        r"definition of|example of)\b", text
    )
    ongoing_targeting = matches(
        r"\b(they|someone|classmates|a classmate)\b.{0,90}\b(me|my|keeps|repeatedly|constantly|every day)\b|"
        r"\b(keeps|repeatedly|constantly|every day)\b.{0,70}\b(mock|exclude|insult|target|humiliate|threaten)\b",
        text
    )
    if reported_or_educational and not ongoing_targeting and not direct_attack:
        return False, []

    return direct_attack or len(reasons) > 0, reasons


# ============================================================
# PRIVACY GUARDIAN
# ============================================================

def detect_privacy(message):
    text = message.strip().lower()
    reasons = []

    # A label alone (for example, "my address is") is not treated as
    # disclosure. The rule looks for a value after the label where possible.
    patterns = [
        (r"\b(password|passcode)\s*(is|[:=])\s*[^\s,.;]{3,}",
         "May contain a password or passcode"),
        (r"\b(otp|verification code)\s*(is|[:=])?\s*\d{4,8}\b",
         "May contain an OTP or verification code"),
        (r"(?<!\d)(?:\+?\d[\s().-]*){10,13}(?!\d)",
         "May contain a phone number"),
        (r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b",
         "Contains an email address"),
        (r"\b\d{12}\b",
         "May contain a 12-digit identification number"),
        (r"\b(my address is|i live at|home address is|my home address is)\s+\d{1,5}\s+[\w.-]+(?:\s+[\w.-]+){0,4}",
         "May contain a home address"),
        (r"\b(my school is|my school name is|i attend)\s+[a-z][a-z0-9&' -]{2,45}",
         "May reveal school identity"),
        (r"\b(my date of birth is|date of birth|my birthday is|born on)\s+\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b|\b(date of birth|my birthday is|born on)\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
         "May reveal date of birth"),
        (r"\b(bank account number|account number is|card number)\s*(is|[:=])?\s*\d[\d -]{7,22}\b|\bcvv\s*(is|[:=])\s*\d{3,4}\b",
         "May contain banking or card information"),
        (r"\b(my phone number is|my mobile number is|contact number is)\s*(?:\+?\d[\d\s().-]{7,}\d)",
         "May contain a phone number"),
        (r"\b(my email is|my email address is|contact email is)\s*[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b",
         "May contain an email address")
    ]

    for pattern, reason in patterns:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    if matches(r"\b(password|passcode)\s+for\s+(my|this|the)\s+(account|sample account)\s+(is|:|=)\s*[^\s,.;]{3,}", text):
        reasons.append("May contain a password or passcode")
    if matches(r"\b(my date of birth is|date of birth)\s+\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b", text):
        reasons.append("May reveal date of birth")

    # Multilingual labels are only flagged when accompanied by a plausible
    # value or a clear disclosure phrase. Numeric/email patterns above also
    # work with Telugu, Hindi and Russian text.
    multilingual_privacy = [
        (r"(?:నా పాస్‌వర్డ్|నా పాస్వర్డ్|मेरा पासवर्ड|мой пароль)\s*(?:है|is|:|=)?\s*\S{4,}",
         "May contain a password or passcode"),
        (r"(?:నా ఓటీపీ|నా రహస్య కోడ్|मेरा ओटीपी|मेरा सत्यापन कोड|мой одноразовый пароль|мой код подтверждения)\s*(?:है|:|=)?\s*\d{4,8}",
         "May contain an OTP or verification code"),
        (r"(?:నా ఫోన్ నంబర్|నా మొబైల్ నంబర్|मेरा फोन नंबर|मेरा मोबाइल नंबर|мой номер телефона)\s*(?:है|:|=)?\s*(?:\+?\d[\d\s-]{7,}\d)",
         "May contain a phone number"),
        (r"(?:నా ఇమెయిల్|मेरा ईमेल|моя электронная почта)\s*(?:है|:|=)?\s*[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
         "May contain an email address"),
        (r"(?:నా చిరునామా|मेरा पता|мой адрес)\s*(?:है|:|=)?\s*\d{1,5}\s+\S+",
         "May contain a home address"),
        (r"(?:నా పుట్టిన తేదీ|मेरी जन्मतिथि|моя дата рождения)\s*(?:है|:|=)?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
         "May reveal date of birth")
    ]

    for pattern, reason in multilingual_privacy:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    return len(reasons) > 0, reasons


# ============================================================
# ORIGINAL TEST DATA
# ============================================================

PHISHING_TESTS = [
    ("Share your OTP to receive your cash reward.", True),
    ("Your account will be blocked. Verify your account immediately using this link.", True),
    ("A stranger asks me to pay a fee to release a prize.", True),
    ("Send me your password to fix your account.", True),
    ("An unknown caller asks me to transfer money to protect my savings.", True),
    ("Good morning! See you at school tomorrow.", False),
    ("Please bring your science notebook to class.", False),
    ("Our lesson explains why OTPs should never be shared.", False),
    ("The word urgent appears in today's vocabulary exercise.", False),
    ("I am writing a fictional story about a bank employee.", False)
]

BULLYING_TESTS = [
    ("You are such an idiot and a loser.", True),
    ("Nobody likes you. You have no friends.", True),
    ("They deliberately leave me out of every group activity.", True),
    ("They made a separate group just to mock me.", True),
    ("Someone keeps sharing embarrassing stories about me.", True),
    ("You did a great job in the competition.", False),
    ("Would you like to join our study group?", False),
    ("Our lesson explains why calling someone an idiot is hurtful.", False),
    ("I disagree with your answer.", False),
    ("We discussed how to support someone who feels excluded.", False)
]

PRIVACY_TESTS = [
    ("My password is School12345.", True),
    ("My OTP is 123456.", True),
    ("My phone number is 9876543210.", True),
    ("My email is student@example.com.", True),
    ("My address is 12 Example Street.", True),
    ("I enjoy reading adventure books.", False),
    ("My favourite subject is science.", False),
    ("The teacher explained what an OTP means.", False),
    ("I am preparing for my science exam.", False),
    ("I enjoy learning Python programming.", False)
]


# ============================================================
# CHALLENGE DATA GENERATOR
# ============================================================

def build_challenge(positive, negative):
    """Build a challenge set from unique supplied examples (no repetition)."""
    cases = []
    seen = set()
    for message in positive:
        key = message.strip().casefold()
        if key and key not in seen:
            cases.append((message, True))
            seen.add(key)
    for message in negative:
        key = message.strip().casefold()
        if key and key not in seen:
            cases.append((message, False))
            seen.add(key)
    return cases


# ============================================================
# CHALLENGE EXAMPLES
# ============================================================

FRESH_PHISHING = build_challenge(
    [
        "A delivery notice says my parcel is held until I pay a release charge",
        "A caller claiming to be from my bank asks me to confirm my login details",
        "A stranger promises a scholarship after I pay a registration fee",
        "Someone says I must reveal the digits sent to my phone to finish setup",
        "A message threatens to close my account unless I act before tonight",
        "An unexpected prize notice demands payment before releasing the reward",
        "A stranger asks me to move my savings to a different account for protection",
        "A message says my school account needs its password confirmed immediately",
        "An unknown sender promises a gift if I provide my banking information",
        "A caller pressures me to send funds before explaining the reason",
        "A parcel message asks me to reveal a code before delivery",
        "A stranger says I won a contest I never entered and must pay first",
        "Someone asks me to install an unknown app to restore my account",
        "A message says my account access will disappear unless I respond today",
        "An unknown person requests private details to unlock a reward",
        "A caller claims my account has unusual activity and demands my details",
        "A message offers a refund but asks me to provide account credentials",
        "A stranger says my payment failed and demands another transfer",
        "An unexpected message asks me to confirm my identity through a link",
        "A sender says a small fee is required before a large reward is released"
    ],
    [
        "Our computer lesson explains why OTPs should never be shared",
        "The word urgent appears in today's vocabulary exercise",
        "We discussed how fake scholarship messages can mislead students",
        "Our teacher explained how account suspension scams work",
        "The worksheet asks us to identify different types of web links",
        "I am writing a fictional story about a bank employee",
        "The class presentation explains how to create a strong password",
        "We learned that a genuine prize should not require suspicious payments",
        "My notebook contains a chapter about online safety",
        "The school timetable was updated this morning",
        "I am researching how people recognise suspicious messages",
        "The word password appears in our computer textbook",
        "Our teacher asked us to define verification for homework",
        "The library sent a reminder about returning books",
        "The football practice has moved to the afternoon",
        "I received the normal class notes from my teacher",
        "Our group is preparing a presentation about online fraud",
        "The school exhibition will display our computer project",
        "We are discussing why unknown senders should be checked",
        "The word reward appears in the reading passage"
    ]
)

FRESH_BULLYING = build_challenge(
    [
        "They deliberately leave me out of every group activity",
        "The group chat becomes silent whenever I try to join",
        "They made a separate group just to mock me",
        "Someone keeps sharing embarrassing stories about me",
        "They tell everyone not to sit or work with me",
        "A classmate repeatedly imitates me to embarrass me",
        "They keep making jokes about me after I asked them to stop",
        "Someone encourages others to ignore me",
        "They repeatedly post unkind comments about my work",
        "A person tells others that I should not be included",
        "Someone repeatedly sends unwanted insulting messages",
        "They deliberately spread false stories about me",
        "My classmates laugh whenever I try to speak",
        "They keep telling me that nobody wants me in the team",
        "Someone is trying to turn my friends against me",
        "They share embarrassing pictures of me without permission",
        "A classmate repeatedly targets me with cruel comments online",
        "They exclude me from activities because they dislike me",
        "Someone keeps making a joke out of my mistakes",
        "They pressure others to stop being friends with me"
    ],
    [
        "Our lesson explains why calling someone an idiot is hurtful",
        "The teacher asked us to discuss the word loser in a story",
        "I am writing an essay about how bullying affects students",
        "The school assembly discussed why nobody should be excluded",
        "We are learning how to respond calmly when we disagree",
        "A character in the novel says shut up during an argument",
        "I reported an insulting comment because it was inappropriate",
        "Our class poster says everyone deserves respect",
        "The teacher explained why threats should be taken seriously",
        "I am studying examples of rumours for media literacy",
        "My friend and I disagreed about the correct answer",
        "We invited everyone to join our study group",
        "I appreciated my teammate's helpful feedback",
        "The class discussed how to apologise after an argument",
        "Our group agreed to give everyone a chance to speak",
        "I asked my classmate to explain the homework",
        "The story includes a character who behaves unkindly",
        "We discussed how to support someone who feels excluded",
        "The teacher asked us to identify respectful language",
        "I enjoyed working with my classmates today"
    ]
)

FRESH_PRIVACY = build_challenge(
    [
        "My password is DemoPassword123",
        "My OTP is 000000",
        "My verification code is 000000",
        "My phone number is 0000000000",
        "My email is learner@example.org",
        "My address is 12 Example Street",
        "My school is Sunrise Public School",
        "My date of birth is 12 March 2012",
        "My bank account number is 000000000000",
        "My passcode is DemoCode123",
        "Please save my phone number 0000000000",
        "The password for my account is SamplePass123",
        "My contact email is student@example.org",
        "My home address is 45 Sample Road",
        "I attend Sunrise Public School",
        "My birthday is 15 August 2012",
        "My account number is 111111111111",
        "The passcode for this sample account is Demo123",
        "My card number is 4111 1111 1111 1111 and CVV is 123",
        "My verification code is 123456"
    ],
    [
        "Our lesson explains what an OTP means without showing a real code",
        "I am learning how to create a secure password",
        "The computer textbook explains why email addresses are personal",
        "We discussed why people should protect their phone numbers",
        "The teacher explained what a home address means",
        "Our class is studying digital privacy",
        "The worksheet asks us to define personal information",
        "I am writing about safe ways to use the internet",
        "The lesson explains why students should protect their accounts",
        "We are learning about data protection",
        "My favourite subject is geography",
        "I enjoy playing football after school",
        "The science exhibition begins next week",
        "I am preparing for my mathematics test",
        "Our class is reading an adventure story",
        "The school library has new books",
        "I enjoy learning computer programming",
        "We are preparing a history presentation",
        "My favourite sport is badminton",
        "I watched an educational documentary today"
    ]
)


# ============================================================
# EVALUATION AND METRICS
# ============================================================

def evaluate_guardian(test_data, detector, guardian):
    results = []

    for message, actual_positive in test_data:
        detected, reasons = detector(message)

        if actual_positive and detected:
            outcome = "True Positive"
        elif not actual_positive and not detected:
            outcome = "True Negative"
        elif detected:
            outcome = "False Alarm"
        else:
            outcome = "Missed Warning"

        results.append({
            "Guardian": guardian,
            "Message": message,
            "Actual": "Threat" if actual_positive else "Safe",
            "Prediction": "Threat" if detected else "Safe",
            "Outcome": outcome,
            "Warning Signs": "; ".join(reasons) if reasons else "None"
        })

    df = pd.DataFrame(results)

    tp = sum(df["Outcome"] == "True Positive")
    tn = sum(df["Outcome"] == "True Negative")
    fp = sum(df["Outcome"] == "False Alarm")
    fn = sum(df["Outcome"] == "Missed Warning")

    total = len(df)
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    metrics = {
        "Accuracy": accuracy * 100,
        "Precision": precision * 100,
        "Recall": recall * 100,
        "F1 Score": f1 * 100,
        "False Alarms": fp,
        "Missed Warnings": fn,
        "Correct Normal": tn,
        "Correct Threat": tp,
        "Total Tests": total
    }

    return metrics, df


def get_safety_guidance(title, message, reasons):
    """Return practical next steps based on the Guardian that flagged the message."""
    text = message.casefold()
    guidance = []
    already_acted = []

    if "Phishing" in title:
        guidance = [
            "Do not reply, click links, open attachments, or download anything from the message.",
            "Do not share an OTP, password, PIN, verification code, or banking information.",
            "Check the claim independently using the organisation's official app, website, or a contact number you already trust.",
            "Block and report the sender using the messaging app or email service's built-in tools.",
            "If you are unsure or worried, show the message to a trusted adult."
        ]

        if re.search(r"\b(otp|verification code|password|passcode|pin|bank|card|payment|transfer|money)\b", text):
            already_acted.append(
                "If you already shared sensitive information, tell a trusted adult and contact the service through its official channels."
            )

        if re.search(r"https?://|www\.", text):
            already_acted.append(
                "If you already opened a link, close the page. Do not enter more information or install anything. Ask a trusted adult for help."
            )

    elif "Cyberbullying" in title:
        guidance = [
            "Do not respond with insults or threats; step away from the conversation if you can.",
            "Save a record of the messages or posts if it is safe to do so. Do not forward or repost hurtful content.",
            "Use the platform's block and report features, and adjust who can contact or tag you.",
            "Talk to a trusted adult, parent, teacher, or school counsellor."
        ]

        if re.search(r"\b(threat|hurt|beat|attack|danger|blackmail)\b", text):
            already_acted.append(
                "If someone may hurt you or you feel in immediate danger, move to a safe place and tell a trusted adult or local emergency service."
            )

    else:
        guidance = [
            "Avoid posting or sending personal details such as your address, phone number, school details, passwords, or verification codes.",
            "Delete or remove exposed information where possible.",
            "Review account privacy settings and limit who can view your profile or contact you.",
            "Tell a trusted adult so they can help you secure your accounts."
        ]

        if re.search(r"\b(password|passcode|otp|verification code|pin|bank|card)\b", text):
            already_acted.append(
                "If a password or code was exposed, change the affected password using the official app or website and tell a trusted adult."
            )

    return guidance, already_acted


# ============================================================
# GROQ AI ANALYSIS
# ============================================================

GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"


def get_groq_api_key():
    """Read the Groq API key from Streamlit Secrets."""
    try:
        return str(st.secrets.get("GROQ_API_KEY", "")).strip()
    except Exception:
        return ""


def parse_groq_json(raw_text):
    """Parse and validate the JSON returned by Groq."""
    if not raw_text:
        raise ValueError("Groq returned an empty response.")

    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("Groq response was not valid JSON.")
        return json.loads(match.group(0))


def analyse_with_gemini(guardian_name, message="", audio_bytes=None):
    """
    Backwards-compatible function name so the existing page keeps working.
    Analysis is performed by Groq. Audio is transcribed first with Whisper.
    """
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError(
            "Groq API key is not configured. Add GROQ_API_KEY in Streamlit Secrets."
        )

    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError(
            "The groq package is missing. Add groq to requirements.txt."
        )

    client = Groq(api_key=api_key)
    transcript = ""

    # Groq Whisper converts a recording into text. The language model then
    # analyses that transcript. It does not assess vocal emotion or identity.
    if audio_bytes:
        transcription = client.audio.transcriptions.create(
            file=("schoolshield_recording.wav", audio_bytes),
            model=GROQ_TRANSCRIPTION_MODEL,
            response_format="json",
            temperature=0.0,
        )
        transcript = str(getattr(transcription, "text", "") or "").strip()

    message_text = (message or "").strip()
    if transcript:
        message_text = (
            message_text + "\n\nTRANSCRIBED VOICE MESSAGE:\n" + transcript
        ).strip()

    if not message_text:
        raise ValueError("Enter a fictional message or record a voice example.")

    guardian_guidance = {
        "Phishing Guardian": (
            "Assess possible deception, impersonation, suspicious links, requests "
            "for credentials or codes, unexpected payments, urgency and pressure. "
            "Distinguish warnings about scams from actual scam requests."
        ),
        "Cyberbullying Guardian": (
            "Assess whether language targets, threatens, humiliates, excludes or "
            "repeatedly harms a person. Distinguish disagreement, quotation, "
            "educational discussion or reporting from targeted abuse. Do not label "
            "a person as a bully based on one ambiguous sentence."
        ),
        "Privacy Guardian": (
            "Assess whether the message exposes or requests personal information, "
            "such as passwords, OTPs, phone numbers, email addresses, home or school "
            "details, identity numbers or financial details. Never repeat sensitive values."
        ),
    }

    prompt = f"""
You are the analysis engine for SchoolShield, a student digital-safety
educational prototype.

GUARDIAN: {guardian_name}
TASK: {guardian_guidance.get(guardian_name, "Assess the message for digital safety risks.")}

Analyse meaning and context, not just keywords. The input may be a fictional
example, quotation, lesson, report, or an attempt to cause harm. Do not assume
intent when context is unclear.

Never repeat passwords, OTPs, phone numbers, email addresses, home addresses,
identity numbers, or other sensitive values. If present, name only the category.

For Cyberbullying, do not call ordinary disagreement or one neutral criticism
bullying. Look for targeted harmful language, threats, exclusion, humiliation,
or repeated behaviour where context supports it.

For Phishing, distinguish a warning such as "never share your OTP" from a
message asking someone to share an OTP.

For Privacy, identify exposed sensitive categories without reproducing values.

WARNING SIGN QUALITY RULES:
- Return only 3 to 5 warning signs when evidence supports them.
- Every warning sign must describe a distinct risk.
- Never repeat the same risk using different wording.
- Prefer short, specific descriptions tied to the actual message.
- Do not invent warning signs.
- For privacy risks, identify the information category without repeating its value.
- If fewer than 3 distinct risks exist, return fewer. Do not pad the list.

Classify the apparent wording tone as one or more of:
friendly, neutral, supportive, angry, threatening, pressuring, manipulative,
or unclear. Tone is an interpretation of wording, not proof of a person's
actual emotional state.

If a voice transcript is included, analyse only the transcribed words.
Do not infer identity, age, personality, or true emotional state from a voice.
Vocal delivery is not assessed.

Return ONLY valid JSON with exactly these keys:
{{
  "transcript": "transcribed words, or empty string when no audio",
  "verdict": "Suspicious" or "No clear warning signs" or "Uncertain",
  "risk_level": "High" or "Medium" or "Low" or "Unclear",
  "explanation": "short explanation in simple student-friendly English",
  "context": "brief context interpretation",
  "warning_signs": ["specific warning sign"],
  "next_steps": ["practical safe next step"],
  "tone": ["tone label"],
  "vocal_delivery": "Not assessed"
}}

Do not guarantee safety. If evidence is incomplete, choose Uncertain.
Keep the response concise and suitable for school students.
"""

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a careful digital-safety assistant. Follow the requested JSON format exactly.",
            },
            {
                "role": "user",
                "content": prompt + "\n\nMESSAGE TO ANALYSE:\n" + message_text,
            },
        ],
        temperature=0.2,
        max_tokens=1200,
        response_format={"type": "json_object"},
    )

    raw_text = completion.choices[0].message.content
    result = parse_groq_json(raw_text)

    allowed_verdicts = {
        "Suspicious", "No clear warning signs", "Uncertain"
    }
    if result.get("verdict") not in allowed_verdicts:
        result["verdict"] = "Uncertain"

    if result.get("risk_level") not in {"High", "Medium", "Low", "Unclear"}:
        result["risk_level"] = "Unclear"

    for key in ("warning_signs", "next_steps", "tone"):
        value = result.get(key, [])
        if not isinstance(value, list):
            value = [str(value)] if value else []
        result[key] = [str(item)[:300] for item in value[:8]]

    for key in ("transcript", "explanation", "context", "vocal_delivery"):
        result[key] = str(result.get(key, ""))[:1200]

    # Prefer the actual Whisper transcript over any model-generated transcript.
    result["transcript"] = transcript
    result["vocal_delivery"] = "Not assessed"
    return result


def show_gemini_result(title, message, detector, label, ai_result):
    """
    Backwards-compatible display function. The displayed provider is Groq.
    Existing guardian_page calls can continue using this function name.
    """
    rules_detected, rule_reasons = detector(message)
    ai_suspicious = ai_result["verdict"] == "Suspicious"
    ai_uncertain = ai_result["verdict"] == "Uncertain"

    st.markdown("---")
    st.subheader("🧠 Groq Context Analysis")
    st.caption(
        f"Language model: {GROQ_MODEL} · Voice transcription: {GROQ_TRANSCRIPTION_MODEL}"
    )

    if rules_detected or ai_suspicious:
        st.error(f"⚠️ {label} — warning signs found")
    elif ai_uncertain:
        st.warning("Needs a closer look — Groq is uncertain")
    else:
        st.success("No clear warning signs identified")

    c1, c2 = st.columns(2)
    c1.metric("Risk level", ai_result["risk_level"])
    c2.metric(
        "Wording tone",
        ", ".join(ai_result["tone"]) if ai_result["tone"] else "Unclear",
    )

    if ai_result.get("transcript"):
        st.write("**Voice transcription:**")
        st.info(ai_result["transcript"])

    st.write("**Groq's explanation:**")
    st.write(
        ai_result["explanation"]
        or "Groq did not provide an explanation."
    )

    if ai_result.get("context"):
        st.write("**Context understood:**")
        st.write(ai_result["context"])

    if ai_result["warning_signs"] or rule_reasons:
        st.write("**Warning signs:**")
        combined = []
        seen_signs = []

        def warning_categories(text):
            value = str(text).lower()
            categories = set()
            if re.search(r"\\b(otp|password|passcode|credential|login|verification code|authentication code)\\b", value):
                categories.add("account credentials")
            if re.search(r"\\b(address|phone|email|location|personal information|private information)\\b", value):
                categories.add("personal information")
            if re.search(r"\\b(urgent|urgency|quickly|immediately|pressure|pressuring|threat|blocked|permanent|act fast)\\b", value):
                categories.add("pressure or threat")
            if re.search(r"\\b(prize|free|reward|gift|offer|winner)\\b", value):
                categories.add("lure or reward")
            if re.search(r"\\b(exclu|humiliat|insult|unwanted|nobody wants|not welcome|targeting)\\b", value):
                categories.add("bullying or exclusion")
            if re.search(r"\\b(link|click|website|url|download|attachment)\\b", value):
                categories.add("suspicious link or file")
            return categories

        for item in ai_result["warning_signs"] + rule_reasons:
            if not item:
                continue

            original = str(item).strip()
            clean_item = " ".join(original.lower().split())
            clean_item = re.sub(r"[^a-z0-9 ]", "", clean_item)
            clean_item = re.sub(r"\\b(may contain|contains|exposed|possible|potential|detected|indicates)\\b", "", clean_item)
            clean_item = re.sub(r"\\s+", " ", clean_item).strip()
            words = set(clean_item.split())
            categories = warning_categories(original)

            duplicate = False
            for existing_text, existing_words, existing_categories in seen_signs:
                word_union = words | existing_words
                word_overlap = len(words & existing_words) / max(1, len(word_union))
                category_overlap = (
                    len(categories & existing_categories) / max(1, min(len(categories), len(existing_categories)))
                    if categories and existing_categories else 0
                )
                if clean_item == existing_text or word_overlap >= 0.60 or category_overlap >= 0.80:
                    duplicate = True
                    break

            if clean_item and not duplicate:
                combined.append(original)
                seen_signs.append((clean_item, words, categories))

        for item in combined[:5]:
            st.markdown("- " + item)
    else:
        st.write("**Warning signs:** No specific warning signs were identified.")

    st.caption(
        "Vocal delivery is not assessed. A transcript may contain recognition errors."
    )

    st.write("**Suggested next steps:**")
    steps = ai_result["next_steps"]
    if not steps:
        steps, _ = get_safety_guidance(title, message, rule_reasons)
    for index, step in enumerate(steps[:6], start=1):
        st.markdown(f"{index}. {step}")

    if rules_detected and not ai_suspicious:
        st.warning(
            "The existing safety rules found a warning sign even though Groq "
            "did not classify the message as suspicious. SchoolShield keeps "
            "that warning visible rather than silently dismissing it."
        )

    st.info(
        "SchoolShield is an educational aid, not a guaranteed detector. "
        "If a message worries you, check with a trusted adult."
    )


# ============================================================
# GUARDIAN PAGE
# ============================================================

def guardian_page(title, description, detector, samples, label):
    # Built-in futuristic Guardian artwork: no extra image files or uploads needed.
    phishing_art = r'''<svg viewBox="0 0 720 470" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Phishing Guardian digital shield illustration" style="width:100%;height:auto;border-radius:22px;background:#090B1B"><defs><linearGradient id="pbg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#21104B"/><stop offset="1" stop-color="#071B35"/></linearGradient><linearGradient id="psh" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#A78BFA"/><stop offset="1" stop-color="#22D3EE"/></linearGradient><filter id="pg"><feGaussianBlur stdDeviation="12"/></filter></defs><rect width="720" height="470" rx="26" fill="url(#pbg)"/><circle cx="360" cy="220" r="150" fill="#7C3AED" opacity=".18" filter="url(#pg)"/><g fill="none" stroke="#6D5AE8" opacity=".25"><path d="M0 90H720M0 180H720M0 270H720M0 360H720M120 0V470M240 0V470M480 0V470M600 0V470"/></g><path d="M360 76 493 126V230c0 91-56 143-133 180-77-37-133-89-133-180V126Z" fill="#11152E" stroke="url(#psh)" stroke-width="8"/><path d="M360 106 466 145V230c0 70-40 112-106 147-66-35-106-77-106-147V145Z" fill="#171A3C" stroke="#8B5CF6" stroke-width="2"/><path d="M315 208c0-25 20-45 45-45s45 20 45 45v18h-90Z" fill="none" stroke="#67E8F9" stroke-width="9"/><rect x="300" y="220" width="120" height="83" rx="13" fill="#7C3AED" stroke="#C4B5FD" stroke-width="4"/><circle cx="360" cy="258" r="9" fill="#E0F2FE"/><path d="M360 267v16" stroke="#E0F2FE" stroke-width="7" stroke-linecap="round"/><path d="m164 150 28 28m0-28-28 28M530 290l28 28m0-28-28 28" stroke="#22D3EE" stroke-width="5" stroke-linecap="round"/><circle cx="170" cy="310" r="9" fill="#A78BFA"/><circle cx="550" cy="130" r="7" fill="#22D3EE"/><text x="360" y="425" fill="#C4B5FD" font-family="Arial,sans-serif" font-size="18" font-weight="700" text-anchor="middle" letter-spacing="5">VERIFY BEFORE YOU CLICK</text></svg>'''
    cyber_art = r'''<svg viewBox="0 0 720 470" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cyberbullying Guardian supportive digital conversation illustration" style="width:100%;height:auto;border-radius:22px;background:#090B1B"><defs><linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#241044"/><stop offset="1" stop-color="#071C36"/></linearGradient><linearGradient id="cglow"><stop stop-color="#A78BFA"/><stop offset="1" stop-color="#22D3EE"/></linearGradient><filter id="cg"><feGaussianBlur stdDeviation="15"/></filter></defs><rect width="720" height="470" rx="26" fill="url(#cbg)"/><circle cx="360" cy="220" r="150" fill="#0EA5E9" opacity=".18" filter="url(#cg)"/><g fill="none" stroke="#6474D9" opacity=".2"><path d="M0 100H720M0 200H720M0 300H720M0 400H720M120 0V470M240 0V470M480 0V470M600 0V470"/></g><rect x="150" y="92" width="420" height="260" rx="28" fill="#11152E" stroke="url(#cglow)" stroke-width="5"/><path d="M205 165h190a18 18 0 0 1 18 18v48a18 18 0 0 1-18 18H265l-35 26v-26h-25a18 18 0 0 1-18-18v-48a18 18 0 0 1 18-18Z" fill="#31205B" stroke="#A78BFA" stroke-width="3"/><circle cx="245" cy="207" r="7" fill="#C4B5FD"/><circle cx="278" cy="207" r="7" fill="#C4B5FD"/><circle cx="311" cy="207" r="7" fill="#C4B5FD"/><path d="M325 275h165a18 18 0 0 1 18 18v28a18 18 0 0 1-18 18H385l-34 23v-23h-26a18 18 0 0 1-18-18v-28a18 18 0 0 1 18-18Z" fill="#12354C" stroke="#22D3EE" stroke-width="3"/><path d="m370 302 13 13 27-29" fill="none" stroke="#67E8F9" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><path d="M360 68v-18m-9 9h18M580 370v-18m-9 9h18" stroke="#A78BFA" stroke-width="4" stroke-linecap="round"/><text x="360" y="430" fill="#C4B5FD" font-family="Arial,sans-serif" font-size="18" font-weight="700" text-anchor="middle" letter-spacing="4">KINDNESS. SAFETY. SUPPORT.</text></svg>'''
    privacy_art_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1000&q=85"
    intro, visual = st.columns([1.35, 0.85], vertical_alignment="center")
    with intro:
        st.markdown("<div style='color:#67E8F9;font-size:12px;font-weight:800;letter-spacing:2px;'>SCHOOLSHIELD / PROTECTION MODULE</div>", unsafe_allow_html=True)
        st.title(title)
        st.write(description)
        st.caption("Explore a fictional example, then review the warning signs and safety guidance.")
    with visual:
        if "Phishing Guardian" in title:
            st.markdown(phishing_art, unsafe_allow_html=True)
        elif "Cyberbullying Guardian" in title:
            st.markdown(cyber_art, unsafe_allow_html=True)
        else:
            st.image(privacy_art_url, use_container_width=True)
    st.markdown("---")
    st.markdown(
        "<div style='padding:12px 16px;border:1px solid rgba(167,139,250,.28);border-radius:14px;background:linear-gradient(100deg,rgba(124,58,237,.14),rgba(8,145,178,.08));color:#C4B5FD;font-size:12px;font-weight:850;letter-spacing:1.5px;'>✦ GUARDIAN SCAN CONSOLE&nbsp;&nbsp; / &nbsp;&nbsp; FICTIONAL EXAMPLES ONLY</div>",
        unsafe_allow_html=True
    )

    options = ["Choose an example"] + [
        f"Example {i + 1}" for i in range(len(samples))
    ]
    selected = st.selectbox("Try a sample message", options, key=title + "_sample")
    sample = ""
    if selected != "Choose an example":
        sample = samples[int(selected.split()[-1]) - 1]

    message = st.text_area(
        "Enter a fictional message:",
        value=sample,
        height=130,
        key=title + "_message"
    )

    st.caption(
        "Use fictional examples only. Do not enter real passwords, OTPs, "
        "contact details, private conversations or identifying information."
    )

    consent = st.checkbox(
        "I understand that the fictional text or recording I submit will be sent "
        "to Groq for analysis. I will not submit real private information "
        "or another person's private voice/message.",
        value=False,
        key=title + "_gemini_consent"
    )

    audio_recording = None
    if consent:
        with st.expander("🎙️ Optional voice message analysis"):
            st.write(
                "Record a short fictional example using your own voice. Groq Whisper transcribes it, then Groq analyses the words. "
                "Vocal delivery is not assessed."
            )
            if hasattr(st, "audio_input"):
                audio_recording = st.audio_input(
                    "Record a fictional voice example",
                    key=title + "_audio"
                )
                if audio_recording is not None:
                    st.audio(audio_recording)
            else:
                st.info(
                    "Voice recording requires a newer Streamlit version. "
                    "Update requirements.txt to streamlit>=1.40.0."
                )
    else:
        st.info("Confirm the data-sharing notice above to enable Groq analysis and microphone recording.")
    if st.button("⚡ Analyse instantly", key=title + "_instant"):
        if not message.strip():
            st.warning("Enter a fictional message or use voice transcription first.")
        else:
            detected, reasons = detector(message.strip())
            st.markdown("### ⚡ Instant rule-based result")

            if detected:
                st.warning("Possible warning signs detected:")
                for reason in reasons:
                    st.markdown("- " + reason)

                guidance, already_acted = get_safety_guidance(
                    title, message.strip(), reasons
                )

                st.markdown("**What you can do next:**")
                for step in guidance:
                    st.markdown("- " + step)

                if already_acted:
                    st.markdown("**If you already did this:**")
                    for step in already_acted:
                        st.markdown("- " + step)
            else:
                st.info("The existing rules found no warning signs in this example.")
    if st.button("🧠 Add Groq explanation", key=title + "_analyse"):
        if not message.strip() and audio_recording is None:
            st.warning("Enter a fictional message or record a fictional voice example.")
        elif not consent:
            st.warning("Please confirm the data-sharing notice before using Groq.")
        else:
            audio_bytes = audio_recording.getvalue() if audio_recording is not None else None
            with st.spinner("Groq is analysing the message context..."):
                try:
                    ai_result = analyse_with_gemini(
                        title,
                        message=message,
                        audio_bytes=audio_bytes
                    )
                    analysed_message = message.strip()
                    if not analysed_message and ai_result.get("transcript"):
                        analysed_message = ai_result["transcript"]
                    show_gemini_result(
                        title,
                        analysed_message,
                        detector,
                        label,
                        ai_result
                    )
                except Exception as error:
                    st.error(
                        "Groq explanation is unavailable right now. "
                        "Your instant rule-based result is separate and can "
                        "still be used."
                    )
                    safe_detail = str(error).strip() or "No additional error details were provided."
                    safe_detail = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[API KEY HIDDEN]", safe_detail)
                    safe_detail = re.sub(
                        r"(?i)(api[_ -]?key\s*[:=]\s*)[^\s,;]+",
                        r"\1[HIDDEN]",
                        safe_detail,
                    )
                    with st.expander("Technical details (API key hidden)"):
                        st.caption("Error type: " + type(error).__name__)
                        st.code(safe_detail[:1200])


# ============================================================
# CHALLENGE EVALUATION HELPER
# ============================================================

def get_challenge_results():
    fresh_tests = {
        "Phishing Guardian": (FRESH_PHISHING, detect_phishing),
        "Cyberbullying Guardian": (FRESH_BULLYING, detect_bullying),
        "Privacy Guardian": (FRESH_PRIVACY, detect_privacy)
    }

    rows = []
    detailed = []

    for name, (tests, detector) in fresh_tests.items():
        metrics, df = evaluate_guardian(tests, detector, name)
        rows.append({"Guardian": name, **metrics})
        detailed.append((name, metrics, df))

    summary = pd.DataFrame(rows)
    all_results = pd.concat(
        [item[2] for item in detailed],
        ignore_index=True
    )

    return summary, detailed, all_results


# ============================================================
# PRIVATE DEVELOPER AUTHENTICATION
# ============================================================

if "developer_authenticated" not in st.session_state:
    st.session_state.developer_authenticated = False

st.sidebar.title("🛡️ SchoolShield")
st.sidebar.caption("One Platform. Three Layers of Protection.")

if get_groq_api_key():
    st.sidebar.caption("🧠 Groq API key detected in Secrets")
else:
    st.sidebar.caption("⚙️ Groq API key not detected — check Streamlit Secrets")

with st.sidebar.expander("🛠️ Developer Access"):

    if st.session_state.developer_authenticated:

        st.success("Developer access granted")

        if st.button("🔒 Log Out", key="developer_logout"):
            st.session_state.developer_authenticated = False
            st.session_state.navigation_page = "Dashboard"
            st.rerun()

    else:

        with st.form("developer_login_form"):
            entered_password = st.text_input(
                "Developer password",
                type="password"
            )

            login_submitted = st.form_submit_button(
                "Unlock Developer Mode"
            )

        if login_submitted:
            try:
                saved_password = str(
                    st.secrets["developer"]["password"]
                )

                if hmac.compare_digest(
                    entered_password,
                    saved_password
                ):
                    st.session_state.developer_authenticated = True
                    st.success("Developer access granted")
                    st.rerun()
                else:
                    st.error("Incorrect password")

            except Exception:
                st.error(
                    "Developer access is not configured. "
                    "Check Streamlit Secrets."
                )

developer_mode = st.session_state.developer_authenticated


# ============================================================
# NAVIGATION
# ============================================================

navigation_options = [
    "Dashboard",
    "Phishing Guardian",
    "Cyberbullying Guardian",
    "Privacy Guardian"
]

if developer_mode:
    navigation_options.extend([
        "Performance Lab",
        "Independent Test Lab"
    ])

if (
    "navigation_page" not in st.session_state
    or st.session_state.navigation_page not in navigation_options
):
    st.session_state.navigation_page = "Dashboard"

# Main navigation is displayed across the top of the app.
st.markdown("""
<style>
/* Holographic top navigation */
div[role="radiogroup"] {
    display:flex; flex-direction:row; flex-wrap:wrap; gap:.5rem;
    padding:.65rem .75rem; background:rgba(18,11,35,.96);
    border:1px solid rgba(167,139,250,.30); border-radius:16px;
    margin:.25rem 0 1.25rem;
    box-shadow:0 8px 28px rgba(0,0,0,.22);
}
div[role="radiogroup"] label {
    background:#100A1D; border:1px solid #302044; border-radius:11px;
    padding:.5rem .9rem; margin:0 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background:linear-gradient(110deg,#32105F,#37308A,#07566B);
    border-color:#67E8F9; box-shadow:0 0 18px rgba(139,92,246,.25);
}
@media(max-width:640px) { div[role="radiogroup"] label { padding:.4rem .55rem; } }
</style>
""", unsafe_allow_html=True)

page = st.radio(
    "NAVIGATION",
    navigation_options,
    horizontal=True,
    key="navigation_page",
    label_visibility="collapsed"
)

# Animate the content only when switching between the three Guardian modules.
# Streamlit reruns the script on navigation, so this detects a genuine page change.
guardian_pages = {
    "Phishing Guardian",
    "Cyberbullying Guardian",
    "Privacy Guardian",
}
previous_page = st.session_state.get("schoolshield_previous_page")
if page in guardian_pages and previous_page in guardian_pages and page != previous_page:
    st.markdown("""
    <style>
    @keyframes ssGuardianEnter {
        0%   { opacity: 0; transform: translate3d(0, 22px, 0) scale(.992); filter: blur(5px); }
        55%  { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate3d(0, 0, 0) scale(1); filter: blur(0); }
    }
    @keyframes ssGuardianSweep {
        0% { transform: translateX(-110%); opacity: 0; }
        18% { opacity: .75; }
        100% { transform: translateX(110%); opacity: 0; }
    }
    div[data-testid="stMainBlockContainer"] {
        animation: ssGuardianEnter .68s cubic-bezier(.2,.75,.25,1) both !important;
        position: relative;
    }
    div[data-testid="stMainBlockContainer"]::after {
        content: ""; position: fixed; pointer-events: none; z-index: 999;
        top: 0; left: 0; width: 38%; height: 3px;
        background: linear-gradient(90deg, transparent, #67e8f9, #a78bfa, transparent);
        box-shadow: 0 0 18px #22d3ee, 0 0 32px rgba(167,139,250,.55);
        animation: ssGuardianSweep .72s ease-out both;
    }
    @media (prefers-reduced-motion: reduce) {
        div[data-testid="stMainBlockContainer"] { animation: none !important; }
        div[data-testid="stMainBlockContainer"]::after { display:none !important; }
    }
    </style>
    <div aria-hidden="true" style="height:0;overflow:hidden">Guardian transition</div>
    """, unsafe_allow_html=True)

st.session_state.schoolshield_previous_page = page
st.caption("Student-built educational prototype")


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    hero_text, hero_art = st.columns([1.15, 0.85], vertical_alignment="center")
    with hero_text:
        st.markdown(
            "<div style='display:inline-block;padding:8px 14px;border:1px solid rgba(167,139,250,.48);border-radius:30px;background:linear-gradient(100deg,rgba(124,58,237,.20),rgba(8,145,178,.13));color:#C4B5FD;font-size:12px;font-weight:900;letter-spacing:1.8px;box-shadow:0 0 24px rgba(139,92,246,.16);'>✦ AI FUTURISTIC DIGITAL SAFETY SYSTEM</div>",
            unsafe_allow_html=True
        )
        st.title("Your digital world.\nA little safer.")
        st.subheader("One Platform. Three Layers of Protection.")
        st.write(
            "A student-focused digital safety command centre that helps identify suspicious messages, potentially harmful language and possible privacy risks."
        )
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px;'>"
            "<span style='padding:7px 11px;border:1px solid rgba(103,232,249,.3);border-radius:30px;background:rgba(8,145,178,.12);color:#A5F3FC;font-size:12px;'>✦ PHISHING DEFENCE</span>"
            "<span style='padding:7px 11px;border:1px solid rgba(167,139,250,.3);border-radius:30px;background:rgba(124,58,237,.12);color:#DDD6FE;font-size:12px;'>✦ CYBERBULLYING AWARENESS</span>"
            "<span style='padding:7px 11px;border:1px solid rgba(74,222,128,.3);border-radius:30px;background:rgba(22,163,74,.10);color:#BBF7D0;font-size:12px;'>✦ PRIVACY PROTECTION</span>"
            "</div>",
            unsafe_allow_html=True
        )
        st.caption("THINK CLEARLY  •  CHECK CAREFULLY  •  STAY SAFE ONLINE")
    with hero_art:
        st.image(
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=90",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### THE SCHOOLSHIELD SYSTEM")
    x, y, z, w = st.columns(4)
    x.metric("Protection layers", "03")
    y.metric("Original examples", "30")
    z.metric("Challenge examples", "120")
    w.metric("Total test examples", "150")


    st.markdown("### YOUR THREE GUARDIANS")
    st.caption("Three focused layers designed to help students recognise common digital-safety risks.")
    g1, g2, g3 = st.columns(3, gap="medium")
    with g1:
        st.markdown("""
        <div class="guardian-showcase">
          <div class="symbol">🎣</div>
          <div class="eyebrow">GUARDIAN 01 / MESSAGE SECURITY</div>
          <div class="name">Phishing Guardian</div>
          <div class="desc">Spot suspicious requests, unexpected rewards, pressure tactics and risky links.</div>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown("""
        <div class="guardian-showcase">
          <div class="symbol">💬</div>
          <div class="eyebrow">GUARDIAN 02 / ONLINE WELLBEING</div>
          <div class="name">Cyberbullying Guardian</div>
          <div class="desc">Recognise potentially harmful, humiliating, threatening or exclusionary language.</div>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown("""
        <div class="guardian-showcase">
          <div class="symbol">🔒</div>
          <div class="eyebrow">GUARDIAN 03 / PERSONAL DATA</div>
          <div class="name">Privacy Guardian</div>
          <div class="desc">Identify possible exposure of passwords, contact details and other private information.</div>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "Choose a Guardian from the navigation menu to begin. Groq provides context-aware explanations when enabled; rule-based checks remain a separate backup."
    )


# ============================================================
# PHISHING GUARDIAN PAGE
# ============================================================

elif page == "Phishing Guardian":

    guardian_page(
        "🎣 Phishing Guardian",
        "Finds common warning signs in suspicious messages.",
        detect_phishing,
        [x[0] for x in PHISHING_TESTS],
        "Possible phishing"
    )


# ============================================================
# CYBERBULLYING GUARDIAN PAGE
# ============================================================

elif page == "Cyberbullying Guardian":

    guardian_page(
        "💬 Cyberbullying Guardian",
        "Checks for potentially harmful or targeted language.",
        detect_bullying,
        [x[0] for x in BULLYING_TESTS],
        "Potentially harmful language"
    )


# ============================================================
# PRIVACY GUARDIAN PAGE
# ============================================================

elif page == "Privacy Guardian":

    guardian_page(
        "🔒 Privacy Guardian",
        "Checks for possible personal or sensitive information.",
        detect_privacy,
        [x[0] for x in PRIVACY_TESTS],
        "Possible privacy risk"
    )


# ============================================================
# PERFORMANCE LAB — PRIVATE
# ============================================================

elif page == "Performance Lab" and developer_mode:

    st.title("📊 SchoolShield Performance Lab")

    st.write(
        "Compare the Guardians using the original demonstration examples "
        "and the 120-example unique challenge dataset."
    )

    st.warning(
        "These are synthetic examples, not an independent real-world benchmark. "
        "These metrics evaluate the existing rule-based detectors only; "
        "Groq AI performance is not included in these scores."
    )

    st.markdown("---")
    st.subheader("Original Demonstration Performance")

    original = [
        ("Phishing Guardian", PHISHING_TESTS, detect_phishing),
        ("Cyberbullying Guardian", BULLYING_TESTS, detect_bullying),
        ("Privacy Guardian", PRIVACY_TESTS, detect_privacy)
    ]

    original_rows = []

    for name, tests, detector in original:
        metrics, df = evaluate_guardian(tests, detector, name)
        original_rows.append({"Guardian": name, **metrics})

    original_summary = pd.DataFrame(original_rows)

    original_columns = [
        "Guardian",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "False Alarms",
        "Missed Warnings"
    ]

    original_shown = original_summary[original_columns].copy()

    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        original_shown[col] = original_shown[col].map(
            lambda x: f"{x:.1f}%"
        )

    st.dataframe(
        original_shown,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Unique Challenge Performance")

    challenge_summary, detailed, all_results = get_challenge_results()

    challenge_columns = [
        "Guardian",
        "Total Tests",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "False Alarms",
        "Missed Warnings"
    ]

    challenge_shown = challenge_summary[challenge_columns].copy()

    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        challenge_shown[col] = challenge_shown[col].map(
            lambda x: f"{x:.1f}%"
        )

    st.dataframe(
        challenge_shown,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "The challenge set contains unique supplied examples. "
        "Results describe performance on this specific test set only."
    )


# ============================================================
# INDEPENDENT TEST LAB — PRIVATE
# ============================================================

elif page == "Independent Test Lab" and developer_mode:

    st.title("🧪 SchoolShield Hard Challenge Lab")

    st.write(
        "A set of 120 unique synthetic challenge examples designed "
        "to test detection, missed warnings and false alarms."
    )

    st.warning(
        "These are curated synthetic examples. Some templates are repeated. "
        "Scores apply only to this dataset, not to real-world performance."
    )

    summary, detailed, all_results = get_challenge_results()

    st.markdown("---")
    st.subheader("Challenge Performance Comparison")

    columns = [
        "Guardian",
        "Total Tests",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "False Alarms",
        "Missed Warnings"
    ]

    shown = summary[columns].copy()

    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        shown[col] = shown[col].map(lambda x: f"{x:.1f}%")

    st.dataframe(
        shown,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # AUTOMATIC MISTAKE ANALYZER — PRIVATE
    # --------------------------------------------------------

    st.markdown("---")
    st.title("🔍 Automatic Mistake Analyzer")

    st.write(
        "Automatically finds messages that the Guardians failed "
        "to detect or incorrectly flagged."
    )

    guardian_choice = st.selectbox(
        "Choose a Guardian to analyse",
        [
            "All Guardians",
            "Phishing Guardian",
            "Cyberbullying Guardian",
            "Privacy Guardian"
        ],
        key="analyzer_guardian"
    )

    outcome_choice = st.selectbox(
        "Choose which mistakes to view",
        [
            "Missed Warnings",
            "False Alarms",
            "All Mistakes"
        ],
        key="analyzer_outcome"
    )

    filtered = all_results.copy()

    if guardian_choice != "All Guardians":
        filtered = filtered[
            filtered["Guardian"] == guardian_choice
        ]

    if outcome_choice == "Missed Warnings":
        filtered = filtered[
            filtered["Outcome"] == "Missed Warning"
        ]

    elif outcome_choice == "False Alarms":
        filtered = filtered[
            filtered["Outcome"] == "False Alarm"
        ]

    else:
        filtered = filtered[
            filtered["Outcome"].isin(
                ["Missed Warning", "False Alarm"]
            )
        ]

    missed_count = len(
        filtered[filtered["Outcome"] == "Missed Warning"]
    )

    false_count = len(
        filtered[filtered["Outcome"] == "False Alarm"]
    )

    a, b, c = st.columns(3)

    a.metric("Mistakes Found", len(filtered))
    b.metric("Missed Warnings", missed_count)
    c.metric("False Alarms", false_count)

    st.markdown("---")

    if filtered.empty:
        st.success("No mistakes found for this selection!")

    else:
        st.subheader("Messages Requiring Improvement")

        st.dataframe(
            filtered[
                [
                    "Guardian",
                    "Message",
                    "Actual",
                    "Prediction",
                    "Outcome",
                    "Warning Signs"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download These Mistakes",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="schoolshield_mistake_analysis.csv",
            mime="text/csv",
            key="download_mistakes"
        )

    # --------------------------------------------------------
    # DETAILED RESULTS
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("Detailed Challenge Results")

    for name, metrics, df in detailed:

        with st.expander(name + " — View all unique tests"):

            a, b, c, d = st.columns(4)

            a.metric("Accuracy", f"{metrics['Accuracy']:.1f}%")
            b.metric("Precision", f"{metrics['Precision']:.1f}%")
            c.metric("Recall", f"{metrics['Recall']:.1f}%")
            d.metric("F1 Score", f"{metrics['F1 Score']:.1f}%")

            e, f, g = st.columns(3)

            e.metric("False Alarms", metrics["False Alarms"])
            f.metric("Missed Warnings", metrics["Missed Warnings"])
            g.metric("Total Tests", metrics["Total Tests"])

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇️ Download CSV Results",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=name.lower().replace(" ", "_") + "_hard_challenge.csv",
                mime="text/csv",
                key="download_" + name
            )

    # --------------------------------------------------------
    # DOWNLOAD ALL TESTS
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("Download All 120 Unique Challenge Tests")

    st.download_button(
        "⬇️ Download Complete Challenge Dataset",
        data=all_results.to_csv(index=False).encode("utf-8"),
        file_name="schoolshield_120_unique_challenge_tests.csv",
        mime="text/csv"
    )

    st.caption(
        "Each Guardian is evaluated on 40 unique synthetic examples (20 labelled threat and "
        "20 labelled safe). These are educational test cases, not a real-world accuracy guarantee."
    )

    st.info(
        "True Positive: a threat correctly detected. "
        "True Negative: a safe message correctly accepted. "
        "False Alarm: a safe message flagged. "
        "Missed Warning: a threat not detected."
    )


# ============================================================
# UNEXPECTED PAGE FALLBACK
# ============================================================

elif page in ["Performance Lab", "Independent Test Lab"]:

    st.session_state.navigation_page = "Dashboard"
    st.warning("Developer access is required for this page.")
    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "SchoolShield | Student-built digital safety prototype. "
    "It may miss threats or flag harmless messages. "
    "Never enter real passwords, OTPs, phone numbers or private messages. "
    "Use only your own voice for fictional recordings. "
    "Submitted fictional examples are sent to Groq when AI analysis is used."
)
