# app.py — Feedback collector (grouped layout, refined spacing & typography)
# Keep these files next to app.py:
#  - "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
#  - "cgmacirclelogo.jpeg"

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="AI-Accelerated Finance & Accounting Skills",
    page_icon="🗳️",
    layout="centered"
)

# ---------- CONFIG ----------
EXCEL_FILE = "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
CSV_OUT    = "ai_feedback_collected.csv"
LOGO_FILE  = "cgmacirclelogo.jpeg"

# ---------- GLOBAL STYLES ----------
st.markdown("""
<style>
/* Base type */
html, body, [class*="css"] { font-size: 18px; }
.block-container { max-width: 900px; padding-top: 1rem; padding-bottom: 2rem; }

/* Headings tighter to content they label */
h1, h2, h3 { font-weight: 800 !important; }
h1 { font-size: 2.05rem !important; margin: 0.15rem 0 0.75rem 0 !important; }
h2 { font-size: 1.32rem !important; margin: 0.15rem 0 0.30rem 0 !important; }
h3 { font-size: 1.08rem !important; margin: 0.10rem 0 0.25rem 0 !important; }

/* Card for a task */
.card {
  background: #fff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.04);
}

/* GROUPS inside the card */
.group {
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 14px;
  background: #fafafa;
  padding: 12px 14px;
  margin: 10px 0 12px 0;
}
.group .title {
  font-weight: 800;
  font-size: 1.02rem;
  margin: 0 0 6px 0;      /* title sits close to content */
  display: flex; align-items: center; gap: 8px;
}
.group .body {
  margin-top: 0;          /* content sits close to title */
  line-height: 1.35;
}

/* Visual accent at left to guide the eye */
.group.skill { border-left: 4px solid #6d28d9; }
.group.ai    { border-left: 4px solid #0ea5e9; }
.group.human { border-left: 4px solid #16a34a; }
.group.review{ border-left: 4px solid #f97316; }

/* Progress text */
.progress-text { font-weight: 700; opacity: .9; margin-bottom: .3rem; }

/* Radio + textarea sizing */
.stRadio > label, .stRadio div[role="radiogroup"] label { font-size: 1rem !important; }
textarea { font-size: 1rem !important; }

/* Primary button */
div.stButton > button:first-child {
  background: linear-gradient(135deg,#ec4899,#a855f7);
  color: #fff; border: none;
  padding: .62rem 1.05rem; font-weight: 700; border-radius: 12px;
}
div.stButton > button:first-child:hover { filter: brightness(.96); }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
if Path(LOGO_FILE).exists():
    st.image(LOGO_FILE, width=180)
st.title("AI-Accelerated Finance & Accounting Skills — Feedback")
st.markdown(
    "Review each AI-supported task and the proposed **Human Capability**. "
    "Choose **Agree** or **Disagree**; if you disagree, provide a revised statement. "
    "Download your feedback as a CSV at the end."
)

# ---------- LOAD DATA ----------
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
    st.error(f"Missing columns: {missing}. Found: {list(df.columns)}")
    st.stop()

# ---------- SESSION ----------
if "responses" not in st.session_state:
    st.session_state.responses = []
if "user_info" not in st.session_state:
    st.session_state.user_info = {"Name": "", "Email": ""}

# ---------- PROGRESS ----------
total = len(df)
done = len(st.session_state.responses)
st.markdown(f'<div class="progress-text">Progress: Task {min(done+1, total)} of {total}</div>', unsafe_allow_html=True)
st.progress(0 if total == 0 else done/total)

# ---------- MAIN ----------
if done < total:
    row = df.iloc[done]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # GROUP 1 — SKILL
    st.markdown('<div class="group skill">', unsafe_allow_html=True)
    st.markdown('<div class="title">🧾 Skill</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="body">{row["Skill"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # GROUP 2 — AI SUPPORTS
    st.markdown('<div class="group ai">', unsafe_allow_html=True)
    st.markdown('<div class="title">🤖 AI/GenAI Supports</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="body">{row["How AI/GenAI Supports"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # GROUP 3 — HUMAN CAPABILITY
    st.markdown('<div class="group human">', unsafe_allow_html=True)
    st.markdown('<div class="title">👤 Proposed Human Capability</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="body">{row["The New Human Capability Statement"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # GROUP 4 — REVIEW & SUBMIT
    st.markdown('<div class="group review">', unsafe_allow_html=True)
    st.markdown('<div class="title">📝 Review & Submit</div>', unsafe_allow_html=True)

    agree = st.radio(
        label="Do you agree with the Human Capability Statement?",
        options=["Yes", "No"],
        horizontal=True,
        key=f"agree_{done}"
    )

    revised = ""
    if agree == "No":
        revised = st.text_area(
            label="If you disagree, suggest your revised statement:",
            placeholder="Type your improved Human Capability statement…",
            key=f"revise_{done}"
        )

    st.markdown('</div>', unsafe_allow_html=True)  # /group review

    st.markdown("")  # small spacer
    if st.button("✅ Submit Feedback", type="primary"):
        st.session_state.responses.append({
            "Skill": row["Skill"],
            "AI Support": row["How AI/GenAI Supports"],
            "Original Human Capability": row["The New Human Capability Statement"],
            "Agree": agree,
            "Revised Human Capability": revised if agree == "No" else ""
        })
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # /card

else:
    st.success("🎉 You’ve completed all tasks — thank you for your insights!")
    st.markdown("Provide contact info (optional) before downloading your results:")

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
