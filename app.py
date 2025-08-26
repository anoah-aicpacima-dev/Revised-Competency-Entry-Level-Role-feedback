# dashboard_app.py — Secure dashboard pulling from Google Sheets (live)
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

st.set_page_config(layout="wide", page_title="Secure Feedback Dashboard")
st.title("🔐 Secure Feedback Dashboard")

# ---------- Password gate ----------
PASSWORD = "CGMA2025"  # change as needed
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.text_input("Enter dashboard password:", type="password")
    if pw == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pw:
        st.error("Incorrect password. Please try again.")
    st.stop()

st.title("📊 Feedback Dashboard — AI-Accelerated Finance & Accounting Tasks")

# ---------- Google Sheets client ----------
SCOPES_RO = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

@st.cache_data(ttl=60, show_spinner=False)
def load_feedback_df():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES_RO)
    client = gspread.authorize(creds)
    sh = client.open_by_key(st.secrets["GSHEET_ID"])
    ws = sh.worksheet(st.secrets.get("GSHEET_WORKSHEET", "Responses"))
    data = ws.get_all_records()  # list of dicts
    return pd.DataFrame(data)

# ---------- Load & sanity ----------
try:
    df = load_feedback_df()
except Exception as e:
    st.error(f"Could not load data from Google Sheets: {e}")
    st.stop()

if df.empty:
    st.warning("Sheet connected, but no responses yet.")
    st.stop()

# Normalize / ensure columns exist
for col in ["Agree", "SessionID", "Name", "Email", "Company Size", "Role Level",
            "Years Experience", "Industry", "Country/Region", "City", "Age Band", "Education", "SubmittedAtUTC"]:
    if col not in df.columns:
        df[col] = ""

df["Agree_norm"] = df["Agree"].astype(str).str.strip().str.lower()

# ---------- Summary metrics ----------
total_rows = len(df)
distinct_practitioners = df["SessionID"].nunique() if "SessionID" in df.columns else df.drop_duplicates(["Name","Email"]).shape[0]
agree_count = (df["Agree_norm"] == "yes").sum()
disagree_count = (df["Agree_norm"] == "no").sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Task Rows", total_rows)
c2.metric("Practitioners Completed", distinct_practitioners)  # ← your requested counter
c3.metric("Agreed", agree_count)
c4.metric("Disagreed", disagree_count)

# ---------- Filters ----------
with st.expander("🔎 Filters"):
    cols = st.columns(3)
    f_company = cols[0].selectbox("Company size", ["All"] + sorted([x for x in df["Company Size"].dropna().unique() if x]))
    f_role    = cols[1].selectbox("Role / Level", ["All"] + sorted([x for x in df["Role Level"].dropna().unique() if x]))
    f_country = cols[2].selectbox("Country/Region", ["All"] + sorted([x for x in df["Country/Region"].dropna().unique() if x]))
    cols2 = st.columns(3)
    f_years   = cols2[0].selectbox("Years Experience", ["All"] + sorted([x for x in df["Years Experience"].dropna().unique() if x]))
    f_industry= cols2[1].text_input("Industry contains (text filter)", "")
    f_agree   = cols2[2].selectbox("Agreement", ["All", "Yes", "No"])

def apply_filters(dfin: pd.DataFrame) -> pd.DataFrame:
    d = dfin.copy()
    if f_company != "All":
        d = d[d["Company Size"] == f_company]
    if f_role != "All":
        d = d[d["Role Level"] == f_role]
    if f_country != "All":
        d = d[d["Country/Region"] == f_country]
    if f_years != "All":
        d = d[d["Years Experience"] == f_years]
    if f_industry:
        d = d[d["Industry"].astype(str).str.contains(f_industry, case=False, na=False)]
    if f_agree != "All":
        d = d[d["Agree_norm"] == f_agree.lower()]
    return d

df_f = apply_filters(df)

# ---------- Table ----------
st.subheader("📋 Detailed Feedback")
st.dataframe(df_f, use_container_width=True)

# ---------- Charts ----------
if {"Skill", "Agree_norm"}.issubset(df_f.columns):
    st.subheader("📊 Agreement by Skill")
    chart = df_f.groupby(["Skill", "Agree_norm"]).size().unstack(fill_value=0)
    st.bar_chart(chart)

if "Company Size" in df_f.columns:
    st.subheader("🏢 Responses by Company Size")
    st.bar_chart(df_f["Company Size"].value_counts().sort_index())

if "Country/Region" in df_f.columns:
    st.subheader("🌍 Top Countries/Regions")
    st.bar_chart(df_f["Country/Region"].value_counts().head(15))

