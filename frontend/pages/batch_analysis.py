import streamlit as st
import pandas as pd
import io
from datetime import datetime

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent  # frontend/pages/ -> frontend/ -> project root
sys.path.append(str(ROOT_DIR))

from backend.predict import predict


ROW_LIMIT = 500


# ── Helpers ───────────────────────────────────────────────────────────────────

def _section_rule(label: str):
    st.markdown(
        f'<div class="section-rule">'
        f'<span class="section-rule-label">{label}</span>'
        f'<span class="section-rule-line"></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _badge(pred: str) -> str:
    cls = "hbadge-cm" if pred == "Code-Mixed" else "hbadge-eng"
    return f'<span class="hbadge {cls}">{pred}</span>'


def _read_upload(uploaded_file) -> pd.DataFrame | None:
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".xlsx") or name.endswith(".xls"):
            return pd.read_excel(uploaded_file)
        return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return None


# ── Main page ─────────────────────────────────────────────────────────────────

def show_batch_page():

    # ======================================================
    # PAGE HEADER
    # ======================================================
    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">Corpus-Level Analysis</div>'
        '<h1>Batch Analysis</h1>'
        '<p>Upload a CSV or Excel dataset of Nigerian social media texts. '
        'The system will classify every row, compute corpus-level statistics, '
        'and produce a fully annotated file for your research.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # ======================================================
    # STEP 1 — UPLOAD
    # ======================================================
    _section_rule("Step 1 — Upload Dataset")

    st.markdown("""
    <div class="callout">
        <strong>Supported formats:</strong> CSV (<code>.csv</code>) and Excel
        (<code>.xlsx</code>).<br>
        Your file must contain at least one column with the texts to analyse.
        All additional columns (e.g. tweet ID, date, label) will be preserved
        in the annotated output. Datasets over <strong>500 rows</strong> will
        require confirmation before processing.
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx", "xls"],
        help="CSV or Excel file with at least one text column.",
    )

    if uploaded_file is None:
        st.markdown("""
        <div class="card">
            <div class="card-eyebrow">Expected CSV Format — Example</div>
            <div style="font-family:var(--mono); font-size:0.8rem;
                        color:var(--text-mid); line-height:2.4;">
                id,&nbsp;text,&nbsp;source<br>
                1,&nbsp;"I no fit come today abeg",&nbsp;twitter<br>
                2,&nbsp;"The meeting has been rescheduled",&nbsp;twitter<br>
                3,&nbsp;"E don do, make we go chop",&nbsp;whatsapp<br>
                4,&nbsp;"Please send the report by Friday",&nbsp;twitter
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ======================================================
    # READ FILE
    # ======================================================
    df_raw = _read_upload(uploaded_file)

    if df_raw is None or df_raw.empty:
        st.error("The uploaded file is empty or could not be parsed.")
        return

    # ======================================================
    # STEP 2 — COLUMN SELECTION & PREVIEW
    # ======================================================
    _section_rule("Step 2 — Select Text Column")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        text_column = st.selectbox(
            "Which column contains the texts to analyse?",
            options=df_raw.columns.tolist(),
        )

    with col_right:
        st.markdown(
            f'<div class="card" style="padding:1rem 1.25rem;">'
            f'<div class="card-eyebrow">File Summary</div>'
            f'<div style="font-family:var(--mono); font-size:0.78rem; '
            f'color:var(--text-mid); line-height:2;">'
            f'<strong>{len(df_raw)}</strong> rows &nbsp;·&nbsp; '
            f'<strong>{len(df_raw.columns)}</strong> column(s)<br>'
            f'Columns:&nbsp;{", ".join(df_raw.columns.tolist())}'
            f'</div></div>',
            unsafe_allow_html=True
        )

    st.dataframe(
        df_raw[[text_column]]
        .head(5)
        .rename(columns={text_column: f"Preview — '{text_column}' (first 5 rows)"}),
        use_container_width=True,
        hide_index=True,
    )

    # ======================================================
    # ROW LIMIT WARNING
    # ======================================================
    total_rows = len(df_raw)

    if total_rows > ROW_LIMIT:
        st.warning(
            f"⚠️ Your dataset has **{total_rows} rows**, which exceeds the "
            f"recommended limit of **{ROW_LIMIT}**. "
            f"Only the first {ROW_LIMIT} rows will be processed."
        )
        if not st.checkbox(f"I understand — process the first {ROW_LIMIT} rows"):
            return
        df_raw = df_raw.head(ROW_LIMIT)

    # ======================================================
    # STEP 3 — RUN BATCH
    # ======================================================
    _section_rule("Step 3 — Run Batch Analysis")

    st.markdown("""
    <div class="callout">
        Both the <strong>Baseline (AfroXLMR)</strong> and <strong>Hybrid</strong>
        models will run on every row. Predictions, confidence scores, and all
        linguistic features will be included in the annotated output file.
    </div>
    """, unsafe_allow_html=True)

    run_col, _ = st.columns([1, 5])
    with run_col:
        start = st.button("Start Batch Analysis")

    if not start:
        return

    # ======================================================
    # PROCESS ROWS
    # ======================================================
    texts    = df_raw[text_column].fillna("").tolist()
    n        = len(texts)
    progress = st.progress(0, text="Initialising…")
    status   = st.empty()
    rows     = []

    for i, text in enumerate(texts):
        try:
            res = predict(str(text))
            b   = res["baseline"]
            h   = res["hybrid"]
            f   = res["features"]
            rows.append({
                "baseline_prediction": b["prediction"],
                "baseline_confidence": round(b["confidence"], 4),
                "hybrid_prediction":   h["prediction"],
                "hybrid_confidence":   round(h["confidence"], 4),
                "models_agree":        b["prediction"] == h["prediction"],
                "pidgin_count":        f["pidgin_count"],
                "switch_count":        f["switch_count"],
                "english_ratio":       round(f["english_ratio"], 4),
                "contains_pidgin":     f["contains_pidgin"],
            })
        except Exception:
            rows.append({
                "baseline_prediction": "ERROR",
                "baseline_confidence": 0.0,
                "hybrid_prediction":   "ERROR",
                "hybrid_confidence":   0.0,
                "models_agree":        False,
                "pidgin_count":        0,
                "switch_count":        0,
                "english_ratio":       0.0,
                "contains_pidgin":     False,
            })

        pct = int((i + 1) / n * 100)
        progress.progress(pct, text=f"Analysing row {i + 1} of {n}…")
        if (i + 1) % 10 == 0 or i + 1 == n:
            status.markdown(
                f'<span style="font-family:var(--mono); font-size:0.75rem; '
                f'color:var(--muted);">{i + 1} / {n} rows complete</span>',
                unsafe_allow_html=True,
            )

    progress.empty()
    status.empty()

    df_results = pd.DataFrame(rows)
    df_output  = pd.concat([df_raw.reset_index(drop=True), df_results], axis=1)

    # ======================================================
    # STEP 4 — CORPUS STATISTICS
    # ======================================================
    _section_rule("Step 4 — Corpus-Level Statistics")

    cm_count       = (df_output["hybrid_prediction"] == "Code-Mixed").sum()
    eng_count      = n - cm_count
    agree_count    = df_output["models_agree"].sum()
    disagree_count = n - agree_count
    cm_pct         = round(cm_count / n * 100, 1)
    agree_pct      = round(agree_count / n * 100, 1)
    avg_pidgin     = round(df_output["pidgin_count"].mean(), 2)
    avg_switches   = round(df_output["switch_count"].mean(), 2)
    avg_eng_ratio  = round(df_output["english_ratio"].mean(), 2)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-cell">
            <div class="metric-val">{n}</div>
            <div class="metric-lbl">Texts Analysed</div>
        </div>
        <div class="metric-cell">
            <div class="metric-val highlight">{cm_count}</div>
            <div class="metric-lbl">Code-Mixed ({cm_pct}%)</div>
        </div>
        <div class="metric-cell">
            <div class="metric-val">{eng_count}</div>
            <div class="metric-lbl">Plain English ({round(100 - cm_pct, 1)}%)</div>
        </div>
        <div class="metric-cell">
            <div class="metric-val">{agree_count}</div>
            <div class="metric-lbl">Models Agree ({agree_pct}%)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-eyebrow">Avg. Pidgin Tokens / Text</div>
            <div class="metric-val highlight" style="font-size:2rem;">{avg_pidgin}</div>
            <div style="font-size:0.78rem; color:var(--muted);
                        margin-top:0.5rem; font-family:var(--mono);">
                Across all {n} texts
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-eyebrow">Avg. Switch Points / Text</div>
            <div class="metric-val" style="font-size:2rem;">{avg_switches}</div>
            <div style="font-size:0.78rem; color:var(--muted);
                        margin-top:0.5rem; font-family:var(--mono);">
                Language transitions per text
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="card-eyebrow">Avg. English Ratio</div>
            <div class="metric-val" style="font-size:2rem;">{avg_eng_ratio}</div>
            <div style="font-size:0.78rem; color:var(--muted);
                        margin-top:0.5rem; font-family:var(--mono);">
                Proportion of English tokens
            </div>
        </div>
        """, unsafe_allow_html=True)

    if disagree_count > 0:
        disagree_pct = round(disagree_count / n * 100, 1)
        st.markdown(f"""
        <div class="callout" style="margin-top:0.5rem;">
            <strong>Model disagreement detected:</strong> The baseline and hybrid
            models produced different predictions on
            <strong>{disagree_count} text(s) ({disagree_pct}%)</strong>
            of your dataset. These cases — where the hybrid model's linguistic
            features changed the outcome — are linguistically significant and
            may be worth examining closely in your research.
        </div>
        """, unsafe_allow_html=True)

    # ======================================================
    # STEP 5 — RESULTS TABLE
    # ======================================================
    _section_rule("Step 5 — Annotated Results")

    display_cols = [
        text_column,
        "hybrid_prediction",   "hybrid_confidence",
        "baseline_prediction", "baseline_confidence",
        "models_agree",
        "pidgin_count",        "switch_count",
        "english_ratio",       "contains_pidgin",
    ]
    display_cols = [c for c in display_cols if c in df_output.columns]

    st.dataframe(
        df_output[display_cols].rename(columns={
            text_column:             "Text",
            "hybrid_prediction":     "Hybrid Prediction",
            "hybrid_confidence":     "Hybrid Confidence",
            "baseline_prediction":   "Baseline Prediction",
            "baseline_confidence":   "Baseline Confidence",
            "models_agree":          "Models Agree",
            "pidgin_count":          "Pidgin Tokens",
            "switch_count":          "Switch Points",
            "english_ratio":         "English Ratio",
            "contains_pidgin":       "Contains Pidgin",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ---- Disagreement expander ----
    disagreements = df_output[~df_output["models_agree"]]
    if not disagreements.empty:
        with st.expander(f"🔍  View {len(disagreements)} disagreement(s) in detail"):
            for _, row in disagreements.iterrows():
                raw_text = str(row.get(text_column, ""))
                snippet  = raw_text[:120] + ("…" if len(raw_text) > 120 else "")
                st.markdown(
                    f'<div class="history-card">'
                    f'<div class="history-text">{snippet}</div>'
                    f'<div class="history-badges">'
                    f'<span class="pill-label">Baseline:</span>'
                    f'{_badge(row["baseline_prediction"])}'
                    f'<span class="pill-label" style="margin-left:8px">Hybrid:</span>'
                    f'{_badge(row["hybrid_prediction"])}'
                    f'<span class="hbadge">'
                    f'{int(row["pidgin_count"])} pidgin &nbsp;·&nbsp; '
                    f'{int(row["switch_count"])} switches &nbsp;·&nbsp; '
                    f'eng ratio {round(row["english_ratio"], 2)}'
                    f'</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

    # ======================================================
    # STEP 6 — EXPORT
    # ======================================================
    _section_rule("Step 6 — Download Annotated Dataset")

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_buffer = io.StringIO()
    df_output.to_csv(csv_buffer, index=False)
    csv_bytes  = csv_buffer.getvalue().encode("utf-8")

    st.markdown(
        f'<div class="export-box">'
        f'<div class="export-info">'
        f'<strong>{n} texts annotated</strong> &nbsp;·&nbsp; '
        f'{cm_count} Code-Mixed &nbsp;·&nbsp; '
        f'{eng_count} Plain English &nbsp;·&nbsp; '
        f'{disagree_count} model disagreement(s)<br>'
        f'The output CSV includes all original columns plus: baseline &amp; hybrid '
        f'predictions, confidence scores, and all linguistic features.'
        f'</div></div>',
        unsafe_allow_html=True
    )

    st.download_button(
        label="↓  Download Annotated CSV",
        data=csv_bytes,
        file_name=f"codemix_batch_{timestamp}.csv",
        mime="text/csv",
    )