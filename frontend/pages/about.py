import streamlit as st


def show_about_page():

    # ======================================================
    # PAGE HEADER
    # ======================================================
    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">Documentation</div>'
        '<h1>About This System</h1>'
        '<p>A research instrument for computational analysis of '
        'Nigerian Pidgin–English code-switching in social media text.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # ======================================================
    # LEFT COLUMN
    # ======================================================
    with col1:

        st.markdown("""
        <div class="about-card">
            <h3>Research Context</h3>
            <ul>
                <li>Focuses on Nigerian Pidgin (Naija)–English code-switching</li>
                <li>Corpus: 4,075 annotated tweets from Nigerian social media</li>
                <li>Task: Binary classification — Code-Mixed vs. Plain English</li>
                <li>Addresses a gap in African NLP tooling for low-resource
                    language varieties</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="about-card">
            <h3>Models Used</h3>
            <ul>
                <li><strong>Baseline:</strong> AfroXLMR — multilingual transformer
                    pretrained on African language corpora</li>
                <li><strong>Hybrid:</strong> AfroXLMR embeddings concatenated with
                    a handcrafted linguistic feature vector</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ======================================================
    # RIGHT COLUMN
    # ======================================================
    with col2:

        st.markdown("""
        <div class="about-card">
            <h3>Linguistic Features (Hybrid Model)</h3>
            <ul>
                <li>Pidgin keyword detection via curated Naija lexicon</li>
                <li>Language switch-point counting between token sequences</li>
                <li>English token ratio per utterance</li>
                <li>Binary Pidgin presence flag</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="about-card">
            <h3>System Architecture</h3>
            <ul>
                <li>Frontend: Streamlit (Python)</li>
                <li>Inference: PyTorch + HuggingFace Transformers</li>
                <li>Feature extraction: Custom Python pipeline</li>
                <li>Export: Structured JSON analysis reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ======================================================
    # LIMITATIONS — FULL WIDTH
    # ======================================================
    st.markdown("""
    <div class="about-card">
        <h3>Limitations &amp; Future Work</h3>
        <ul>
            <li>Dataset exhibits class imbalance (3,575 Pidgin : 500 English) —
                per-class metrics should be prioritised over macro averages</li>
            <li>Pidgin lexicon coverage is finite; unseen slang and neologisms
                may be missed by the feature extractor</li>
            <li>Future work: larger balanced corpus, fine-grained switch-point
                labelling, multi-class extension (Yoruba, Igbo, Hausa mixing)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
