# app.py — Feedback collector (grouped layout fixed)
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

# ---------- STYLES ----------
st.markdown(
    """
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { max-width: 900px; padding-top: 1rem; padding-bottom: 2rem; }

h1, h2, h3 { font-weight: 800 !important; }
h1 { font-size: 2.05rem !important; margin: .15rem 0 .75rem 0 !important; }
h2 { font-size: 1.32rem !important; margin: .15rem 0 .30rem 0 !important; }
h3 { font-size: 1.08rem !important; margin: .10rem 0 .25rem 0 !important; }

.card {
  background: #fff;
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 8px 20px rgba(0,0,0,.04);
}

.group {
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 14px;
  background: #fafafa;
  padding: 12px 14px;
  margin: 10px 0 12px 0;
  position: relative;
}
.group:before {
  content: "";
  position: absolute;
  left: -1px; top: -1px; bottom: -1px;
  width: 6px; border-radius: 14px 0 0 14px;
}
.group.skill:before { background: #6d28d9; }
.group.ai:before    { background: #0ea5e9; }
.group.human:before { background: #16a34a; }
.group.review:before{ background: #f97316; }

.group .title {
  font-weight: 800;
  font-size: 1.02rem;
  margin: 0 0 6px 0;
  display: flex; align-items: center; gap: 8px;
}
.group .body { margin-top: 0; line-height: 1.35; }

.progress-text { font-weight: 700; opacity: .9; margin-bottom: .3rem; }

.stRadio > label, .stRadio div[role="radiogroup"] label { font-size: 1rem !important; }
textarea { font-size: 1rem !important; }

div.stButton > button:first-child {
  background: linear-gradient(135deg,#ec4899,#a855f7);
  color: #fff; border: none;
  padding: .62rem 1.05rem; font-weight: 700; border-radius: 12px;
}
div.stButton > button:first-child:hover { fil
