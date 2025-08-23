# app.py — Feedback collector for AI-Accelerated Finance & Accounting Skills
# Place this file in the same repo folder as:
#   - "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
#   - "cgmacirclelogo.jpeg"

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI-Accelerated Finance & Accounting Skills Feedback", page_icon="🗳️", layout="centered")

# ---------- CONFIG ----------
EXCEL_FILE = "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
CSV_OUT    = "ai_feedback_collected.csv"
LOGO_FILE  = "cgmacirclelogo.jpeg"  # <- ensure this exact file name exists next to app.py
PROGRESS_BAR_HEIGHT = 20

# ---------- HEADER ----------
logo_path = Path(LOGO_FILE)
if logo_path.exists():
    st.image(str(logo_path), width=180)
else:
    st.warning(f"Logo not found: {LOGO_FILE}. (Upload it next to app.py)")

st.title("AI-Accelerated Finance & Accounting Skills — Feedback")
st.markdown(
    "Review each AI-supported task and the proposed **Human Capability**. "
    "Choose **Agree** or **Disagree**; if you disagree, provide a revised statement. "
    "At the end, you can download your feedback as a CSV."
)

# ---------- LOAD DATA ----------
xlsx_path = Path(EXCEL_FILE)
if not xlsx_path.exists():
    st.error(f"Could not find the Excel file: **{EXCEL_FILE}**. Upload it next to `app.py` and rerun.")
    st.stop()

try:
    df = pd.read_excel(xlsx_path)
except Exception as e:
    st.error(f"Failed to read Excel file `{EXCEL_FILE}`: {e}")
    st.stop()

required_cols = ["Skill", "How AI/GenAI Supports", "The New Human Capability Statement"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Your Excel is missing required columns: {missing}\n\nFound columns: {list(df.columns)}")
    st.stop()

# ---------- SESSION STATE ----------
if "responses" not in st.session_state:
    st.session_state.responses = []  # list of dict rows

if "user_info" not in st.session_state:
    st.session_state.user_info = {"Name": "", "Email": ""}

# ---------- PROGRESS ----------
total = len(df)
progress_count = len(st.session_state.responses)
progress_ratio = 0.0 if total == 0 else progress_count / total

st.markdown(f"**Progress: Task {min(progress_count + 1, total)} of {total}**")
st.progress(progress_ratio)

# ---------- MAIN FLOW ----------
if progress_count < total:
    row = df.iloc[progress_count]

    st.markdown("---")
    st.subheader(f"🧾 Skill")
    st.write(row["Skill"])

    st.markdown("**🤖 AI/GenAI Supports**")
    st.write(row["How AI/GenAI Supports"])

    st.markdown("**👤 Proposed Human Capability**")
    st.write(row["The New Human Capability Statement"])

    agree = st.radio(
        "Do you agree with the Human Capability Statement?",
        ["Yes", "No"],
        key=f"agree_{progress_count}"
    )

    if agree == "No":
        revised = st.text_area(
            "💬 Suggest your revised Human Capability Statement:",
            value="",
            key=f"revise_{progress_count}"
        )
    else:
        revised = ""  # keep blank to clearly separate from the original

    if st.button("✅ Submit Feedback", type="primary"):
        st.session_state.responses.append({
            "Skill": row["Skill"],
            "AI Support": row["How AI/GenAI Supports"],
            "Original Human Capability": row["The New Human Capability Statement"],
            "Agree": agree,
            "Revised Human Capability": revised
        })
        st.rerun()

else:
    st.markdown("---")
    st.success("🎉 You’ve completed all tasks — thank you for your insights!")

    # Collect optional contact info
    st.markdown("Before downloading your results, you may provide your contact details (optional):")
    name  = st.text_input("Name (optional)", key="name")
    email = st.text_input("Email (optional)", key="email")

    st.session_state.user_info["Name"]  = name
    st.session_state.user_info["Email"] = email

    # Build results DataFrame
    result_df = pd.DataFrame(st.session_state.responses)
    if not result_df.empty:
        result_df["Name"]  = st.session_state.user_info["Name"]
        result_df["Email"] = st.session_state.user_info["Email"]

        # Save & offer download
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
