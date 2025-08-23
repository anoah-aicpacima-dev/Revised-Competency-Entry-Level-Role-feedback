# app.py — Feedback collector (grouped layout fixed: single-block groups)
# Files expected in the same folder:
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

# ---------- STYLES ----------
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { max-width: 900px; padding-top: 1rem; padding-bottom: 2rem; }

/* Headings tighter to content they label */
h1, h2, h3 { font-weight: 800 !important; }
h1 { font-size: 2.05rem !important; margin: .15rem 0 .75rem 0 !important; }
h2 { font-size: 1.32rem !important; margin: .15rem 0 .30rem 0 !important; }
h3 { font-size: 1.08rem !important; margin: .10rem 0 .25rem 0 !important; }

/* Card */
.card {
  background: #fff;
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 8px 20px rgba(0,0,0,.04);
}

/* Group box; render title + body inside the SAME block */
.group {
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 14px;
  background: #fafafa;
  padding: 12px 14px;
  margin: 10px 0 12px 0;
  position: relative;
}
.group:before {
  conte
