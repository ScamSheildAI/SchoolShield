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
        if st.button("ENTER SCHOOLSHIELD  →", use_container_width=True):
            st.session_state.schoolshield_intro_complete = True
            st.rerun()


# ============================================================
# MAIN SCHOOLSHIELD APPLICATION
# ============================================================
if st.session_state.schoolshield_intro_complete:
    st.title("🛡️ SchoolShield")
    st.caption("One Platform. Three Layers of Protection.")

    tab1, tab2, tab3 = st.tabs([
        "Phishing Guardian",
        "Cyberbullying Guardian",
        "Privacy Guardian",
    ])

    with tab1:
        st.subheader("Phishing Guardian")
        msg_input = st.text_area("Paste a suspicious message, email, or link:")
        if st.button("Analyze Message", key="phishing_btn"):
            if msg_input.strip():
                st.info("Analysis complete. Add your detection rules or model here.")
            else:
                st.warning("Please enter text to analyze.")

    with tab2:
        st.subheader("Cyberbullying Guardian")
        st.write("Monitor and flag harmful or abusive messages.")

    with tab3:
        st.subheader("Privacy Guardian")
        st.write("Check for exposed personal or sensitive student information.")
