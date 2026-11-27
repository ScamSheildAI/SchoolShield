
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

def normalize_text(text):
    """Normalize text consistently while preserving non-English scripts."""
    import unicodedata
    text = unicodedata.normalize("NFKC", str(text or ""))
    return re.sub(r"\s+", " ", text).strip()


def matches(pattern, text):
    return re.search(pattern, text, re.IGNORECASE) is not None


def contains_any(text, phrases):
    """Unicode-safe phrase matching for Telugu, Hindi and Russian."""
    lowered = normalize_text(text).casefold()
    return any(normalize_text(phrase).casefold() in lowered for phrase in phrases)


def add_reason(reasons, reason):
    if reason not in reasons:
        reasons.append(reason)


# ============================================================
# PHISHING GUARDIAN
# ============================================================


def detect_phishing(message):
    text = normalize_text(message)
    reasons = []
    if not text:
        return False, reasons

    educational_context = matches(
        r"\b(our lesson explains|teacher explained|class discussed|"
        r"we discussed|textbook explains|worksheet asks|school presentation|"
        r"learning about|chapter explains|writing an essay about|"
        r"studying examples of|researching how|computer lesson)\b", text
    )
    protective_context = matches(
        r"\b(never share|do not share|don't share|should not share|"
        r"must not share|never reveal|do not reveal|don't reveal|"
        r"keep .* private|protect .* password|should be kept secret)\b", text
    )

    # A high-risk request requires an action verb close to a credential.
    action = r"\b(share|send|tell|reveal|provide|give|submit|enter|type|reply with|confirm)\b"
    credential = r"\b(otp|one[- ]time (?:password|code)|verification code|security code|"
    credential += r"password|passcode|login details|bank details|banking information|account credentials|private details|digits sent to my phone)\b"
    sensitive_request = (
        matches(action + r".{0,65}" + credential, text)
        or matches(credential + r".{0,65}" + action, text)
    )
    contextual_code_request = matches(action + r".{0,55}\b(code|digits)\b", text) and matches(r"\b(phone|parcel|delivery|account|verification|security)\b", text)
    if contextual_code_request:
        sensitive_request = True
    if sensitive_request and not protective_context:
        add_reason(reasons, "Requests sensitive verification or login information")

    payment = matches(r"\b(pay|payment|fee|charge|transfer|send money|send funds|funds|deposit|customs charges)\b", text)
    if matches(r"\b(no payment|without payment|not asking for payment|no fee required)\b", text):
        payment = False
    unexpected_benefit = matches(
        r"\b(prize|reward|scholarship|refund|lottery|contest|gift|winning|winner|unlock|release|"
        r"claim|gift|cashback|winning|winner)\b", text
    )
    if payment and unexpected_benefit:
        add_reason(reasons, "Connects a payment request with an unexpected benefit")
    advance_prize_fee = matches(r"\b(won|winner|selected|chosen)\b", text) and matches(r"\b(pay|fee|postage|processing charge)\b", text)
    if advance_prize_fee:
        add_reason(reasons, "Requests an advance payment to receive a claimed prize or reward")
    delivery_payment = matches(r"\b(parcel|package|delivery|customs)\b", text) and payment and matches(r"\b(held|release|before delivery|before it can be delivered|unknown sender|unexpected notice|waiting)\b", text)
    if delivery_payment:
        add_reason(reasons, "Requests a delivery or customs payment through an unexpected notice")

    account = matches(r"\b(account|school account|profile|access)\b", text)
    restriction = matches(
        r"\b(blocked|suspended|closed|locked|disabled|deactivated|terminated|close|disappear|lose access|expires|expire)\b", text
    )
    urgency = matches(
        r"\b(urgent|immediately|today|act now|within 24 hours|right away|"
        r"before tonight|limited time|final warning)\b", text
    )
    if account and restriction and urgency:
        add_reason(reasons, "Uses an account restriction threat with urgency")

    verification = matches(r"\b(verify|verification|confirm|restore|recover|unlock|reactivate)\b", text)
    action_destination = matches(r"\b(link|website|page|details|information|identity|password|otp)\b|https?://|www\.", text)
    if account and verification and action_destination:
        add_reason(reasons, "Connects account verification with a request for action")

    link_present = matches(r"https?://|www\.|\b(through|using)\s+(a\s+)?link\b|\b(click|tap|open|visit)\b.{0,45}\b(link|website|page)\b", text)
    risky_link_context = matches(
        r"\b(urgent|verify|verification|password|otp|reward|prize|blocked|"
        r"suspended|unlock|restore|payment|claim)\b", text
    )
    if link_present and risky_link_context:
        add_reason(reasons, "Contains a link connected with suspicious activity")

    organisation = matches(
        r"\b(bank|delivery|parcel|school account|support team|security team|administrator|"
        r"tax office|courier)\b", text
    )
    asks_credentials = matches(
        r"\b(asking|asks|requesting|requests|demands|demand|send|provide|reveal|confirm)\b", text
    ) and matches(credential + r"|\b(payment|bank details)\b", text)
    if organisation and asks_credentials and not protective_context:
        add_reason(reasons, "Uses an organisation identity to request sensitive information")

    # Additional contextual combinations for common impersonation patterns.
    money_movement = matches(r"\b(transfer|move|send)\b.{0,55}\b(money|funds|savings)\b", text)
    money_protection_claim = matches(r"\b(protect|protection|secure|safe|unusual activity|unsafe)\b", text)
    savings_relocation = matches(r"\b(savings|money|funds)\b.{0,70}\b(move|transfer|send)\b.{0,45}\b(account|somewhere|new account)\b", text)
    if money_movement and money_protection_claim or savings_relocation:
        add_reason(reasons, "Pressures the recipient to move money under a safety claim")
    if matches(r"\b(account|school account)\b", text) and matches(r"\b(password|passcode|login details)\b", text) and matches(r"\b(confirm|confirmed|verify|immediately|today)\b", text):
        add_reason(reasons, "Requests account verification involving login information")
    if matches(r"\b(unknown|unexpected|stranger|caller|sender)\b", text) and matches(r"\b(demand|demands|asks|asking|requests|pressures|provide)\b", text) and matches(r"\b(details|information|credentials|identity|banking information)\b", text):
        add_reason(reasons, "An unknown contact requests sensitive account or identity details")
    if matches(r"\b(payment failed|failed payment)\b", text) and matches(r"\b(another transfer|send funds|pay again|transfer again)\b", text):
        add_reason(reasons, "Requests another payment after a claimed payment problem")
    if matches(r"\b(install|download)\b.{0,45}\b(unknown|unfamiliar|unverified)\b.{0,35}\b(app|application)\b", text) and matches(r"\b(account|restore|recover|unlock)\b", text):
        add_reason(reasons, "Links account recovery to installing an unverified app")
    unfamiliar_page = matches(r"\b(unfamiliar|unknown|unverified|suspicious)\b.{0,35}\b(page|website|site|link)\b", text)
    sign_in_action = matches(r"\b(sign in|log in|login)\b", text)
    if account and restriction and unfamiliar_page and sign_in_action:
        add_reason(reasons, "Pressures the recipient to sign in through an unfamiliar page")
    if matches(r"\b(confirm|verify)\b.{0,35}\b(identity)\b", text) and link_present:
        add_reason(reasons, "Requests identity confirmation through a link")
    caller_money_pressure = matches(r"\b(caller|unknown person|stranger|unknown sender)\b", text) and matches(r"\b(pressures|pressure|asks|asking|demands)\b", text) and matches(r"\b(send funds|transfer money|move money|send money)\b", text)
    unusual_activity_details = matches(r"\b(account|bank)\b", text) and matches(r"\bunusual activity\b", text) and matches(r"\b(demands|demand|asks|request)\b", text) and matches(r"\b(details|information|credentials)\b", text)
    if caller_money_pressure:
        add_reason(reasons, "Pressures the recipient to transfer money")
    if unusual_activity_details:
        add_reason(reasons, "Uses an account activity claim to request private details")

    # Phrase-based multilingual patterns. These require combinations, not a lone keyword.
    multi_sensitive = [
        "ఓటీపీ", "పాస్‌వర్డ్", "పాస్వర్డ్", "రహస్య కోడ్", "సత్యాపన కోడ్",
        "ओटीपी", "पासवर्ड", "सत्यापन कोड", "गुप्त कोड",
        "одноразовый пароль", "пароль", "код подтверждения"
    ]
    multi_action = [
        "పంపండి", "చెప్పండి", "పంచుకోండి", "నమోదు చేయండి", "ఇవ్వండి",
        "भेजें", "बताएं", "साझा करें", "दर्ज करें", "दीजिए",
        "отправьте", "сообщите", "поделитесь", "введите", "предоставьте"
    ]
    multi_urgent = ["వెంటనే", "తక్షణమే", "ఈరోజే", "ఇప్పుడే", "तुरंत", "अभी", "आज ही", "срочно", "немедленно", "сегодня"]
    multi_account = ["ఖాతా", "అకౌంట్", "खाता", "аккаунт", "учётная запись"]
    multi_block = ["బ్లాక్", "నిలిపివేయబడుతుంది", "మూసివేయబడుతుంది", "बंद", "ब्लॉक", "निलंबित", "заблокирован", "закрыт"]
    multi_payment = ["చెల్లింపు", "డబ్బు పంపండి", "ఫీజు", "భాగ్యము", "भुगतान", "पैसे भेजें", "शुल्क", "इनाम", "оплата", "переведите деньги", "платёж", "награда", "приз"]
    multi_benefit = ["బహుమతి", "బహుమానం", "రివార్డ్", "విడుదల", "इनाम", "पुरस्कार", "रिवॉर्ड", "जारी", "награда", "приз", "вознаграждение"]
    multi_link = ["లింక్", "క్లిక్ చేయండి", "లింక్ తెరవండి", "लिंक", "क्लिक करें", "ссылка", "перейдите по ссылке"]
    multi_verify = ["ధృవీకరించండి", "నిర్ధారించండి", "వెరిఫై", "सत्यापित करें", "पुष्टि करें", "проверьте", "подтвердите"]
    protective_multi = ["పంచుకోవద్దు", "పంపవద్దు", "చెప్పకండి", "साझा न करें", "मत भेजें", "कभी न बताएं", "не сообщайте", "не отправляйте", "не делитесь"]

    if contains_any(text, multi_sensitive) and contains_any(text, multi_action) and not contains_any(text, protective_multi):
        add_reason(reasons, "Requests sensitive verification or login information")
    if contains_any(text, multi_account) and contains_any(text, multi_block) and contains_any(text, multi_urgent):
        add_reason(reasons, "Uses an account restriction threat with urgency")
    if contains_any(text, multi_payment) and contains_any(text, multi_benefit):
        add_reason(reasons, "Links a payment request with an unexpected benefit")
    if contains_any(text, multi_verify) and (contains_any(text, multi_link) or contains_any(text, multi_account)):
        add_reason(reasons, "Connects account verification with a request for action")

    # Only suppress clear educational/protective discussion when there is no
    # actionable credential request or suspicious payment combination.
    if educational_context and protective_context and not sensitive_request and not (payment and unexpected_benefit):
        return False, []

    high_risk = (
        sensitive_request
        or (payment and unexpected_benefit)
        or delivery_payment
        or advance_prize_fee
        or (account and restriction and urgency)
        or (account and verification and action_destination)
        or (link_present and risky_link_context)
        or (organisation and asks_credentials)
        or (money_movement and money_protection_claim)
        or savings_relocation
        or (account and matches(r"\b(password|passcode|login details)\b", text) and matches(r"\b(confirm|confirmed|verify|immediately|today)\b", text))
        or (matches(r"\b(payment failed|failed payment)\b", text) and matches(r"\b(another transfer|send funds|pay again|transfer again)\b", text))
        or (matches(r"\b(install|download)\b.{0,45}\b(unknown|unfamiliar|unverified)\b.{0,35}\b(app|application)\b", text) and matches(r"\b(account|restore|recover|unlock)\b", text))
        or (matches(r"\b(confirm|verify)\b.{0,35}\b(identity)\b", text) and link_present)
        or (account and restriction and unfamiliar_page and sign_in_action)
        or caller_money_pressure
        or unusual_activity_details
        or (matches(r"\b(unknown|unexpected|stranger|caller|sender)\b", text) and matches(r"\b(demand|demands|asks|asking|requests|pressures|provide)\b", text) and matches(r"\b(details|information|credentials|identity|banking information)\b", text) and matches(r"\b(reward|unlock|account|prize)\b", text))
        or contains_any(text, multi_sensitive) and contains_any(text, multi_action) and not contains_any(text, protective_multi)
        or contains_any(text, multi_account) and contains_any(text, multi_block) and contains_any(text, multi_urgent)
        or contains_any(text, multi_payment) and contains_any(text, multi_benefit)
        or contains_any(text, multi_verify) and (contains_any(text, multi_link) or contains_any(text, multi_account))
    )
    # Two independent lower-strength warning signs can also justify review.
    suspicious = bool(high_risk or len(reasons) >= 2)
    return suspicious, reasons


# ============================================================
# CYBERBULLYING GUARDIAN
# ============================================================

def detect_bullying(message):
    text = normalize_text(message)
    reasons = []
    if not text:
        return False, reasons

    educational_context = matches(
        r"\b(lesson explains|teacher asked us|essay about|poster says|worksheet asks|"
        r"we are learning|we discussed|studying examples|story includes|character in the novel|textbook explains|"
        r"discussed why|learning how to|class discussed|class presentation about)\b", text
    )
    reporting_context = matches(
        r"\b(i reported|i am reporting|someone called me|they called me|"
        r"a person called me|the message said|the comment said)\b", text
    )

    patterns = [
        (r"\b(you are|you're|ur)\s+(such an?\s+)?(stupid|idiot|loser|worthless|ugly|dumb|pathetic)\b", "Contains a direct personal insult"),
        (r"\b(nobody likes you|everyone hates you|you have no friends|nobody wants you)\b", "Contains hurtful personal remarks"),
        (r"\b(i will hurt you|i will beat you|you will regret this|i'm going to hurt you)\b", "Contains threatening language"),
        (r"\b(you don't belong here|you should not be here|we don't want you here)\b", "Contains exclusionary language"),
        (r"\b(shut up|hate you)\b", "Contains hostile language"),
        (r"\b(spreading|spread|sharing)\s+(rumours|rumors|false stories)\b", "Mentions spreading rumours"),
        (r"\b(make fun of|mock|humiliate|embarrass)\b", "Mentions mocking or humiliating someone"),
        (r"\b(deliberately|repeatedly|keeps|keep|constantly)\b.{0,65}\b(ignore|mock|exclude|excluding|insult|target|embarrass|humiliate)\b", "Describes repeated targeted behaviour"),
        (r"\b(tell|telling|tells|pressure|pressuring)\b.{0,50}\b(others|everyone|friends)\b.{0,40}\b(ignore|avoid|exclude|not talk|not sit)\b", "Describes encouraging others to exclude someone"),
        (r"\b(separate group|group chat)\b.{0,60}\b(mock|make fun|target|embarrass|insult|threaten|send threatening)\b", "Describes group-based targeting"),
        (r"\b(group chat|someone|they|a classmate)\b.{0,65}\b(keeps|keep|repeatedly|constantly)\b.{0,50}\b(sending|send|posts|posting)\b.{0,35}\b(threatening|threats|insulting)\b", "Describes repeated threatening or abusive messages"),
        (r"\b(group of classmates|classmates|group chat|class chat)\b.{0,80}\b(chat|share|sharing|send|sends|sending|post|posting)\b.{0,70}\b(cruel jokes|abusive messages|threatening messages|mean comments)\b", "Describes group-based harmful messages"),
        (r"\b(they|someone|a person|my classmates|a classmate)\b.{0,50}\b(keep telling|keeps telling|repeatedly tell|tell)\b.{0,60}\b(others|everyone|the others)\b.{0,50}\b(not to include me|not include me|leave me out|exclude me)\b", "Describes encouraging others to exclude someone"),
        (r"\b(called me|calls me|calling me)\b.{0,30}\b(stupid|idiot|loser|worthless|ugly|dumb|pathetic)\b", "Contains a direct personal insult"),
        (r"\b(share|shares|shared|sharing|post|posts|posted|send|sends|sent)\b.{0,50}\b(embarrassing|private|unwanted)\b.{0,40}\b(picture|photo|story|message|comment)\b", "May involve sharing embarrassing content"),
        (r"\b(after i asked them to stop|asked them to stop|told them to stop)\b", "Indicates unwanted behaviour continued after being asked to stop"),
        (r"\b(turn my friends against me|stop being friends with me)\b", "Describes attempts to damage friendships"),
        (r"\b(laugh whenever i speak|laugh whenever i try to speak|laugh at my mistakes|laugh at me|group chat becomes silent whenever i try to join)\b", "Describes repeated humiliation or exclusion"),
        (r"\b(they|someone|a person|my classmates|a classmate)\b.{0,65}\b(leave me out|exclude me|not include me|keep me out|ignore me|share embarrassing|post unkind|send unwanted insulting|spread false stories|make a joke out of|target me)\b", "Describes targeted or exclusionary behaviour"),
        (r"\b(they|someone|a person|my classmates|a classmate)\b.{0,65}\b(tell|tells|telling|encourage|encourages|pressure|pressures)\b.{0,55}\b(others|everyone|friends)\b.{0,40}\b(ignore|avoid|exclude|not sit|not work|not include)\b", "Describes encouraging others to exclude someone"),
        (r"\b(someone|they|a classmate|my classmates)\b.{0,65}\b(keeps|keep|repeatedly)\b.{0,45}\b(sharing|sends|sending|posts|posting)\b.{0,40}\b(embarrassing|unwanted|insulting|unkind|cruel)\b", "Describes repeated unwanted or humiliating messages"),
        (r"\b(they|someone|a person|my classmates|a classmate)\b.{0,65}\b(tell|tells|telling)\b.{0,45}\b(everyone|others|friends)\b.{0,50}\b(not to sit|not to work|should not be included|not include me)\b", "Describes encouraging others to exclude someone"),
        (r"\b(my classmates|they|someone|a classmate)\b.{0,55}\b(laugh|laughs|laughing)\b.{0,40}\b(whenever i try to speak|at my mistakes|at me)\b", "Describes repeated humiliation"),
        (r"\b(they|someone|a person|a classmate)\b.{0,65}\b(keep|keeps|repeatedly)\b.{0,45}\b(telling|tell)\b.{0,45}\b(nobody wants me|no one wants me|not wanted in the team)\b", "Describes repeated hurtful remarks"),
        (r"\b(a classmate|someone|they)\b.{0,45}\b(repeatedly|keeps|keep)\b.{0,40}\b(targets|target)\b.{0,30}\b(me|my work)\b", "Describes repeated targeted behaviour"),
        (r"\b(someone|they|a person)\b.{0,50}\b(keeps making|keep making|make|makes|making)\b.{0,35}\b(a joke out of|fun of)\b", "Describes repeated mocking"),
        (r"\b(they|someone|a classmate|people)\b.{0,55}\b(keep|keeps|repeatedly|constantly)\b.{0,45}\b(insult|mock|exclude|target|threaten|humiliate)\b", "Describes repeated harmful behaviour")
    ]

    # Direct insults are detected only when directed at a person, not when a
    # keyword merely appears in an unrelated sentence.
    for pattern, reason in patterns:
        if matches(pattern, text):
            add_reason(reasons, reason)

    multilingual_bullying = [
        (["నువ్వు మూర్ఖుడివి", "నువ్వు వెధవ", "అందరూ నిన్ను ద్వేషిస్తారు", "నీకు స్నేహితులు లేరు", "నిన్ను కొడతాను"], "Contains insulting or threatening language"),
        (["बेवकूफ हो", "तुम मूर्ख हो", "सब तुमसे नफरत करते हैं", "तुम्हारा कोई दोस्त नहीं", "मैं तुम्हें मारूंगा", "दूर रहो"], "Contains insulting or threatening language"),
        (["ты дурак", "ты идиот", "никому ты не нравишься", "у тебя нет друзей", "я тебя побью", "заткнись", "ненавижу тебя"], "Contains insulting or threatening language"),
        (["నిన్ను గ్రూప్‌లో చేర్చము", "నిన్ను దూరంగా ఉంచుతున్నారు", "నీ గురించి తప్పుడు మాటలు", "నిన్ను అవమానిస్తున్నారు"], "Describes exclusion or repeated humiliation"),
        (["तुम्हें समूह में शामिल नहीं करेंगे", "तुम्हें बाहर रखेंगे", "तुम्हारा मज़ाक उड़ाते हैं", "तुम्हें अपमानित करते हैं"], "Describes exclusion or repeated humiliation"),
        (["тебя не возьмут в группу", "тебя исключают", "над тобой смеются", "тебя унижают"], "Describes exclusion or repeated humiliation")
    ]
    for phrases, reason in multilingual_bullying:
        if contains_any(text, phrases):
            add_reason(reasons, reason)

    if educational_context and not reporting_context:
        return False, []

    return bool(reasons), reasons


# ============================================================
# PRIVACY GUARDIAN
# ============================================================

def detect_privacy(message):
    text = normalize_text(message)
    reasons = []
    if not text:
        return False, reasons

    # Do not flag a label alone. Require a plausible value after the label.
    secret_labels = [
        (r"\b(password|passcode)\s*(?:is|[:=])\s*([A-Za-z0-9!@#$%^&*_-]{4,})", "May contain a password or passcode"),
        (r"\b(password|passcode)\s+for\s+.{1,45}?\s+(?:is|[:=])\s*([A-Za-z0-9!@#$%^&*_-]{4,})", "May contain a password or passcode"),
        (r"\b(otp|verification code|security code)\s*(?:is|[:=])?\s*(\d{4,8})\b", "May contain an OTP or verification code"),
        (r"\b(pin|login pin)\s*(?:is|[:=])\s*(\d{4,8})\b", "May contain a PIN or access code"),
        (r"\b(bank account number|account number)\s*(?:is|[:=])\s*(\d[\d -]{7,})", "May contain a bank or account number"),
        (r"\b(card number)\s*(?:is|[:=])\s*(\d[\d -]{11,})", "May contain payment card information"),
        (r"\b(cvv|security code)\s*(?:is|[:=])\s*(\d{3,4})\b", "May contain payment card security information")
    ]
    for pattern, reason in secret_labels:
        if matches(pattern, text):
            add_reason(reasons, reason)

    if matches(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", text):
        add_reason(reasons, "Contains an email address")

    # Phone numbers: labelled numbers or common 10-digit digit strings.
    labelled_phone = matches(
        r"\b(phone|mobile|contact)\s*(number|no\.?|#)?\s*(?:is|:|=)?\s*\+?[\d][\d ()-]{7,}\d", text
    )
    plain_phone = matches(r"(?<!\d)(?:\+?91[- ]?)?[6-9]\d{9}(?!\d)", text)
    if labelled_phone or plain_phone:
        add_reason(reasons, "May contain a phone number")

    if matches(r"\b(aadhaar|identification number|national id|id number)\s*(?:is|[:=])?\s*\d{8,16}\b", text):
        add_reason(reasons, "May contain an identification number")
    elif matches(r"(?<!\d)\d{12}(?!\d)", text) and not matches(r"\b(sample|example|worksheet|fictional|demo|project)\b", text):
        add_reason(reasons, "May contain a 12-digit identification number")

    address_label = matches(r"\b(my address is|address\s*[:=]|i live at|home address is|my home address is)", text)
    address_has_value = matches(
        r"\b(?:my address is|address\s*[:=]|i live at|home address is|my home address is)\s+"
        r"(?:\d{1,6}\s+)?[A-Za-z0-9][A-Za-z0-9 ,./-]{3,70}", text
    ) and matches(r"\d|\b(road|street|lane|avenue|colony|apartment|flat|nagar|cross)\b", text)
    if address_label and address_has_value:
        add_reason(reasons, "May contain a home address")

    school_label = matches(r"\b(my school is|my school name is|i attend)\s+[A-Z][A-Za-z0-9&.' -]{2,}", text)
    if school_label:
        add_reason(reasons, "Mentions a school identity")

    dob_label = matches(r"\b(my date of birth|date of birth|my birthday is|born on|dob)\s*(?:is|[:=])?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/ ](?:\d{1,2}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[-/ , ]+\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", text)
    if dob_label:
        add_reason(reasons, "May contain a date of birth")

    if matches(r"\b(my email is|my email address is|contact email is)\s+[\w.+-]+@[\w-]+\.[\w.-]+", text):
        add_reason(reasons, "Contains a personal email address")

    # Multilingual labels. Require a concrete numeric value where possible.
    if contains_any(text, ["నా పాస్‌వర్డ్", "నా పాస్వర్డ్", "मेरा पासवर्ड", "мой пароль"]):
        if matches(r"\b\S{4,}\s*$", text) or matches(r"(?:है|is|:|=)\s*\S{4,}", text):
            add_reason(reasons, "May contain a password or passcode")
    if contains_any(text, ["నా ఓటీపీ", "నా రహస్య కోడ్", "मेरा ओटीपी", "मेरा सत्यापन कोड", "мой одноразовый пароль", "мой код подтверждения"]):
        if matches(r"\d{4,8}", text):
            add_reason(reasons, "May contain an OTP or verification code")
    if contains_any(text, ["నా ఫోన్ నంబర్", "నా మొబైల్ నంబర్", "मेरा फोन नंबर", "मेरा मोबाइल नंबर", "мой номер телефона"]) and matches(r"\d{7,}", text):
        add_reason(reasons, "May contain a phone number")
    if contains_any(text, ["నా ఇమెయిల్", "मेरा ईमेल", "моя электронная почта"]) and matches(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        add_reason(reasons, "Contains an email address")
    if contains_any(text, ["నా చిరునామా", "मेरा पता", "мой адрес"]) and matches(r"\d|\b(road|street|lane|nagar)\b", text):
        add_reason(reasons, "May contain a home address")

    return bool(reasons), reasons


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
    """Keep each curated synthetic example once; never inflate scores by repetition."""
    cases = []
    seen = set()
    for message in positive:
        key = normalize_text(message).casefold()
        if key and key not in seen:
            cases.append((message, True))
            seen.add(key)
    for message in negative:
        key = normalize_text(message).casefold()
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
        "My card number is 0000000000000000 and my CVV is 000.",
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


# Add a second, distinct batch of synthetic examples to broaden evaluation.
# These are still curated examples, not an independent real-world benchmark.
FRESH_PHISHING.extend([
    ("Your bank account has been locked. Call this number and provide the security code to restore access.", True),
    ("A package is waiting but customs charges must be paid before it can be delivered.", True),
    ("Congratulations on being selected. Pay a processing fee to receive your gift card.", True),
    ("Your school portal expires tonight. Sign in through this unfamiliar page to keep access.", True),
    ("IT support says to install an unknown app and share your login details.", True),
    ("A caller says your savings are unsafe and asks you to move them to a new account.", True),
    ("Your subscription renews tomorrow. Open the official app if you want to review it.", False),
    ("The teacher posted the school portal timetable in the class group.", False),
    ("I got an email about a parcel delivery date. It has no payment request.", False),
    ("Our class is learning how to identify fake bank messages.", False),
    ("Please check the school website for tomorrow's assembly schedule.", False),
    ("My friend sent me a link to a funny video.", False)
])
FRESH_BULLYING.extend([
    ("Everyone in the chat keeps making memes about my appearance after I asked them to stop.", True),
    ("They keep excluding me from lunch and group projects.", True),
    ("Someone shared an embarrassing photo of me without permission.", True),
    ("The group chat keeps sending me threatening messages.", True),
    ("Nobody wants you on this team.", True),
    ("A classmate repeatedly sends cruel messages about my work.", True),
    ("I disagree with your opinion about the game.", False),
    ("My friend teased me once, apologised, and we moved on.", False),
    ("Please stop messaging me about the homework.", False),
    ("The novel describes a character who bullies another student.", False),
    ("We should invite everyone to join the activity.", False),
    ("That was a difficult match, but you played well.", False)
])
FRESH_PRIVACY.extend([
    ("Contact: +91 98765 43210", True),
    ("My date of birth: 05/09/2011", True),
    ("My email address: learner@example.com", True),
    ("I live at flat 12, Green Park Road.", True),
    ("My identification number is 123456789012.", True),
    ("My school is Riverdale Academy.", True),
    ("The meeting starts at 12:30 tomorrow.", False),
    ("The code for our science project is written on the board.", False),
    ("My favourite number is twelve.", False),
    ("We are studying why passwords should be private.", False),
    ("Please email the school office using its public website.", False),
    ("The lesson explains what a date of birth is.", False)
])

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

    st.caption("Use fictional examples only. Never enter real passwords, OTPs, phone numbers or addresses.")
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

            # Store only the result summary, not the submitted message.
            category = (
                "Phishing" if "Phishing" in title else
                "Cyberbullying" if "Cyberbullying" in title else
                "Privacy"
            )
            if "schoolshield_assessments" not in st.session_state:
                st.session_state.schoolshield_assessments = {}
            st.session_state.schoolshield_assessments[category] = {
                "detected": bool(detected),
                "reasons": list(reasons),
                "checked_at": pd.Timestamp.now().strftime("%H:%M")
            }

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
    "Risk Radar",
    "What Can We Do Now?",
    "Phishing Guardian",
    "Cyberbullying Guardian",
    "Privacy Guardian"
]

if developer_mode:
    navigation_options.extend([
        "Performance Lab",
        "Challenge Test Lab"
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
    z.metric("Hard Challenge Tests", "156")
    w.metric("Total Tests", "186")

    st.info(
        "Use the sidebar to explore the three Guardians."
    )


# ============================================================
# SCHOOLSHIELD RISK RADAR
# ============================================================

elif page == "Risk Radar":

    st.title("📡 SchoolShield Risk Radar")
    st.write(
        "A live overview of the latest checks you have run in SchoolShield. "
        "The radar updates from actual Guardian results stored in this session."
    )

    assessments = st.session_state.get("schoolshield_assessments", {})
    categories = ["Phishing", "Cyberbullying", "Privacy"]
    values = []
    labels = []

    for category in categories:
        result = assessments.get(category)
        if result is None:
            values.append(0)
            labels.append("Not assessed")
        else:
            # This is a visual status indicator, not a probability or validated risk score.
            values.append(75 if result["detected"] else 15)
            labels.append("Warning signs found" if result["detected"] else "No warning signs found")

    st.caption(
        "Radar scale: 75 = warning signs found; 15 = no warning signs found; "
        "0 = not assessed. These are display indicators, not percentages or proof of safety."
    )

    # Dependency-free SVG radar visualization.
    points = [(200, 45), (335, 285), (65, 285)]
    center = (200, 190)
    scaled = []
    for (x, y), value in zip(points, values):
        factor = value / 100
        scaled.append((center[0] + (x - center[0]) * factor,
                       center[1] + (y - center[1]) * factor))
    polygon = " ".join(f"{x:.1f},{y:.1f}" for x, y in scaled)
    svg = f"""
    <div style="background:#101F35;border:1px solid #263B58;border-radius:16px;padding:12px;">
    <svg viewBox="0 0 400 340" width="100%" role="img" aria-label="SchoolShield risk radar">
      <polygon points="200,45 335,285 65,285" fill="none" stroke="#49617D" stroke-width="2"/>
      <polygon points="200,93 281,237 119,237" fill="none" stroke="#334B68" stroke-width="1.5"/>
      <polygon points="200,141 227,189 173,189" fill="none" stroke="#334B68" stroke-width="1.5"/>
      <line x1="200" y1="190" x2="200" y2="45" stroke="#49617D"/>
      <line x1="200" y1="190" x2="335" y2="285" stroke="#49617D"/>
      <line x1="200" y1="190" x2="65" y2="285" stroke="#49617D"/>
      <polygon points="{polygon}" fill="rgba(34,211,238,0.22)" stroke="#22D3EE" stroke-width="3"/>
      {''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#22D3EE"/>' for x,y in scaled)}
      <text x="200" y="24" text-anchor="middle" fill="#E2E8F0" font-size="14">PHISHING</text>
      <text x="345" y="310" text-anchor="middle" fill="#E2E8F0" font-size="13">CYBERBULLYING</text>
      <text x="55" y="310" text-anchor="middle" fill="#E2E8F0" font-size="13">PRIVACY</text>
    </svg></div>
    """
    st.markdown(svg, unsafe_allow_html=True)

    cols = st.columns(3)
    for col, category, status in zip(cols, categories, labels):
        with col:
            if status == "Not assessed":
                col.metric(category, "—", "Not assessed")
            elif status == "Warning signs found":
                col.metric(category, "Review", "Warning signs found")
            else:
                col.metric(category, "Clear*", "No warning signs found")

    st.info(
        "Only the three existing Guardians are represented. Deepfake and other "
        "categories will remain unassessed until a working checker is added. "
        "*Clear means the current rules found no warning signs; it does not guarantee safety."
    )
    if st.button("Open What Can We Do Now?"):
        st.session_state.navigation_page = "What Can We Do Now?"
        st.rerun()


# ============================================================
# WHAT CAN WE DO NOW? — ACTION CENTRE
# ============================================================

elif page == "What Can We Do Now?":

    st.title("🧭 What Can We Do Now?")
    st.write(
        "Practical next steps based on the latest results from your SchoolShield Guardians."
    )

    assessments = st.session_state.get("schoolshield_assessments", {})
    if not assessments:
        st.info(
            "No Guardian checks have been run in this session yet. "
            "Start with Phishing Guardian, Cyberbullying Guardian, or Privacy Guardian. "
            "Your submitted message is not saved here."
        )

    action_guides = {
        "Phishing": {
            "detected": [
                "Do not click links or open unexpected attachments.",
                "Do not reply with passwords, OTPs, or account details.",
                "Verify the sender using an official contact method you already trust.",
                "Show the message to a trusted adult or school IT contact if unsure."
            ],
            "clear": [
                "Check the sender and destination address carefully.",
                "Do not share passwords or OTPs, even if the message looks familiar.",
                "Remember: no warning signs detected does not prove a message is safe."
            ]
        },
        "Cyberbullying": {
            "detected": [
                "Do not retaliate or escalate the conversation.",
                "Save relevant evidence, such as screenshots, if it is safe to do so.",
                "Use the platform's block and report options where appropriate.",
                "Talk to a trusted adult, teacher, or school counsellor."
            ],
            "clear": [
                "Keep communication respectful and avoid sharing hurtful content.",
                "If behaviour feels repeated, targeted, or upsetting, seek help even if the checker did not flag it."
            ]
        },
        "Privacy": {
            "detected": [
                "Do not post or forward the information publicly.",
                "Remove exposed personal details from the message or post where possible.",
                "If a password or account secret may have been exposed, ask a trusted adult to help secure the account through its official settings.",
                "Never share an OTP or password with anyone."
            ],
            "clear": [
                "Continue keeping passwords, OTPs, addresses, and private account details confidential.",
                "Review privacy settings before sharing personal information."
            ]
        }
    }

    for category in ["Phishing", "Cyberbullying", "Privacy"]:
        result = assessments.get(category)
        with st.expander(f"{'⚠️' if result and result['detected'] else '🛡️'} {category} — recommended actions", expanded=bool(result and result["detected"])):
            if result is None:
                st.caption("Not assessed in this session. Run the relevant Guardian to get tailored next steps.")
            else:
                st.write(
                    "**Latest result:** Warning signs found"
                    if result["detected"] else
                    "**Latest result:** No warning signs found by the current rules"
                )
                if result["reasons"]:
                    st.write("**Reasons:** " + "; ".join(result["reasons"]))
                for action in action_guides[category]["detected" if result["detected"] else "clear"]:
                    st.markdown(f"- {action}")

    st.warning(
        "SchoolShield is an educational prototype, not an emergency service or a guarantee of detection. "
        "If someone is in immediate danger, contact a trusted adult or local emergency services."
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
        "and the 156-example challenge dataset."
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
    st.subheader("156-Example Challenge Performance")

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
        "Each challenge example appears once. Results describe performance on this synthetic test set only."
    )


# ============================================================
# CHALLENGE TEST LAB — PRIVATE
# ============================================================

elif page == "Challenge Test Lab" and developer_mode:

    st.title("🧪 SchoolShield Challenge Test Lab")

    st.write(
        "A set of 156 unique synthetic challenge examples designed "
        "to test detection, missed warnings and false alarms."
    )

    st.warning(
        "These are curated synthetic examples, not a real-world benchmark. "
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
    st.subheader("Download All 156 Challenge Tests")

    st.download_button(
        "⬇️ Download Complete Challenge Dataset",
        data=all_results.to_csv(index=False).encode("utf-8"),
        file_name="schoolshield_156_hard_challenge_tests.csv",
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

elif page in ["Performance Lab", "Challenge Test Lab"]:

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
