import streamlit as st


def show_comparison_page():

    # ======================================================
    # PAGE HEADER
    # ======================================================
    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">Performance Evaluation</div>'
        '<h1>Model Comparison</h1>'
        '<p>Quantitative benchmarks comparing the AfroXLMR baseline '
        'against the hybrid model on the NaijaCodeMix test set.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # ======================================================
    # SUMMARY METRIC ROW
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Summary</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="metric-row">
        <div class="metric-cell">
            <div class="metric-val highlight">81.4%</div>
            <div class="metric-lbl">Hybrid Accuracy</div>
        </div>
        <div class="metric-cell">
            <div class="metric-val">70.6%</div>
            <div class="metric-lbl">Baseline Accuracy</div>
        </div>
        <div class="metric-cell">
            <div class="metric-val highlight">+10.8%</div>
            <div class="metric-lbl">Accuracy Gain</div>
        </div>
        <div class="metric-cell">
            <div class="metric-val highlight">0.827</div>
            <div class="metric-lbl">Hybrid F1-Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # FULL RESULTS TABLE
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Full Results Table</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    st.table({
        "Metric":        ["Accuracy", "Precision", "Recall", "F1-Score"],
        "Baseline":      ["70.6%",    "0.720",     "0.740",  "0.730"],
        "Hybrid":        ["81.4%",    "0.814",     "0.840",  "0.827"],
        "Absolute Gain": ["+10.8pp",  "+9.4pp",    "+10.0pp","+9.7pp"],
    })

    # ======================================================
    # INTERPRETATION
    # ======================================================
    st.markdown(
        '<div class="section-rule">'
        '<span class="section-rule-label">Interpretation</span>'
        '<span class="section-rule-line"></span>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="card">
        <div class="card-eyebrow">Why the Hybrid Model Outperforms</div>
        <div style="font-size:0.9rem; color:var(--text-mid); line-height:1.8;">
            The baseline AfroXLMR model relies solely on contextual transformer
            embeddings and lacks explicit knowledge of Naija Pidgin vocabulary or
            the structural patterns of Pidgin–English switching.<br><br>
            The hybrid model augments these embeddings with three handcrafted
            linguistic features: <strong>Pidgin keyword presence</strong>,
            <strong>language switch-point count</strong>, and
            <strong>English token ratio</strong>. These features encode
            domain-specific knowledge that the transformer cannot reliably infer
            from multilingual pretraining alone — particularly for a low-resource
            language variety like Naija Pidgin.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout">
        <strong>Note on class imbalance:</strong> The evaluation set reflects a
        7:1 ratio (Pidgin-dominant : English). Per-class F1 scores should be
        consulted alongside macro averages when interpreting these results.
        This imbalance is acknowledged as a key limitation of the current study.
    </div>
    """, unsafe_allow_html=True)
