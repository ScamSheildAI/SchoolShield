
import re
import hmac
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SchoolShield",
    page_icon="🛡️",
    layout="wide"
)

# ============================================================
# DESIGN
# ============================================================

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
    padding: 15px;
    border-radius: 12px;
}
.stButton button {
    background: #2563EB;
    color: #FFFFFF;
    border-radius: 8px;
}
div[data-testid="stTextArea"] textarea {
    background-color: #172A43 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid #49617D !important;
    border-radius: 10px !important;
    caret-color: #FFFFFF !important;
    font-size: 16px !important;
}
div[data-testid="stTextArea"] textarea::placeholder {
    color: #A9BCD3 !important;
    opacity: 1 !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border: 2px solid #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}
@media (max-width: 768px) {
    div[data-testid="stTextArea"] textarea {
        font-size: 16px !important;
        min-height: 130px;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER
# ============================================================

def matches(pattern, text):
    return re.search(pattern, text, re.IGNORECASE) is not None


# ============================================================
# PHISHING GUARDIAN
# ============================================================

def detect_phishing(message):
    text = message.lower()
    reasons = []

    rules = [
        (r"\b(share|send|tell|reveal|provide|confirm|give)\b.{0,60}\b(otp|verification code|password|passcode|login details)\b",
         "Requests sensitive verification or login information"),
        (r"\b(otp|verification code|password|passcode|login details)\b.{0,60}\b(share|send|tell|reveal|provide|confirm|give)\b",
         "Connects sensitive information with a sharing request"),
        (r"\b(pay|payment|fee|charge|transfer|send)\b.{0,55}\b(release|unlock|claim|restore|receive|avoid|prize|parcel|reward|account)\b",
         "Links payment with a promised benefit or threat"),
        (r"\b(prize|reward|gift|scholarship|refund|lottery)\b.{0,55}\b(fee|payment|charge|transfer|bank details|account details)\b",
         "Requests payment or details for an unexpected offer"),
        (r"\b(account|profile|access)\b.{0,45}\b(blocked|suspended|closed|locked|disabled)\b",
         "Mentions a possible account restriction"),
        (r"\b(blocked|suspended|closed|locked|disabled)\b.{0,45}\b(account|profile|access)\b",
         "Mentions a possible threat to account access"),
        (r"\b(unknown sender|stranger|unfamiliar caller|unexpected message|unfamiliar link|unknown link)\b",
         "Mentions an unfamiliar sender or link"),
        (r"\b(click|tap|open|visit)\b.{0,50}\b(link|website|page)\b",
         "Encourages opening a link"),
        (r"https?://|www\.",
         "Contains a web link"),
        (r"\b(urgent|immediately|act now|before tonight|within 24 hours|right away|today only)\b",
         "Uses urgency or pressure"),
        (r"\b(bank|delivery|parcel|school account|support team|security team)\b.{0,60}\b(confirm|verify|provide|send|reveal|pay)\b",
         "Connects a claimed organisation with a request for action"),
        (r"\b(account|school account|profile|login)\b.{0,60}\b(verify|verification|confirm|validate|restore|reactivate|recover)\b",
         "Requests account verification or restoration"),
        (r"\b(verify|verification|confirm|validate|restore|reactivate|recover)\b.{0,60}\b(account|school account|profile|login|access)\b",
         "Connects verification with account access"),
        (r"\b(restore|restored|recover|unlock|reactivate)\b.{0,50}\b(account|access|profile|login)\b",
         "Mentions restoring or unlocking account access"),
        (r"\b(open|click|tap|visit)\b.{0,70}\b(verify|verification|restore|unlock|recover|confirm)\b",
         "Directs the recipient to a verification or recovery action"),
        (r"\b(verify|verification|confirm)\b.{0,60}\b(your|personal|account|login)?\s*(details|information|identity)\b",
         "Requests verification of personal or account details"),
        (r"\b(account|school account|profile|access)\b.{0,80}\b(deactivation|deactivated|disable|disabled|suspend|suspended|termination)\b",
         "Warns about possible account deactivation or suspension"),
        (r"\b(security check|security verification|complete a check|keep your access|maintain access|avoid deactivation)\b",
         "Requests a security check to maintain account access")
    ]

    for pattern, reason in rules:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    sensitive_request = (
        matches(r"\b(otp|verification code|password|passcode|bank details|login details)\b", text)
        and matches(r"\b(share|send|tell|reveal|provide|confirm|give)\b", text)
    )

    payment_pressure = (
        matches(r"\b(pay|payment|fee|charge|transfer)\b", text)
        and matches(r"\b(prize|reward|parcel|account|scholarship|refund|unlock|release)\b", text)
    )

    verification_link = (
        matches(r"\b(account|school account|profile|access|login)\b", text)
        and matches(r"\b(verify|verification|confirm|restore|recover|unlock|reactivate)\b", text)
        and matches(r"\b(link|website|page)\b|https?://|www\.", text)
    )

    account_verification_pressure = (
        matches(r"\b(account|profile|access|login)\b", text)
        and matches(r"\b(restore|restored|recover|unlock|reactivate)\b", text)
        and matches(r"\b(verify|verification|confirm)\b", text)
        and matches(r"\b(details|information|identity)\b", text)
    )

    if account_verification_pressure:
        reason = "Connects account restoration with verification of personal details"
        if reason not in reasons:
            reasons.append(reason)

    account_deactivation_pressure = (
        matches(r"\b(account|school account|profile|access)\b", text)
        and matches(r"\b(deactivation|deactivated|disable|disabled|suspend|suspended|termination)\b", text)
        and matches(r"\b(security check|security verification|complete a check|verify)\b", text)
    )

    if account_deactivation_pressure:
        reason = "Connects account deactivation with a security verification request"
        if reason not in reasons:
            reasons.append(reason)

    suspicious = (
        sensitive_request
        or payment_pressure
        or verification_link
        or account_verification_pressure
        or account_deactivation_pressure
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
        (r"\b(stupid|idiot|loser|worthless|ugly|dumb|pathetic)\b",
         "Contains insulting language"),
        (r"\b(nobody likes you|everyone hates you|you have no friends|nobody wants you)\b",
         "Contains hurtful personal remarks"),
        (r"\b(i will hurt you|i will beat you|you will regret this)\b",
         "Contains threatening language"),
        (r"\b(go away|you don't belong here|you should not be here)\b",
         "Contains exclusionary language"),
        (r"\b(shut up|hate you)\b",
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
         "Describes repeated humiliation")
    ]

    for pattern, reason in patterns:
        if matches(pattern, text) and reason not in reasons:
            reasons.append(reason)

    if educational_context:
        return False, []

    direct_attack = matches(
        r"\b(stupid|idiot|loser|worthless|ugly|dumb|pathetic|"
        r"nobody likes you|everyone hates you|i will hurt you|"
        r"i will beat you|shut up|hate you)\b",
        text
    )

    return direct_attack or len(reasons) > 0, reasons


# ============================================================
# PRIVACY GUARDIAN
# ============================================================

def detect_privacy(message):
    text = message.lower()
    reasons = []

    patterns = [
        (r"\b(password|passcode)\s*(is|[:=])\s*\S+",
         "May contain a password or passcode"),
        (r"\b(my password is|my passcode is)\s+\S+",
         "May contain a password or passcode"),
        (r"\b(otp|verification code)\s*(is|[:=])?\s*\d{4,8}\b",
         "May contain an OTP or verification code"),
        (r"\b\d{10}\b",
         "May contain a 10-digit phone number"),
        (r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
         "Contains an email address"),
        (r"\b\d{12}\b",
         "May contain a 12-digit identification number"),
        (r"\b(my address is|i live at|home address is|my home address is)\b",
         "Mentions a home address"),
        (r"\b(my school is|my school name is|i attend)\b",
         "Mentions school identity"),
        (r"\b(date of birth|my birthday is|born on)\b",
         "Mentions date of birth"),
        (r"\b(bank account number|account number is|card number|cvv)\b",
         "Mentions banking or card information"),
        (r"\b(my phone number is|my mobile number is|contact number is)\b",
         "Mentions a phone number"),
        (r"\b(my email is|my email address is|contact email is)\b",
         "Mentions an email address")
    ]

    for pattern, reason in patterns:
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
    cases = []
    for i in range(50):
        cases.append((positive[i % len(positive)], True))
    for i in range(50):
        cases.append((negative[i % len(negative)], False))
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


# ============================================================
# GUARDIAN PAGE
# ============================================================

def guardian_page(title, description, detector, samples, label):
    st.title(title)
    st.write(description)
    st.markdown("---")

    options = ["Choose an example"] + [
        f"Example {i + 1}" for i in range(len(samples))
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
                st.success(
                    "No warning signs detected by the current rules."
                )
                st.info(
                    "This does not guarantee that a message is safe. "
                    "Check the sender and context."
                )


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

page = st.sidebar.radio(
    "NAVIGATION",
    navigation_options,
    key="navigation_page"
)

st.sidebar.markdown("---")
st.sidebar.caption("Student-built educational prototype")


# ============================================================
# DASHBOARD
# ============================================================

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
        st.write(
            "Checks for suspicious links, pressure and information requests."
        )

    with b:
        st.subheader("💬 Cyberbullying Guardian")
        st.write(
            "Identifies potentially harmful or targeted language."
        )

    with c:
        st.subheader("🔒 Privacy Guardian")
        st.write(
            "Looks for possible personal information."
        )

    st.markdown("---")
    st.subheader("📊 SchoolShield Test Dataset")

    x, y, z, w = st.columns(4)

    x.metric("Guardians", "3")
    y.metric("Original Tests", "30")
    z.metric("Hard Challenge Tests", "300")
    w.metric("Total Tests", "330")

    st.info(
        "Use the sidebar to explore the three Guardians."
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
        "and the 300-example challenge dataset."
    )

    st.warning(
        "These are synthetic examples, not an independent real-world benchmark. "
        "SchoolShield currently uses rule-based detection."
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
    st.subheader("300-Example Challenge Performance")

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
        "The challenge examples include repeated templates. "
        "Results describe performance on this specific test set only."
    )


# ============================================================
# INDEPENDENT TEST LAB — PRIVATE
# ============================================================

elif page == "Independent Test Lab" and developer_mode:

    st.title("🧪 SchoolShield Hard Challenge Lab")

    st.write(
        "A set of 300 synthetic challenge examples designed "
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
    st.subheader("Download All 300 Challenge Tests")

    st.download_button(
        "⬇️ Download Complete Challenge Dataset",
        data=all_results.to_csv(index=False).encode("utf-8"),
        file_name="schoolshield_300_hard_challenge_tests.csv",
        mime="text/csv"
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
    "Never enter real passwords, OTPs, phone numbers or private information."
)
