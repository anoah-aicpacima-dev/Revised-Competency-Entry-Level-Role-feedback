
import streamlit as st
import pandas as pd
from PIL import Image

# Load logo
logo = Image.open("cgma-chartered-global-management-accountant-seeklogo.svg")
st.image(logo, width=150)

# Load the Excel file
FILE_NAME = "3 column ai_accelerated_accounting_skills Ops level blueprint.xlsx"
df = pd.read_excel(FILE_NAME)

# Initialize response storage
if "responses" not in st.session_state:
    st.session_state.responses = []

# App title and instructions
st.title("AI-Accelerated Finance & Accounting Skills Feedback")
st.markdown("Review each AI-supported task and the associated human capability statement. Let us know if you agree or suggest a revision.")

# Progress bar
total = len(df)
progress = len(st.session_state.responses)
st.progress(progress / total)

# Display current task
if progress < total:
    row = df.iloc[progress]

    st.markdown("---")
    st.subheader(f"🧾 Skill: {row['Skill']}")
    st.write(f"🤖 **AI/GenAI Supports**: {row['How AI/GenAI Supports']}")
    st.write(f"👤 **Proposed Human Capability**: {row['The New Human Capability Statement']}")

    agree = st.radio("Do you agree with the Human Capability Statement?", ["Yes", "No"], key=f"agree_{progress}")

    if agree == "No":
        revised = st.text_area("💬 Suggest your revised Human Capability Statement:",
                               value="", key=f"revise_{progress}")
    else:
        revised = ""

    if st.button("✅ Submit Feedback"):
        st.session_state.responses.append({
            "Skill": row["Skill"],
            "AI Support": row["How AI/GenAI Supports"],
            "Original Human Capability": row["The New Human Capability Statement"],
            "Agree": agree,
            "Revised Human Capability": revised
        })
        st.rerun()

else:
    st.success("🎉 All tasks reviewed — thank you for your insights!")
    result_df = pd.DataFrame(st.session_state.responses)

    csv_filename = "ai_feedback_collected.csv"
    result_df.to_csv(csv_filename, index=False)

    with open(csv_filename, "rb") as f:
        st.download_button(
            label="📥 Download Feedback as CSV",
            data=f,
            file_name=csv_filename,
            mime="text/csv"
        )
