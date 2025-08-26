# app.py — Feedback collector (Google Sheets + per-person tabs + demographics)
# Put these files next to app.py:
#   1) Excel:  "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
#   2) (Optional) Logo: "cgmacirclelogo.jpeg"  (change LOGO_FILE if different)

import streamlit as st
import pandas as pd
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import html
import re

# --- Google Sheets ---
from google.oauth2.service_account import Credentials
import gspread

st.set_page_config(page_title="AI-Accelerated Finance & Accounting Skills — Feedback",
                   page_icon="🗳️", layout="centered")

# ---------------- CONFIG ----------------
EXCEL_FILE = "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
CSV_OUT    = "ai_feedback_collected.csv"  # still offered as a download
LOGO_FILE  = "cgmacirclelogo.jpeg"        # set to your logo file name

# ---------------- STYLES ----------------
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { max-width: 900px; padding-top: 1rem; padding-bottom: 2rem; }
h1, h2, h3 { font-weight: 800 !important; }
h1 { font-size: 2.05rem !important; margin: .15rem 0 .75rem 0 !important; }
h2 { font-size: 1.32rem !important; margin: .15rem 0 .30rem 0 !important; }
h3 { font-size: 1.08rem !important; margin: .10rem 0 .25rem 0 !important; }
.card { background:#fff; border:1px solid rgba(0,0,0,.06); border-radius:18px; padding:14px 16px; box-shadow:0 8px 20px rgba(0,0,0,.04); }
.group { border:1px solid rgba(0,0,0,.06); border-radius:14px; background:#fafafa; padding:12px 14px; margin:10px 0 12px 0; position:relative; }
.group:before { content:""; position:absolute; left:-1px; top:-1px; bottom:-1px; width:6px; border-radius:14px 0 0 14px; }
.group.skill:before { background:#6d28d9; }
.group.ai:before    { background:#0ea5e9; }
.group.human:before { background:#16a34a; }
.group.review:before{ background:#f97316; }
.group .title { font-weight:800; font-size:1.02rem; margin:0 0 6px 0; display:flex; align-items:center; gap:8px; }
.group .body { margin-top:0; line-height:1.35; }
.progress-text { font-weight:700; opacity:.9; margin-bottom:.3rem; }
.stRadio > label, .stRadio div[role="radiogroup"] label { font-size:1rem !important; }
textarea { font-size:1rem !important; }
div.stButton > button:first-child { background:linear-gradient(135deg,#ec4899,#a855f7); color:#fff; border:none; padding:.62rem 1.05rem; font-weight:700; border-radius:12px; }
div.stButton > button:first-child:hover { filter:brightness(.96); }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
if Path(LOGO_FILE).exists():
    st.image(LOGO_FILE, width=180)

st.title("AI-Accelerated Finance & Accounting Skills — Feedback")
st.markdown(
    "Review each AI-supported task and the proposed **Human Capability**. "
    "Choose **Agree** or **Disagree**; if you disagree, provide a revised statement. "
    "At the end, share a few optional details about yourself and **submit**. "
    "Your input helps shape the next generation of entry-level competencies."
)

# ---------------- DATA LOAD ----------------
if not Path(EXCEL_FILE).exists():
    st.error(f"Could not find: **{EXCEL_FILE}**. Upload it next to `app.py` and rerun.")
    st.stop()

try:
    df = pd.read_excel(EXCEL_FILE)
except Exception as e:
    st.error(f"Failed to read `{EXCEL_FILE}`: {e}")
    st.stop()

required_cols = ["Skill", "How AI/GenAI Supports", "The New Human Capability Statement"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing columns in Excel: {missing}\n\nFound: {list(df.columns)}")
    st.stop()

# ---------------- STATE ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid4().hex  # unique per respondent
if "responses" not in st.session_state:
    st.session_state.responses = []  # list of dicts (one per task)
if "idx" not in st.session_state:
    st.session_state.idx = 0  # current row pointer

# ---------------- HELPERS: HTML blocks ----------------
def esc(x: object) -> str:
    return html.escape(str(x)).replace("\n", "<br>")

def group_html(title: str, body: str, cls: str) -> str:
    return f"<div class='group {cls}'><div class='title'>{title}</div><div class='body'>{body}</div></div>"

# ---------------- HELPERS: Google Sheets ----------------
SCOPES_RW = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource(show_spinner=False)
def _gs_client():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES_RW)
    return gspread.authorize(creds)

def _open_sheet():
    client = _gs_client()
    return client.open_by_key(st.secrets["GSHEET_ID"])

def _sanitize_title(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return "Anonymous"
    s = re.sub(r"[^A-Za-z0-9 _\\-()]+", "", s)
    s = re.sub(r"\\s+", " ", s)
    return s[:80]

def _get_or_create_ws(sh, title: str, rows: int = 200, cols: int = 26):
    try:
        return sh.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=rows, cols=cols)

def _append_df(ws, df: pd.DataFrame):
    existing = ws.get_all_values()
    if not existing:
        ws.append_row(df.columns.tolist())
    if not df.empty:
        ws.append_rows(df.astype(str).values.tolist())

def save_submission_to_sheets(result_df: pd.DataFrame, name: str, email: str):
    """Append rows to Master tab + a per-person tab."""
    sh = _open_sheet()
    master_title = st.secrets.get("GSHEET_WORKSHEET", "Responses")
    ws_master = _get_or_create_ws(sh, master_title)
    _append_df(ws_master, result_df)

    # per-person tab title
    email_user = (email or "").split("@")[0]
    base = (name or "") + (f" ({email_user})" if email_user else "")
    person_title = _sanitize_title(base or "Anonymous")
    ws_person = _get_or_create_ws(sh, person_title)
    _append_df(ws_person, result_df)

# ---------------- PROGRESS ----------------
total = len(df)
done = st.session_state.idx
st.markdown(f"<div class='progress-text'>Progress: Task {min(done+1, total)} of {total}</div>", unsafe_allow_html=True)
st.progress(0 if total == 0 else done/total)

# ---------------- MAIN FLOW ----------------
if st.session_state.idx < total:
    row = df.iloc[st.session_state.idx]

    skill_html = group_html("🧾 Skill", esc(row["Skill"]), "skill")
    ai_html    = group_html("🤖 AI/GenAI Supports", esc(row["How AI/GenAI Supports"]), "ai")
    human_html = group_html("👤 Proposed Human Capability", esc(row["The New Human Capability Statement"]), "human")

    st.markdown("<div class='card'>" + skill_html + ai_html + human_html + "</div>", unsafe_allow_html=True)

    st.markdown(group_html("📝 Review &amp; Submit for this task", "", "review"), unsafe_allow_html=True)

    agree = st.radio("Do you agree with the Human Capability Statement?",
                     ["Yes", "No"], horizontal=True, key=f"agree_{st.session_state.idx}")

    revised = ""
    if agree == "No":
        revised = st.text_area("If you disagree, suggest your revised statement:",
                               placeholder="Type your improved Human Capability statement…",
                               key=f"revise_{st.session_state.idx}")

    if st.button("✅ Save & Next", type="primary"):
        st.session_state.responses.append({
            "SessionID": st.session_state.session_id,
            "Skill": row["Skill"],
            "AI Support": row["How AI/GenAI Supports"],
            "Original Human Capability": row["The New Human Capability Statement"],
            "Agree": agree,
            "Revised Human Capability": revised if agree == "No" else "",
        })
        st.session_state.idx += 1
        st.rerun()

else:
    st.success("🎉 You’ve completed all tasks — thank you!")
    st.markdown("Please share a few optional details, then press **Submit to AICPA & CIMA** to record your input.")

    with st.form("respondent_meta"):
        name  = st.text_input("Name (optional)")
        email = st.text_input("Email (optional)")
        company_size = st.selectbox("Company size", [
            "", "1–10", "11–50", "51–200", "201–1,000", "1,001–5,000", "5,001–10,000", "10,000+"
        ])
        role_level = st.selectbox("Role / Level", [
            "", "Student", "Entry", "Associate", "Senior", "Manager", "Director", "VP/CFO", "Other"
        ])
        years_exp = st.selectbox("Years of experience", ["", "0–1", "2–4", "5–9", "10–14", "15+"])
        industry = st.text_input("Industry (free text, optional)")
        country = st.text_input("Country / Region (optional)")
        city = st.text_input("City (optional)")
        age_band = st.selectbox("Age Band (optional)", ["", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"])
        education = st.selectbox("Highest education (optional)", ["", "High school", "Associate", "Bachelor's", "Master's", "Doctorate", "Other"])

        submitted = st.form_submit_button("📤 Submit to AICPA & CIMA (save to Google Sheets)", type="primary")

    if submitted:
        if not st.session_state.responses:
            st.warning("No responses found for this session.")
            st.stop()

        # Build final DataFrame with demographics replicated across rows
        result_df = pd.DataFrame(st.session_state.responses)
        result_df["Name"] = name
        result_df["Email"] = email
        result_df["Company Size"] = company_size
        result_df["Role Level"] = role_level
        result_df["Years Experience"] = years_exp
        result_df["Industry"] = industry
        result_df["Country/Region"] = country
        result_df["City"] = city
        result_df["Age Band"] = age_band
        result_df["Education"] = education
        result_df["Completed"] = True
        result_df["SubmittedAtUTC"] = datetime.utcnow().isoformat() + "Z"

        # Save to Google Sheets (Master + Per-person tab)
        try:
            save_submission_to_sheets(result_df, name=name, email=email)
            st.success("✅ Responses recorded to Google Sheets (master + personal tab).")
        except Exception as e:
            st.warning(f"Could not save to Google Sheets: {e}")

        # Also offer a CSV download for the respondent
        result_df.to_csv(CSV_OUT, index=False)
        with open(CSV_OUT, "rb") as f:
            st.download_button("📥 Download your responses (CSV)", f, file_name=CSV_OUT, mime="text/csv")

        st.markdown("You may now close this tab. Thank you for contributing!")
