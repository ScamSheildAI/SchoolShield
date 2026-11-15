
import re
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SchoolShield",
    page_icon="🛡️",
    layout="wide"
)

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: #081426;
    color: #F1F5F9;
}
[data-testid="stSidebar"] {
    background: #101F35;
}
h1, h2, h3 {
    color: #E2E8F0;
}
p, label, li {
    color: #CBD5E1;
}
div[data-testid="stMetric"] {
    background: #14243B;
    border: 1px solid #263B58;
    padding: 16px;
    border-radius: 12px;
}
.stButton button {
    background: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# -------------------- DETECTION RULES --------------------

def detect_phishing(message):
    text = message.lower()
    reasons = []

    rules = [
        (r"\b(otp|one.time password|verification code)\b", "Requests or mentions an OTP or verification code"),
        (r"\b(password|passcode|login details|bank details)\b", "Mentions sensitive login or banking information"),
        (r"\b(click here|tap here|open this link|verify your account)\b", "Encourages clicking or verifying an account"),
        (r"\b(account (?:will be|has been) (?:blocked|suspended|closed))\b", "Uses an account-blocking threat"),
        (r"\b(urgent|immediately|act now|within 24 hours|limited time)\b", "Uses urgency or pressure"),
        (r"\b(free prize|free gift|cash reward|won a|claim your reward|scholarship)\b", "Uses a prize or reward offer"),
        (r"\b(send money|transfer money|pay now|processing fee)\b", "Requests money or a payment"),
        (r"\b(won a lottery|lottery winner|congratulations, you won)\b", "Claims an unexpected prize"),
        (r"\b(share your otp|tell me your otp|send me your password)\b", "Asks for confidential information"),
        (r"https?://|www\.", "Contains a web link")
    ]

    for pattern, reason in rules:
        if re.search(pattern, text):
            reasons.append(reason)

    suspicious = len(reasons) >= 2 or any(
        phrase in text for phrase in [
            "share your otp", "send me your password",
            "tell me your otp", "send money immediately"
        ]
    )

    return suspicious, reasons


def detect_bullying(message):
    text = message.lower()
    reasons = []

    patterns = [
        (r"\b(stupid|idiot|loser|worthless|ugly|dumb)\b", "Contains insulting language"),
        (r"\b(nobody likes you|everyone hates you|you have no friends)\b", "Contains hurtful personal remarks"),
        (r"\b(i will hurt you|i will beat you|you will regret this)\b", "Contains threatening language"),
        (r"\b(go away|nobody wants you|you don't belong here)\b", "Contains exclusionary language"),
        (r"\b(kill yourself|you should disappear)\b", "Contains seriously harmful language"),
        (r"\b(keep bullying|make fun of|humiliate you)\b", "Suggests targeted harassment"),
        (r"\b(?:spreading|srpreading|spread)\s+(?:rumou?rs|roumers)(?:\s+about\s+(?:you|u))?\b", "Mentions spreading rumours"),
        (r"\b(shut up|hate you|pathetic)\b", "Contains hostile language")
    ]

    for pattern, reason in patterns:
        if re.search(pattern, text):
            reasons.append(reason)

    return len(reasons) > 0, reasons


def detect_privacy(message):
    text = message.lower()
    reasons = []

    patterns = [
        (r"\bpassword\s*[:=]\s*\S+|\bmy password is\s+\S+|\bpasscode\s*(?:is|[:=])\s*\S+", "May contain a password or passcode"),
        (r"\b(?:otp|verification code)\s*(?:is|[:=])?\s*\d{4,8}\b", "May contain an OTP or verification code"),
        (r"\b\d{10}\b", "May contain a 10-digit phone number"),
        (r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "Contains an email address"),
        (r"\b\d{12}\b", "May contain a 12-digit identification number"),
        (r"\b(my address is|i live at|home address)\b", "Mentions a home address"),
        (r"\b(my school is|my school name is)\b", "Mentions school identity"),
        (r"\b(date of birth|my birthday is|born on)\b", "Mentions date of birth"),
        (r"\b(bank account number|card number|cvv)\b", "Mentions banking or card information")
    ]

    for pattern, reason in patterns:
        if re.search(pattern, text):
            reasons.append(reason)

    return len(reasons) > 0, reasons


# -------------------- TEST DATA --------------------

PHISHING_TESTS = [
    ("Your account will be blocked. Verify your account immediately using this link.", True),
    ("Congratulations, you won a free prize. Pay a processing fee now.", True),
    ("Share your OTP to receive your cash reward.", True),
    ("Send me your password to fix your account.", True),
    ("Urgent! Transfer money immediately to avoid account closure.", True),
    ("Click here to claim your free gift within 24 hours.", True),
    ("You won a lottery. Send your bank details to claim the reward.", True),
    ("Your verification code is needed. Tell me your OTP now.", True),
    ("Your account has been suspended. Open this link to verify your login details.", True),
    ("A scholarship is waiting for you. Pay the processing fee now.", True),

    ("Good morning! See you at school tomorrow.", False),
    ("Please bring your science notebook to class.", False),
    ("Our school sports day is on Friday.", False),
    ("The homework deadline is next Monday.", False),
    ("Thank you for helping me with the project.", False),
    ("The library will remain open until 4 PM.", False),
    ("I enjoyed today's football match.", False),
    ("Please send me the class timetable.", False),
    ("The science exhibition starts next week.", False),
    ("Happy birthday! Have a wonderful day.", False)
]

BULLYING_TESTS = [
    ("You are such an idiot and a loser.", True),
    ("Nobody likes you. You have no friends.", True),
    ("I will hurt you after school.", True),
    ("Go away, nobody wants you here.", True),
    ("You are worthless and dumb.", True),
    ("I will make fun of you in front of everyone.", True),
    ("Everyone hates you. You do not belong here.", True),
    ("I am spreading rumours about you.", True),
    ("Shut up, you are pathetic.", True),
    ("You will regret this. I will beat you.", True),

    ("You did a great job in the competition.", False),
    ("Would you like to join our study group?", False),
    ("Thank you for helping me yesterday.", False),
    ("I disagree with your answer.", False),
    ("Let's work together on the project.", False),
    ("Your presentation was interesting.", False),
    ("Can you explain this question to me?", False),
    ("I hope you have a good day.", False),
    ("We should include everyone in the game.", False),
    ("That was a funny joke. Well done.", False)
]

PRIVACY_TESTS = [
    ("My password is School12345.", True),
    ("My OTP is 123456.", True),
    ("My verification code is 765432.", True),
    ("My phone number is 9876543210.", True),
    ("My email is student@example.com.", True),
    ("My address is near the main market.", True),
    ("My school is Green Valley School.", True),
    ("My date of birth is 15 August 2012.", True),
    ("My bank account number is 123456789012.", True),
    ("My card number and CVV are private.", True),

    ("I enjoy reading adventure books.", False),
    ("My favourite subject is science.", False),
    ("I like playing football after school.", False),
    ("The weather is pleasant today.", False),
    ("I am preparing for my science exam.", False),
    ("Our class is going on a school trip.", False),
    ("I enjoy learning Python programming.", False),
    ("My favourite colour is blue.", False),
    ("We have a mathematics test tomorrow.", False),
    ("I watched an educational video today.", False)
]


# -------------------- PERFORMANCE EVALUATION --------------------

def evaluate_guardian(test_data, detector, guardian):
    results = []

    for message, actual_positive in test_data:
        detected, reasons = detector(message)
        predicted_positive = detected

        if actual_positive and predicted_positive:
            outcome = "True Positive"
        elif not actual_positive and not predicted_positive:
            outcome = "True Negative"
        elif not actual_positive and predicted_positive:
            outcome = "False Alarm"
        else:
            outcome = "Missed Warning"

        results.append({
            "Guardian": guardian,
            "Message": message,
            "Actual": "Threat" if actual_positive else "Safe",
            "Prediction": "Threat" if predicted_positive else "Safe",
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
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) else 0
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


# -------------------- PAGE FUNCTIONS --------------------

def guardian_page(title, description, detector, samples, positive_label):
    st.title(title)
    st.write(description)

    st.markdown("---")

    sample_names = ["Choose an example"] + [
        f"Example {i+1}" for i in range(len(samples))
    ]

    selected = st.selectbox("Try a sample message", sample_names)
    sample_text = ""

    if selected != "Choose an example":
        sample_index = int(selected.split()[-1]) - 1
        sample_text = samples[sample_index]

    message = st.text_area(
        "Enter a fictional message to check:",
        value=sample_text,
        height=130,
        placeholder="Type or paste a message here..."
    )

    if st.button("Analyse Message", key=title):
        if not message.strip():
            st.warning("Please enter a message first.")
        else:
            detected, reasons = detector(message)

            if detected:
                st.error(f"⚠️ {positive_label} detected")
                st.write("**Warning signs found:**")
                for reason in reasons:
                    st.write(f"- {reason}")
                st.info("Stay calm. Do not share private information, click suspicious links, or respond to harmful messages. Ask a trusted adult for help when needed.")
            else:
                st.success("No warning signs detected by the current rules.")
                st.write("This does not guarantee that the message is safe.")
                st.info("Always check the sender and context before trusting a message.")


# -------------------- SIDEBAR --------------------

st.sidebar.title("🛡️ SchoolShield")
st.sidebar.caption("One Platform. Three Layers of Protection.")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Phishing Guardian",
        "Cyberbullying Guardian",
        "Privacy Guardian",
        "Performance Lab"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Student-built educational prototype")


# -------------------- DASHBOARD --------------------

if page == "Dashboard":
    st.title("🛡️ Welcome to SchoolShield")
    st.subheader("One Platform. Three Layers of Protection.")
    st.write(
        "A student-focused digital safety platform designed to help "
        "people recognise suspicious messages, harmful language, "
        "and possible privacy risks."
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎣")
        st.subheader("Phishing Guardian")
        st.write("Checks messages for suspicious links, pressure, and requests for sensitive information.")

    with col2:
        st.markdown("### 💬")
        st.subheader("Cyberbullying Guardian")
        st.write("Identifies potentially insulting, threatening, or exclusionary language.")

    with col3:
        st.markdown("### 🔒")
        st.subheader("Privacy Guardian")
        st.write("Looks for possible personal information that should be kept private.")

    st.markdown("---")
    st.subheader("📊 Built-in Testing Dataset")

    a, b, c, d = st.columns(4)
    a.metric("Guardians", "3")
    b.metric("Phishing Tests", len(PHISHING_TESTS))
    c.metric("Bullying Tests", len(BULLYING_TESTS))
    d.metric("Privacy Tests", len(PRIVACY_TESTS))

    st.info(
        "Select a Guardian from the sidebar to test a fictional message, "
        "or open Performance Lab to see the results of the built-in test set."
    )


# -------------------- PHISHING GUARDIAN --------------------

elif page == "Phishing Guardian":
    guardian_page(
        "🎣 Phishing Guardian",
        "Finds common warning signs in suspicious messages.",
        detect_phishing,
        [x[0] for x in PHISHING_TESTS],
        "Possible phishing"
    )


# -------------------- CYBERBULLYING GUARDIAN --------------------

elif page == "Cyberbullying Guardian":
    guardian_page(
        "💬 Cyberbullying Guardian",
        "Checks for potentially harmful or targeted language.",
        detect_bullying,
        [x[0] for x in BULLYING_TESTS],
        "Potentially harmful language"
    )


# -------------------- PRIVACY GUARDIAN --------------------

elif page == "Privacy Guardian":
    guardian_page(
        "🔒 Privacy Guardian",
        "Checks whether a message may contain personal or sensitive information.",
        detect_privacy,
        [x[0] for x in PRIVACY_TESTS],
        "Possible privacy risk"
    )


# -------------------- PERFORMANCE LAB --------------------

elif page == "Performance Lab":
    st.title("📊 SchoolShield Performance Lab")
    st.write("Test results calculated from the built-in labelled examples.")
    st.warning(
        "These are small demonstration datasets, not an independent "
        "real-world accuracy benchmark. SchoolShield currently uses "
        "rule-based detection, not a trained machine-learning model."
    )

    evaluations = [
        ("Phishing Guardian", PHISHING_TESTS, detect_phishing),
        ("Cyberbullying Guardian", BULLYING_TESTS, detect_bullying),
        ("Privacy Guardian", PRIVACY_TESTS, detect_privacy)
    ]

    all_metrics = []
    all_results = []

    for name, tests, detector in evaluations:
        metrics, df = evaluate_guardian(tests, detector, name)
        all_metrics.append({"Guardian": name, **metrics})
        all_results.append((name, df))

    results_df = pd.DataFrame(all_metrics)

    st.subheader("Overall Guardian Comparison")

    display_columns = [
        "Guardian", "Accuracy", "Precision", "Recall", "F1 Score",
        "False Alarms", "Missed Warnings"
    ]

    display_df = results_df[display_columns].copy()

    for column in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        display_df[column] = display_df[column].map(
            lambda x: f"{x:.1f}%"
        )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Individual Guardian Results")

    for name, df in all_results:
        with st.expander(f"🔍 {name} — View detailed tests"):
            metrics = results_df[results_df["Guardian"] == name].iloc[0]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", f"{metrics['Accuracy']:.1f}%")
            c2.metric("Precision", f"{metrics['Precision']:.1f}%")
            c3.metric("Recall", f"{metrics['Recall']:.1f}%")
            c4.metric("F1 Score", f"{metrics['F1 Score']:.1f}%")

            c5, c6, c7 = st.columns(3)
            c5.metric("False Alarms", int(metrics["False Alarms"]))
            c6.metric("Missed Warnings", int(metrics["Missed Warnings"]))
            c7.metric("Total Tests", int(metrics["Total Tests"]))

            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            file_name = name.lower().replace(" ", "_") + "_results.csv"

            st.download_button(
                "⬇️ Download CSV Results",
                data=csv,
                file_name=file_name,
                mime="text/csv",
                key=file_name
            )

    st.markdown("---")
    st.caption(
        "Accuracy = correct predictions / all tests. "
        "Precision = correct threat detections / all threat detections. "
        "Recall = detected threats / all actual threats. "
        "F1 Score combines precision and recall."
    )


# -------------------- FOOTER --------------------

st.markdown("---")
st.caption(
    "SchoolShield | A student-built digital safety prototype. "
    "It may miss threats or flag harmless messages. "
    "Do not enter real passwords, OTPs, phone numbers, or private information."
)
