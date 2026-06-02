import streamlit as st


def explain_prediction(features):

    explanations = []

    # ==========================================
    # PIDGIN TOKENS
    # ==========================================
    if features["contains_pidgin"]:

        explanations.append(
            (
                "Pidgin vocabulary identified",
                f"The text contains "
                f"<strong>{features['pidgin_count']} "
                f"Pidgin token(s)</strong>, suggesting "
                f"Nigerian Pidgin usage."
            )
        )

    # ==========================================
    # SWITCH POINTS
    # ==========================================
    if features["switch_count"] > 0:

        explanations.append(
            (
                "Language switching detected",
                f"<strong>{features['switch_count']} "
                f"switch point(s)</strong> identified "
                f"between English and Pidgin tokens."
            )
        )

    # ==========================================
    # ENGLISH RATIO
    # ==========================================
    if features["english_ratio"] > 0.5:

        explanations.append(
            (
                "High English token proportion",
                f"The text contains "
                f"<strong>{round(features['english_ratio'] * 100)}%"
                f"</strong> English tokens."
            )
        )

    # ==========================================
    # FALLBACK
    # ==========================================
    if not explanations:

        explanations.append(
            (
                "No strong code-mixing indicators",
                "The linguistic features do not strongly "
                "suggest code-mixing."
            )
        )

    # ==========================================
    # BUILD HTML
    # ==========================================
    findings_html = ""

    for i, (title, detail) in enumerate(explanations):

        findings_html += (
            '<div class="finding">'
            f'<div class="finding-num">F{i+1:02d}</div>'
            '<div class="finding-text">'
            f'<strong>{title}.</strong> {detail}'
            '</div>'
            '</div>'
        )

    st.markdown(
        f'<div class="card">{findings_html}</div>',
        unsafe_allow_html=True
    )