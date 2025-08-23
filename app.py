# app.py — Feedback collector (styled with reliable logo handling)
# Keep these files next to app.py:
#  - "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
#  - "cgmacirclelogo.jpeg"   <-- your logo file

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI-Accelerated Finance & Accounting Skills", page_icon="🗳️", layout="centered")

# ---------------- CONFIG ----------------
EXCEL_FILE = "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
CSV_OUT    = "ai_feedback_collected.csv"
LOGO_FILE  = "cgmacirclelogo.jpeg"     # <- exact file name of your logo
# ----------------------------------------

# ---------- GLOBAL STYLES (CSS) ----------
st.markdown("""
<style>
html, body, [class*="css"]  { font-size: 18px; }

.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2.5rem;
  max-width: 900px;
}

h1, h2, h3 { font-weight: 800 !important; }
h1 { font-size: 2.1rem !important; margin: 0.2rem 0 0.9rem 0 !important; }
h2 { font-size: 1.35rem !important; margin: 0.2rem 0 0.35rem 0 !important; }
h3 { font-size: 1.1rem !important; margin: 0.1rem 0 0.25rem 0 !important; }

.section-label {
  font-weight: 700; letter-spacing: 0.15px;
  margin: 0.25rem 0 0.35rem 0;
}

.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 20px 22px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}

.hr {
  height: 1px;
  background: linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0.02));
  border: none;
  margin: 14px 0;
}

.progress-text {
  font-size: 0.95rem; font-weight: 700; opacity: 0.88;
  margin-bottom: 0.35rem;
}

.stRadio > label, .stRadio div[role="radiogroup"] label { font-size: 1rem !important; }
textarea { font-size: 1rem !important; }

div.stButton > button:first-child {
  background: linear-gradient(135deg, #ec4899, #a855f7);
  color: white; border: none;
  padding: 0.65rem 1.1rem;
  font-weight: 700;
  border-radius: 12px;
}
div.stButton > button:first-child:hover { filter: brightness(0.95); }

.caption { font-size: 0.95rem; opacity: 0.8; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
if Path(LOGO_FILE).exists():
    st.image(LOGO_FILE, width=180)
else:
    st.warning(f"⚠️ Logo file not found: {LOGO_FILE}. Upload it next to app.py.")

st.title("AI-Accelerated Finance & Accounting Skills — Feedback")
st.markdown(
    "Review each AI-supported task and the proposed **Human Capability**. "
    "Choose **Agree** or **Disagree**; if you disagree, provide a revised statement. "
    "At the end, you can download your feedback as a CSV."
)

# ---------- LOAD DATA ----------
if not Path(EXCEL_FILE).exists():
    st.error(f"Could not find the Excel file: **{EXCEL_FILE}**. Upload it next to `app.py` and rerun.")
    st.stop()

try:
    df = pd.read_excel(EXCEL_FILE)
except Exception as e:
    st.error(f"Failed to read Excel file `{EXCEL_FILE}`: {e}")
    st.stop()

required_cols = ["Skill", "How AI/GenAI Supports", "The New Human Capability Statement"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Your Excel is missing required columns: {missing}\n\nFound columns: {list(df.columns)}")
    st.stop()

# ---------- SESSION ----------
if "responses" not in st.session_state:
    st.session_state.responses = []
if "user_info" not in st.session_state:
    st.session_state.user_info = {"Name": "", "Email": ""}

# ---------- PROGRESS ----------
total = len(df)
progress_count = len(st.session_state.responses)
progress_ratio = 0.0 if total == 0 else progress_count / total

st.markdown(f'<div class="progress-text">Progress: Task {min(progress_count + 1, total)} of {total}</div>', unsafe_allow_html=True)
st.progress(progress_ratio)

# ---------- MAIN ----------
if progress_count < total:
    row = df.iloc[progress_count]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 🧾 Skill")
    st.markdown(f"{row['Skill']}")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">🤖 AI/GenAI Supports</div>', unsafe_allow_html=True)
    st.markdown(f"{row['How AI/GenAI Supports']}")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">👤 Proposed Human Capability</div>', unsafe_allow_html=True)
    st.markdown(f"{row['The New Human Capability Statement']}")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Do you agree with the Human Capability Statement?</div>', unsafe_allow_html=True)
    agree = st.radio("", ["Yes", "No"], horizontal=True, key=f"agree_{progress_count}")

    revised = ""
    if agree == "No":
        st.markdown('<div class="section-label">💬 Suggest your revised statement</div>', unsafe_allow_html=True)
        revised = st.text_area("", placeholder="Type your improved Human Capability statement here…", key=f"revise_{progress_count}")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if st.button("✅ Submit Feedback", type="primary"):
        st.session_state.responses.append({
            "Skill": row["Skill"],
            "AI Support": row["How AI/GenAI Supports"],
            "Original Human Capability": row["The New Human Capability Statement"],
            "Agree": agree,
            "Revised Human Capability": revised if agree == "No" else ""
        })
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.success("🎉 You’ve completed all tasks — thank you for your insights!")

    st.markdown("Before downloading your results, you may provide your contact details (optional):")
    name  = st.text_input("Name (optional)", key="name")
    email = st.text_input("Email (optional)", key="email")

    st.session_state.user_info["Name"]  = name
    st.session_state.user_info["Email"] = email

    result_df = pd.DataFrame(st.session_state.responses)
    if not result_df.empty:
        result_df["Name"]  = st.session_state.user_info["Name"]
        result_df["Email"] = st.session_state.user_info["Email"]

        result_df.to_csv(CSV_OUT, index=False)
        with open(CSV_OUT, "rb") as f:
            st.download_button(
                label="📥 Download Feedback as CSV",
                data=f,
                file_name=CSV_OUT,
                mime="text/csv",
                type="primary"
            )

        with st.expander("Preview your CSV data"):
            st.dataframe(result_df, use_container_width=True)
    else:
        st.info("No responses captured. Go back and submit at least one task.")
