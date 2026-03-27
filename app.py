# -*- coding: utf-8 -*-
import os, zipfile, tempfile, traceback, hashlib, shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Análise Espacial em Climatologia Urbana",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root {
    --bg: #f5f1ea;
    --bg-alt: #fbf8f3;
    --surface: rgba(255, 255, 253, 0.92);
    --surface-strong: rgba(255, 255, 254, 0.98);
    --surface-soft: rgba(250, 246, 240, 0.96);
    --stroke: rgba(73, 58, 40, 0.10);
    --stroke-strong: rgba(138, 98, 45, 0.18);
    --text: #1f1a15;
    --muted: #6a6157;
    --heading: #241d17;
    --heading-2: #1a1511;
    --blue-1: #5f4526;
    --blue-2: #b87333;
    --blue-3: #c68642;
    --action-blue-1: #a0522d;
    --action-blue-2: #8b4513;
    --action-blue-3: #5c3317;
    --teal: #617468;
    --accent: #b87333;
    --success: #456650;
    --warning: #a5672b;
    --shadow-xs: 0 8px 18px rgba(30, 22, 14, 0.05);
    --shadow-sm: 0 16px 36px rgba(30, 22, 14, 0.08);
    --shadow-md: 0 28px 58px rgba(30, 22, 14, 0.11);
    --shadow-lg: 0 42px 92px rgba(30, 22, 14, 0.15);
    --radius-3xl: 30px;
    --radius-2xl: 24px;
    --radius-xl: 20px;
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 9px;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"], .stApp {
    font-family: "Aptos", "Segoe UI Variable", Inter, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    color: var(--text) !important;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stMarkdown, .stCaption, .stAlert, .stRadio, .stSelectbox, .stMultiSelect,
.stSlider, .stNumberInput, .stCheckbox, .stButton, .stDownloadButton,
label, p, li, h1, h2, h3, h4, h5, h6, span, div[data-baseweb="select"],
div[data-baseweb="popover"], div[data-baseweb="slider"], button[kind],
input, textarea, [data-testid="stFileUploader"], table {
    font-family: "Aptos", "Segoe UI Variable", Inter, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

code, pre, .stCodeBlock, .stCode, .stTextArea textarea {
    font-family: Consolas, "SFMono-Regular", "Courier New", monospace !important;
}

body {
    font-size: 16px !important;
    line-height: 1.65 !important;
}

p, li, label {
    font-size: 0.98rem !important;
    line-height: 1.68 !important;
    color: var(--text) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--heading) !important;
    letter-spacing: -0.028em;
    font-weight: 760;
}

[data-testid="stSidebar"], [data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    right: 1rem;
}

input, textarea, [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    border-radius: 12px !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.38rem;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,252,0.94) !important;
    border: 1px solid var(--stroke) !important;
    border-radius: 999px !important;
    padding: 0.48rem 0.88rem !important;
    box-shadow: var(--shadow-xs);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(97,69,38,0.98), rgba(154,106,47,0.96)) !important;
}

.stTabs [aria-selected="true"] p {
    color: #ffffff !important;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(154,106,47,0.07), transparent 30%),
        radial-gradient(circle at 92% 10%, rgba(97,116,104,0.06), transparent 22%),
        linear-gradient(180deg, #fcfbf8 0%, var(--bg) 100%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.main .block-container {
    max-width: 1490px;
    padding-top: 1.2rem;
    padding-bottom: 2.8rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}

div[data-testid="stVerticalBlock"] > div:empty {
    display: none;
}

.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 20% 20%, rgba(184,115,51,0.35), transparent 30%),
        radial-gradient(circle at 80% 10%, rgba(198,134,66,0.25), transparent 25%),
        linear-gradient(135deg, #2b1a12 0%, #4a2c1a 40%, #b87333 100%);
border: 1px solid rgba(255,255,255,0.08);
    border-radius: 30px;
    padding: 1.38rem 1.5rem 1.18rem 1.5rem;
    box-shadow: 0 30px 78px rgba(14, 10, 8, 0.18), inset 0 1px 0 rgba(255,255,255,0.04);
    color: #fbf7f2 !important;
    margin-bottom: 0.8rem;
    isolation: isolate;
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
    background-size: 52px 52px;
    mask-image: linear-gradient(180deg, rgba(0,0,0,0.52), transparent 72%);
    opacity: 0.10;
    pointer-events: none;
    z-index: 0;
}

.hero::after {
    content: "";
    position: absolute;
    inset: auto -8% -48% auto;
    width: 360px;
    height: 360px;
    border-radius: 50%;
    background:
        radial-gradient(circle, rgba(208,165,109,0.12), rgba(208,165,109,0.03) 48%, transparent 72%);
    filter: blur(2px);
    pointer-events: none;
    z-index: 0;
}

.hero,
.hero *,
.hero h1,
.hero h2,
.hero h3,
.hero h4,
.hero h5,
.hero h6,
.hero p,
.hero span,
.hero strong,
.hero em,
.hero li,
.hero ol,
.hero ul,
.hero div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

.hero-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(320px, 0.9fr);
    gap: 0.88rem;
    align-items: stretch;
    position: relative;
    z-index: 1;
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.72rem;
}

.hero-brand-text {
    min-width: 0;
}

.hero h1 {
    margin: 0.22rem 0 0.5rem 0;
    font-size: clamp(1.55rem, 2.08vw, 2.1rem);
    line-height: 1.08;
    font-weight: 800;
    max-width: 22ch;
}

.hero p {
    margin: 0.3rem 0;
    font-size: 0.91rem !important;
    line-height: 1.7 !important;
    color: rgba(255,252,247,0.90) !important;
    max-width: 76ch;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.44rem;
    padding: 0.42rem 0.86rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    font-size: 0.78rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.62rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}

.hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.52rem;
    margin-top: 0.92rem;
}

.hero-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.48rem 0.8rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.10);
    font-size: 0.81rem;
    font-weight: 700;
    color: rgba(255,252,247,0.95) !important;
    letter-spacing: 0.01em;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    backdrop-filter: blur(8px);
}

.hero-panel {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 1.04rem 1.08rem;
    backdrop-filter: blur(12px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 16px 30px rgba(0,0,0,0.08);
}

.hero-panel-title {
    margin: 0 0 0.68rem 0;
    font-size: 0.84rem;
    font-weight: 760;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.84) !important;
}

.hero-kpi {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 0.72rem;
    margin-top: 0.08rem;
}

.hero-kpi div {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 0.84rem 0.9rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}

.hero-kpi strong {
    display: block;
    font-size: 0.96rem;
    font-weight: 780;
    margin-bottom: 0.16rem;
}

.hero-kpi span {
    display: block;
    font-size: 0.84rem;
    line-height: 1.5;
    color: rgba(255,255,255,0.82) !important;
}

.top-nav-shell {
    background: rgba(255,255,252,0.84);
    border: 1px solid rgba(73, 58, 40, 0.08);
    border-radius: 18px;
    padding: 0.68rem 0.9rem 0.54rem 0.9rem;
    backdrop-filter: blur(12px);
    box-shadow: var(--shadow-md);
    margin: 0.42rem 0 1rem 0;
}

.top-nav-caption {
    color: var(--muted) !important;
    font-size: 0.92rem !important;
    line-height: 1.54 !important;
    margin: 0 0 0.18rem 0.16rem;
    font-weight: 520;
}

div[role="radiogroup"] {
    gap: 0.58rem;
    flex-wrap: wrap;
}

div[role="radiogroup"] label {
    background: rgba(255,255,252,0.94) !important;
    border: 1px solid rgba(15, 23, 42, 0.08) !important;
    border-radius: 999px !important;
    padding: 0.66rem 1rem !important;
    min-height: 46px !important;
    box-shadow: 0 10px 20px rgba(30, 22, 14, 0.05);
    transition: all 0.18s ease;
}

div[role="radiogroup"] label:hover {
    transform: translateY(-1px);
    border-color: rgba(154,106,47,0.24) !important;
    box-shadow: 0 14px 24px rgba(30, 22, 14, 0.07);
}

div[role="radiogroup"] label p {
    font-weight: 740 !important;
    font-size: 0.94rem !important;
    color: var(--text) !important;
}

div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(95,69,38,0.98), rgba(154,106,47,0.96)) !important;
    border-color: rgba(154,106,47,0.26) !important;
    box-shadow: 0 18px 32px rgba(95,69,38,0.18);
}

div[role="radiogroup"] label[data-checked="true"] p {
    color: #ffffff !important;
}

.reg-step,
.section-title,
.card,
.info-card,
.stat-card,
.top-toolbar,
[data-testid="stExpander"],
[data-testid="stMetric"],
[data-testid="stDataFrame"],
div[data-testid="stFileUploader"] > section {
    backdrop-filter: blur(10px);
}

.reg-step {
    background: linear-gradient(180deg, rgba(255,255,253,0.99), rgba(249,245,238,0.98));
    border: 1px solid var(--stroke);
    border-left: 4px solid var(--blue-2);
    border-radius: 18px;
    padding: 1rem 1.04rem 0.98rem 1.04rem;
    box-shadow: var(--shadow-sm);
    margin: 1rem 0 0.8rem 0;
}

.reg-step h3 {
    margin: 0;
    font-size: 1.08rem;
    line-height: 1.34;
    font-weight: 760;
    color: var(--blue-1) !important;
    letter-spacing: -0.01em;
}

.reg-step p {
    margin: 0.34rem 0 0 0;
    font-size: 0.94rem !important;
    line-height: 1.62 !important;
    color: var(--muted) !important;
}

.reg-mini-title {
    margin: 0 0 0.5rem 0;
}

.reg-mini-title h4 {
    margin: 0;
    font-size: 0.99rem;
    line-height: 1.36;
    font-weight: 740;
    color: var(--text) !important;
}

.reg-mini-title p {
    margin: 0.24rem 0 0 0;
    font-size: 0.89rem !important;
    line-height: 1.54 !important;
    color: var(--muted) !important;
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0,1fr));
    gap: 0.8rem;
    margin: 0.24rem 0 1rem 0;
}

.quick-card {
    background: linear-gradient(180deg, rgba(255,255,253,0.98), rgba(255,252,247,0.95));
    border: 1px solid var(--stroke);
    border-radius: 18px;
    padding: 0.96rem 1rem;
    box-shadow: var(--shadow-sm);
}

.quick-card h4 {
    margin: 0;
    font-size: 0.96rem;
    font-weight: 760;
    color: var(--blue-1) !important;
}

.quick-card p {
    margin: 0.28rem 0 0 0;
    color: var(--muted) !important;
    font-size: 0.91rem !important;
}

.section-title {
    background:
        linear-gradient(135deg, rgba(255,255,253,0.98), rgba(249,245,238,0.97)),
        linear-gradient(180deg, rgba(154,106,47,0.03), rgba(97,116,104,0.02));
    border: 1px solid var(--stroke);
    border-left: 4px solid var(--blue-1);
    border-radius: 18px;
    padding: 0.96rem 1.06rem;
    box-shadow: var(--shadow-sm);
    margin: 0.42rem 0 0.96rem 0;
}

.section-title h2 {
    margin: 0;
    font-size: clamp(1.18rem, 1.42vw, 1.42rem);
    line-height: 1.24;
    font-weight: 780;
    color: var(--heading-2) !important;
}

.section-title p {
    margin: 0.24rem 0 0 0;
    color: var(--muted) !important;
    font-size: 0.92rem !important;
    max-width: 82ch;
}

.card, .info-card, .stat-card, .top-toolbar {
    background: linear-gradient(180deg, rgba(255,255,253,0.98), rgba(252,248,242,0.95));
    border: 1px solid var(--stroke);
    border-radius: 18px;
    box-shadow: var(--shadow-sm);
}

.info-card,
.stat-card {
    padding: 0.98rem 1.02rem;
    min-height: 100%;
}

.info-card h4 {
    margin: 0 0 0.28rem 0;
    font-size: 0.96rem;
    font-weight: 760;
    color: var(--blue-1) !important;
}

.info-card p {
    margin: 0;
    color: var(--muted) !important;
    font-size: 0.92rem !important;
}

.stat-card .label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 740;
    margin-bottom: 0.26rem;
}

.stat-card .value {
    font-size: clamp(1.16rem, 1.55vw, 1.48rem);
    font-weight: 800;
    line-height: 1.1;
    color: var(--heading);
}

.stat-card .hint {
    margin-top: 0.24rem;
    color: var(--muted);
    font-size: 0.86rem;
}

.top-toolbar {
    padding: 0.9rem 0.98rem;
    margin-bottom: 0.88rem;
}

.upload-toolbar {
    margin-top: 0.22rem;
}

.upload-box-label {
    font-size: 0.98rem;
    font-weight: 780;
    color: var(--heading);
    margin-bottom: 0.24rem;
}

.upload-box-description {
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.56;
    margin-bottom: 0.42rem;
}

.upload-box-hint, .upload-box-footer {
    color: var(--muted);
    font-size: 0.86rem;
    line-height: 1.52;
}

div[data-testid="stFileUploader"] > section {
    border-radius: 16px !important;
    border: 1.15px dashed rgba(154,106,47,0.24) !important;
    background: linear-gradient(180deg, rgba(252,248,242,0.97), rgba(255,255,253,0.95)) !important;
    padding: 0.8rem !important;
    box-shadow: var(--shadow-xs);
}

div[data-testid="stFileUploader"] small {
    color: var(--muted) !important;
}

button[kind="primary"], .stButton > button, .stDownloadButton > button {
    border-radius: 14px !important;
    border: 1px solid rgba(154,106,47,0.26) !important;
    background: linear-gradient(135deg, var(--action-blue-1) 0%, var(--action-blue-2) 58%, var(--action-blue-3) 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 780 !important;
    letter-spacing: 0.01em !important;
    min-height: 2.85rem !important;
    padding: 0.6rem 1.02rem !important;
    box-shadow:
        0 14px 28px rgba(109, 56, 24, 0.18),
        inset 0 1px 0 rgba(255,255,255,0.20) !important;
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        filter 0.18s ease !important;
}

button[kind="primary"] p,
.stButton > button p,
.stDownloadButton > button p,
button[kind="primary"] span,
.stButton > button span,
.stDownloadButton > button span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 780 !important;
}

button[kind="primary"]:hover, .stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.02);
    box-shadow:
        0 18px 30px rgba(109, 56, 24, 0.22),
        inset 0 1px 0 rgba(255,255,255,0.24) !important;
}

button[kind="primary"]:focus, .stButton > button:focus, .stDownloadButton > button:focus,
button[kind="primary"]:focus-visible, .stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
    outline: none !important;
    box-shadow:
        0 0 0 0.16rem rgba(154,106,47,0.18),
        0 16px 28px rgba(109, 56, 24, 0.20),
        inset 0 1px 0 rgba(255,255,255,0.26) !important;
}

button[kind="primary"]:active, .stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(0);
    filter: brightness(0.98);
    box-shadow:
        0 8px 18px rgba(109, 56, 24, 0.16),
        inset 0 1px 0 rgba(255,255,255,0.14) !important;
}

button[kind="secondary"] {
    border-radius: 12px !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255,255,253,0.98), rgba(252,248,242,0.95));
    border: 1px solid var(--stroke);
    border-radius: 16px;
    padding: 0.78rem 0.9rem;
    box-shadow: var(--shadow-sm);
}

[data-testid="stMetricLabel"] p {
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted) !important;
    font-weight: 740 !important;
}

[data-testid="stMetricValue"] {
    font-size: clamp(1.14rem, 1.48vw, 1.46rem) !important;
    font-weight: 800 !important;
    color: var(--heading) !important;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--stroke) !important;
    border-radius: 16px !important;
    overflow: hidden;
    box-shadow: var(--shadow-xs);
    background: rgba(255,255,252,0.95) !important;
}

div[data-testid="stExpander"] summary {
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
}

div[data-testid="stDataFrame"], [data-testid="stTable"] {
    border-radius: 16px !important;
    overflow: hidden;
    border: 1px solid var(--stroke) !important;
    box-shadow: var(--shadow-xs);
}

[data-baseweb="tab-list"] {
    gap: 0.4rem;
}

button[data-baseweb="tab"] {
    border-radius: 999px !important;
    padding: 0.5rem 0.9rem !important;
    background: rgba(252,249,244,0.84) !important;
    border: 1px solid rgba(15,23,42,0.08) !important;
    box-shadow: var(--shadow-xs);
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(95,69,38,0.98), rgba(154,106,47,0.96)) !important;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    color: #ffffff !important;
}

div[data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    border-radius: 12px !important;
    border-color: rgba(73,58,40,0.12) !important;
    background: rgba(255,255,252,0.96) !important;
}

.stAlert {
    border-radius: 14px !important;
    border: 1px solid var(--stroke) !important;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(154,106,47,0.18), transparent);
    margin: 1.16rem 0;
}

@media (max-width: 1100px) {
    .hero-grid,
    .quick-grid {
        grid-template-columns: 1fr;
    }

    .hero-panel {
        min-height: auto;
    }
}

@media (max-width: 768px) {
    .main .block-container {
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    .hero {
        padding: 1.26rem 1.06rem 1.06rem 1.06rem;
        border-radius: 22px;
    }

    .hero h1 {
        font-size: 1.76rem;
        max-width: none;
    }

    .hero-kpi {
        grid-template-columns: 1fr;
    }

    .section-title,
    .reg-step,
    .card,
    .top-toolbar {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }
}
</style>
""", unsafe_allow_html=True)

def section_title(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="section-title">
            <h2>{title}</h2>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )



def regression_step_title(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="reg-step">
            <h3>{title}</h3>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def regression_block_title(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="reg-mini-title">
            <h4>{title}</h4>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def regression_spacer(height_rem: float = 1.25):
    st.markdown(
        f"<div style='height:{height_rem:.2f}rem; width:100%;'></div>",
        unsafe_allow_html=True,
    )


def info_card(title: str, text: str):
    st.markdown(
        f"""
        <div class="info-card">
            <h4>{title}</h4>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, hint: str = ""):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {f'<div class="hint">{hint}</div>' if hint else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import xy, rowcol

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
from libpysal.weights import KNN
from esda.moran import Moran
from scipy.stats import t as student_t


SR_SCALE = 0.0000275
SR_OFFSET = -0.2
ST_SCALE = 0.00341802
ST_OFFSET = 149.0
EXPORT_NODATA = -9999.0

SEQUENTIAL_CMAP_OPTIONS = ["viridis", "cividis", "inferno", "magma", "plasma", "YlGn", "YlOrBr", "YlOrRd"]
DIVERGING_CMAP_OPTIONS = ["RdBu_r", "coolwarm", "Spectral_r", "PuOr_r", "BrBG"]
THEMATIC_CMAP_OPTIONS = sorted(set(SEQUENTIAL_CMAP_OPTIONS + DIVERGING_CMAP_OPTIONS))
DEFAULT_THEMATIC_CMAP = "viridis"
DEFAULT_LAYER_CMAP = {
    "NDVI": "YlGn",
    "SAVI": "YlGn",
    "NDBI": "YlOrRd",
    "BSI": "YlOrBr",
    "UI": "YlOrRd",
    "NDBSI": "YlOrRd",
    "WETNESS": "YlGnBu",
    "RSEI": "YlGn",
    "LST_C": "inferno",
    "ANOMALIA_Z": "RdBu_r",
}
SIGNED_LAYER_KEYWORDS = ("anomalia", "anomaly", "resid", "resíduo", "residu", "coef", "beta", "t value", "t-value", "zscore", "z-score")
BINARY_SIGNIFICANCE_KEYWORDS = ("signif.", "signific", "p<0.05", "p < 0.05", "significance")


def is_binary_significance_layer(layer_name: str) -> bool:
    if not layer_name:
        return False
    lower_name = str(layer_name).lower()
    return any(token in lower_name for token in BINARY_SIGNIFICANCE_KEYWORDS)


def is_signed_thematic_layer(layer_name: str) -> bool:
    if not layer_name:
        return False
    upper_name = str(layer_name).upper()
    lower_name = str(layer_name).lower()
    if upper_name == "ANOMALIA_Z":
        return True
    return any(token in lower_name for token in SIGNED_LAYER_KEYWORDS)


SIGNIFICANCE_CMAP = mcolors.ListedColormap(["lightgray", "red"])


def palette_options_for_layer(layer_name: str) -> List[str]:
    if is_binary_significance_layer(layer_name):
        return ["Cinza/Vermelho (fixo)"]
    return DIVERGING_CMAP_OPTIONS if is_signed_thematic_layer(layer_name) else SEQUENTIAL_CMAP_OPTIONS


def default_cmap_for_layer(layer_name: str) -> str:
    if layer_name in DEFAULT_LAYER_CMAP:
        return DEFAULT_LAYER_CMAP[layer_name]
    if is_binary_significance_layer(layer_name):
        return "Cinza/Vermelho (fixo)"
    return "RdBu_r" if is_signed_thematic_layer(layer_name) else DEFAULT_THEMATIC_CMAP


def build_thematic_norm(arr: np.ndarray, layer_name: str):
    arr = np.asarray(arr, dtype="float32")
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return None
    if is_binary_significance_layer(layer_name):
        return mcolors.BoundaryNorm([-0.5, 0.5, 1.5], 2)
    vmin = float(np.nanmin(valid))
    vmax = float(np.nanmax(valid))
    if not np.isfinite(vmin) or not np.isfinite(vmax):
        return None
    if np.isclose(vmin, vmax):
        vmax = vmin + 1e-9
    if is_signed_thematic_layer(layer_name) and vmin < 0 < vmax:
        vmax_abs = max(abs(vmin), abs(vmax))
        return plt.Normalize(vmin=-vmax_abs, vmax=vmax_abs)
    return plt.Normalize(vmin=vmin, vmax=vmax)


def thematic_cmap_for_layer(layer_name: str, cmap_name: str | None = None):
    if is_binary_significance_layer(layer_name):
        return SIGNIFICANCE_CMAP
    return cmap_name or default_cmap_for_layer(layer_name)


def apply_thematic_colorbar(fig, im, layer_name: str):
    cbar = fig.colorbar(im, fraction=0.03, pad=0.02)
    if is_binary_significance_layer(layer_name):
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(["0 = não significativo", "1 = significativo"])
    return cbar


@dataclass
class RasterBand:
    name: str
    arr: np.ndarray
    profile: dict
    transform: rasterio.Affine
    crs: object
    nodata: Optional[float]


def uploaded_file_signature(uploaded_file) -> str:
    content = uploaded_file.getvalue()
    return hashlib.md5(content).hexdigest()


def ensure_clean_dir(path: str):
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        full = os.path.join(path, name)
        try:
            if os.path.isdir(full):
                shutil.rmtree(full)
            else:
                os.remove(full)
        except Exception:
            pass


def get_cached_extracted_dir(uploaded_file, cache_key_prefix: str) -> str:
    signature = uploaded_file_signature(uploaded_file)
    sig_key = f"{cache_key_prefix}_signature"
    dir_key = f"{cache_key_prefix}_dir"
    cached_dir = st.session_state.get(dir_key)
    cached_sig = st.session_state.get(sig_key)
    if cached_dir and cached_sig == signature and os.path.isdir(cached_dir):
        return cached_dir
    extracted_dir = extract_zip(uploaded_file)
    st.session_state[sig_key] = signature
    st.session_state[dir_key] = extracted_dir
    return extracted_dir


def save_uploaded_file(uploaded_file, prefix: str = "upload_") -> str:
    td = tempfile.mkdtemp(prefix=prefix)
    path = os.path.join(td, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def extract_zip(uploaded_file) -> str:
    td = tempfile.mkdtemp(prefix="app_hibrido_")
    zip_path = os.path.join(td, uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    out_dir = os.path.join(td, "unzipped")
    os.makedirs(out_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    return out_dir


def find_band_file(folder: str, band_code: str) -> Optional[str]:
    band_code = band_code.upper()
    for root, _, files in os.walk(folder):
        for f in files:
            fu = f.upper()
            if band_code in fu and (fu.endswith(".TIF") or fu.endswith(".TIFF")):
                return os.path.join(root, f)
    return None


def read_band(path: str) -> RasterBand:
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        return RasterBand(
            name=os.path.splitext(os.path.basename(path))[0],
            arr=arr,
            profile=src.profile.copy(),
            transform=src.transform,
            crs=src.crs,
            nodata=src.nodata
        )


def build_mask(arr: np.ndarray, nodata: Optional[float]) -> np.ndarray:
    mask = ~np.isfinite(arr)
    if nodata is not None:
        mask |= (arr == nodata)
    return mask


def safe_index(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(np.abs(den) < 1e-10, np.nan, num / den)
    return out.astype("float32")


def normalize_01(arr: np.ndarray, invert: bool = False) -> np.ndarray:
    arr = np.asarray(arr, dtype="float32")
    valid = arr[np.isfinite(arr)]
    out = np.full(arr.shape, np.nan, dtype="float32")
    if valid.size == 0:
        return out
    lo = float(np.nanmin(valid))
    hi = float(np.nanmax(valid))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        out[np.isfinite(arr)] = 0.5
        return out
    out = (arr - lo) / (hi - lo)
    out = np.clip(out, 0, 1)
    if invert:
        out = 1.0 - out
    out[~np.isfinite(arr)] = np.nan
    return out.astype("float32")


def compute_rsei(ndvi: np.ndarray, wetness: np.ndarray, ndbsi: np.ndarray, lst: np.ndarray) -> Tuple[np.ndarray, Dict[str, object]]:
    components = {
        "greenness": normalize_01(ndvi),
        "wetness": normalize_01(wetness),
        "dryness": normalize_01(ndbsi),
        "heat": normalize_01(lst),
    }

    valid_mask = np.logical_and.reduce([np.isfinite(v) for v in components.values()])
    rsei = np.full(ndvi.shape, np.nan, dtype="float32")
    info = {"explained_variance_ratio": np.nan, "loadings": {}, "pc_inverted": False}

    if np.count_nonzero(valid_mask) < 10:
        return rsei, info

    X = np.column_stack([components[k][valid_mask] for k in ["greenness", "wetness", "dryness", "heat"]]).astype("float32")
    pca = PCA(n_components=1, random_state=42)
    pc1 = pca.fit_transform(X).ravel().astype("float32")

    loadings = {
        "greenness": float(pca.components_[0][0]),
        "wetness": float(pca.components_[0][1]),
        "dryness": float(pca.components_[0][2]),
        "heat": float(pca.components_[0][3]),
    }
    eco_signal = loadings["greenness"] + loadings["wetness"] - loadings["dryness"] - loadings["heat"]
    if eco_signal < 0:
        pc1 = -pc1
        info["pc_inverted"] = True
        loadings = {k: -v for k, v in loadings.items()}

    pc1_min = float(np.nanmin(pc1))
    pc1_max = float(np.nanmax(pc1))
    if np.isfinite(pc1_min) and np.isfinite(pc1_max) and pc1_max > pc1_min:
        rsei_values = (pc1 - pc1_min) / (pc1_max - pc1_min)
    else:
        rsei_values = np.full(pc1.shape, 0.5, dtype="float32")

    rsei[valid_mask] = np.clip(rsei_values, 0, 1).astype("float32")
    info["explained_variance_ratio"] = float(pca.explained_variance_ratio_[0])
    info["loadings"] = loadings
    return rsei.astype("float32"), info


def percentile_stretch(arr: np.ndarray, p2: float = 2, p98: float = 98) -> np.ndarray:
    arr = arr.astype("float32")
    valid = arr[np.isfinite(arr)]
    out = np.zeros(arr.shape, dtype="float32")
    if valid.size == 0:
        return out
    lo, hi = np.nanpercentile(valid, [p2, p98])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        lo = float(np.nanmin(valid))
        hi = float(np.nanmax(valid))
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            return out
    out = (arr - lo) / (hi - lo)
    out = np.clip(out, 0, 1)
    out[~np.isfinite(arr)] = 0
    return out.astype("float32")


def compose_rgb(red: np.ndarray, green: np.ndarray, blue: np.ndarray) -> np.ndarray:
    r = percentile_stretch(red)
    g = percentile_stretch(green)
    b = percentile_stretch(blue)

    invalid = (
        (~np.isfinite(red)) |
        (~np.isfinite(green)) |
        (~np.isfinite(blue))
    )

    alpha = np.ones(red.shape, dtype="float32")
    alpha[invalid] = 0.0

    r[invalid] = 0.0
    g[invalid] = 0.0
    b[invalid] = 0.0

    rgba = np.dstack([r, g, b, alpha]).astype("float32")
    return rgba


def save_rgb_png(path: str, rgba: np.ndarray):
    rgba8 = np.clip(rgba * 255, 0, 255).astype("uint8")
    plt.imsave(path, rgba8)


def render_layer_on_rgb(ax, rgb_rgba: np.ndarray, layer_name: str, layer_arr: np.ndarray, alpha: float = 0.45, cmap_name: Optional[str] = None):
    ax.imshow(rgb_rgba, interpolation="nearest")
    if layer_name == "RGB_COLORIDO":
        return None

    arr = np.asarray(layer_arr, dtype="float32").copy()
    arr[~np.isfinite(arr)] = np.nan
    valid_mask = np.isfinite(arr)
    if not np.any(valid_mask):
        return None

    alpha = float(np.clip(alpha, 0.0, 1.0))
    masked = np.ma.masked_invalid(arr)

    if layer_name == "ANOMALIA_CLASS":
        cmap = anomaly_class_cmap()
        norm = mcolors.BoundaryNorm(np.arange(0.5, 7.5, 1.0), cmap.N)
        return ax.imshow(masked, cmap=cmap, norm=norm, interpolation="nearest", alpha=alpha)

    cmap_name = cmap_name or default_cmap_for_layer(layer_name)
    cmap = thematic_cmap_for_layer(layer_name, cmap_name)
    norm = build_thematic_norm(arr, layer_name)
    if norm is None:
        return None
    return ax.imshow(masked, cmap=cmap, norm=norm, interpolation="nearest", alpha=alpha)


def zscore_anomaly(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype("float32").copy()
    arr[~np.isfinite(arr)] = np.nan
    arr[(arr < -100) | (arr > 100)] = np.nan
    valid = arr[np.isfinite(arr)]
    out = np.full(arr.shape, np.nan, dtype="float32")
    if valid.size == 0:
        return out
    mu = np.nanmean(valid)
    sigma = np.nanstd(valid)
    if sigma == 0 or not np.isfinite(sigma):
        out[np.isfinite(arr)] = 0.0
        return out.astype("float32")
    out = (arr - mu) / sigma
    out[~np.isfinite(arr)] = np.nan
    return out.astype("float32")

def classify_anomaly(z: np.ndarray) -> np.ndarray:
    out = np.full(z.shape, np.nan, dtype="float32")
    out[(z <= -2.0)] = 1
    out[(z > -2.0) & (z <= -1.0)] = 2
    out[(z > -1.0) & (z <= 0.0)] = 3
    out[(z > 0.0) & (z <= 1.0)] = 4
    out[(z > 1.0) & (z <= 2.0)] = 5
    out[(z > 2.0)] = 6
    return out


def anomaly_class_labels():
    return {
        1: "Muito fria",
        2: "Fria",
        3: "Levemente fria",
        4: "Levemente quente",
        5: "Quente",
        6: "Muito quente",
    }

def anomaly_class_cmap():
    return mcolors.ListedColormap([
        "#08306b",  # 1 - Muito fria
        "#2171b5",  # 2 - Fria
        "#6baed6",  # 3 - Levemente fria
        "#fcae91",  # 4 - Levemente quente
        "#fb6a4a",  # 5 - Quente
        "#cb181d",  # 6 - Muito quente
    ])

def area_table_from_classes(class_grid: np.ndarray, ref_band: RasterBand) -> pd.DataFrame:
    labels = anomaly_class_labels()
    valid = np.isfinite(class_grid)
    pixel_area_m2 = abs(ref_band.transform.a * ref_band.transform.e)
    pixel_area_km2 = pixel_area_m2 / 1_000_000.0
    total_pixels = int(np.sum(valid))
    rows = []
    for cls, label in labels.items():
        n = int(np.nansum(class_grid == cls))
        area_km2 = n * pixel_area_km2
        pct = (n / total_pixels * 100.0) if total_pixels > 0 else 0.0
        rows.append({
            "classe_codigo": cls,
            "classe": label,
            "pixels": n,
            "area_km2": area_km2,
            "area_percentual": pct,
        })
    return pd.DataFrame(rows)

def anomaly_interpretation(df_area: pd.DataFrame, z_grid: np.ndarray) -> str:
    if df_area.empty:
        return "Não foi possível interpretar a anomalia térmica."
    hottest = df_area.sort_values("area_percentual", ascending=False).iloc[0]
    hotspot_pct = float(df_area.loc[df_area["classe"].isin(["Hotspot", "Hotspot intenso"]), "area_percentual"].sum())
    cool_pct = float(df_area.loc[df_area["classe"].isin(["Fria", "Mod. fria"]), "area_percentual"].sum())
    zmin = float(np.nanmin(z_grid)) if np.isfinite(z_grid).any() else float("nan")
    zmax = float(np.nanmax(z_grid)) if np.isfinite(z_grid).any() else float("nan")
    zmean = float(np.nanmean(z_grid)) if np.isfinite(z_grid).any() else float("nan")
    parts = []
    parts.append(
        f"A classe predominante foi '{hottest['classe']}', ocupando {hottest['area_percentual']:.2f}% da área analisada."
    )
    parts.append(
        f"As classes quentes (Hotspot + Hotspot intenso) somaram {hotspot_pct:.2f}% da área, enquanto as classes frias (Fria + Mod. fria) representaram {cool_pct:.2f}%."
    )
    parts.append(
        f"A anomalia térmica variou de {zmin:.2f} a {zmax:.2f}, com média espacial de {zmean:.2f}."
    )
    if hotspot_pct > 30:
        parts.append("Esse padrão sugere forte concentração espacial de superfícies aquecidas e presença expressiva de hotspots urbanos.")
    elif hotspot_pct > 15:
        parts.append("Esse padrão sugere presença moderada de hotspots, distribuídos em setores específicos da área urbana.")
    else:
        parts.append("Esse padrão sugere predominância de condições térmicas normais, com hotspots mais pontuais.")
    return " ".join(parts)


def array_stats(arr: np.ndarray) -> Dict[str, float]:
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return {"min": np.nan, "max": np.nan, "mean": np.nan, "std": np.nan}
    return {
        "min": float(np.nanmin(valid)),
        "max": float(np.nanmax(valid)),
        "mean": float(np.nanmean(valid)),
        "std": float(np.nanstd(valid)),
    }


def fmt_num(v: float) -> str:
    return "—" if not np.isfinite(v) else f"{v:.3f}"


def pretty_dataframe(df: pd.DataFrame, caption: str = "", hide_index: bool = True):
    if caption:
        st.caption(caption)

    if df is None:
        st.info("Sem dados para exibir.")
        return

    df = df.copy()
    removable_cols = {"index", "level_0", "Unnamed: 0", ""}
    df = df.loc[:, [c for c in df.columns if str(c) not in removable_cols and not str(c).startswith("Unnamed:")]]

    try:
        styler = df.style.hide(axis="index") if hide_index else df.style
        styler = styler.set_table_styles([
            {"selector": "thead th", "props": [("background", "linear-gradient(135deg, #0f4c81, #2563eb)"), ("color", "white"), ("font-weight", "700"), ("text-align", "center"), ("padding", "8px 10px"), ("border", "0")]},
            {"selector": "tbody td", "props": [("border-bottom", "1px solid #e8eef5"), ("padding", "7px 10px")]},
            {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f5f9ff")]},
            {"selector": "tbody tr:hover", "props": [("background-color", "#e6f7f7")]},
        ])
        styler = styler.format(precision=4, na_rep="—")
        st.dataframe(styler, use_container_width=True)
    except Exception:
        st.dataframe(df, use_container_width=True, hide_index=hide_index)


def load_vector(uploaded_file) -> gpd.GeoDataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".zip"):
        td = get_cached_extracted_dir(uploaded_file, "cached_vector")
        shp = list(Path(td).rglob("*.shp"))
        if not shp:
            raise RuntimeError("ZIP vetorial sem shapefile.")
        return gpd.read_file(shp[0])
    if name.endswith(".geojson") or name.endswith(".json"):
        path = save_uploaded_file(uploaded_file, prefix="vector_")
        return gpd.read_file(path)
    raise RuntimeError("Formato vetorial não suportado.")


def mask_by_geometries(arr: np.ndarray, transform, geoms) -> np.ndarray:
    m = geometry_mask(geoms, transform=transform, invert=True, out_shape=arr.shape)
    return np.where(m, arr, np.nan).astype("float32")


def apply_clip(layers: Dict[str, np.ndarray], ref_band: RasterBand, aoi_gdf: gpd.GeoDataFrame) -> Dict[str, np.ndarray]:
    aoi = aoi_gdf.to_crs(ref_band.crs)
    geoms = [g.__geo_interface__ for g in aoi.geometry if g is not None and not g.is_empty]
    return {k: mask_by_geometries(v, ref_band.transform, geoms) for k, v in layers.items()}


def save_asc(path: str, arr: np.ndarray, ref_band: RasterBand):
    nrows, ncols = arr.shape
    xllcorner = ref_band.transform.c
    cellsize = ref_band.transform.a
    yulcorner = ref_band.transform.f
    yllcorner = yulcorner - nrows * abs(ref_band.transform.e)
    out = np.where(np.isfinite(arr), arr, EXPORT_NODATA)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"ncols         {ncols}\n")
        f.write(f"nrows         {nrows}\n")
        f.write(f"xllcorner     {xllcorner}\n")
        f.write(f"yllcorner     {yllcorner}\n")
        f.write(f"cellsize      {cellsize}\n")
        f.write(f"NODATA_value  {EXPORT_NODATA}\n")
        np.savetxt(f, out, fmt="%.6f")


def save_tif(path: str, arr: np.ndarray, ref_band: RasterBand):
    profile = ref_band.profile.copy()
    profile.update(dtype="float32", count=1, nodata=EXPORT_NODATA, compress="lzw")
    out = np.where(np.isfinite(arr), arr, EXPORT_NODATA).astype("float32")
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(out, 1)


def package_outputs(out_dir: str, zip_name: str) -> str:
    zip_path = os.path.join(out_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(out_dir):
            for f in files:
                if f == zip_name:
                    continue
                full = os.path.join(root, f)
                zf.write(full, os.path.relpath(full, out_dir))
    return zip_path


def raster_coords(ref_band: RasterBand) -> Tuple[np.ndarray, np.ndarray]:
    rows, cols = np.indices(ref_band.arr.shape)
    xs, ys = xy(ref_band.transform, rows, cols, offset="center")
    xs = np.array(xs).reshape(ref_band.arr.shape)
    ys = np.array(ys).reshape(ref_band.arr.shape)
    return xs, ys


def extract_training_samples(feature_layers: Dict[str, np.ndarray], ref_band: RasterBand, gdf: gpd.GeoDataFrame, class_field: str) -> pd.DataFrame:
    gdf = gdf.to_crs(ref_band.crs)
    records = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        cls = row[class_field]
        if geom.geom_type.lower().startswith("point"):
            rr, cc = rowcol(ref_band.transform, geom.x, geom.y)
            if 0 <= rr < ref_band.arr.shape[0] and 0 <= cc < ref_band.arr.shape[1]:
                vals = {k: feature_layers[k][rr, cc] for k in feature_layers}
                if all(np.isfinite(list(vals.values()))):
                    vals[class_field] = cls
                    records.append(vals)
        else:
            m = geometry_mask([geom.__geo_interface__], transform=ref_band.transform, invert=True, out_shape=ref_band.arr.shape)
            rows, cols = np.where(m)
            for rr, cc in zip(rows, cols):
                vals = {k: feature_layers[k][rr, cc] for k in feature_layers}
                if all(np.isfinite(list(vals.values()))):
                    vals[class_field] = cls
                    records.append(vals)
    if not records:
        raise RuntimeError("Nenhuma amostra válida foi extraída.")
    return pd.DataFrame(records)




def get_classification_features() -> List[str]:
    return ["NDVI", "SAVI", "NDBI", "BSI", "UI", "NDBSI", "WETNESS", "RSEI", "LST_C", "ANOMALIA_Z"]


CLASSIFICATION_PALETTE = [
    "#1a9641",  # vegetação
    "#d7191c",  # urbano
    "#fdae61",  # solo exposto
    "#2b83ba",  # água
    "#ffffbf",  # outros
    "#bdbdbd",
    "#984ea3",
    "#66c2a5",
    "#ffd92f",
    "#a6d854",
]

def build_classification_palette(grid: np.ndarray):
    valid = np.unique(grid[np.isfinite(grid)]).astype(int) if np.isfinite(grid).any() else np.array([1], dtype=int)
    n_classes = max(int(valid.max()), 1)
    colors = CLASSIFICATION_PALETTE[:n_classes]
    if len(colors) < n_classes:
        extra = plt.cm.tab20(np.linspace(0, 1, n_classes - len(colors)))
        colors = colors + [mcolors.to_hex(c) for c in extra]
    cmap = mcolors.ListedColormap(colors[:n_classes])
    cmap.set_bad((0, 0, 0, 0))
    norm = mcolors.BoundaryNorm(np.arange(0.5, n_classes + 1.5, 1), cmap.N)
    return cmap, norm, list(range(1, n_classes + 1))

def render_classification_grid(
    grid: np.ndarray,
    title: str,
    legend_labels: Optional[List[str]] = None,
    base_rgb: Optional[np.ndarray] = None,
    overlay_on_rgb: bool = False,
    overlay_alpha: float = 0.55,
):
    cmap, norm, ticks = build_classification_palette(grid)
    masked = np.ma.masked_invalid(grid)

    fig = plt.figure(figsize=(8.8, 5.6))
    ax = plt.gca()

    if overlay_on_rgb and base_rgb is not None:
        ax.imshow(base_rgb, interpolation="nearest")
        im = ax.imshow(masked, cmap=cmap, norm=norm, interpolation="nearest", alpha=overlay_alpha)
    else:
        im = ax.imshow(masked, cmap=cmap, norm=norm, interpolation="nearest")

    cbar = plt.colorbar(im, fraction=0.03, pad=0.02)
    cbar.set_ticks(ticks)
    if legend_labels is None or len(legend_labels) != len(ticks):
        cbar.set_ticklabels([f"Classe {i}" for i in ticks])
    else:
        cbar.set_ticklabels(legend_labels)

    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def run_supervised_classification_ui(layers: Dict[str, np.ndarray], ref_band: RasterBand, out_dir: str, class_field_default: str, rgb_colorido: Optional[np.ndarray] = None):
    features = get_classification_features()

    with st.container(border=True):
        st.markdown("**Parâmetros da classificação supervisionada**")
        class_field_value = st.text_input(
            "**Classes**",
            value=class_field_default,
            help="Nome do atributo categórico presente nas amostras de treinamento.",
            placeholder="Ex.: class",
            key="class_field_classificacao",
        )
        samples_file_value = st.file_uploader(
            "**Amostras de uso do solo**",
            type=["zip", "geojson", "json"],
            help="Uploader específico para classificação supervisionada.",
            key="samples_file_classificacao",
        )

    if samples_file_value is None:
        st.info("Envie amostras de uso do solo para habilitar a classificação supervisionada.")
        return

    try:
        train_gdf = load_vector(samples_file_value)
        if class_field_value not in train_gdf.columns:
            st.error(f"O campo '{class_field_value}' não existe nas amostras.")
            return

        sample_df = extract_training_samples({k: layers[k] for k in features}, ref_band, train_gdf, class_field_value)
        st.write(f"Amostras válidas: **{len(sample_df)}**")

        if sample_df.empty:
            st.warning("Nenhuma amostra válida foi extraída. Verifique a projeção, a área de sobreposição e o campo de classes.")
            return

        n_trees = st.slider("Árvores do Random Forest", 10, 500, 150, 10)
        seed = st.number_input("Seed classificação", min_value=0, max_value=999999, value=42, step=1)

        if not st.button("Executar classificação supervisionada"):
            return

        progress = st.progress(0)
        status_box = st.empty()

        def update_step(frac: int, msg: str):
            progress.progress(frac)
            status_box.info(msg)

        update_step(10, "Etapa 1/6 — Preparando as amostras e a matriz de atributos.")
        X = sample_df[features]
        y = sample_df[class_field_value].astype(str)

        if y.nunique() < 2:
            st.error("A classificação supervisionada exige pelo menos duas classes distintas nas amostras.")
            return

        class_counts = y.value_counts()
        if (class_counts < 2).any():
            problem_classes = ", ".join(class_counts[class_counts < 2].index.tolist())
            st.error(f"Cada classe precisa ter pelo menos 2 amostras para a divisão estratificada. Classes insuficientes: {problem_classes}.")
            return

        update_step(25, "Etapa 2/6 — Dividindo amostras em treino e teste.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.30, random_state=int(seed), stratify=y
        )

        update_step(45, "Etapa 3/6 — Ajustando o modelo Random Forest.")
        clf = RandomForestClassifier(n_estimators=n_trees, random_state=int(seed), n_jobs=-1)
        clf.fit(X_train, y_train)

        update_step(60, "Etapa 4/6 — Avaliando desempenho nas amostras de teste.")
        pred = clf.predict(X_test)
        acc = accuracy_score(y_test, pred)
        cm = confusion_matrix(y_test, pred)
        rpt = classification_report(y_test, pred, output_dict=True)

        c1, c2 = st.columns(2)
        c1.metric("Acurácia global", f"{acc:.4f}")
        c2.metric("Nº de classes", len(sorted(y.unique())))

        cm_df = pd.DataFrame(cm)
        rpt_df = pd.DataFrame(rpt).T

        update_step(78, "Etapa 5/6 — Classificando todos os pixels válidos da cena.")
        feature_df, valid_mask = build_feature_df({k: layers[k] for k in features}, ref_band)
        pred_all = clf.predict(feature_df[features])
        classes = sorted(y.unique())
        label_map = {cls: i + 1 for i, cls in enumerate(classes)}
        grid = np.full(ref_band.arr.shape, np.nan, dtype="float32")
        grid[valid_mask] = [label_map[v] for v in pred_all]

        update_step(92, "Etapa 6/6 — Preparando a visualização temática e os arquivos de saída.")
        legend_labels = [str(cls) for cls in classes]

        st.session_state["classification_state"] = {
            "grid": grid,
            "title": "Classificação supervisionada",
            "legend_labels": legend_labels,
            "mode": "Supervisionada",
        }
        st.session_state["classification_tables"] = [
            {"caption": "Matriz de confusão da classificação supervisionada.", "df": cm_df, "hide_index": False},
            {"caption": "Relatório de desempenho por classe.", "df": rpt_df, "hide_index": False},
        ]

        rpt_df.to_csv(os.path.join(out_dir, "classificacao_supervisionada_relatorio.csv"))
        pd.DataFrame({"classe": list(label_map.keys()), "codigo": list(label_map.values())}).to_csv(
            os.path.join(out_dir, "classificacao_supervisionada_legenda.csv"), index=False
        )
        save_asc(os.path.join(out_dir, "classificacao_supervisionada.asc"), grid, ref_band)
        progress.progress(100)
        status_box.success("Classificação supervisionada concluída com sucesso.")

    except Exception as e:
        st.error(f"Falha na classificação supervisionada: {e}")
        st.code(traceback.format_exc())

def run_unsupervised_classification_ui(layers: Dict[str, np.ndarray], ref_band: RasterBand, out_dir: str, rgb_colorido: Optional[np.ndarray] = None):
    available_features = [feat for feat in get_classification_features() if feat in layers]
    default_features = available_features.copy()

    st.info(
        "Escolha os índices que deseja usar na classificação não supervisionada. A classificação não supervisionada agrupa pixels usando índices padronizados (z-score), reduzindo o efeito de diferenças de escala."
    )

    selected_features = st.multiselect(
        "**Variáveis usadas na classificação não supervisionada**",
        options=available_features,
        default=default_features,
        help=(
            "Selecione os índices/camadas que participarão do K-Means. "
            "Cada variável selecionada é padronizada individualmente antes do agrupamento."
        ),
        key="unsup_feature_selector",
    )

    if not selected_features:
        st.warning("Selecione pelo menos uma variável para executar a classificação não supervisionada.")
        return

    n_clusters = st.slider("**Número de classes (K-Means)**", 2, 10, 5)
    seed_unsup = st.number_input("**Seed não supervisionada**", min_value=0, max_value=999999, value=42, step=1, key="seed_unsup")

    st.caption("Variáveis selecionadas: " + ", ".join(selected_features))

    if not st.button("Executar classificação não supervisionada"):
        return

    try:
        progress = st.progress(0)
        status_box = st.empty()

        def update_step(frac: int, msg: str):
            progress.progress(frac)
            status_box.info(msg)

        update_step(12, "Etapa 1/6 — Montando a base de índices para o agrupamento.")
        feature_df, valid_mask = build_feature_df({k: layers[k] for k in selected_features}, ref_band)
        X_raw = feature_df[selected_features].values.astype("float32")
        features = selected_features

        update_step(28, "Etapa 2/6 — Padronizando os índices (z-score).")
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw).astype("float32")

        update_step(45, "Etapa 3/6 — Ajustando o modelo K-Means com os índices padronizados.")
        km = KMeans(n_clusters=n_clusters, random_state=int(seed_unsup), n_init=10)
        labels = km.fit_predict(X)

        update_step(62, "Etapa 4/6 — Gerando o raster classificado.")
        grid = np.full(ref_band.arr.shape, np.nan, dtype="float32")
        grid[valid_mask] = labels + 1

        update_step(80, "Etapa 5/6 — Calculando estatísticas médias por classe.")
        cluster_stats = []
        cluster_centers_std = km.cluster_centers_
        for cluster_id in range(n_clusters):
            mask_cluster = labels == cluster_id
            row = {"classe_codigo": cluster_id + 1, "pixels": int(mask_cluster.sum())}
            for feat_idx, feat in enumerate(features):
                row[f"media_padronizada_{feat}"] = float(np.mean(X[mask_cluster, feat_idx])) if np.any(mask_cluster) else np.nan
                row[f"media_original_{feat}"] = float(np.mean(X_raw[mask_cluster, feat_idx])) if np.any(mask_cluster) else np.nan
                row[f"centroide_padronizado_{feat}"] = float(cluster_centers_std[cluster_id, feat_idx])
            cluster_stats.append(row)
        cluster_df = pd.DataFrame(cluster_stats)

        update_step(93, "Etapa 6/6 — Preparando legenda, visualização temática e exportação.")
        legend_labels = [f"Classe {i}" for i in range(1, n_clusters + 1)]

        st.session_state["classification_state"] = {
            "grid": grid,
            "title": f"Classificação não supervisionada (K-Means com {len(features)} variáveis padronizadas)",
            "legend_labels": legend_labels,
            "mode": "Não supervisionada",
        }
        st.session_state["classification_tables"] = [
            {"caption": f"Estatísticas por classe ({len(features)} variáveis selecionadas; médias padronizadas e valores originais)", "df": cluster_df, "hide_index": True},
        ]

        legend_df = pd.DataFrame({
            "classe_codigo": list(range(1, n_clusters + 1)),
            "rotulo_sugerido": legend_labels
        })
        scaler_df = pd.DataFrame({
            "variavel": features,
            "media_treinamento": scaler.mean_,
            "desvio_padrao_treinamento": scaler.scale_,
        })
        selected_features_df = pd.DataFrame({
            "ordem": np.arange(1, len(features) + 1),
            "variavel_selecionada": features,
        })
        centers_std_df = pd.DataFrame(cluster_centers_std, columns=[f"centroide_padronizado_{feat}" for feat in features])
        centers_std_df.insert(0, "classe_codigo", np.arange(1, n_clusters + 1))

        cluster_df.to_csv(os.path.join(out_dir, "classificacao_nao_supervisionada_estatisticas.csv"), index=False)
        legend_df.to_csv(os.path.join(out_dir, "classificacao_nao_supervisionada_legenda.csv"), index=False)
        scaler_df.to_csv(os.path.join(out_dir, "classificacao_nao_supervisionada_padronizacao.csv"), index=False)
        selected_features_df.to_csv(os.path.join(out_dir, "classificacao_nao_supervisionada_variaveis_selecionadas.csv"), index=False)
        centers_std_df.to_csv(os.path.join(out_dir, "classificacao_nao_supervisionada_centroides_padronizados.csv"), index=False)
        save_asc(os.path.join(out_dir, "classificacao_nao_supervisionada.asc"), grid, ref_band)

        progress.progress(100)

    except Exception as e:
        st.error(f"Falha na classificação não supervisionada: {e}")
        st.code(traceback.format_exc())

def build_feature_df(feature_layers: Dict[str, np.ndarray], ref_band: RasterBand):
    xs, ys = raster_coords(ref_band)
    valid = np.ones(ref_band.arr.shape, dtype=bool)
    for arr in feature_layers.values():
        valid &= np.isfinite(arr)
    data = {"x": xs[valid], "y": ys[valid]}
    for k, arr in feature_layers.items():
        data[k] = arr[valid]
    return pd.DataFrame(data), valid


def calculate_vif(X: np.ndarray, predictors: List[str]) -> pd.DataFrame:
    rows = []
    for i, name in enumerate(predictors):
        y_i = X[:, i]
        X_others = np.delete(X, i, axis=1)
        if X_others.shape[1] == 0:
            vif = 1.0
        else:
            Xd = np.column_stack([np.ones(X_others.shape[0]), X_others])
            beta = np.linalg.lstsq(Xd, y_i, rcond=None)[0]
            yhat = Xd @ beta
            ss_res = np.sum((y_i - yhat) ** 2)
            ss_tot = np.sum((y_i - np.mean(y_i)) ** 2)
            r2_i = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
            vif = np.inf if r2_i >= 0.999999 else 1.0 / (1.0 - r2_i)
        rows.append({"variavel": name, "VIF": float(vif)})
    return pd.DataFrame(rows)

def contribution_table(params: np.ndarray, predictors: List[str]) -> pd.DataFrame:
    abs_means = np.abs(params).mean(axis=0)
    total = abs_means.sum()
    pct = (abs_means / total * 100.0) if total > 0 else np.zeros_like(abs_means)
    return pd.DataFrame({
        "variavel": predictors,
        "coef_medio": params.mean(axis=0),
        "coef_mediano": np.median(params, axis=0),
        "abs_coef_medio": abs_means,
        "contribuicao_percentual": pct,
    }).sort_values("contribuicao_percentual", ascending=False)


def local_pvalues_from_t(tvalues: np.ndarray, n_obs: int, n_params: int) -> np.ndarray:
    df = max(int(n_obs - n_params), 1)
    pvals = 2.0 * student_t.sf(np.abs(tvalues), df)
    return np.nan_to_num(pvals, nan=1.0, posinf=1.0, neginf=1.0).astype("float32")


def local_significance_from_pvalues(pvalues: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    p_arr = np.asarray(pvalues, dtype=float)
    sig = np.where(np.isfinite(p_arr) & (p_arr < float(alpha)), 1.0, 0.0)
    return sig.astype("float32")


def local_tvalues_from_params(params: np.ndarray, bse: np.ndarray) -> np.ndarray:
    params_arr = np.asarray(params, dtype=float)
    bse_arr = np.asarray(bse, dtype=float)
    out = np.zeros_like(params_arr, dtype="float32")
    valid = np.isfinite(params_arr) & np.isfinite(bse_arr) & (np.abs(bse_arr) > 0)
    np.divide(params_arr, bse_arr, out=out, where=valid)
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0).astype("float32")


def extract_local_inference(fit, n_obs: int, n_params: int):
    params = np.asarray(getattr(fit, "params"), dtype=float)
    try:
        bse = np.asarray(getattr(fit, "bse"), dtype=float)
        tvalues = local_tvalues_from_params(params, bse)
    except Exception:
        tvalues = np.zeros_like(params, dtype="float32")

    df_resid = None
    try:
        df_candidate = getattr(fit, "df_resid")
        if df_candidate is not None:
            df_resid = float(np.asarray(df_candidate).reshape(-1)[0])
    except Exception:
        df_resid = None

    if df_resid is not None and np.isfinite(df_resid) and df_resid > 0:
        pvalues = 2.0 * student_t.sf(np.abs(tvalues), max(int(round(df_resid)), 1))
        pvalues = np.nan_to_num(pvalues, nan=1.0, posinf=1.0, neginf=1.0).astype("float32")
    else:
        pvalues = local_pvalues_from_t(tvalues, n_obs=n_obs, n_params=n_params)

    return tvalues, pvalues

def export_regression_grid_set(model_prefix: str, name: str, values: np.ndarray, ref_band: RasterBand, valid_mask: np.ndarray, sampled_mask: np.ndarray, filled_exports: bool, sparse_exports: bool, out_dir: str):
    outputs = []
    if filled_exports:
        xs, ys = raster_coords(ref_band)
        sample_coords = np.column_stack([xs[sampled_mask], ys[sampled_mask]])
        valid_coords = np.column_stack([xs[valid_mask], ys[valid_mask]])
        if len(sample_coords) > 0 and len(valid_coords) > 0:
            from scipy.spatial import cKDTree
            idx = cKDTree(sample_coords).query(valid_coords, k=1)[1]
            filled = np.full(ref_band.arr.shape, np.nan, dtype="float32")
            filled[valid_mask] = values[idx]
            asc = os.path.join(out_dir, f"{model_prefix}_{name}_filled.asc")
            save_asc(asc, filled, ref_band)
            outputs.append(asc)
    if sparse_exports:
        sparse = np.full(ref_band.arr.shape, np.nan, dtype="float32")
        sparse[sampled_mask] = values
        asc = os.path.join(out_dir, f"{model_prefix}_{name}_sparse.asc")
        save_asc(asc, sparse, ref_band)
        outputs.append(asc)
    return outputs

def run_spatial_regression_advanced(df: pd.DataFrame, dependent: str, predictors: List[str], model_type: str, sample_step: int, max_points: int, mgwr_sampling_mode: str, mgwr_auto_max_points: int, mgwr_auto_min_step: int):
    # build sampled mask from dataframe row order externally not possible; here operate on df already sampled if needed
    coords = df[["x", "y"]].values
    y = df[[dependent]].values.astype(float)
    X = df[predictors].values.astype(float)

    # standardize
    y = (y - y.mean(axis=0)) / np.where(y.std(axis=0) == 0, 1, y.std(axis=0))
    X = (X - X.mean(axis=0)) / np.where(X.std(axis=0) == 0, 1, X.std(axis=0))

    vif_df = calculate_vif(X, predictors)
    results = {}
    mgwr_status = "não solicitado"
    mgwr_error = None
    mgwr_auto_adjust = False
    mgwr_manual_warning = False

    if model_type in ["MGWR", "Ambos"] and mgwr_sampling_mode == "Automático":
        # only metadata flag here, actual downsampling done before dataframe is passed
        mgwr_auto_adjust = True
    elif model_type in ["MGWR", "Ambos"] and mgwr_sampling_mode == "Manual":
        if max_points > mgwr_auto_max_points or sample_step < mgwr_auto_min_step:
            mgwr_manual_warning = True

    if model_type in ["GWR", "Ambos"]:
        sel = Sel_BW(coords, y, X, kernel="bisquare", fixed=False)
        bw = sel.search()
        fit = GWR(coords, y, X, bw=bw, kernel="bisquare", fixed=False).fit()
        tvalues, pvalues = extract_local_inference(fit, n_obs=len(y), n_params=len(predictors) + 1)
        w = KNN.from_array(coords, k=8); w.transform = "R"
        moran = Moran(fit.resid_response.flatten(), w)
        results["GWR"] = {
            "bw": bw,
            "params": np.asarray(fit.params, dtype="float32"),
            "tvalues": tvalues,
            "pvalues": pvalues,
            "significant_005": local_significance_from_pvalues(pvalues, alpha=0.05),
            "localR2": np.asarray(fit.localR2, dtype="float32").flatten(),
            "aicc": float(fit.aicc),
            "bic": float(fit.bic),
            "rmse": float(np.sqrt(np.mean((y.flatten() - fit.predy.flatten()) ** 2))),
            "mae": float(np.mean(np.abs(y.flatten() - fit.predy.flatten()))),
            "r2": float(1 - np.sum((y.flatten() - fit.predy.flatten()) ** 2) / np.sum((y.flatten() - y.flatten().mean()) ** 2)),
            "moran_i": float(moran.I),
            "moran_p": float(moran.p_sim),
            "contrib": contribution_table(np.asarray(fit.params, dtype=float)[:, 1:], predictors),
        }

    if model_type in ["MGWR", "Ambos"]:
        try:
            sel = Sel_BW(coords, y, X, multi=True, kernel="bisquare", fixed=False)
            bws = sel.search()
            fit = MGWR(coords, y, X, selector=sel, kernel="bisquare", fixed=False).fit()
            tvalues, pvalues = extract_local_inference(fit, n_obs=len(y), n_params=len(predictors) + 1)
            w = KNN.from_array(coords, k=8); w.transform = "R"
            moran = Moran(fit.resid_response.flatten(), w)
            mgwr_status = "ok"
            results["MGWR"] = {
                "bw": bws,
                "params": np.asarray(fit.params, dtype="float32"),
                "tvalues": tvalues,
                "pvalues": pvalues,
                "significant_005": local_significance_from_pvalues(pvalues, alpha=0.05),
                "aicc": float(fit.aicc),
                "bic": float(fit.bic),
                "rmse": float(np.sqrt(np.mean((y.flatten() - fit.predy.flatten()) ** 2))),
                "mae": float(np.mean(np.abs(y.flatten() - fit.predy.flatten()))),
                "r2": float(1 - np.sum((y.flatten() - fit.predy.flatten()) ** 2) / np.sum((y.flatten() - y.flatten().mean()) ** 2)),
                "moran_i": float(moran.I),
                "moran_p": float(moran.p_sim),
                "contrib": contribution_table(np.asarray(fit.params, dtype=float)[:, 1:], predictors),
            }
        except Exception as e:
            mgwr_status = "falhou"
            mgwr_error = str(e)

    meta = {
        "vif_df": vif_df,
        "mgwr_status": mgwr_status,
        "mgwr_error": mgwr_error,
        "mgwr_auto_adjust": mgwr_auto_adjust,
        "mgwr_manual_warning": mgwr_manual_warning,
    }
    return results, meta



def write_regression_outputs(results, predictors, valid_mask, sampled_mask, ref_band, out_dir, filled_exports, sparse_exports):
    for model, info in results.items():
        coef_df = pd.DataFrame(info["params"], columns=["Intercepto"] + predictors)
        coef_df.to_csv(os.path.join(out_dir, f"{model}_coeficientes_locais.csv"), index=False)

        # export local t and p tables too
        if "tvalues" in info:
            pd.DataFrame(info["tvalues"], columns=["Intercepto"] + predictors).to_csv(
                os.path.join(out_dir, f"{model}_tvalues_locais.csv"), index=False
            )
        if "pvalues" in info and info["pvalues"] is not None:
            pd.DataFrame(info["pvalues"], columns=["Intercepto"] + predictors).to_csv(
                os.path.join(out_dir, f"{model}_pvalues_locais.csv"), index=False
            )
        if "significant_005" in info and info["significant_005"] is not None:
            pd.DataFrame(info["significant_005"], columns=["Intercepto"] + predictors).to_csv(
                os.path.join(out_dir, f"{model}_significancia_p_menor_0_05.csv"), index=False
            )

        metrics = pd.DataFrame({
            "metrica": ["AICc", "BIC", "RMSE", "MAE", "R2", "Moran_I", "Moran_p", "bandwidth"],
            "valor": [info["aicc"], info["bic"], info["rmse"], info["mae"], info["r2"], info["moran_i"], info["moran_p"], str(info["bw"])]
        })
        metrics.to_csv(os.path.join(out_dir, f"{model}_metricas.csv"), index=False)
        info["contrib"].to_csv(os.path.join(out_dir, f"{model}_contribuicao.csv"), index=False)

        for j, name in enumerate(["Intercepto"] + predictors):
            export_regression_grid_set(model, f"coef_{name}", info["params"][:, j], ref_band, valid_mask, sampled_mask, filled_exports, sparse_exports, out_dir)
            if "pvalues" in info and info["pvalues"] is not None:
                export_regression_grid_set(model, f"pvalue_{name}", info["pvalues"][:, j], ref_band, valid_mask, sampled_mask, filled_exports, sparse_exports, out_dir)
            if "significant_005" in info and info["significant_005"] is not None:
                export_regression_grid_set(model, f"significancia_p_menor_0_05_{name}", info["significant_005"][:, j], ref_band, valid_mask, sampled_mask, filled_exports, sparse_exports, out_dir)

        if model == "GWR":
            export_regression_grid_set(model, "localR2", info["localR2"], ref_band, valid_mask, sampled_mask, filled_exports, sparse_exports, out_dir)
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="hero-brand">
                    <div class="hero-brand-text">
                        <h1 style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">UrbanClimaX</h1>
                        <p style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"><strong style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">Autores:</strong> Dr. Elis Alves (IF Goiano) e
                        Antônio Pasqualetto (PUC Goiás)</p>
                    </div>
                </div>
                <p style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"><div class="hero-description">Aplicativo para processamento de imagens Landsat 8/9, cálculo de índices espectrais, estimativa da temperatura de superfície (LST), análise de anomalias térmicas, classificação temática e regressão espacial (GWR/MGWR) aplicada à climatologia urbana.</div></p>
                <div class="hero-meta">
                    <span class="hero-chip" style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">Geoprocessamento</span>
                    <span class="hero-chip" style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">Climatologia Urbana</span>
                    <span class="hero-chip" style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">Anomalias Térmicas</span>
                </div>
            </div>
            <div class="hero-panel">
                <div class="hero-panel-title" style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"></div>
                <div class="hero-kpi">
                    <div style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"><strong style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">1. Entrada</strong><span style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">ZIP Landsat, área de estudo e amostras</span></div>
                    <div style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"><strong style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">2. Processamento</strong><span style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">NDVI, NDBI, NDBSI, Wetness, RSEI, RGB, LST e anomalia térmica</span></div>
                    <div style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"><strong style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">3. Modelagem</strong><span style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">Classificação supervisionada e GWR/MGWR</span></div>
                    <div style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;"><strong style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">4. Produtos</strong><span style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;">ASC, tabelas, gráficos e estatísticas.</span></div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



st.markdown('<div class="upload-toolbar">', unsafe_allow_html=True)
upload_col1, upload_col2 = st.columns([1, 1], gap="small")
samples_file = None
class_field = "Vegetação"
with upload_col1:
    with st.container(border=True):
        st.markdown(
            '''
            <div class="upload-box-label">Landsat 8/9</div>
            <div class="upload-box-description">*ZIP das bandas 2, 3, 4, 5, 6, 7 e 10 da <strong>Collection 2 Level-2</strong>, do <strong>Landsat 8/9</strong>.</div>
            <div class="upload-box-hint">
            <div class="upload-box-footer"><strong>Envio ideal:</strong> Arquivo com bandas recortadas para facilitar o processamento.</div>
            ''',
            unsafe_allow_html=True,
        )
        landsat_zip = st.file_uploader(
            "ZIP Landsat 8/9 Level-2",
            type=["zip"],
            help="Envie o ZIP original da cena Landsat 8/9 Collection 2 Level-2.",
            label_visibility="collapsed",
        )
with upload_col2:
    with st.container(border=True):
        st.markdown(
            '''
            <div class="upload-box-label">Limite da área</div>
            <div class="upload-box-description">*ZIP do polígono da área de estudo.</div>
            <div class="upload-box-hint">
            <div class="upload-box-footer"><strong>Use:</strong> Limite municipal ou perímetro urbano.</div>
            ''',
            unsafe_allow_html=True,
        )
        aoi_file = st.file_uploader(
            "Limite da área",
            type=["zip", "geojson", "json"],
            help="Use um polígono vetorial da área de estudo em ZIP shapefile ou GeoJSON.",
            label_visibility="collapsed",
        )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '''
    <div class="top-nav-shell">
        <p class="top-nav-caption">Carregue o <strong>ZIP</strong> do Landsat 8/9 e o <strong>ZIP</strong> do limite da área de estudo. O app organiza automaticamente o fluxo de trabalho em módulos: Visão Geral, Índices, Classificação, Regressão Espacial e Download de produtos finais.</p>
    </div>
    ''',
    unsafe_allow_html=True,
)
nav = st.radio(
    "Navegação",
    ["Visão Geral", "Índices", "Classificação", "Regressão Espacial", "Download"],
    horizontal=True,
    label_visibility="collapsed",
)

if landsat_zip is None:
    st.stop()

current_upload_signature = uploaded_file_signature(landsat_zip)
if st.session_state.get("hybrid_landsat_signature") != current_upload_signature:
    st.session_state["hybrid_landsat_signature"] = current_upload_signature
    st.session_state["hybrid_out_dir"] = tempfile.mkdtemp(prefix="hybrid_v16_out_")
    ensure_clean_dir(st.session_state["hybrid_out_dir"])
    st.session_state.pop("regression_spatial_state", None)
    st.session_state.pop("classification_state", None)
    st.session_state.pop("classification_tables", None)

out_dir = st.session_state["hybrid_out_dir"]

try:
    landsat_dir = get_cached_extracted_dir(landsat_zip, "cached_landsat")
    band_files = {
        "B2": find_band_file(landsat_dir, "SR_B2"),
        "B3": find_band_file(landsat_dir, "SR_B3"),
        "B4": find_band_file(landsat_dir, "SR_B4"),
        "B5": find_band_file(landsat_dir, "SR_B5"),
        "B6": find_band_file(landsat_dir, "SR_B6"),
        "B7": find_band_file(landsat_dir, "SR_B7"),
        "B10": find_band_file(landsat_dir, "ST_B10"),
    }
    missing = [k for k, v in band_files.items() if v is None]
    if missing:
        st.error(f"Bandas ausentes: {missing}")
        st.stop()

    ref_band = read_band(band_files["B2"])
    bands = {k: read_band(v) for k, v in band_files.items()}

    mask = np.zeros(ref_band.arr.shape, dtype=bool)
    for b in bands.values():
        if b.arr.shape != ref_band.arr.shape:
            st.error("As bandas possuem dimensões diferentes.")
            st.stop()
        mask |= build_mask(b.arr, b.nodata)

    SR = {}
    for k in ["B2", "B3", "B4", "B5", "B6", "B7"]:
        SR[k] = np.where(mask, np.nan, bands[k].arr * SR_SCALE + SR_OFFSET).astype("float32")

    lst_raw = bands["B10"].arr.astype("float32")
    lst_mask = build_mask(lst_raw, bands["B10"].nodata) | mask
    lst = lst_raw * ST_SCALE + ST_OFFSET - 273.15
    lst = np.where(lst_mask, np.nan, lst).astype("float32")
    lst[(lst < -50) | (lst > 80)] = np.nan

    ndvi = safe_index(SR["B5"] - SR["B4"], SR["B5"] + SR["B4"])
    savi = safe_index(1.5 * (SR["B5"] - SR["B4"]), SR["B5"] + SR["B4"] + 0.5)
    ndbi = safe_index(SR["B6"] - SR["B5"], SR["B6"] + SR["B5"])
    bsi = safe_index((SR["B6"] + SR["B4"]) - (SR["B5"] + SR["B2"]), (SR["B6"] + SR["B4"]) + (SR["B5"] + SR["B2"]))
    ui = safe_index(SR["B7"] - SR["B5"], SR["B7"] + SR["B5"])
    wetness = (
        0.1511 * SR["B2"] +
        0.1973 * SR["B3"] +
        0.3283 * SR["B4"] +
        0.3407 * SR["B5"] -
        0.7117 * SR["B6"] -
        0.4559 * SR["B7"]
    ).astype("float32")
    ndbsi = np.nanmean(np.stack([ndbi, bsi]), axis=0).astype("float32")
    rsei, rsei_info = compute_rsei(ndvi, wetness, ndbsi, lst)
    anomalia = zscore_anomaly(lst)
    anomalia_class = classify_anomaly(anomalia)

    rgb_colorido = compose_rgb(SR["B4"], SR["B3"], SR["B2"])

    layers = {
        "NDVI": ndvi,
        "SAVI": savi,
        "NDBI": ndbi,
        "BSI": bsi,
        "UI": ui,
        "NDBSI": ndbsi,
        "WETNESS": wetness,
        "RSEI": rsei,
        "LST_C": lst,
        "ANOMALIA_Z": anomalia,
        "ANOMALIA_CLASS": anomalia_class,
    }

    if aoi_file is not None:
        aoi_gdf = load_vector(aoi_file)
        layers = apply_clip(layers, ref_band, aoi_gdf)
        aoi_clip = aoi_gdf.to_crs(ref_band.crs)
        aoi_geoms = [g.__geo_interface__ for g in aoi_clip.geometry if g is not None and not g.is_empty]
        rgb_colorido = compose_rgb(
            mask_by_geometries(SR["B4"], ref_band.transform, aoi_geoms),
            mask_by_geometries(SR["B3"], ref_band.transform, aoi_geoms),
            mask_by_geometries(SR["B2"], ref_band.transform, aoi_geoms),
        )

    rgb_png_path = os.path.join(out_dir, "RGB_COLORIDO.png")
    save_rgb_png(rgb_png_path, rgb_colorido)
    if nav == "Visão Geral":
        section_title("Visão Geral", "")
        total_pixels = int(np.isfinite(lst).sum())
        rgb_status = "Recortado pela AOI" if aoi_file is not None else "Cena completa"
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            stat_card("Camadas geradas", str(len(layers) + 1), "índices temáticos + RGB")
        with c2:
            stat_card("Pixels válidos", f"{total_pixels:,}".replace(",", "."), "área útil para análise")
        with c3:
            stat_card("Base visual", "RGB", rgb_status)
        with c4:
            stat_card("Anomalia", "6 classes", "classificação térmica automática")

        v1, v2 = st.columns([1.25, 1], gap="large")
        with v1:
            with st.container(border=True):
                fig = plt.figure(figsize=(9.2, 5.6))
                ax = plt.gca()
                ax.imshow(rgb_colorido, interpolation="nearest")
                ax.set_title("RGB colorido — Visão Geral da cena")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        with v2:
            with st.container(border=True):
                st.markdown("**Resumo dos Índices**")
                summary_rows = []
                summary_layer_names = [name for name in list(layers.keys()) if name != "ANOMALIA_CLASS"]
                for name in summary_layer_names:
                    stats = array_stats(layers[name])
                    summary_rows.append({
                        "camada": name,
                        "mín": fmt_num(stats["min"]),
                        "máx": fmt_num(stats["max"]),
                        "média": fmt_num(stats["mean"]),
                    })
                pretty_dataframe(pd.DataFrame(summary_rows), caption="")

    elif nav == "Índices":
        section_title("RGB com Índices", "")
        left, right = st.columns([0.95, 1.35], gap="large")

        preview_options = [k for k in list(layers.keys()) if k != "RGB_COLORIDO"]

        with left:
            with st.container(border=True):
                st.markdown("**Camadas disponíveis para sobreposição**")
                preview = st.selectbox("Camada temática", preview_options, index=0)


                overlay_on_rgb = st.toggle(
                    "Usar RGB como mapa base",
                    value=True,
                    disabled=(preview == "RGB_COLORIDO")
                )

                overlay_alpha = st.slider(
                    "Opacidade da sobreposição",
                    0.10, 0.95, 0.45, 0.05,
                    disabled=(preview == "RGB_COLORIDO" or not overlay_on_rgb)
                )

                preview_cmap_options = palette_options_for_layer(preview)
                preview_default_cmap = default_cmap_for_layer(preview)
                cmap_name = st.selectbox(
                    "Paleta da camada temática",
                    preview_cmap_options,
                    index=preview_cmap_options.index(preview_default_cmap) if preview_default_cmap in preview_cmap_options else 0,
                    disabled=(preview in ["RGB_COLORIDO", "ANOMALIA_CLASS"])
                )

                if preview == "ANOMALIA_CLASS":
                    st.info("# Classes (movido para aba Classificação): 1=fria, 2=mod. fria, 3=normal, 4=mod. quente, 5=hotspot, 6=hotspot intenso")
                elif preview == "RGB_COLORIDO":
                    st.info("Composição colorida natural Landsat: R=B4, G=B3, B=B2, com realce percentil 2–98%.")
                else:
                    st.info("Os arquivos estão disponíveis na aba **Download**.")

        with right:
            with st.container(border=True):
                fig = plt.figure(figsize=(9.4, 5.8))
                ax = plt.gca()

                if preview == "RGB_COLORIDO":
                    ax.imshow(rgb_colorido, interpolation="nearest")
                    im = None
                else:
                    if overlay_on_rgb:
                        im = render_layer_on_rgb(
                            ax, rgb_colorido, preview, layers[preview],
                            alpha=overlay_alpha, cmap_name=cmap_name
                        )
                    else:
                        if preview == "ANOMALIA_CLASS":
                            masked = np.ma.masked_invalid(layers[preview])
                            im = ax.imshow(masked, cmap="tab10", interpolation="nearest", vmin=1, vmax=6)
                        else:
                            preview_norm = build_thematic_norm(layers[preview], preview)
                            im = ax.imshow(layers[preview], cmap=thematic_cmap_for_layer(preview, cmap_name), interpolation="nearest", norm=preview_norm)

                    if im is not None:
                        cbar = plt.colorbar(im, fraction=0.03, pad=0.02)
                        if preview == "ANOMALIA_CLASS":
                            cbar.set_ticks([1, 2, 3, 4, 5, 6])
                            cbar.set_ticklabels(["Fria", "Mod. fria", "Normal", "Mod. quente", "Hotspot", "Hotspot intenso"])

                if preview == "RGB_COLORIDO":
                    title_map = "RGB base"
                elif overlay_on_rgb:
                    title_map = f"RGB + {preview}"
                else:
                    title_map = preview

                ax.set_title(title_map)
                ax.set_xticks([])
                ax.set_yticks([])
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

        # Gera automaticamente os arquivos de apoio da anomalia térmica para o download final,
        # sem exibir o painel de resultados no webapp.
        area_df = area_table_from_classes(layers["ANOMALIA_CLASS"], ref_band)
        csv_path = os.path.join(out_dir, "anomalia_area_classes.csv")
        area_df.to_csv(csv_path, index=False)

        fig_bar = plt.figure(figsize=(7.6, 4.8))
        plt.bar(area_df["classe"], area_df["area_percentual"])
        plt.ylabel("Área (%)")
        interp_text = anomaly_interpretation(area_df, layers["ANOMALIA_Z"])
        txt_path = os.path.join(out_dir, "interpretacao_automatica_anomalia.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(interp_text)



    elif nav == "Classificação":
        section_title("Classificação do uso e ocupação do solo", "")
        with st.container(border=True):
            class_mode = st.radio("**Tipo de classificação**", ["Supervisionada", "Não supervisionada"], horizontal=True)

        if class_mode == "Supervisionada":
            run_supervised_classification_ui(layers, ref_band, out_dir, class_field, rgb_colorido=rgb_colorido)
        else:
            run_unsupervised_classification_ui(layers, ref_band, out_dir, rgb_colorido=rgb_colorido)

        classification_state = st.session_state.get("classification_state")
        if classification_state and isinstance(classification_state, dict):
            st.markdown("")
            left, right = st.columns([0.95, 1.35], gap="large")
            with left:
                with st.container(border=True):
                    st.markdown("**Camadas disponíveis para sobreposição**")
                    overlay_on_rgb = st.toggle(
                        "Usar RGB como mapa base",
                        value=True,
                        key="class_overlay_on_rgb",
                    )
                    overlay_alpha = st.slider(
                        "Opacidade da sobreposição",
                        0.10, 0.95, 0.55, 0.05,
                        disabled=not overlay_on_rgb,
                        key="class_overlay_alpha",
                    )
                    st.info("Os arquivos estão disponíveis na aba **Download**.")

            with right:
                with st.container(border=True):
                    render_classification_grid(
                        classification_state["grid"],
                        "RGB + classificação" if overlay_on_rgb else classification_state.get("title", "Classificação"),
                        legend_labels=classification_state.get("legend_labels"),
                        base_rgb=rgb_colorido,
                        overlay_on_rgb=overlay_on_rgb,
                        overlay_alpha=overlay_alpha,
                    )

            classification_tables = st.session_state.get("classification_tables", [])
            if classification_tables:
                st.markdown("")
                with st.container(border=True):
                    st.markdown("**Tabela de classificação**")
                    for table_item in classification_tables:
                        pretty_dataframe(
                            table_item.get("df"),
                            caption=table_item.get("caption", ""),
                            hide_index=table_item.get("hide_index", True),
                        )

    elif nav == "Regressão Espacial":
        section_title("Regressão Espacial (GWR / MGWR)", "")

        # Etapa 1 — Estrutura analítica
        regression_step_title(
            "Etapa 1 — Estrutura do modelo",
            "Defina a variável dependente e as variáveis preditoras para o modelo de regressão.",
        )
        step1_col1, step1_col2 = st.columns([1, 1.35], gap="large")
        with step1_col1:
            with st.container(border=True):
                regression_block_title(
                    "Variável dependente",
                    "Escolha o raster que será explicado pelo modelo espacial.",
                )
                dependent = st.selectbox(
                    "",
                    list(layers.keys()),
                    index=list(layers.keys()).index("LST_C"),
                    help="É a variável que será explicada pelo modelo espacial.",
                )
                st.caption("Exemplo mais comum: LST_C e ANOMALIA_Z.")

        with step1_col2:
            with st.container(border=True):
                regression_block_title(
                    "Variáveis preditoras",
                    "Selecione os índices ou variáveis que ajudarão a explicar o comportamento espacial da resposta.",
                )
                predictor_options = [k for k in layers.keys() if k != dependent]
                default_predictors = [k for k in ["NDBSI", "NDBI", "NDVI"] if k in predictor_options]
                if not default_predictors:
                    default_predictors = predictor_options[:3]
                predictors = st.multiselect(
                    "",
                    predictor_options,
                    default=default_predictors,
                    help="Escolha as variáveis explicativas que ajudam a interpretar a variável dependente.",
                )
                st.caption("Evite excesso de variáveis altamente correlacionadas. O app calcula VIF ao final.")

        if predictors:
            preview_valid = np.ones_like(layers[dependent], dtype=bool)
            for _name in [dependent] + predictors:
                preview_valid &= np.isfinite(layers[_name])
            st.success(f"Modelo base definido: **{dependent} ~ {' + '.join(predictors)}**")
        else:
            preview_valid = None
            st.info(f"Modelo base definido: **{dependent} ~ ?**")

        # Etapa 2 — Escolha do modelo
        regression_step_title(
            "Etapa 2 — Tipo de regressão",
            "Escolha o modelo GWR, MGWR ou ambos para comparação.",
        )
        with st.container(border=True):
            model_type = st.selectbox(
                "Modelo espacial",
                ["GWR", "MGWR", "Ambos"],
                index=0,
                help="GWR usa uma largura de banda global; MGWR permite escalas diferentes para cada variável.",
            )

            model_help = {
                "GWR": "Use **GWR** quando quiser um modelo local mais direto, com interpretação mais simples e menor custo computacional.",
                "MGWR": "Use **MGWR** quando quiser capturar escalas espaciais distintas entre as variáveis explicativas.",
                "Ambos": "Use **Ambos** quando quiser comparar GWR e MGWR com a mesma base amostral.",
            }
            st.info(model_help[model_type])

        if model_type == "GWR":
            regression_step_title(
                "Etapa 3 - Configuração do GWR",
                "Defina a amostragem e o tipo de exportação para o modelo GWR.",
            )
            sample_col, export_col = st.columns([1.3, 1], gap="large")

            with sample_col:
                with st.container(border=True):
                    regression_block_title(
                        "Amostragem do GWR",
                        "Defina a malha amostral global usada pelo GWR.",
                    )
                    sample_step = st.slider(
                        "Passo de amostragem espacial",
                        1, 20, 6, 1,
                        help="Quanto maior o passo, menor a densidade amostral e mais leve o processamento.",
                    )
                    max_points = st.slider(
                        "Máximo de pontos",
                        500, 20000, 5000, 500,
                        help="Limite superior de amostras usadas na regressão.",
                    )
                    est_points = int(np.count_nonzero(preview_valid[::sample_step, ::sample_step])) if preview_valid is not None else None

            with export_col:
                with st.container(border=True):
                    regression_block_title(
                        "Exportações",
                        "Escolha como os resultados espaciais serão salvos.",
                    )
                    export_filled = st.checkbox("Exportar mapas preenchidos", value=True)
                    export_sparse = st.checkbox("Exportar mapas não preenchidos", value=True)
                    st.caption("Deve-se manter pelo menos um tipo de exportação ativo.")

            mgwr_sampling_mode = "Automático"
            mgwr_auto_max_points = max_points
            mgwr_auto_min_step = sample_step

        elif model_type == "MGWR":
            regression_step_title(
                "Etapa 3 - Configuração do MGWR",
                "Defina a base amostral, a estratégia de amostragem e o tipo de exportação para o modelo MGWR.",
            )
            mgwr_col1, mgwr_col2, export_col = st.columns(3, gap="large")

            with mgwr_col1:
                with st.container(border=True):
                    regression_block_title(
                        "Base amostral do MGWR",
                        "Defina a malha inicial da análise multiescala.",
                    )
                    sample_step = st.slider(
                        "Passo de amostragem espacial",
                        1, 20, 6, 1,
                        help="Quanto maior o passo, menor a densidade amostral e mais leve o processamento.",
                    )
                    max_points = st.slider(
                        "Máximo de pontos",
                        500, 20000, 5000, 500,
                        help="Limite superior de amostras usadas na regressão.",
                    )
                    est_points = int(np.count_nonzero(preview_valid[::sample_step, ::sample_step])) if preview_valid is not None else None


            with mgwr_col2:
                with st.container(border=True):
                    regression_block_title(
                        "Estratégia de amostragem do MGWR",
                        "",
                    )
                    mgwr_sampling_mode = st.selectbox(
                        "Modo de amostragem do MGWR",
                        ["Automático", "Manual"],
                        index=0,
                        help="No modo automático, o app reduz a carga computacional do MGWR quando necessário.",
                    )
                    if mgwr_sampling_mode == "Automático":

                        mgwr_auto_max_points = st.slider("Limite automático de máximo de pontos.", 500, 5000, 2000, 100)
                        mgwr_auto_min_step = st.slider("Limite automático de passo mínimo.", 1, 20, 10, 1)

                    else:
                        mgwr_auto_max_points = max_points
                        mgwr_auto_min_step = sample_step
                        st.warning("No modo manual, o app respeita os parâmetros escolhidos. Configurações densas podem ficar pesadas.")


            with export_col:
                with st.container(border=True):
                    regression_block_title(
                        "Exportações",
                        "Escolha como os resultados espaciais serão salvos.",
                    )
                    export_filled = st.checkbox("Exportar mapas preenchidos", value=True)
                    export_sparse = st.checkbox("Exportar mapas não preenchidos", value=True)
                    st.caption("Deve-se manter pelo menos um tipo de exportação ativo.")


        else:
            regression_step_title(
                "Etapa 3 — Comparação entre GWR e MGWR",
                "Combine controles gerais e parâmetros multiescala para comparar os dois modelos na mesma execução.",
            )
            sample_col, mgwr_col, export_col = st.columns(3, gap="large")

            with sample_col:
                with st.container(border=True):
                    regression_block_title(
                        "Base amostral compartilhada",
                        "Defina a malha principal usada na comparação entre GWR e MGWR.",
                    )
                    sample_step = st.slider(
                        "Passo de amostragem espacial",
                        1, 20, 6, 1,
                        help="Quanto maior o passo, menor a densidade amostral e mais leve o processamento.",
                    )
                    max_points = st.slider(
                        "Máximo de pontos",
                        500, 20000, 5000, 500,
                        help="Limite superior de amostras usadas na regressão.",
                    )
                    est_points = int(np.count_nonzero(preview_valid[::sample_step, ::sample_step])) if preview_valid is not None else None


            with mgwr_col:
                with st.container(border=True):
                    regression_block_title(
                        "Ajustes adicionais do MGWR",
                        "",
                    )
                    mgwr_sampling_mode = st.selectbox(
                        "Modo de amostragem do MGWR",
                        ["Automático", "Manual"],
                        index=0,
                        help="No modo automático, o app reduz a carga computacional do MGWR quando necessário.",
                    )
                    if mgwr_sampling_mode == "Automático":
                        st.info("O app pode aumentar o passo e reduzir o número máximo de pontos para tornar o MGWR mais estável.")
                        mgwr_auto_max_points = st.slider("Limite automático de máximo de pontos.", 500, 5000, 2000, 100)
                        mgwr_auto_min_step = st.slider("Limite automático de passo mínimo.", 1, 20, 10, 1)

                    else:
                        mgwr_auto_max_points = max_points
                        mgwr_auto_min_step = sample_step
                        st.warning("No modo manual, o app respeita os parâmetros escolhidos. Configurações densas podem ficar pesadas.")


            with export_col:
                with st.container(border=True):
                    regression_block_title(
                        "Exportações",
                        "Escolha como os resultados espaciais serão salvos.",
                    )
                    export_filled = st.checkbox("Exportar mapas preenchidos", value=True)
                    export_sparse = st.checkbox("Exportar mapas não preenchidos", value=True)
                    st.caption("Deve-se manter pelo menos um tipo de exportação ativo.")

        # Execução direta da regressão espacial
        run_regression = st.button(
            "Executar Regressão Espacial",
            use_container_width=True,
            type="primary",
            key="run_spatial_regression",
        )

        regression_state = st.session_state.get("regression_spatial_state")

        def render_regression_results_panel(state):
            if not state:
                return

            with st.container(border=True):
                if state.get("mgwr_warning"):
                    st.warning(state["mgwr_warning"])

                regression_overlay_layers = state.get("overlay_layers", {})
                if regression_overlay_layers:
                    overlay_left, overlay_right = st.columns([0.95, 1.35], gap="large")

                    with overlay_left:
                        with st.container(border=True):
                            st.markdown("**Camadas disponíveis para sobreposição**")
                            regression_preview = st.selectbox(
                                "Camada da regressão",
                                list(regression_overlay_layers.keys()),
                                key="regression_overlay_preview",
                            )

                            regression_overlay_on_rgb = st.toggle(
                                "Usar RGB como mapa base",
                                value=True,
                                key="regression_overlay_on_rgb",
                            )

                            regression_overlay_alpha = st.slider(
                                "Opacidade da sobreposição",
                                0.10, 0.95, 0.55, 0.05,
                                key="regression_overlay_alpha",
                                disabled=not regression_overlay_on_rgb,
                            )

                            regression_cmap_options = palette_options_for_layer(regression_preview)
                            regression_default_cmap = default_cmap_for_layer(regression_preview)
                            regression_cmap = st.selectbox(
                                "Paleta da camada da regressão",
                                regression_cmap_options,
                                index=regression_cmap_options.index(regression_default_cmap) if regression_default_cmap in regression_cmap_options else 0,
                                key="regression_overlay_cmap",
                                disabled=is_binary_significance_layer(regression_preview),
                            )

                            st.info("Os arquivos estão disponíveis na aba **Download**.")


                    with overlay_right:
                        with st.container(border=True):
                            fig = plt.figure(figsize=(9.4, 5.8))
                            ax = plt.gca()
                            current_layer = regression_overlay_layers[regression_preview]

                            if regression_overlay_on_rgb:
                                im = render_layer_on_rgb(
                                    ax,
                                    rgb_colorido,
                                    regression_preview,
                                    current_layer,
                                    alpha=regression_overlay_alpha,
                                    cmap_name=regression_cmap,
                                )
                            else:
                                masked = np.ma.masked_invalid(current_layer)
                                regression_norm = build_thematic_norm(current_layer, regression_preview)
                                im = ax.imshow(masked, cmap=thematic_cmap_for_layer(regression_preview, regression_cmap), interpolation="nearest", norm=regression_norm)

                            if im is not None:
                                apply_thematic_colorbar(fig, im, regression_preview)

                            ax.set_title(f"RGB + {regression_preview}" if regression_overlay_on_rgb else regression_preview)
                            ax.set_xticks([])
                            ax.set_yticks([])
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close(fig)

        if run_regression:
            if not predictors:
                st.error("Escolha pelo menos uma preditora.")
            elif not export_filled and not export_sparse:
                st.error("Selecione pelo menos um tipo de exportação.")
            else:
                progress_bar = st.progress(0, text="Iniciando regressão espacial...")
                status_box = st.empty()
                try:
                    status_box.info("Etapa 1/6 — Construindo a base analítica")
                    progress_bar.progress(10, text="Montando a matriz de dados")
                    df_full, valid_full = build_feature_df({k: layers[k] for k in [dependent] + predictors}, ref_band)

                    status_box.info("Etapa 2/6 — Preparando a amostragem espacial")
                    progress_bar.progress(25, text="Definindo pixels válidos e amostragem")
                    sampled_mask = np.zeros_like(valid_full, dtype=bool)
                    sampled_mask[::sample_step, ::sample_step] = True
                    sampled_mask &= valid_full

                    idx = np.flatnonzero(sampled_mask)
                    effective_max = max_points
                    effective_step = sample_step

                    if model_type in ["MGWR", "Ambos"] and mgwr_sampling_mode == "Automático":
                        effective_max = min(max_points, mgwr_auto_max_points)
                        effective_step = max(sample_step, mgwr_auto_min_step)
                        sampled_mask[:] = False
                        sampled_mask[::effective_step, ::effective_step] = True
                        sampled_mask &= valid_full
                        idx = np.flatnonzero(sampled_mask)

                    if len(idx) > effective_max:
                        rng = np.random.default_rng(42)
                        chosen = rng.choice(idx, size=effective_max, replace=False)
                        sampled_mask[:] = False
                        sampled_mask.flat[chosen] = True

                    status_box.info("Etapa 3/6 — Organizando coordenadas e variáveis do modelo")
                    progress_bar.progress(40, text="Preparando coordenadas e preditoras")
                    xs, ys = raster_coords(ref_band)
                    sampled_df = pd.DataFrame({
                        "x": xs[sampled_mask],
                        "y": ys[sampled_mask],
                    })
                    for k in [dependent] + predictors:
                        sampled_df[k] = layers[k][sampled_mask]

                    status_box.info("Etapa 4/6 — Ajustando o modelo espacial")
                    if model_type == "GWR":
                        progress_bar.progress(55, text="Executando GWR")
                    elif model_type == "MGWR":
                        progress_bar.progress(55, text="Executando MGWR")
                    else:
                        progress_bar.progress(55, text="Executando GWR e MGWR")

                    results, meta = run_spatial_regression_advanced(
                        sampled_df,
                        dependent,
                        predictors,
                        model_type,
                        effective_step,
                        effective_max,
                        mgwr_sampling_mode,
                        mgwr_auto_max_points,
                        mgwr_auto_min_step,
                    )

                    status_box.info("Etapa 5/6 — Exportando tabelas, diagnósticos e rasters")
                    progress_bar.progress(82, text="Gravando saídas da regressão")
                    write_regression_outputs(results, predictors, valid_full, sampled_mask, ref_band, out_dir, export_filled, export_sparse)

                    status_box.info("Etapa 6/6 — Empacotando os resultados para download")
                    progress_bar.progress(94, text="Gerando pacote ZIP")
                    zip_path = package_outputs(out_dir, "regressao_espacial_resultados_v16.zip")
                    progress_bar.progress(100, text="Processamento concluído")

                    regression_overlay_layers = {}

                    ref_shape = None
                    if hasattr(ref_band, "arr") and getattr(ref_band, "arr") is not None:
                        ref_shape = ref_band.arr.shape
                    elif hasattr(ref_band, "shape"):
                        ref_shape = ref_band.shape
                    elif hasattr(ref_band, "YSize") and hasattr(ref_band, "XSize"):
                        ref_shape = (ref_band.YSize, ref_band.XSize)
                    elif valid_full is not None:
                        ref_shape = valid_full.shape

                    if ref_shape is None:
                        raise ValueError("Não foi possível determinar a grade de referência para as camadas da regressão espacial.")

                    sampled_positions = np.flatnonzero(sampled_mask)
                    valid_positions = np.flatnonzero(valid_full) if valid_full is not None else np.array([], dtype=int)
                    use_filled_overlay = True

                    try:
                        xs_overlay, ys_overlay = raster_coords(ref_band)
                    except Exception:
                        xs_overlay = ys_overlay = None

                    sampled_coords_overlay = None
                    valid_coords_overlay = None
                    if xs_overlay is not None and ys_overlay is not None and sampled_positions.size > 0 and valid_positions.size > 0:
                        sampled_coords_overlay = np.column_stack([xs_overlay.ravel()[sampled_positions], ys_overlay.ravel()[sampled_positions]])
                        valid_coords_overlay = np.column_stack([xs_overlay.ravel()[valid_positions], ys_overlay.ravel()[valid_positions]])

                    def sampled_values_to_grid(values):
                        arr = np.asarray(values, dtype=float).reshape(-1)
                        grid = np.full(ref_shape, np.nan, dtype=float)
                        if arr.size == 0:
                            return grid

                        n_sampled = min(arr.size, sampled_positions.size)
                        sparse_grid = np.full(ref_shape, np.nan, dtype=float)
                        if n_sampled > 0:
                            sparse_flat = sparse_grid.ravel()
                            sparse_flat[sampled_positions[:n_sampled]] = arr[:n_sampled]
                            sparse_grid = sparse_flat.reshape(ref_shape)

                        if (not use_filled_overlay) or valid_positions.size == 0 or n_sampled == 0:
                            return sparse_grid

                        if sampled_coords_overlay is not None and valid_coords_overlay is not None:
                            try:
                                from scipy.spatial import cKDTree
                                idx = cKDTree(sampled_coords_overlay[:n_sampled]).query(valid_coords_overlay, k=1)[1]
                                filled = np.full(ref_shape, np.nan, dtype=float)
                                filled_flat = filled.ravel()
                                filled_flat[valid_positions] = arr[:n_sampled][idx]
                                return filled_flat.reshape(ref_shape)
                            except Exception:
                                pass

                        filled = np.full(ref_shape, np.nan, dtype=float)
                        filled_flat = filled.ravel()
                        fill_count = min(arr.size, valid_positions.size)
                        filled_flat[valid_positions[:fill_count]] = arr[:fill_count]
                        return filled_flat.reshape(ref_shape)

                    for _model_name, _info in results.items():
                        if "localR2" in _info:
                            regression_overlay_layers[f"{_model_name} • R² local"] = sampled_values_to_grid(_info["localR2"])
                        if "params" in _info:
                            coef_names = ["Intercepto"] + predictors
                            for _j, _coef_name in enumerate(coef_names):
                                regression_overlay_layers[f"{_model_name} • Coef. {_coef_name}"] = sampled_values_to_grid(_info["params"][:, _j])
                        if "tvalues" in _info:
                            coef_names = ["Intercepto"] + predictors
                            for _j, _coef_name in enumerate(coef_names):
                                regression_overlay_layers[f"{_model_name} • t {_coef_name}"] = sampled_values_to_grid(_info["tvalues"][:, _j])
                        if "pvalues" in _info and _info["pvalues"] is not None:
                            coef_names = ["Intercepto"] + predictors
                            for _j, _coef_name in enumerate(coef_names):
                                regression_overlay_layers[f"{_model_name} • p {_coef_name}"] = sampled_values_to_grid(_info["pvalues"][:, _j])
                        if "significant_005" in _info and _info["significant_005"] is not None:
                            coef_names = ["Intercepto"] + predictors
                            for _j, _coef_name in enumerate(coef_names):
                                regression_overlay_layers[f"{_model_name} • Signif. p<0.05 {_coef_name}"] = sampled_values_to_grid(_info["significant_005"][:, _j])

                    mgwr_warning = None
                    if model_type in ["MGWR", "Ambos"] and meta["mgwr_status"] == "falhou":
                        mgwr_warning = f"O MGWR falhou durante o processamento: {meta['mgwr_error']}"

                    st.session_state["regression_spatial_state"] = {
                        "model_type": model_type,
                        "dependent": dependent,
                        "predictors": predictors[:],
                        "effective_step": int(effective_step),
                        "effective_max": int(effective_max),
                        "n_points": int(len(sampled_df)),
                        "overlay_layers": regression_overlay_layers,
                        "zip_path": zip_path,
                        "mgwr_warning": mgwr_warning,
                    }
                    regression_state = st.session_state["regression_spatial_state"]

                except Exception as e:
                    progress_bar.empty()
                    status_box.empty()
                    st.error(f"Falha na Regressão Espacial: {e}")
                    st.code(traceback.format_exc())

        if regression_state:
            render_regression_results_panel(regression_state)
    elif nav == "Download":
        section_title("Download")

        regression_state = st.session_state.get("regression_spatial_state")
        regression_zip_path = regression_state.get("zip_path") if regression_state else None

        # Garante que as camadas básicas existam para seleção, se o usuário quiser incluí-las
        basic_files_created = []
        for name, arr in layers.items():
            asc_path = os.path.join(out_dir, f"{name}.asc")
            if not os.path.exists(asc_path):
                save_asc(asc_path, arr, ref_band)
                basic_files_created.append(os.path.relpath(asc_path, out_dir))

        existing_files = []
        if os.path.isdir(out_dir):
            for root, _, files in os.walk(out_dir):
                for f in files:
                    if f.lower().endswith(".zip"):
                        continue
                    existing_files.append(os.path.relpath(os.path.join(root, f), out_dir))
        existing_files = sorted(existing_files)

        with st.container(border=True):

            if existing_files:
                st.caption(f"{len(existing_files)} arquivos disponíveis para exportação.")
                selected_files = st.multiselect(
                    "",
                    existing_files,
                    default=existing_files,
                    help="Desmarque os itens que não deseja levar para o pacote final."
                )
            else:
                selected_files = []
                st.info("Nenhum arquivo disponível para exportação ainda.")

            st.markdown("<div style='height: 0.35rem;'></div>", unsafe_allow_html=True)

            col_zip_1, col_zip_2 = st.columns([3.2, 1], vertical_alignment="bottom")

            with col_zip_1:
                custom_zip_name = st.text_input(
                    "",
                    value="analise_espacial_climatologia_urbana_resultados.zip"
                )

            with col_zip_2:
                prepare_zip = st.button("Preparar ZIP", use_container_width=True)

            if prepare_zip:
                if not selected_files:
                    st.error("Selecione pelo menos um arquivo para o ZIP.")
                else:
                    zip_path = os.path.join(out_dir, custom_zip_name)
                    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                        for rel_path in selected_files:
                            full_path = os.path.join(out_dir, rel_path)
                            if os.path.exists(full_path):
                                zf.write(full_path, rel_path)

                    st.success("ZIP preparado com sucesso.")

                    with open(zip_path, "rb") as f:
                        st.download_button(
                            "Download ZIP",
                            f.read(),
                            custom_zip_name,
                            use_container_width=True
                        )

except Exception as e:
    st.error(f"Falha no processamento do pacote Landsat: {e}")
    st.code(traceback.format_exc())

