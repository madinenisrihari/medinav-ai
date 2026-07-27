"""
MediNav AI — Streamlit app.

Run with:
    streamlit run app.py

Real, working features (not just UI mockups):
  - Account creation and login backed by a local SQLite database
    (passwords are salted + hashed, never stored in plain text)
  - Session-based auth (st.session_state) with a logout button
  - Appointment "booking" writes real rows to the database, tied to
    the logged-in user, visible on the My Account page
  - Hospital search and doctor specialization filter
  - A working rule-based AI assistant using Streamlit's chat UI
  - Emergency SOS simulation and a contact form that saves messages
"""

import time
import streamlit as st

import db
import data

# ------------------------------------------------------------------ #
# Page config + one-time DB init
# ------------------------------------------------------------------ #

st.set_page_config(
    page_title="MediNav AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

db.init_db()

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi, I'm the MediNav Assistant. Tell me a symptom, or ask about a "
                                          "specialist or hospital timing."}
    ]

PRIMARY = "#2563EB"
ACCENT = "#06B6D4"


def go(page_name: str):
    st.session_state.page = page_name


# ------------------------------------------------------------------ #
# Global CSS — glassmorphism / blue-cyan theme
# ------------------------------------------------------------------ #

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html {{ scroll-behavior: smooth; }}
html, body, [class*="css"]  {{
    font-family: 'Inter', sans-serif;
}}
h1, h2, h3, h4 {{
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.02em;
}}
.stApp {{
    background: radial-gradient(at 15% 20%, rgba(37,99,235,0.10) 0px, transparent 50%),
                radial-gradient(at 85% 0%, rgba(6,182,212,0.12) 0px, transparent 50%),
                #F8FAFC;
}}
[data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}

/* ---- page-load transition ---- */
@keyframes mnFadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
[data-testid="stAppViewContainer"] .main .block-container {{
    animation: mnFadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1);
    max-width: 1200px;
}}

/* ---- cards ---- */
.mn-card {{
    background: rgba(255,255,255,0.68);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.7);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 8px 30px -12px rgba(37,99,235,0.15);
    transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease, border-color 0.25s ease;
}}
.mn-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 18px 40px -14px rgba(37,99,235,0.30);
    border-color: rgba(37,99,235,0.35);
}}
.mn-badge {{
    display:inline-block; padding: 4px 12px; border-radius: 999px;
    background: rgba(37,99,235,0.10); color:{PRIMARY}; font-weight:600; font-size:0.78rem;
    margin-bottom: 0.6rem; letter-spacing: 0.01em;
}}
.mn-gradient-text {{
    background: linear-gradient(120deg, {PRIMARY}, {ACCENT});
    -webkit-background-clip: text; background-clip: text; color: transparent !important;
}}
.mn-pill {{
    display:inline-block; padding: 3px 10px; border-radius: 999px; font-size:0.72rem;
    background: rgba(37,99,235,0.10); color:{PRIMARY}; margin: 2px 4px 2px 0; font-weight:600;
    transition: background 0.2s ease, transform 0.2s ease;
}}
.mn-pill:hover {{ background: rgba(37,99,235,0.2); transform: translateY(-1px); }}
.mn-hero {{
    background: linear-gradient(120deg, {PRIMARY}, {ACCENT});
    border-radius: 24px; padding: 2.6rem 2.2rem; color: white; margin-bottom: 1.4rem;
    box-shadow: 0 24px 60px -20px rgba(37,99,235,0.45);
    position: relative; overflow: hidden;
}}
.mn-hero::after {{
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(circle at 85% 15%, rgba(255,255,255,0.18), transparent 55%);
    pointer-events: none;
}}
.stApp, .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
    color: #0F172A;
}}

/* ---- buttons: base ---- */
.stButton>button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    padding: 0.45rem 0.65rem !important;
    font-size: 0.83rem !important;
    letter-spacing: 0;
    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, border-color 0.18s ease !important;
}}
.stButton>button:hover {{ transform: translateY(-2px); }}
.stButton>button:active {{ transform: translateY(0); }}

/* secondary (default) buttons — used for nav links + inactive states */
.stButton>button[kind="secondary"] {{
    background: rgba(37,99,235,0.06) !important;
    color: {PRIMARY} !important;
    border: 1px solid rgba(37,99,235,0.16) !important;
}}
.stButton>button[kind="secondary"]:hover {{
    background: rgba(37,99,235,0.14) !important;
    border-color: rgba(37,99,235,0.35) !important;
    box-shadow: 0 8px 18px -8px rgba(37,99,235,0.35);
}}

/* primary buttons — used for active nav item + CTAs */
.stButton>button[kind="primary"] {{
    background: linear-gradient(120deg, {PRIMARY}, {ACCENT}) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 8px 20px -8px rgba(37,99,235,0.55);
}}
.stButton>button[kind="primary"]:hover {{
    box-shadow: 0 12px 26px -8px rgba(37,99,235,0.6);
}}

[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {{
    background: #FFFFFF !important;
    color: #0F172A !important;
    border-radius: 10px !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {{
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}}
.mn-primary-btn button {{
    background: linear-gradient(120deg, {PRIMARY}, {ACCENT}) !important;
    color: white !important;
    border: none !important;
}}
div[data-testid="stForm"] {{
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 1.6rem;
    border: 1px solid rgba(255,255,255,0.7);
    box-shadow: 0 10px 34px -16px rgba(37,99,235,0.18);
}}

/* ---- expanders (FAQ) ---- */
[data-testid="stExpander"] {{
    border-radius: 14px !important;
    border: 1px solid rgba(37,99,235,0.12) !important;
    background: rgba(255,255,255,0.55) !important;
    overflow: hidden;
    transition: box-shadow 0.2s ease;
}}
[data-testid="stExpander"]:hover {{ box-shadow: 0 6px 20px -10px rgba(37,99,235,0.25); }}

/* ---- chat bubbles ---- */
[data-testid="stChatMessage"] {{
    border-radius: 16px !important;
    box-shadow: 0 4px 16px -8px rgba(15,23,42,0.12);
}}

/* ---- nav bar wrapper ---- */
.mn-navbar {{
    position: sticky; top: 0; z-index: 999;
    padding-top: 0.4rem;
    background: rgba(248,250,252,0.85);
    backdrop-filter: blur(14px);
}}

/* ---- scrollbar ---- */
::-webkit-scrollbar {{ height: 8px; width: 8px; }}
::-webkit-scrollbar-thumb {{ background: rgba(37,99,235,0.25); border-radius: 999px; }}

footer {{visibility:hidden;}}

/* ---- responsive tweaks ---- */
@media (max-width: 1150px) {{
    .stButton>button {{ font-size: 0.74rem !important; padding: 0.42rem 0.4rem !important; }}
}}
@media (max-width: 640px) {{
    .mn-hero {{ padding: 1.8rem 1.4rem; }}
    .stButton>button {{ font-size: 0.85rem !important; }}
}}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ #
# Navbar
# ------------------------------------------------------------------ #

def navbar():
    st.markdown("<div class='mn-navbar'>", unsafe_allow_html=True)

    # Row 1 — branding + auth, kept short so nothing wraps or overflows
    top_left, top_right = st.columns([3, 2.2])
    with top_left:
        st.markdown("### 🩺 MediNav <span class='mn-gradient-text'>AI</span>", unsafe_allow_html=True)
    with top_right:
        if st.session_state.user:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"👤 {st.session_state.user['name'].split()[0]}", key="nav_account", use_container_width=True):
                    go("My Account")
            with c2:
                if st.button("Logout", key="nav_logout", use_container_width=True):
                    st.session_state.user = None
                    go("Home")
                    st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Login", key="nav_login", use_container_width=True):
                    go("Login")
            with c2:
                if st.button("Get Started", key="nav_register", use_container_width=True, type="primary"):
                    go("Register")

    # Row 2 — nav links get the FULL page width (not squeezed next to the logo),
    # which is what fixes the label text spilling outside the button edges.
    labels = ["Home", "Hospitals", "Doctors", "AI Assistant", "Navigation", "Emergency", "About", "Contact"]
    nav_cols = st.columns(len(labels))
    for c, label in zip(nav_cols, labels):
        with c:
            is_active = st.session_state.page == label
            if st.button(label, key=f"nav_{label}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                go(label)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()


# ------------------------------------------------------------------ #
# Pages
# ------------------------------------------------------------------ #

def page_home():
    st.markdown(f"""
    <div class="mn-hero">
        <div class="mn-badge" style="background:rgba(255,255,255,0.2); color:white;">✨ AI-Powered Hospital Navigation</div>
        <h1 style="margin:0; font-size:2.6rem; color:white;">Navigate Hospitals Smarter with AI</h1>
        <p style="font-size:1.05rem; opacity:0.92; max-width:640px; color:white;">
        MediNav AI helps patients find hospitals, navigate inside hospitals, discover doctors,
        and receive instant AI healthcare assistance — all from one place.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("Get Started →", use_container_width=True, type="primary"):
            go("Register" if not st.session_state.user else "Hospitals")
            st.rerun()
    with c2:
        if st.button("Explore Hospitals", use_container_width=True):
            go("Hospitals")
            st.rerun()

    st.write("")
    s1, s2, s3, s4 = st.columns(4)
    for col, (num, label) in zip(
        [s1, s2, s3, s4],
        [("420+", "Hospitals connected"), ("1,850+", "Doctors available"),
         ("96,000+", "Patients helped"), ("98%", "Navigation accuracy")],
    ):
        with col:
            st.markdown(f"<div class='mn-card' style='text-align:center;'>"
                        f"<h2 class='mn-gradient-text' style='margin:0;'>{num}</h2>"
                        f"<p style='color:#64748B; margin:0;'>{label}</p></div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='mn-badge'>WHAT YOU GET</div>", unsafe_allow_html=True)
    st.subheader("Everything you need for a calmer hospital visit")
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(data.FEATURES):
        with cols[i % 3]:
            st.markdown(f"<div class='mn-card' style='min-height:150px; margin-bottom:1rem;'>"
                        f"<div style='font-size:1.6rem;'>{icon}</div>"
                        f"<b>{title}</b><p style='color:#64748B; font-size:0.9rem;'>{desc}</p></div>",
                        unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='mn-badge'>FAQ</div>", unsafe_allow_html=True)
    st.subheader("Common questions")
    for q, a in data.FAQS:
        with st.expander(q):
            st.write(a)


def page_about():
    st.markdown("<div class='mn-badge'>About MediNav AI</div>", unsafe_allow_html=True)
    st.title("Built to remove the confusion from hospital visits")
    st.write("MediNav AI is a healthcare navigation platform that combines hospital discovery, indoor "
             "wayfinding, and an AI health assistant into a single, calm experience.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='mn-card'><h4>🎯 Our mission</h4>"
                    "<p style='color:#64748B;'>To make every hospital visit predictable — helping patients "
                    "find the right care, the right doctor, and the right room without stress or delay.</p></div>",
                    unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='mn-card'><h4>👁 Our vision</h4>"
                    "<p style='color:#64748B;'>A future where AI quietly handles the logistics of healthcare, "
                    "so patients and doctors can focus on what matters — the visit itself.</p></div>",
                    unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='mn-card'><h4>The problem we're solving</h4>"
                "<p style='color:#64748B;'>Large hospitals are difficult to navigate on foot, patients don't "
                "know which department treats their symptoms, and appointment discovery is scattered across "
                "phone calls and front-desk queues. MediNav AI addresses each of these gaps with a connected "
                "hospital directory, indoor QR-based navigation, and an AI assistant trained to triage common "
                "questions.</p></div>", unsafe_allow_html=True)


def page_hospitals():
    st.markdown("<div class='mn-badge'>🏥 Hospital Finder</div>", unsafe_allow_html=True)
    st.title("Find a hospital near you")
    query = st.text_input("Search hospitals, departments, or areas...", "")

    filtered = [
        h for h in data.HOSPITALS
        if query.lower() in h["name"].lower()
        or query.lower() in h["location"].lower()
        or any(query.lower() in d.lower() for d in h["depts"])
    ] if query else data.HOSPITALS

    if not filtered:
        st.info("No hospitals match your search. Try a different term.")
        return

    cols = st.columns(3)
    for i, h in enumerate(filtered):
        with cols[i % 3]:
            status = "🟢 Open now" if h["open"] else "🔴 Closed"
            pills = "".join(f"<span class='mn-pill'>{d}</span>" for d in h["depts"])
            st.markdown(f"""
            <div class='mn-card' style='margin-bottom:1rem;'>
                <b>{h['name']}</b><br>
                <span style='color:#64748B; font-size:0.85rem;'>📍 {h['location']}</span><br>
                <span style='color:{ACCENT}; font-weight:600; font-size:0.85rem;'>⭐ {h['rating']} rating · {status}</span>
                <div style='margin:0.5rem 0;'>{pills}</div>
            </div>
            """, unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Navigate", key=f"nav_h_{i}", use_container_width=True):
                    go("Navigation")
                    st.rerun()
            with b2:
                if st.button("Book Appointment", key=f"book_h_{i}", use_container_width=True, type="primary"):
                    if not st.session_state.user:
                        st.session_state["pending_notice"] = "hospital"
                        go("Login")
                        st.rerun()
                    else:
                        db.create_booking(st.session_state.user["id"], hospital=h["name"])
                        st.toast(f"Appointment requested at {h['name']}!", icon="✅")


def page_doctors():
    st.markdown("<div class='mn-badge'>🩺 Doctor Finder</div>", unsafe_allow_html=True)
    st.title("Discover doctors by specialization")
    specs = ["All"] + sorted({d["spec"] for d in data.DOCTORS})
    chosen = st.radio("Filter by specialty", specs, horizontal=True, label_visibility="collapsed")

    filtered = data.DOCTORS if chosen == "All" else [d for d in data.DOCTORS if d["spec"] == chosen]

    cols = st.columns(3)
    for i, d in enumerate(filtered):
        with cols[i % 3]:
            langs = ", ".join(d["langs"])
            st.markdown(f"""
            <div class='mn-card' style='margin-bottom:1rem;'>
                <div style='display:flex; align-items:center; gap:0.7rem;'>
                    <div style='width:48px; height:48px; border-radius:50%; background:linear-gradient(120deg,{PRIMARY},{ACCENT});
                        color:white; display:flex; align-items:center; justify-content:center; font-weight:700;'>{d['initials']}</div>
                    <div><b>{d['name']}</b><br><span style='color:{ACCENT}; font-size:0.85rem; font-weight:600;'>{d['spec']}</span></div>
                </div>
                <p style='color:#64748B; font-size:0.85rem; margin-top:0.6rem;'>
                    🏥 {d['hospital']}<br>🎓 {d['exp']} experience<br>🌐 {langs}<br>📅 Available {d['avail']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Book Appointment", key=f"book_d_{i}", use_container_width=True, type="primary"):
                if not st.session_state.user:
                    st.session_state["pending_notice"] = "doctor"
                    go("Login")
                    st.rerun()
                else:
                    db.create_booking(st.session_state.user["id"], doctor=d["name"], department=d["spec"])
                    st.toast(f"Appointment requested with {d['name']}!", icon="✅")


def page_assistant():
    st.markdown("<div class='mn-badge'>🤖 AI Health Assistant</div>", unsafe_allow_html=True)
    st.title("Ask MediNav anything about your care")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    suggestion_cols = st.columns(4)
    suggestions = ["I have fever", "Nearest cardiologist", "Hospital timings", "What is diabetes?"]
    for col, s in zip(suggestion_cols, suggestions):
        with col:
            if st.button(s, key=f"sugg_{s}", use_container_width=True):
                _handle_chat(s)
                st.rerun()

    prompt = st.chat_input("Type your question...")
    if prompt:
        _handle_chat(prompt)
        st.rerun()

    st.caption("⚠️ MediNav Assistant offers general guidance only and does not replace diagnosis by a licensed "
               "medical professional. In an emergency, use the Emergency page or call your local emergency number.")


def _handle_chat(text: str):
    st.session_state.chat_history.append({"role": "user", "content": text})
    reply = data.get_bot_reply(text)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})


def page_navigation():
    st.markdown("<div class='mn-badge'>📱 Indoor Navigation</div>", unsafe_allow_html=True)
    st.title("Never get lost in a hospital again")
    st.write("Scan the QR code at any connected hospital entrance and MediNav AI plots the shortest route "
             "to your destination, floor by floor.")

    steps = [
        ("1", "Scan hospital QR", "Point your camera at the QR code posted near the entrance or help desk."),
        ("2", "Choose destination", "Pick a department, doctor's room, pharmacy, or lab from the indoor directory."),
        ("3", "AI calculates shortest path", "The route engine factors in lifts, ramps, and current corridor congestion."),
        ("4", "Voice navigation starts", "Follow spoken turn-by-turn directions in English, Hindi, or Telugu."),
    ]
    for num, title, desc in steps:
        st.markdown(f"""
        <div style='display:flex; gap:0.8rem; margin-bottom:0.8rem;'>
            <div style='width:34px; height:34px; border-radius:50%; background:linear-gradient(120deg,{PRIMARY},{ACCENT});
                color:white; display:flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0;'>{num}</div>
            <div><b>{title}</b><br><span style='color:#64748B; font-size:0.9rem;'>{desc}</span></div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🎙️ Try voice navigation demo", type="primary"):
        lines = ["Head straight for 40 meters.", "Turn right near Radiology.",
                 "Take the lift to Floor 2.", "Cardiology is on your left. You have arrived."]
        placeholder = st.empty()
        for line in lines:
            placeholder.info(f"🔊 \"{line}\"")
            time.sleep(1.1)
        placeholder.success("You have arrived at Cardiology, Room 204.")


def page_emergency():
    st.markdown("<div class='mn-badge' style='background:rgba(239,68,68,0.1); color:#EF4444;'>🚨 Emergency</div>",
                unsafe_allow_html=True)
    st.title("Get emergency help, fast")
    st.write("One tap connects you to the nearest emergency department and dispatches an ambulance to your location.")

    if st.button("🆘  SOS — TAP FOR EMERGENCY HELP", type="primary", use_container_width=True):
        with st.spinner("Alerting nearest hospital and dispatching ambulance..."):
            time.sleep(1.5)
        st.success("✅ Ambulance MH-42-AB dispatched · ETA 6 minutes")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='mn-card'><h4>Nearest hospitals</h4>", unsafe_allow_html=True)
        for h in data.HOSPITALS[:3]:
            st.markdown(f"**{h['name']}** — {h['location']}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='mn-card'>
            <h4>Emergency contacts</h4>
            National Ambulance: <b>108</b><br>
            Police: <b>100</b><br>
            MediNav Emergency Desk: <b>1800-123-4567</b>
        </div>
        """, unsafe_allow_html=True)


def page_contact():
    st.markdown("<div class='mn-badge'>✉️ Contact</div>", unsafe_allow_html=True)
    st.title("We'd love to hear from you")

    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Send message", type="primary")

        if submitted:
            if not (name and email and message):
                st.error("Please fill in your name, email, and message.")
            else:
                db.save_contact_message(name, email, phone, message)
                st.success("Message sent — we'll get back to you soon.")

    st.markdown("""
    <div class='mn-card' style='margin-top:1rem;'>
        📍 Level 6, Skyline Tech Park, Hyderabad, India<br>
        ✉️ hello@medinav.ai<br>
        📞 +91 90000 12345
    </div>
    """, unsafe_allow_html=True)


def page_login():
    st.markdown("<div style='max-width:420px; margin:0 auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Welcome back</h2>"
                "<p style='text-align:center; color:#64748B;'>Log in to manage your appointments and reports.</p>",
                unsafe_allow_html=True)

    if st.session_state.get("pending_notice"):
        st.info("Log in to continue booking your appointment.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            if not (email and password):
                st.error("Please enter both email and password.")
            else:
                ok, result = db.verify_login(email, password)
                if ok:
                    st.session_state.user = result
                    st.session_state.pending_notice = None
                    st.success(f"Welcome back, {result['name']}!")
                    time.sleep(0.6)
                    go("Home")
                    st.rerun()
                else:
                    st.error(result)

    st.markdown("<p style='text-align:center; color:#64748B;'>New to MediNav AI?</p>", unsafe_allow_html=True)
    if st.button("Create an account", use_container_width=True):
        go("Register")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def page_register():
    st.markdown("<div style='max-width:460px; margin:0 auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Create your account</h2>"
                "<p style='text-align:center; color:#64748B;'>Book appointments and get AI health guidance in minutes.</p>",
                unsafe_allow_html=True)

    with st.form("register_form"):
        name = st.text_input("Patient name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        c1, c2 = st.columns(2)
        with c1:
            password = st.text_input("Password", type="password")
        with c2:
            confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

        if submitted:
            if not (name and email and phone and password and confirm):
                st.error("Please fill in every field.")
            elif len(password) < 6:
                st.error("Password should be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, result = db.create_user(name, email, phone, password)
                if ok:
                    st.session_state.user = result
                    st.session_state.pending_notice = None
                    st.success("Account created successfully!")
                    time.sleep(0.6)
                    go("Home")
                    st.rerun()
                else:
                    st.error(result)

    st.markdown("<p style='text-align:center; color:#64748B;'>Already have an account?</p>", unsafe_allow_html=True)
    if st.button("Log in", use_container_width=True):
        go("Login")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def page_account():
    user = st.session_state.user
    if not user:
        go("Login")
        st.rerun()
        return

    st.markdown("<div class='mn-badge'>👤 My Account</div>", unsafe_allow_html=True)
    st.title(user["name"])
    st.write(f"📧 {user['email']}  ·  📞 {user['phone']}")

    st.subheader("Your appointments")
    bookings = db.get_bookings_for_user(user["id"])
    if not bookings:
        st.info("No appointments yet — book one from the Hospitals or Doctors page.")
    else:
        for b in bookings:
            target = b["doctor"] or b["hospital"]
            sub = f" · {b['department']}" if b["department"] else ""
            st.markdown(f"<div class='mn-card' style='margin-bottom:0.6rem;'>"
                        f"<b>{target}</b>{sub}<br>"
                        f"<span style='color:#64748B; font-size:0.85rem;'>Status: {b['status']} · "
                        f"Requested {b['created_at'][:10]}</span></div>", unsafe_allow_html=True)

    if st.button("Logout", type="primary"):
        st.session_state.user = None
        go("Home")
        st.rerun()


# ------------------------------------------------------------------ #
# Router
# ------------------------------------------------------------------ #

PAGES = {
    "Home": page_home,
    "About": page_about,
    "Hospitals": page_hospitals,
    "Doctors": page_doctors,
    "AI Assistant": page_assistant,
    "Navigation": page_navigation,
    "Emergency": page_emergency,
    "Contact": page_contact,
    "Login": page_login,
    "Register": page_register,
    "My Account": page_account,
}

navbar()
PAGES.get(st.session_state.page, page_home)()

st.write("")
st.divider()
st.caption("© 2026 MediNav AI. All rights reserved. Not a substitute for professional medical advice.")
