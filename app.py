
import streamlit as st
import re
import pandas as pd

# ==========================================
# SCHOOLSHIELD — MAIN APPLICATION
# ==========================================

st.set_page_config(
    page_title="SchoolShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: #0b1120;
    color: #f1f5f9;
}
section[data-testid="stSidebar"] {
    background: #111c30;
}
h1, h2, h3 {
    color: #e2eaff;
}
p, label {
    color: #cbd5e1;
}
div.stButton > button {
    background: linear-gradient(90deg,#2563eb,#6366f1);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 25px;
    font-weight: bold;
}
div.stButton > button:hover {
    background: #3b82f6;
    color: white;
}
[data-testid="stMetric"] {
    background: #14213a;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263957;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DETECTION ENGINES ----------------

def phishing_guardian(message):
    text = message.lower()
    warnings = []

    patterns = {
        "Password request": r"\b(send|share|enter|reveal|provide)\b.{0,35}\b(password|passcode|login details)\b",
        "OTP request": r"\b(send|share|tell|provide)\b.{0,25}\b(otp|one.time code|verification code)\b",
        "Urgency": r"\b(immediately|urgent|right now|within \d+ minutes|act fast)\b",
        "Account threat": r"\b(account.*(blocked|suspended|locked)|cancelled|lose access)\b",
        "Payment pressure": r"\b(pay|transfer|payment)\b.{0,35}\b(now|immediately|fee|claim)\b",
        "Suspicious link": r"https?://[^\s]+"
    }

    for name, pattern in patterns.items():
        if re.search(pattern, text):
            warnings.append(name)

    detected = len(warnings) >= 2 or any(
        x in warnings for x in ["Password request", "OTP request"]
    )

    return detected, warnings


def cyberbullying_guardian(message):
    text = message.lower()
    warnings = []

    patterns = {
        "Personal insults": r"\b(useless|stupid|idiot|worthless|pathetic)\b",
        "Humiliation": r"\b(everyone.*laugh|embarrass you|make fun of you)\b",
        "Threatening language": r"\b(you will regret|you'll regret|scared of me)\b",
        "Targeted exclusion": r"\b(nobody wants you|leave this group|nobody likes you)\b",
        "Repeated harassment": r"\b(keep|always|every day)\b.{0,30}\b(insult|mock|bully|harass)\w*\b"
    }

    for name, pattern in patterns.items():
        if re.search(pattern, text):
            warnings.append(name)

    reporting_context = any(x in text for x in [
        "reported it", "help me report", "someone said",
        "teacher", "story describes", "fictional villain"
    ])

    return bool(warnings) and not reporting_context, warnings


def privacy_guardian(message):
    warnings = []

    patterns = {
        "Email address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "Possible password": r"\bpassword\s*[:=]\s*\S+|\bmy password is\s+\S+",
        "Possible OTP": r"\b(?:otp|verification code)\s*[:=]?\s*\d{4,8}\b",
        "Phone-number pattern": r"(?<!\d)(?:\+?\d[\s-]?){9,12}(?!\d)"
    }

    for name, pattern in patterns.items():
        if re.search(pattern, message, re.IGNORECASE):
            warnings.append(name)

    return bool(warnings), warnings


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("# 🛡️ SchoolShield")
    st.caption("Digital Safety Platform")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "🎣 Phishing Guardian",
         "💬 Cyberbullying Guardian", "🔒 Privacy Guardian"]
    )

    st.divider()
    st.caption("SCHOOLSHIELD")
    st.caption("One Platform. Three Layers of Protection.")
    st.caption("Educational prototype • Version 1.0")


# ---------------- DASHBOARD ----------------

st.markdown("# 🛡️ SchoolShield")
st.caption("SMART DIGITAL PROTECTION FOR STUDENTS")

if page == "🏠 Dashboard":

    st.markdown("## Welcome to SchoolShield")
    st.write(
        "An educational digital safety platform designed "
        "to help students recognise online risks."
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🎣")
        st.subheader("Phishing Guardian")
        st.write("Identify suspicious messages, fake requests and warning signs.")

    with c2:
        st.markdown("### 💬")
        st.subheader("Cyberbullying Guardian")
        st.write("Recognise harmful language, intimidation and targeted insults.")

    with c3:
        st.markdown("### 🔒")
        st.subheader("Privacy Guardian")
        st.write("Identify possible exposure of sensitive information.")

    st.divider()

    st.markdown("## How SchoolShield works")

    a, b, c = st.columns(3)

    a.info("**01 — INPUT**\n\nEnter a message for analysis.")
    b.info("**02 — ANALYSIS**\n\nThe selected guardian checks for warning signs.")
    c.info("**03 — RESULTS**\n\nUnderstand the result and receive safety guidance.")

    st.warning(
        "SchoolShield is a student-built educational prototype. "
        "Its automated results can be incorrect. Do not enter real "
        "passwords, OTPs, phone numbers or private information."
    )


# ---------------- GUARDIAN PAGES ----------------

guardians = {
    "🎣 Phishing Guardian": {
        "description": "Check messages for possible online scams.",
        "function": phishing_guardian,
        "tips": [
            "Never share passwords or verification codes.",
            "Check links carefully before opening them.",
            "Verify unexpected requests through official channels.",
            "Be cautious of urgent payment demands."
        ]
    },
    "💬 Cyberbullying Guardian": {
        "description": "Check text for potentially harmful or targeted language.",
        "function": cyberbullying_guardian,
        "tips": [
            "Treat others respectfully online.",
            "Do not encourage group harassment.",
            "Save relevant evidence and report harmful behaviour.",
            "Talk to a trusted adult if someone is being targeted."
        ]
    },
    "🔒 Privacy Guardian": {
        "description": "Check for possible exposure of sensitive information.",
        "function": privacy_guardian,
        "tips": [
            "Keep passwords and verification codes private.",
            "Avoid posting personal information publicly.",
            "Use strong, unique passwords.",
            "Remove sensitive information before sharing messages."
        ]
    }
}

if page in guardians:

    guardian = guardians[page]

    st.markdown(f"## {page}")
    st.write(guardian["description"])

    st.divider()

    st.markdown("### Enter your sample message")

    message = st.text_area(
        "Message to analyse",
        placeholder="Enter a fictional sample message here...",
        height=160,
        max_chars=3000
    )

    st.caption("Use fictional examples only. Never enter real private information.")

    if st.button("🔍 Analyse Message", use_container_width=True):

        if not message.strip():
            st.warning("Please enter a sample message first.")

        else:
            detected, warnings = guardian["function"](message)

            st.divider()
            st.markdown("## Analysis Results")

            if detected:
                st.error("⚠️ POTENTIAL RISK DETECTED")
                st.write("One or more warning signs were identified.")
            else:
                st.success("✓ NO SUPPORTED WARNING SIGNS DETECTED")
                st.write(
                    "The current rules did not identify a strong warning sign. "
                    "This does not guarantee that the message is safe."
                )

            if warnings:
                st.markdown("### Detected warning signs")

                for warning in warnings:
                    st.warning(f"⚠️ {warning}")

            else:
                st.info("No warning signs matched the current detection rules.")

            st.markdown("### Safety Guidance")

            for tip in guardian["tips"]:
                st.markdown(f"- {tip}")

            st.caption(
                "Automated analysis is not a final judgement. "
                "Review the context before taking action."
            )

st.divider()
st.caption("© SchoolShield | Student Hackathon Project")
