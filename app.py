import streamlit as st
from PIL import Image, ImageFilter
import io
import zipfile
import re
import json
import time
import csv
import os
import subprocess
import tempfile
import shutil
from datetime import datetime
import pandas as pd
import google.generativeai as genai
import streamlit.components.v1 as components

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="PixelBoost AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ SESSION STATE ============
if 'processed' not in st.session_state:
    st.session_state.processed = 0
if 'metadata_generated' not in st.session_state:
    st.session_state.metadata_generated = 0
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'upscale_click_count' not in st.session_state:
    st.session_state.upscale_click_count = 0

# ============ CSS MOBILE-FRIENDLY ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: #07070e;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main > div { 
    padding: 0 !important; 
    max-width: 100% !important;
}

#MainMenu, footer, .stDeployButton { display: none !important; visibility: hidden !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #6d6aff44; border-radius: 99px; }

/* ════════════════════════════════
   HEADER - MOBILE FRIENDLY
════════════════════════════════ */
.pb-header {
    position: relative;
    overflow: hidden;
    padding: 1.25rem 1rem 1rem;
    border-bottom: 1px solid #ffffff0a;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.pb-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(circle, #6d6aff18 1px, transparent 1px);
    background-size: 28px 28px;
    animation: gridShimmer 8s ease-in-out infinite;
    pointer-events: none;
}

.pb-header::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        #07070e 0%,
        transparent 30%,
        transparent 70%,
        #07070e 100%);
    pointer-events: none;
}

@keyframes gridShimmer {
    0%, 100% { opacity: 0.4; transform: translateX(0); }
    50% { opacity: 0.9; transform: translateX(14px); }
}

.pb-logo-wrap {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 0.625rem;
    flex-wrap: wrap;
}

.pb-logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #6d6aff, #a78bfa);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: 0 0 24px #6d6aff44;
    flex-shrink: 0;
}

.pb-logo-text {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e2ff;
    letter-spacing: -0.02em;
    white-space: nowrap;
}

.pb-logo-text span {
    color: #6d6aff;
}

.pb-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #6d6aff18;
    border: 1px solid #6d6aff33;
    color: #a78bfa;
    padding: 0.15rem 0.6rem;
    border-radius: 99px;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.pb-header-right {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.pb-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #ffffff06;
    border: 1px solid #ffffff0d;
    border-radius: 99px;
    padding: 0.2rem 0.7rem;
    font-size: 0.65rem;
    color: #ffffff55;
    font-weight: 500;
    white-space: nowrap;
}

.pb-pill-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 6px #22c55e;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ════════════════════════════════
   STATS STRIP - MOBILE FRIENDLY
════════════════════════════════ */
.pb-stats {
    display: flex;
    align-items: stretch;
    gap: 0;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #ffffff0a;
    background: #0f0f1a;
    flex-wrap: wrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.pb-stat {
    padding: 0.75rem 1.25rem 0.75rem 0;
    margin-right: 1.25rem;
    border-right: 1px solid #ffffff08;
    flex-shrink: 0;
}

.pb-stat:last-child {
    border-right: none;
    margin-right: 0;
}

.pb-stat-num {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #6d6aff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}

.pb-stat-label {
    font-size: 0.6rem;
    color: #ffffff33;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
    margin-top: 0.15rem;
}

/* ════════════════════════════════
   MAIN WORKSPACE - MOBILE FRIENDLY
════════════════════════════════ */
.pb-workspace {
    padding: 1rem;
    display: grid;
    gap: 1rem;
}

/* ════════════════════════════════
   SECTION LABEL
════════════════════════════════ */
.pb-section-label {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #ffffff30;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.pb-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #ffffff08;
}

/* ════════════════════════════════
   CARD - MOBILE FRIENDLY
════════════════════════════════ */
.pb-card {
    background: #0f0f1a;
    border: 1px solid #ffffff0a;
    border-radius: 12px;
    padding: 1rem;
    transition: border-color 0.2s;
}

.pb-card:hover {
    border-color: #6d6aff22;
}

/* ════════════════════════════════
   API KEY CARD - MOBILE FRIENDLY
════════════════════════════════ */
.pb-api-card {
    background: linear-gradient(135deg, #0f0f1a 0%, #12102a 100%);
    border: 1px solid #6d6aff22;
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.pb-key-icon {
    width: 32px;
    height: 32px;
    background: #6d6aff18;
    border: 1px solid #6d6aff33;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}

/* ════════════════════════════════
   STREAMLIT OVERRIDES - MOBILE
════════════════════════════════ */

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
div[data-baseweb="select"] > div {
    background: #161628 !important;
    border: 1px solid #ffffff12 !important;
    border-radius: 10px !important;
    color: #e2e2ff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    transition: border-color 0.2s !important;
    padding: 0.5rem 0.75rem !important;
    min-height: 40px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #6d6aff66 !important;
    box-shadow: 0 0 0 3px #6d6aff18 !important;
}

.stTextInput > div > div > input::placeholder {
    color: #ffffff30 !important;
}

/* Labels */
.stTextInput label,
.stSelectbox label,
.stSlider label,
.stCheckbox label {
    color: #ffffff55 !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
    margin-bottom: 0.3rem !important;
}

/* Slider */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #6d6aff, #a78bfa) !important;
}

.stSlider > div > div > div > div {
    background: #ffffff !important;
    border: 2px solid #6d6aff !important;
    box-shadow: 0 0 8px #6d6aff66 !important;
    width: 18px !important;
    height: 18px !important;
}

[data-testid="stSliderTickBarMin"],
[data-testid="stSliderTickBarMax"] {
    color: #ffffff33 !important;
    font-size: 0.6rem !important;
}

/* Checkboxes */
.stCheckbox > label {
    color: #e2e2ff !important;
    font-size: 0.8rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-weight: 400 !important;
}

/* Buttons - Mobile Friendly */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
    min-height: 44px !important;
    touch-action: manipulation !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6d6aff 0%, #8b7ff7 100%) !important;
    color: white !important;
    box-shadow: 0 4px 16px #6d6aff44 !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px #6d6aff55 !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

.stButton > button:not([kind="primary"]) {
    background: #161628 !important;
    color: #e2e2ff !important;
    border: 1px solid #ffffff12 !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: #1d1d38 !important;
    border-color: #6d6aff44 !important;
    transform: translateY(-1px) !important;
}

/* File uploader - Mobile */
[data-testid="stFileUploader"] > div {
    background: #0f0f1a !important;
    border: 2px dashed #ffffff12 !important;
    border-radius: 12px !important;
    transition: border-color 0.2s, background 0.2s !important;
    padding: 1.5rem 1rem !important;
}

[data-testid="stFileUploader"] > div:hover {
    border-color: #6d6aff55 !important;
    background: #12102a !important;
}

[data-testid="stFileUploader"] label {
    color: #ffffff55 !important;
    font-size: 0.8rem !important;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6d6aff, #a78bfa) !important;
    border-radius: 99px !important;
}

.stProgress > div > div {
    background: #161628 !important;
    border-radius: 99px !important;
    height: 6px !important;
}

/* Alerts */
.stAlert {
    border-radius: 10px !important;
    border: none !important;
}

[data-baseweb="notification"] {
    background: #161628 !important;
    border-radius: 10px !important;
}

.stSuccess > div {
    background: #052013 !important;
    border: 1px solid #22c55e33 !important;
    color: #4ade80 !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-size: 0.8rem !important;
}

.stError > div {
    background: #1a0505 !important;
    border: 1px solid #ef444433 !important;
    color: #f87171 !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-size: 0.8rem !important;
}

.stInfo > div {
    background: #050f2a !important;
    border: 1px solid #6d6aff33 !important;
    color: #a78bfa !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-size: 0.8rem !important;
}

/* Dataframe - Mobile */
[data-testid="stDataFrame"] {
    border: 1px solid #ffffff0a !important;
    border-radius: 10px !important;
    overflow: auto !important;
    -webkit-overflow-scrolling: touch !important;
}

[data-testid="stDataFrame"] table {
    font-size: 0.7rem !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #ffffff0a !important;
    border-radius: 10px !important;
    background: #0f0f1a !important;
}

[data-testid="stExpander"] summary {
    color: #ffffff55 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f0f1a !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #ffffff08 !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    color: #ffffff44 !important;
    font-weight: 500 !important;
    font-size: 0.7rem !important;
    padding: 0.3rem 0.75rem !important;
    white-space: nowrap !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #6d6aff22 !important;
    color: #e2e2ff !important;
}

/* Download button */
.stDownloadButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    background: #161628 !important;
    color: #e2e2ff !important;
    border: 1px solid #6d6aff33 !important;
    min-height: 44px !important;
}

.stDownloadButton > button:hover {
    background: #1d1d38 !important;
    border-color: #6d6aff66 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px #6d6aff22 !important;
}

/* Select dropdown */
div[data-baseweb="popover"] {
    background: #161628 !important;
    border: 1px solid #ffffff12 !important;
    border-radius: 10px !important;
}

div[data-baseweb="menu"] li {
    color: #e2e2ff !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 0.75rem !important;
}

div[data-baseweb="menu"] li:hover {
    background: #6d6aff22 !important;
}

/* ── Mobile grid adjustments ── */
@media (max-width: 768px) {
    .stColumns {
        flex-wrap: wrap !important;
    }
    
    [data-testid="column"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
        padding: 0.25rem 0 !important;
    }
    
    .stSlider > div > div {
        padding: 0.25rem 0 !important;
    }
    
    .stSelectbox > div {
        margin: 0.25rem 0 !important;
    }
    
    .stCheckbox {
        margin: 0.25rem 0 !important;
    }
}

/* ── Small mobile ── */
@media (max-width: 480px) {
    .pb-header {
        padding: 0.75rem 0.75rem 0.75rem;
    }
    
    .pb-logo-text {
        font-size: 0.95rem;
    }
    
    .pb-logo-icon {
        width: 30px;
        height: 30px;
        font-size: 0.85rem;
    }
    
    .pb-badge {
        font-size: 0.5rem;
        padding: 0.1rem 0.4rem;
    }
    
    .pb-pill {
        font-size: 0.55rem;
        padding: 0.15rem 0.5rem;
    }
    
    .pb-stats {
        padding: 0.5rem 0.75rem;
        gap: 0.25rem;
    }
    
    .pb-stat {
        padding: 0.5rem 0.75rem 0.5rem 0;
        margin-right: 0.75rem;
    }
    
    .pb-stat-num {
        font-size: 1.25rem;
    }
    
    .pb-stat-label {
        font-size: 0.5rem;
    }
    
    .pb-workspace {
        padding: 0.75rem;
        gap: 0.75rem;
    }
    
    .pb-card {
        padding: 0.75rem;
    }
    
    .pb-section-label {
        font-size: 0.55rem;
    }
    
    .stButton > button {
        font-size: 0.75rem !important;
        padding: 0.5rem 0.75rem !important;
        min-height: 40px !important;
    }
    
    .stDownloadButton > button {
        font-size: 0.75rem !important;
        padding: 0.5rem 0.75rem !important;
        min-height: 40px !important;
    }
    
    [data-testid="stFileUploader"] > div {
        padding: 1rem 0.75rem !important;
    }
    
    [data-testid="stFileUploader"] label {
        font-size: 0.7rem !important;
    }
    
    .stTextInput > div > div > input {
        font-size: 0.7rem !important;
        padding: 0.4rem 0.6rem !important;
        min-height: 36px !important;
    }
    
    .stSelectbox > div > div {
        font-size: 0.7rem !important;
        min-height: 36px !important;
    }
}

/* ── Touch-friendly buttons ── */
@media (pointer: coarse) {
    .stButton > button {
        min-height: 48px !important;
    }
    
    .stDownloadButton > button {
        min-height: 48px !important;
    }
    
    .stTextInput > div > div > input {
        min-height: 44px !important;
        font-size: 16px !important; /* Prevent iOS zoom */
    }
    
    .stSelectbox > div > div {
        min-height: 44px !important;
    }
}

/* ════════════════════════════════
   CUSTOM COMPONENTS - MOBILE
════════════════════════════════ */
.pb-click-hint {
    margin-top: 0.6rem;
    padding: 0.5rem 0.75rem;
    background: #6d6aff0d;
    border: 1px solid #6d6aff22;
    border-radius: 8px;
    font-size: 0.65rem;
    color: #ffffff44;
    text-align: center;
    line-height: 1.5;
}

.pb-click-hint strong {
    color: #a78bfa;
    font-weight: 600;
}

.pb-file-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #161628;
    border: 1px solid #ffffff0d;
    border-radius: 99px;
    padding: 0.15rem 0.6rem;
    font-size: 0.65rem;
    color: #ffffff44;
    font-weight: 500;
    white-space: nowrap;
}

.pb-file-thumb {
    background: #161628;
    border: 1px solid #ffffff0a;
    border-radius: 10px;
    padding: 0.5rem;
    text-align: center;
    transition: border-color 0.2s;
}

.pb-file-thumb:hover {
    border-color: #6d6aff33;
}

.pb-file-name {
    font-size: 0.6rem;
    color: #ffffff33;
    margin-top: 0.3rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.pb-action-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}

.pb-action-header-icon {
    width: 24px;
    height: 24px;
    background: #6d6aff18;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    flex-shrink: 0;
}

.pb-action-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #e2e2ff;
    letter-spacing: -0.01em;
}

.pb-action-sub {
    font-size: 0.6rem;
    color: #ffffff33;
    font-weight: 400;
    margin-left: auto;
}

.pb-divider {
    height: 1px;
    background: #ffffff08;
    margin: 1rem 0;
}

.pb-footer {
    text-align: center;
    padding: 1.5rem 1rem;
    color: #ffffff18;
    font-size: 0.65rem;
    border-top: 1px solid #ffffff06;
    font-weight: 400;
    letter-spacing: 0.02em;
}

.pb-footer span {
    color: #6d6aff55;
}

/* File preview grid - mobile */
.pb-file-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.5rem;
    margin: 0.5rem 0;
}

@media (max-width: 480px) {
    .pb-file-grid {
        grid-template-columns: repeat(auto-fill, minmax(65px, 1fr));
        gap: 0.4rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════
# HEADER
# ════════════════════════════════
st.markdown(f"""
<div class="pb-header">
    <div class="pb-logo-wrap">
        <div class="pb-logo-icon">✦</div>
        <div>
            <div class="pb-logo-text">Pixel<span>Boost</span> AI</div>
        </div>
        <div class="pb-badge">Pro · v5.0</div>
    </div>
    <div class="pb-header-right">
        <div class="pb-pill">
            <div class="pb-pill-dot"></div>
            Online
        </div>
        <div class="pb-pill">⚡ AI</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════
# STATS STRIP
# ════════════════════════════════
st.markdown(f"""
<div class="pb-stats">
    <div class="pb-stat">
        <div class="pb-stat-num">{st.session_state.processed}</div>
        <div class="pb-stat-label">Processed</div>
    </div>
    <div class="pb-stat">
        <div class="pb-stat-num">{st.session_state.metadata_generated}</div>
        <div class="pb-stat-label">Metadata</div>
    </div>
    <div class="pb-stat">
        <div class="pb-stat-num">4K</div>
        <div class="pb-stat-label">Max Res</div>
    </div>
    <div class="pb-stat">
        <div class="pb-stat-num">8×</div>
        <div class="pb-stat-label">Max Up</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pb-workspace">', unsafe_allow_html=True)

# ════════════════════════════════
# API KEY
# ════════════════════════════════
st.markdown('<div class="pb-section-label">🔑 API Configuration</div>', unsafe_allow_html=True)

api_key = ""
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        st.success("✅ API key loaded from secrets")
    else:
        raise KeyError
except:
    col_key, col_status = st.columns([4, 1])
    with col_key:
        api_key = st.text_input(
            "GEMINI API KEY",
            type="password",
            value=st.session_state.api_key,
            placeholder="AIzaSy...",
            label_visibility="visible"
        )
        if api_key:
            st.session_state.api_key = api_key
    with col_status:
        if api_key:
            st.success("✅ Set")
        else:
            st.markdown("""
            <div style="padding:0.5rem 0; color:#ffffff30; font-size:0.65rem;">
                🔒 Secure
            </div>
            """, unsafe_allow_html=True)

if api_key:
    genai.configure(api_key=api_key)

st.markdown('<div class="pb-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════
# SETTINGS - MOBILE FRIENDLY
# ════════════════════════════════
st.markdown('<div class="pb-section-label">⚙️ Settings</div>', unsafe_allow_html=True)

# Gunakan columns dengan responsive
c1, c2, c3 = st.columns(3)

with c1:
    scale = st.slider("Upscale", min_value=2, max_value=8, value=4, step=1)
    format_type = st.selectbox("Format", ["PNG", "JPEG"])

with c2:
    sharpen = st.checkbox("✦ Sharpen", value=True)
    multisize = st.checkbox("⊞ Multi-Size", value=False)
    keyword_language = st.selectbox(
        "Language",
        ["English", "Indonesian", "Spanish", "French", "German",
         "Japanese", "Chinese", "Arabic", "Russian", "Portuguese"]
    )

with c3:
    max_keywords = st.slider("Keywords", min_value=10, max_value=50, value=30, step=5)
    media_type = st.selectbox(
        "Media",
        ["Photo", "Video", "Illustration", "Vector", "3D Render", "AI Generated"]
    )

st.markdown('<div class="pb-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════
# UPLOAD - MOBILE FRIENDLY
# ════════════════════════════════
st.markdown('<div class="pb-section-label">📤 Upload Files</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drop files here — JPG, PNG, MP4, MOV, AVI",
    type=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'],
    accept_multiple_files=True,
    label_visibility="visible"
)

# ════════════════════════════════
# CATEGORY MAP
# ════════════════════════════════
CATEGORY_MAP = {
    "Abstract": "1", "Animals/Wildlife": "2", "Arts/Entertainment": "3",
    "Backgrounds/Textures": "4", "Beauty/Fashion": "5", "Buildings/Landmarks": "6",
    "Business/Finance": "7", "Education": "8", "Food/Drink": "9",
    "Healthcare/Medical": "10", "Holidays": "11", "Industrial": "12",
    "Landscapes": "13", "Lifestyle": "14", "Nature": "15",
    "Objects": "16", "People": "17", "Religion": "18",
    "Science": "19", "Sports/Recreation": "20", "Technology": "21",
    "Transportation": "22", "Travel": "23"
}

# ════════════════════════════════
# HELPERS
# ════════════════════════════════
def is_video_file(filename):
    return any(filename.lower().endswith(ext) for ext in {'.mp4', '.mov', '.avi', '.mkv', '.webm'})

def is_image_file(filename):
    return any(filename.lower().endswith(ext) for ext in {'.jpg', '.jpeg', '.png', '.tiff', '.tif'})

def clean_filename(name):
    name = re.sub(r'[^a-z0-9\-]', '-', name.lower())
    name = re.sub(r'-+', '-', name).strip('-')
    return name[:80]

def generate_metadata(filename, api_key, media_type, keyword_language, max_keywords=30):
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        language_map = {
            "English": "English", "Indonesian": "Indonesian (Bahasa Indonesia)",
            "Spanish": "Spanish (Español)", "French": "French (Français)",
            "German": "German (Deutsch)", "Japanese": "Japanese (日本語)",
            "Chinese": "Chinese (中文)", "Arabic": "Arabic (العربية)",
            "Russian": "Russian (Русский)", "Portuguese": "Portuguese (Português)"
        }
        lang = language_map.get(keyword_language, "English")
        is_video = is_video_file(filename)
        media_label = "VIDEO" if is_video else "IMAGE"
        video_prompt = "" if not is_video else """
            - duration_suggestion: estimated duration in seconds
            - shot_type: zoom, timelapse, aerial, pan, tilt, static
            - technique: slow motion, hyperlapse, drone, handheld
            - audio: music/no music/sound effects
        """
        prompt = f"""You are an Adobe Stock SEO expert. Based on this {media_label} filename: "{filename}"
Generate COMPLETE metadata in JSON format only, no explanation, no markdown:

{{
  "title": "max 70 characters, descriptive, SEO-friendly, engaging, no AI/generated words",
  "description": "max 150 characters, compelling description",
  "keywords": ["{max_keywords} relevant keywords in {lang}, mix of broad and specific terms"],
  "category": "one of: Abstract, Animals/Wildlife, Arts/Entertainment, Backgrounds/Textures, Beauty/Fashion, Buildings/Landmarks, Business/Finance, Education, Food/Drink, Healthcare/Medical, Holidays, Industrial, Landscapes, Lifestyle, Nature, Objects, People, Religion, Science, Sports/Recreation, Technology, Transportation, Travel",
  "alt_text": "max 100 characters, descriptive alt text",
  "release_required": false,
  "suggested_usage": ["3-5 suggested use cases"]
  {video_prompt}
}}"""
        response = model.generate_content(prompt)
        text = re.sub(r'```json|```', '', response.text.strip())
        data = json.loads(text)
        result = {
            "filename": filename, "media_type": media_type,
            "title": data.get("title", ""), "description": data.get("description", ""),
            "keywords": data.get("keywords", []), "category": data.get("category", "Abstract"),
            "alt_text": data.get("alt_text", ""),
            "release_required": "Yes" if data.get("release_required", False) else "No",
            "suggested_usage": ", ".join(data.get("suggested_usage", [])),
            "language": keyword_language, "status": "success"
        }
        if is_video:
            result["duration"] = data.get("duration_suggestion", "")
            result["shot_type"] = data.get("shot_type", "")
            result["technique"] = data.get("technique", "")
            result["audio"] = data.get("audio", "")
        return result
    except Exception as e:
        return {
            "filename": filename, "media_type": media_type,
            "title": "", "description": "", "keywords": [],
            "category": "Abstract", "alt_text": "",
            "release_required": "No", "suggested_usage": "",
            "language": keyword_language, "status": f"error: {str(e)[:50]}"
        }

def upscale_video(input_bytes, filename, scale=4):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(input_bytes)
            input_path = tmp.name
        output_dir = tempfile.mkdtemp()
        output_path = os.path.join(output_dir, f"upscaled_{filename}")
        frames_dir = os.path.join(output_dir, "frames")
        upscaled_dir = os.path.join(output_dir, "upscaled")
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(upscaled_dir, exist_ok=True)
        subprocess.run(f"ffmpeg -i {input_path} -q:v 2 {frames_dir}/frame_%06d.png -y",
                       shell=True, capture_output=True)
        for frame in sorted(f for f in os.listdir(frames_dir) if f.endswith(".png")):
            img = Image.open(os.path.join(frames_dir, frame))
            img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
            img.save(os.path.join(upscaled_dir, frame))
        subprocess.run(
            f"ffmpeg -framerate 30 -i {upscaled_dir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p {output_path} -y",
            shell=True, capture_output=True)
        with open(output_path, "rb") as f:
            out = f.read()
        shutil.rmtree(output_dir, ignore_errors=True)
        os.unlink(input_path)
        return out
    except Exception:
        return None

def create_complete_csv(metadata_results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Media Type","Filename","Title","Description","Keywords Language",
                     "Keywords","Category","Alt Text","Release Required","Suggested Usage",
                     "Duration","Shot Type","Technique","Audio","Status"])
    for item in metadata_results:
        kw = ", ".join(item["keywords"]) if isinstance(item["keywords"], list) else item["keywords"]
        writer.writerow([item.get("media_type",""), item["filename"], item.get("title",""),
                         item.get("description",""), item.get("language",""), kw,
                         item.get("category",""), item.get("alt_text",""),
                         item.get("release_required","No"), item.get("suggested_usage",""),
                         item.get("duration",""), item.get("shot_type",""),
                         item.get("technique",""), item.get("audio",""), item.get("status","")])
    return output.getvalue()

def create_adobe_stock_csv(metadata_results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Filename","Title","Keywords","Category","Releases"])
    for item in metadata_results:
        code = CATEGORY_MAP.get(item.get("category","Abstract"), "1")
        kw = item.get("keywords", [])
        kw_str = ", ".join(kw[:49]) if isinstance(kw, list) else str(kw)
        writer.writerow([item.get("filename",""), item.get("title","")[:200], kw_str, code, ""])
    return output.getvalue()

# ════════════════════════════════
# FILE PREVIEW + ACTIONS - MOBILE
# ════════════════════════════════
if uploaded_files:
    # File count
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.5rem; margin:0.5rem 0 0.5rem;">
        <div class="pb-section-label" style="margin-bottom:0;">📄 Files</div>
        <div class="pb-file-chip">{len(uploaded_files)} file{'s' if len(uploaded_files)>1 else ''}</div>
    </div>
    """, unsafe_allow_html=True)

    # Responsive grid untuk preview
    preview_cols = st.columns(min(4, len(uploaded_files)))
    for idx, file in enumerate(uploaded_files[:4]):
        with preview_cols[idx % 4]:
            if is_image_file(file.name):
                img = Image.open(file)
                img.thumbnail((100, 100))
                st.image(img, use_column_width=True)
                st.markdown(f'<div class="pb-file-name">{file.name[:12]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="pb-file-thumb">
                    <div style="font-size:1.5rem;">🎬</div>
                    <div class="pb-file-name">{file.name[:12]}</div>
                </div>
                """, unsafe_allow_html=True)

    if len(uploaded_files) > 4:
        st.caption(f"+ {len(uploaded_files) - 4} more")

    st.markdown('<div class="pb-divider"></div>', unsafe_allow_html=True)

    # ── ACTION PANELS ──
    col_meta, col_upscale = st.columns(2)

    # ── METADATA ──
    with col_meta:
        st.markdown("""
        <div class="pb-card">
            <div class="pb-action-header">
                <div class="pb-action-header-icon">🤖</div>
                <div class="pb-action-title">Metadata</div>
                <div class="pb-action-sub">Adobe Ready</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🤖 Generate", use_container_width=True, type="primary"):
            if not api_key:
                st.error("❌ Enter API key first.")
            else:
                with st.spinner(f"Generating metadata..."):
                    metadata_results = []
                    prog = st.progress(0)
                    for idx, file in enumerate(uploaded_files):
                        result = generate_metadata(file.name, api_key, media_type, keyword_language, max_keywords)
                        if result:
                            metadata_results.append(result)
                            st.session_state.metadata_generated += 1
                        prog.progress((idx + 1) / len(uploaded_files))
                        time.sleep(0.3)

                st.success(f"✅ {len(metadata_results)} files")

                df_data = []
                for item in metadata_results:
                    code = CATEGORY_MAP.get(item.get("category", "Abstract"), "1")
                    title = item.get("title", "")
                    df_data.append({
                        "File": item["filename"][:20],
                        "Title": (title[:25] + "…") if len(title) > 25 else title,
                        "Category": f"{item.get('category','')[:10]} ({code})",
                        "Status": "✅" if item.get("status") == "success" else "❌"
                    })

                if df_data:
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)

                st.markdown('<div style="margin-top:0.75rem;"></div>', unsafe_allow_html=True)
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button(
                        "↓ CSV Full",
                        data=create_complete_csv(metadata_results),
                        file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with dl2:
                    st.download_button(
                        "↓ Adobe CSV",
                        data=create_adobe_stock_csv(metadata_results),
                        file_name=f"adobe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

    # ── UPSCALE — 2-click logic ──
    with col_upscale:
        st.markdown("""
        <div class="pb-card">
            <div class="pb-action-header">
                <div class="pb-action-header-icon">🚀</div>
                <div class="pb-action-title">Upscale</div>
                <div class="pb-action-sub">LANCZOS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Upscale & Download", use_container_width=True, type="primary"):

            if st.session_state.upscale_click_count == 0:
                # ── KLIK 1: buka affiliate ──
                components.html(
                    """<script>
                        window.open(
                            'https://www.effectivecpmnetwork.com/hetg54us4?key=052b147073a8a1411c3b8815ecc9fa2e',
                            '_blank'
                        );
                    </script>""",
                    height=0,
                )
                st.session_state.upscale_click_count = 1
                st.info("✅ Sponsor opened! Click again to process.")

            else:
                # ── KLIK 2: proses ──
                with st.spinner(f"Processing {len(uploaded_files)} file(s)…"):
                    zip_buf = io.BytesIO()
                    zip_name = f"pixelboost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    prog = st.progress(0)
                    status = st.empty()

                    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for idx, file in enumerate(uploaded_files):
                            status.caption(f"📄 {idx+1}/{len(uploaded_files)}: {file.name[:20]}")
                            clean_name = clean_filename(os.path.splitext(file.name)[0])

                            if is_video_file(file.name):
                                out = upscale_video(file.getvalue(), file.name, scale)
                                zf.writestr(f"upscaled_{file.name}" if out else f"original_{file.name}",
                                            out if out else file.getvalue())

                            elif is_image_file(file.name):
                                img = Image.open(file)
                                img = img.resize((int(img.width * scale), int(img.height * scale)),
                                                 Image.Resampling.LANCZOS)
                                if sharpen:
                                    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    img = img.convert('RGB')
                                buf = io.BytesIO()
                                if format_type == "PNG":
                                    img.save(buf, format='PNG', optimize=False, compress_level=0)
                                    ext = ".png"
                                else:
                                    img.save(buf, format='JPEG', quality=95, optimize=False)
                                    ext = ".jpg"
                                zf.writestr(f"{clean_name}_{scale}x{ext}", buf.getvalue())

                                if multisize:
                                    img_src = Image.open(file)
                                    for w, h, label in [(1920,1080,"1080p"),(2560,1440,"2K"),(3840,2160,"4K")]:
                                        if img_src.width >= w and img_src.height >= h:
                                            res = img_src.resize((w, h), Image.Resampling.LANCZOS)
                                            if res.mode in ('RGBA', 'LA', 'P'):
                                                res = res.convert('RGB')
                                            sb = io.BytesIO()
                                            res.save(sb, format='PNG', optimize=False)
                                            zf.writestr(f"{clean_name}_{label}.png", sb.getvalue())

                            prog.progress((idx + 1) / len(uploaded_files))

                    zip_buf.seek(0)
                    st.session_state.processed += len(uploaded_files)
                    st.session_state.upscale_click_count = 0
                    status.empty()

                    st.success(f"✅ {len(uploaded_files)} files processed!")
                    mb = len(zip_buf.getvalue()) / (1024 * 1024)
                    st.download_button(
                        f"↓ ZIP ({mb:.1f} MB)",
                        data=zip_buf.getvalue(),
                        file_name=zip_name,
                        mime="application/zip",
                        use_container_width=True,
                        type="primary"
                    )

        # Hint
        if st.session_state.upscale_click_count == 1:
            st.markdown("""
            <div class="pb-click-hint">
                ✅ Sponsor opened — <strong>click again</strong> to process
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="pb-click-hint">
                Click <strong>once</strong> sponsor · Click <strong>again</strong> process
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════
# CATEGORY REFERENCE
# ════════════════════════════════
with st.expander("📋 Category Codes — Adobe Stock"):
    c1, c2 = st.columns(2)
    cats = list(CATEGORY_MAP.items())
    mid = len(cats) // 2
    with c1:
        for cat, code in cats[:mid]:
            st.markdown(f"`{code}` — {cat}")
    with c2:
        for cat, code in cats[mid:]:
            st.markdown(f"`{code}` — {cat}")

# ════════════════════════════════
# FOOTER
# ════════════════════════════════
st.markdown("""
<div class="pb-footer">
    Made with <span>✦</span> by Alley Production · 2026
</div>
""", unsafe_allow_html=True)
