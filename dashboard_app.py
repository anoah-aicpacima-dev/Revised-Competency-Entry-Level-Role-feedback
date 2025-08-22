import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("📊 Feedback Dashboard: AI-Accelerated Finance & Accounting Tasks")

# Load CSV file
csv_file = "ai_feedback_collected.csv"

if not os.path.exists(csv_file):
    st.warning("No feedback CSV found yet. Please collect responses first.")
else:
    df = pd.read_csv(csv_file)

    # Summary metrics
    st.subheader("🔍 Summary Insights")
    total_responses = len(df)
    agree_count = df["Agree"].str.lower().value_counts().get("yes", 0)
    disagree_count = df["Agree"].str.lower().value_counts().get("no", 0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks Reviewed", total_responses)
    col2.metric("Agreed", agree_count)
    col3.metric("Disagreed", disagree_count)

    # Show detailed feedback table
    st.subheader("📋 Detailed Feedback")
    st.dataframe(df)

    # Bar chart of agreement by task
    st.subheader("📊 Agreement by Task")
    agree_chart = df.groupby(["Skill", "Agree"]).size().unstack(fill_value=0)
    st.bar_chart(agree_chart)

    # Optional filter for reviewers
    if "Name" in df.columns and df["Name"].notna().any():
        st.subheader("👤 Filter by Reviewer (optional)")
        reviewers = ["All"] + sorted(df["Name"].dropna().unique())
        selected = st.selectbox("Reviewer", reviewers)

        if selected != "All":
            st.dataframe(df[df["Name"] == selected])
