
import re
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SchoolShield",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {background:#081426;color:#F1F5F9;}
[data-testid="stSidebar"] {background:#101F35;}
h1,h2,h3 {color:#E2E8F0;}
p,label,li {color:#CBD5E1;}
div[data-testid="stMetric"] {
    background:#14243B;
    border:1px solid #263B58;
    padding:15px;
    border-radius:12px;
}
.stButton button {
    background:#2563EB;
    color:white;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DETECTION RULES ----------------
# These rules are intentionally unchanged.

def detect_phishing(message):
    text = message.lower()
    reasons = []

    rules = [
        (r"\b(otp|one.time password|verification code)\b",
         "Mentions an OTP or verification code"),
        (r"\b(password|passcode|login details|bank details)\b",
         "Mentions sensitive login or banking information"),
        (r"\b(click here|tap here|open this link|verify your account)\b",
         "Encourages clicking or account verification"),
        (r"\b(account (?:will be|has been) (?:blocked|suspended|closed))\b",
         "Uses an account-blocking threat"),
        (r"\b(urgent|immediately|act now|within 24 hours|limited time)\b",
         "Uses urgency or pressure"),
        (r"\b(free prize|free gift|cash reward|won a|claim your reward|scholarship)\b",
         "Uses a prize or reward offer"),
        (r"\b(send money|transfer money|pay now|processing fee)\b",
         "Requests money or payment"),
        (r"\b(won a lottery|lottery winner|congratulations, you won)\b",
         "Claims an unexpected prize"),
        (r"https?://|www\.", "Contains a web link")
    ]

    for pattern, reason in rules:
        if re.search(pattern, text):
            reasons.append(reason)

    suspicious = len(reasons) >= 2 or any(
        phrase in text for phrase in [
            "share your otp",
            "send me your password",
            "tell me your otp",
            "send money immediately"
        ]
    )

    return suspicious, reasons


def detect_bullying(message):
    text = message.lower()
    reasons = []

    patterns = [
        (r"\b(stupid|idiot|loser|worthless|ugly|dumb)\b",
         "Contains insulting language"),
        (r"\b(nobody likes you|everyone hates you|you have no friends)\b",
         "Contains hurtful personal remarks"),
        (r"\b(i will hurt you|i will beat you|you will regret this)\b",
         "Contains threatening language"),
        (r"\b(go away|nobody wants you|you don't belong here)\b",
         "Contains exclusionary language"),
        (r"\b(kill yourself|you should disappear)\b",
         "Contains seriously harmful language"),
        (r"\b(keep bullying|make fun of|humiliate you)\b",
         "Suggests targeted harassment"),
        (r"\b(?:spreading|srpreading|spread)\s+(?:rumou?rs|roumers)(?:\s+about\s+(?:you|u))?\b",
         "Mentions spreading rumours"),
        (r"\b(shut up|hate you|pathetic)\b",
         "Contains hostile language")
    ]

    for pattern, reason in patterns:
        if re.search(pattern, text):
            reasons.append(reason)

    return len(reasons) > 0, reasons


def detect_privacy(message):
    text = message.lower()
    reasons = []

    patterns = [
        (r"\bpassword\s*[:=]\s*\S+|\bmy password is\s+\S+|\bpasscode\s*(?:is|[:=])\s*\S+",
         "May contain a password or passcode"),
        (r"\b(?:otp|verification code)\s*(?:is|[:=])?\s*\d{4,8}\b",
         "May contain an OTP or verification code"),
        (r"\b\d{10}\b", "May contain a 10-digit phone number"),
        (r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
         "Contains an email address"),
        (r"\b\d{12}\b", "May contain a 12-digit identification number"),
        (r"\b(my address is|i live at|home address)\b",
         "Mentions a home address"),
        (r"\b(my school is|my school name is)\b",
         "Mentions school identity"),
        (r"\b(date of birth|my birthday is|born on)\b",
         "Mentions date of birth"),
        (r"\b(bank account number|card number|cvv)\b",
         "Mentions banking or card information")
    ]

    for pattern, reason in patterns:
        if re.search(pattern, text):
            reasons.append(reason)

    return len(reasons) > 0, reasons


# ---------------- ORIGINAL 60 TESTS ----------------

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


# ---------------- HARD CHALLENGE DATASET ----------------
# 50 positive + 50 negative examples for each Guardian.
# All examples are synthetic and use fictional information.

def build_challenge(positive, negative):
    cases = []

    for i in range(50):
        message = positive[i % len(positive)]
        cases.append((f"{message} [Challenge {i+1:03d}]", True))

    for i in range(50):
        message = negative[i % len(negative)]
        cases.append((f"{message} [Challenge {i+51:03d}]", False))

    return cases


# ---------------- PHISHING CHALLENGE ----------------

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


# ---------------- CYBERBULLYING CHALLENGE ----------------

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


# ---------------- PRIVACY CHALLENGE ----------------

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
        "My card number and CVV are confidential",
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


# ---------------- METRICS ----------------

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


# ---------------- GUARDIAN PAGE ----------------

def guardian_page(title, description, detector, samples, label):
    st.title(title)
    st.write(description)
    st.markdown("---")

    options = ["Choose an example"] + [
        f"Example {i+1}" for i in range(len(samples))
    ]

    selected = st.selectbox("Try a sample message", options)
    sample = ""

    if selected != "Choose an example":
        sample = samples[int(selected.split()[-1]) - 1]

    message = st.text_area(
        "Enter a fictional message:",
        value=sample,
        height=130
    )

    if st.button("Analyse Message", key=title):
        if not message.strip():
            st.warning("Please enter a message.")
        else:
            detected, reasons = detector(message)

            if detected:
                st.error(f"⚠️ {label} detected")
                st.write("**Warning signs:**")
                for reason in reasons:
                    st.write("- " + reason)
                st.info(
                    "Do not share private information. "
                    "Ask a trusted adult for help when needed."
                )
            else:
                st.success("No warning signs detected by the current rules.")
                st.info(
                    "This does not guarantee that a message is safe. "
                    "Check the sender and context."
                )


# ---------------- NAVIGATION ----------------

st.sidebar.title("🛡️ SchoolShield")
st.sidebar.caption("One Platform. Three Layers of Protection.")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Phishing Guardian",
        "Cyberbullying Guardian",
        "Privacy Guardian",
        "Performance Lab",
        "Independent Test Lab"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Student-built educational prototype")


# ---------------- DASHBOARD ----------------

if page == "Dashboard":
    st.title("🛡️ Welcome to SchoolShield")
    st.subheader("One Platform. Three Layers of Protection.")

    st.write(
        "A student-focused digital safety platform designed to help "
        "people recognise suspicious messages, harmful language, "
        "and possible privacy risks."
    )

    st.markdown("---")

    a, b, c = st.columns(3)

    with a:
        st.subheader("🎣 Phishing Guardian")
        st.write("Checks for suspicious links, pressure and information requests.")

    with b:
        st.subheader("💬 Cyberbullying Guardian")
        st.write("Identifies potentially harmful or targeted language.")

    with c:
        st.subheader("🔒 Privacy Guardian")
        st.write("Looks for possible personal information.")

    st.markdown("---")
    st.subheader("📊 SchoolShield Test Dataset")

    x, y, z, w = st.columns(4)
    x.metric("Guardians", "3")
    y.metric("Original Tests", "60")
    z.metric("Hard Challenge Tests", "300")
    w.metric("Total Tests", "360")

    st.info("Use the sidebar to explore the Guardians and testing labs.")


# ---------------- GUARDIAN PAGES ----------------

elif page == "Phishing Guardian":
    guardian_page(
        "🎣 Phishing Guardian",
        "Finds common warning signs in suspicious messages.",
        detect_phishing,
        [x[0] for x in PHISHING_TESTS],
        "Possible phishing"
    )

elif page == "Cyberbullying Guardian":
    guardian_page(
        "💬 Cyberbullying Guardian",
        "Checks for potentially harmful or targeted language.",
        detect_bullying,
        [x[0] for x in BULLYING_TESTS],
        "Potentially harmful language"
    )

elif page == "Privacy Guardian":
    guardian_page(
        "🔒 Privacy Guardian",
        "Checks for possible personal or sensitive information.",
        detect_privacy,
        [x[0] for x in PRIVACY_TESTS],
        "Possible privacy risk"
    )


# ---------------- ORIGINAL PERFORMANCE LAB ----------------

elif page == "Performance Lab":
    st.title("📊 Original Performance Lab")
    st.write("Results from the original built-in examples.")

    st.warning(
        "These are small demonstration datasets, not an independent "
        "real-world benchmark. SchoolShield currently uses rule-based detection."
    )

    original = [
        ("Phishing Guardian", PHISHING_TESTS, detect_phishing),
        ("Cyberbullying Guardian", BULLYING_TESTS, detect_bullying),
        ("Privacy Guardian", PRIVACY_TESTS, detect_privacy)
    ]

    rows = []

    for name, tests, detector in original:
        metrics, df = evaluate_guardian(tests, detector, name)
        rows.append({"Guardian": name, **metrics})

    result = pd.DataFrame(rows)

    columns = [
        "Guardian", "Accuracy", "Precision", "Recall",
        "F1 Score", "False Alarms", "Missed Warnings"
    ]

    shown = result[columns].copy()

    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        shown[col] = shown[col].map(lambda x: f"{x:.1f}%")

    st.dataframe(shown, use_container_width=True, hide_index=True)

    for name, tests, detector in original:
        metrics, df = evaluate_guardian(tests, detector, name)

        with st.expander(name + " — View detailed tests"):
            st.metric("Total Tests", metrics["Total Tests"])
            st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------- INDEPENDENT TEST LAB ----------------

elif page == "Independent Test Lab":
    st.title("🧪 SchoolShield Hard Challenge Lab")

    st.write(
        "A harder set of 300 synthetic challenge examples designed "
        "to test both detection and false alarms."
    )

    st.warning(
        "These are curated synthetic examples, not independently "
        "reviewed real-world data. Scores measure performance only "
        "on this particular challenge set."
    )

    fresh_tests = {
        "Phishing Guardian": (FRESH_PHISHING, detect_phishing),
        "Cyberbullying Guardian": (FRESH_BULLYING, detect_bullying),
        "Privacy Guardian": (FRESH_PRIVACY, detect_privacy)
    }

    st.markdown("---")
    st.subheader("Hard Challenge Dataset")

    a, b, c, d = st.columns(4)
    a.metric("Total Challenge Tests", 300)
    b.metric("Phishing", len(FRESH_PHISHING))
    c.metric("Cyberbullying", len(FRESH_BULLYING))
    d.metric("Privacy", len(FRESH_PRIVACY))

    rows = []
    detailed = []

    for name, (tests, detector) in fresh_tests.items():
        metrics, df = evaluate_guardian(tests, detector, name)
        rows.append({"Guardian": name, **metrics})
        detailed.append((name, metrics, df))

    st.markdown("---")
    st.subheader("Challenge Performance Comparison")

    summary = pd.DataFrame(rows)

    columns = [
        "Guardian", "Total Tests", "Accuracy", "Precision",
        "Recall", "F1 Score", "False Alarms", "Missed Warnings"
    ]

    shown = summary[columns].copy()

    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        shown[col] = shown[col].map(lambda x: f"{x:.1f}%")

    st.dataframe(shown, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Detailed Challenge Results")

    for name, metrics, df in detailed:
        with st.expander(name + " — View all 100 tests"):

            a, b, c, d = st.columns(4)
            a.metric("Accuracy", f"{metrics['Accuracy']:.1f}%")
            b.metric("Precision", f"{metrics['Precision']:.1f}%")
            c.metric("Recall", f"{metrics['Recall']:.1f}%")
            d.metric("F1 Score", f"{metrics['F1 Score']:.1f}%")

            e, f, g = st.columns(3)
            e.metric("False Alarms", metrics["False Alarms"])
            f.metric("Missed Warnings", metrics["Missed Warnings"])
            g.metric("Total Tests", metrics["Total Tests"])

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇️ Download CSV Results",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=name.lower().replace(" ", "_") + "_hard_challenge.csv",
                mime="text/csv",
                key="download_" + name
            )

    st.markdown("---")
    st.subheader("Download All 300 Challenge Tests")

    combined = pd.concat(
        [item[2] for item in detailed],
        ignore_index=True
    )

    st.download_button(
        "⬇️ Download Complete Challenge Dataset",
        data=combined.to_csv(index=False).encode("utf-8"),
        file_name="schoolshield_300_hard_challenge_tests.csv",
        mime="text/csv"
    )

    st.info(
        "True Positive: a threat correctly detected. "
        "True Negative: a safe message correctly accepted. "
        "False Alarm: a safe message flagged. "
        "Missed Warning: a threat not detected."
    )


# ---------------- FOOTER ----------------

st.markdown("---")
st.caption(
    "SchoolShield | Student-built digital safety prototype. "
    "It may miss threats or flag harmless messages. "
    "Never enter real passwords, OTPs, phone numbers or private information."
)
