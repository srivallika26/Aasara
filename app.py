import os
import json
import requests
import streamlit as st
from gnani.tts import GnaniTTSClient

import logic
import style

# ---------- Settings ----------
GNANI_KEY = os.environ.get("GNANI_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.6-flash"  # change if your key uses a different model
VOICE = "Kaveri"                   # any voice from the supported list (case-sensitive)

LANGS = {"Telugu": "te-IN", "Hindi": "hi-IN"}

# Fixed Telugu follow-up questions (one per profile field)
FIELD_Q = {
    "age": "మీ వయస్సు ఎంత?",
    "gender": "మీరు పురుషుడా లేదా మహిళా?",
    "owns_land": "మీ పేరు మీద వ్యవసాయ భూమి ఉందా?",
    "income_tax_payer": "మీరు ఆదాయపు పన్ను కడుతున్నారా?",
    "white_ration_card": "మీ దగ్గర తెలుపు రేషన్ కార్డు ఉందా?",
    "small_business": "మీరు చిన్న వ్యాపారం చేస్తున్నారా లేదా మొదలుపెట్టాలనుకుంటున్నారా?",
    "has_lpg": "మీ ఇంట్లో ఇప్పటికే గ్యాస్ కనెక్షన్ ఉందా?",
    "daughter_under_10": "మీకు 10 సంవత్సరాల లోపు కూతురు ఉందా?",
}
INTRO = "తప్పకుండా! కొన్ని ప్రశ్నలు అడుగుతాను. ఒకేసారి చాలా విషయాలు చెప్పవచ్చు. "
RETRY = "క్షమించండి, సరిగ్గా వినపడలేదు. "
FALLBACK = "క్షమించండి, నాకు ఆ విషయం తెలియదు. దయచేసి పన్ను లేదా ప్రభుత్వ పథకాల గురించి అడగండి."

# Scheme categories for the filter. A "category" field in schemes.json, if you add one, takes priority.
CATEGORY = {
    "pm_kisan": "Agriculture",
    "pmjay": "Healthcare",
    "aarogyasri": "Healthcare",
    "apy": "Pension",
    "aasara_pension": "Pension",
    "mudra": "Business & Loans",
    "pmuy": "Energy & Household",
    "gruha_jyothi": "Energy & Household",
    "ssy": "Girl Child & Savings",
}
CATEGORY_ORDER = ["Agriculture", "Healthcare", "Pension", "Business & Loans", "Energy & Household", "Girl Child & Savings"]


def category_of(s):
    return s.get("category") or CATEGORY.get(s["id"], "Other")


# ---------- Gnani speech ----------
def transcribe(audio_bytes, lang_code):
    r = requests.post(
        "https://api.vachana.ai/stt/v3",
        headers={"X-API-Key-ID": GNANI_KEY},
        files={"audio_file": ("input.wav", audio_bytes, "audio/wav")},
        data={"language_code": lang_code, "format": "transcribe"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["transcript"]


def speak(text):
    return GnaniTTSClient().synthesize(text, voice=VOICE)


# ---------- Gemini ----------
def gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    r = requests.post(
        url,
        headers={"x-goog-api-key": GEMINI_KEY},  # header keeps the key out of error messages
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def parse_json(raw):
    a, b = raw.find("{"), raw.rfind("}")
    return json.loads(raw[a:b + 1])


def understand(question, pending):
    ids = list(logic.SCHEMES.keys())
    prompt = f"""You help a voice assistant about Indian government schemes. The user speaks Telugu, Hindi or English.
Return ONLY a JSON object, no other text, with these keys:
"intent": one of
  "tax" (asks about income tax),
  "scheme" (asks about ONE specific scheme),
  "discover" (asks which schemes they can get or are eligible for),
  "answer" (replying to the assistant's last question),
  "other"
"annual_income_rupees": number or null ("6 lakh" = 600000)
"scheme": one of {ids} or null
"profile": an object with ONLY facts the user actually stated, using null for the rest:
  "age" (integer), "gender" ("male" or "female"),
  "owns_land" (true/false: agricultural land in their own name),
  "income_tax_payer" (true/false),
  "has_lpg" (true/false: household already has an LPG gas connection),
  "daughter_under_10" (true/false),
  "white_ration_card" (true/false),
  "small_business" (true/false: runs or plans a small non-farm business)
The assistant's last question was about the field: {pending or "none"}.
If the user just answers yes, no or a number, fill that field and use intent "answer".
User said: {question}"""
    try:
        return parse_json(gemini(prompt))
    except Exception:
        return {"intent": "other", "profile": {}}


def phrase_in_telugu(question, facts, extra=""):
    prompt = f"""Answer in simple, friendly spoken Telugu for someone who may not read well.
Maximum 3 short sentences. Use ONLY the facts below. Write numbers in digits. No markdown.
{extra}
Question: {question}
Facts: {facts}"""
    return gemini(prompt).strip()


# ---------- One conversation turn ----------
def handle_turn(question):
    ss = st.session_state
    info = understand(question, ss["pending"])
    ss["profile"].update(logic.clean_profile(info.get("profile")))
    intent = info.get("intent")
    pending = ss["pending"]

    # Continue the follow-up question flow
    if intent == "discover" or (pending and intent == "answer"):
        missing = logic.missing_fields(ss["profile"])
        if missing:
            ss["pending"] = missing[0]
            prefix = INTRO if (intent == "discover" and not pending) else ""
            return prefix + FIELD_Q[missing[0]], None
        ss["pending"] = None
        results = logic.discover(ss["profile"])
        answer = phrase_in_telugu(
            question, logic.discover_facts(results),
            "Say which schemes the person may qualify for and which need checking, "
            "and that the government department makes the final decision.")
        return answer, {"type": "discover", "results": results}

    if pending and intent == "other":  # did not understand the reply: ask again
        return RETRY + FIELD_Q[pending], None

    ss["pending"] = None

    if intent == "scheme" and info.get("scheme") in logic.SCHEMES:
        sid = info["scheme"]
        return phrase_in_telugu(question, logic.scheme_facts(sid)), {"type": "scheme", "id": sid}

    if intent == "tax" and info.get("annual_income_rupees"):
        income = float(info["annual_income_rupees"])
        tax = logic.new_regime_tax(income)
        facts = (f"Annual income Rs {income:,.0f}. Estimated income tax under the new regime "
                 f"(salaried person, simplified calculation) is Rs {tax:,}.")
        return phrase_in_telugu(question, facts), {"type": "tax", "income": income, "tax": tax}

    return FALLBACK, None


# ---------- Display helpers ----------
def render_scheme(sid):
    s = logic.SCHEMES[sid]
    with st.expander(f"{s['name']}: details and sources"):
        st.markdown(f"**{s['name_te']}**")
        st.markdown(f"**Benefit:** {s['benefit']}")
        st.markdown("**Eligibility**")
        for x in s["eligibility"]:
            st.markdown(f"- {x}")
        st.markdown("**Documents needed**")
        for x in s["documents"]:
            st.markdown(f"- {x}")
        st.markdown("**How to apply**")
        for i, x in enumerate(s["how_to_apply"], 1):
            st.markdown(f"{i}. {x}")
        st.markdown("**Official sources**")
        for src in s["sources"]:
            st.markdown(f"- [{src['label']}]({src['url']})")
        st.caption(f"{s.get('level', 'Central')} scheme. Last checked: {s['last_checked']}. Open the official source to confirm before relying on it.")
        if s.get("verification_note"):
            st.warning(s["verification_note"])
        for x in s["limitations"]:
            st.caption(f"Note: {x}")


def render_payload(payload):
    if not payload:
        return
    if payload["type"] == "discover":
        for r in payload["results"]:
            st.markdown(f"**{logic.STATUS_LABEL[r['status']]}: {r['name']}**")
            st.caption(r["reason"])
            if r["status"] != "not_eligible":
                render_scheme(r["id"])
        st.caption("Informational estimate only. The relevant department makes the final decision.")
    elif payload["type"] == "scheme":
        render_scheme(payload["id"])
    elif payload["type"] == "tax":
        st.caption(f"Simplified new-regime estimate for Rs {payload['income']:,.0f}: Rs {payload['tax']:,}. "
                   "Demo calculation, not tax advice.")


def friendly_error(e):
    """Plain-language message for common failures (display only)."""
    if isinstance(e, requests.exceptions.Timeout):
        return "The request took too long. Check your internet connection and try again."
    if isinstance(e, requests.exceptions.ConnectionError):
        return "Could not reach the speech or answer service. Check your internet connection and try again."
    if isinstance(e, requests.exceptions.HTTPError):
        code = getattr(e.response, "status_code", None)
        if code in (401, 403):
            return "A service rejected the API key. Check GNANI_API_KEY and GEMINI_API_KEY, then restart the app."
        if code == 429:
            return "Too many requests right now. Wait a moment and try again."
        return f"A service returned an error (code {code}). Please try again, or type your question."
    if isinstance(e, KeyError):
        return "The speech service sent an unexpected reply. Please try again, or type your question."
    return f"Something went wrong: {e}"


PANEL = None  # set in the UI section below: the one place that shows the voice state


def _panel(state):
    """Show ready / processing / speaking in the voice panel (display only)."""
    if PANEL is None:
        return
    secs = style.audio_seconds(st.session_state.get("last_audio")) if state == "speaking" else None
    style.voice_panel(state, PANEL, seconds=secs)


def run_turn(get_question):
    ss = st.session_state
    try:
        _panel("processing")
        question = get_question()
        answer, payload = handle_turn(question)
        ss["chat"].append({"q": question, "a": answer, "payload": payload})
        try:
            ss["last_audio"] = speak(answer)
            ss["audio_on"] = True     # show the player
            ss["audio_fresh"] = True  # autoplay once, not on every rerun
        except Exception as e:
            ss["last_audio"] = None
            ss["error"] = f"The answer is ready below, but the Telugu voice could not be generated. {friendly_error(e)}"
        _panel("speaking" if ss.get("last_audio") else "ready")
    except Exception as e:
        ss["error"] = friendly_error(e)
        _panel("ready")


# ---------- UI ----------
st.set_page_config(page_title="Aasara", page_icon="🎙️", layout="wide")
style.inject()

ss = st.session_state
for k, v in {"chat": [], "profile": {}, "pending": None, "last_audio": None, "mic_n": 0}.items():
    if k not in ss:
        ss[k] = v

style.hero(len(logic.SCHEMES))
st.caption("Your answers stay in this browser session and are not stored. "
           "Informational only, not an official decision or financial advice.")

if not GNANI_KEY or not GEMINI_KEY:
    st.error("Set GNANI_API_KEY and GEMINI_API_KEY in this terminal, then restart the app.")
    st.stop()

# ---- One primary voice section (the "Start Speaking" button scrolls here) ----
style.anchor("talk")
st.markdown("### Talk to Aasara")
QUICK = [
    ("🧑‍🌾 Which schemes can I get?", "నాకు ఏ పథకాలు వస్తాయి?"),
    ("🌾 PM-KISAN", "పీఎం కిసాన్ అంటే ఏమిటి?"),
    ("🏥 Ayushman Bharat", "ఆయుష్మాన్ భారత్ అంటే ఏమిటి?"),
    ("💰 Tax on ₹9 lakh", "నా జీతం 9 లక్షలు, పన్ను ఎంత?"),
]

with st.container(border=True):
    PANEL = st.empty()
    _panel(ss.pop("voice_state", "ready"))

    lang_name = st.selectbox("Language you will speak", list(LANGS.keys()))
    st.caption("Tap the mic, or start with a quick question below. Answer follow-up questions by voice.")

    audio = st.audio_input("Tap the mic and ask your question", key=f"mic{ss['mic_n']}")
    st.caption("If the mic does not start, allow microphone access in your browser (click the lock icon next to the address bar) "
               "and reload the page. You can also type your question below.")
    with st.form("typed_form", clear_on_submit=True):
        typed = st.text_input("Or type your question (backup if the mic fails)",
                              placeholder="Ask anything about government schemes...")
        submitted = st.form_submit_button("➤ Send")

    cols = st.columns(len(QUICK))
    for col, (label, q) in zip(cols, QUICK):
        if col.button(label, use_container_width=True):
            run_turn(lambda q=q: q)

if submitted and typed.strip():
    run_turn(lambda: typed.strip())
elif audio is not None:
    run_turn(lambda: transcribe(audio.getvalue(), LANGS[lang_name]))
    ss["voice_state"] = "speaking" if ss.get("last_audio") else "ready"  # shown after the rerun
    ss["mic_n"] += 1  # clears the recorder so the same clip is not processed twice
    st.rerun()

if ss.get("error"):
    st.error(ss.pop("error"))

# Conversation history
last = len(ss["chat"]) - 1
for i, turn in enumerate(ss["chat"]):
    with st.chat_message("user"):
        st.write(turn["q"])
    with st.chat_message("assistant"):
        st.write(turn["a"])
        render_payload(turn["payload"])
        if i == last and ss["last_audio"]:
            if ss.get("audio_on", True):
                fresh = ss.pop("audio_fresh", False)  # autoplay only right after a new answer
                try:
                    st.audio(ss["last_audio"], format="audio/wav", autoplay=fresh)
                except TypeError:
                    st.audio(ss["last_audio"], format="audio/wav")
            b1, b2, _gap = st.columns([1, 1, 3])
            if b1.button("🔁 Replay answer", key="replay_audio", use_container_width=True):
                ss["audio_on"], ss["audio_fresh"] = True, True
                st.rerun()
            if b2.button("⏹ Stop audio", key="stop_audio", use_container_width=True):
                ss["audio_on"] = False
                st.rerun()

if ss["chat"]:
    with st.expander("What Aasara understood"):
        st.json({"profile_collected": ss["profile"], "waiting_for_answer_about": ss["pending"]})
    if st.button("Start over"):
        for k in ("chat", "profile", "pending", "last_audio", "audio_on", "audio_fresh"):
            ss.pop(k, None)
        st.rerun()

style.anchor("schemes")
st.markdown("### Schemes covered")

_cats = {category_of(x) for x in logic.SCHEMES.values()}
CATS = [c for c in CATEGORY_ORDER if c in _cats] + sorted(_cats - set(CATEGORY_ORDER))
with st.container(border=True):
    query = st.text_input("Search schemes by name", placeholder="Search by scheme name, for example PM-KISAN", key="scheme_q")
    gov = st.radio("Government", ["All", "Central Government", "Telangana Government"], horizontal=True, key="scheme_gov")
    cat = st.radio("Category", ["All"] + CATS, horizontal=True, key="scheme_cat")


def _matches(x):
    if gov != "All" and style.level_label(x.get("level", "Central")) != gov:
        return False
    if cat != "All" and category_of(x) != cat:
        return False
    q = query.strip().lower()
    return not q or q in x["name"].lower() or q in x["name_te"].lower() or q in x["id"].lower()


shown = {k: x for k, x in logic.SCHEMES.items() if _matches(x)}
st.caption(f"Showing {len(shown)} of {len(logic.SCHEMES)} schemes")
if shown:
    style.scheme_cards(shown)
else:
    st.info("No schemes match your search. Clear the search box or choose All.")
style.steps()
style.footer()