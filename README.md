# MediNav AI — Streamlit App

A working healthcare navigation app built in Python with Streamlit. Unlike a static HTML mockup, the
buttons, login, and account creation here are **real**:

- **Real accounts** — registration and login are backed by a local SQLite database (`medinav.db`,
  created automatically on first run). Passwords are salted and hashed with PBKDF2 — never stored in plain text.
- **Real session state** — you stay logged in as you move between pages, with a logout button.
- **Real bookings** — tapping "Book Appointment" while logged in writes an actual row to the database,
  visible on the **My Account** page.
- **Working AI assistant** — a rule-based chatbot using Streamlit's native chat UI.
- **Working search/filter** — on the Hospitals and Doctors pages.
- **Working contact form** — messages are saved to the database.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

This opens the app in your browser, usually at `http://localhost:8501`.

## Files

```
.
├── app.py            # main app: navigation, pages, UI
├── db.py             # SQLite layer: users, bookings, contact messages
├── data.py           # static content: hospitals, doctors, FAQs, chatbot replies
├── requirements.txt
└── medinav.db         # created automatically on first run — safe to delete to reset all data
```

## Notes for deployment (Streamlit Community Cloud)

1. Push these files to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, and set the main file to `app.py`.
3. One caveat: Streamlit Community Cloud's filesystem resets on redeploys, so `medinav.db` (and any
   accounts/bookings in it) won't persist permanently there. For a production deployment, swap `db.py`
   to point at a hosted database (e.g. Postgres via `st.connection`) instead of local SQLite.

## Extending it

- Add more chatbot rules in `data.py` → `CHAT_RESPONSES`.
- Add more hospitals/doctors in `data.py`.
- Add password-reset, email verification, or admin views in `db.py` + `app.py`.
