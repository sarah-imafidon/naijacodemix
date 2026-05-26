import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add frontend/ to path so components can be found on Streamlit Cloud
FRONTEND_DIR = Path(__file__).parent.parent
sys.path.append(str(FRONTEND_DIR))

# Add project root to path so backend can be found
ROOT_DIR = FRONTEND_DIR.parent
sys.path.append(str(ROOT_DIR))

from components.explanation import explain_prediction
from backend.predict import predict
from backend.features import pidgin_keywords, english_words

from components.cards import prediction_card
from components.metrics import metrics_row
from components.token_display import display_tokens
from components.export import export_results


def show_analyze_page():

    # ======================================================
    # PAGE HEADER
    # ======================================================
    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">NaijaCodeMix — Research Tool</div>'
        '<h1>Code-Switching Analysis</h1>'
        '<p>Submit Nigerian social media text to detect Pidgin–English '
        'code-mixing, inspect token-level evidence, and compare model predictions.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # ======================================================
    # INPUT SECTION
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Step 1 — Input Text</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="callout">
        Paste any Nigerian social media text below — a tweet, WhatsApp message,
        or forum post. The system will classify it, explain the linguistic
        evidence, annotate each token, and generate a downloadable report.
    </div>
    """, unsafe_allow_html=True)

    text = st.text_area(
        "Input Text",
        height=150,
        placeholder="e.g. 'I no fit come today, the work don too much for me abeg...'"
    )

    # ======================================================
    # ANALYSE BUTTON
    # ======================================================
    btn_col, _ = st.columns([1, 6])
    with btn_col:
        run = st.button("Run Analysis")

    if not run:
        return

    if not text.strip():
        st.warning("Please enter some text before running analysis.")
        return

    # ======================================================
    # RUN PREDICTION
    # ======================================================
    with st.spinner("Running inference…"):
        result = predict(text)

    baseline = result["baseline"]
    hybrid   = result["hybrid"]
    features = result["features"]

    b_pred = baseline["prediction"]
    h_pred = hybrid["prediction"]
    b_conf = int(baseline["confidence"] * 100)
    h_conf = int(hybrid["confidence"] * 100)

    # ======================================================
    # STEP 2 — CLASSIFICATION RESULT
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Step 2 — Classification Result</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        prediction_card(
            model_name="Baseline — AfroXLMR",
            prediction=b_pred,
            confidence=b_conf,
            color_class="verdict-codemixed" if b_pred == "Code-Mixed" else "verdict-english",
            description="Transformer embeddings only",
            fill_class="conf-fill-red"
        )

    with col2:
        prediction_card(
            model_name="Hybrid — Transformer + Linguistic Features",
            prediction=h_pred,
            confidence=h_conf,
            color_class="verdict-codemixed" if h_pred == "Code-Mixed" else "verdict-english",
            description="AfroXLMR + linguistic feature engineering",
            fill_class="conf-fill-blue"
        )

    # Agreement / disagreement note
    if b_pred == h_pred:
        st.markdown(
            f'<div class="agreement-box agree">'
            f'<strong>Both models agree:</strong> The text is classified as '
            f'<strong>{h_pred}</strong>. The hybrid model\'s linguistic features '
            f'corroborate the transformer prediction.'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="agreement-box disagree">'
            f'<strong>Models disagree.</strong> Baseline predicts '
            f'<strong>{b_pred}</strong>; hybrid predicts '
            f'<strong>{h_pred}</strong>. The hybrid\'s linguistic features may '
            f'be resolving ambiguity the baseline transformer cannot detect.'
            f'</div>',
            unsafe_allow_html=True
        )

    # ======================================================
    # STEP 3 — LINGUISTIC EVIDENCE
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Step 3 — Linguistic Evidence</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    metrics_row(features)

    # ======================================================
    # STEP 4 — LINGUISTIC FINDINGS
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Step 4 — Linguistic Findings</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    explain_prediction(features)

    # ======================================================
    # STEP 5 — TOKEN ANNOTATION
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Step 5 — Token-Level Annotation</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    display_tokens(text, pidgin_keywords, english_words)

    # ======================================================
    # STEP 6 — EXPORT
    # ======================================================
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_text": text,
        "baseline": {
            "prediction": b_pred,
            "confidence": f"{b_conf}%"
        },
        "hybrid": {
            "prediction": h_pred,
            "confidence": f"{h_conf}%"
        },
        "features": {
            "pidgin_count":    features["pidgin_count"],
            "switch_count":    features["switch_count"],
            "english_ratio":   round(features["english_ratio"], 4),
            "contains_pidgin": features["contains_pidgin"],
        }
    }

    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Step 6 — Export Results</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    export_results(report)