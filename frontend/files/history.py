"""
frontend/pages/history.py
Analysis History page — shows the last 50 analyses run by the logged-in user.
"""

import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from auth import get_user_data, save_bookmark


def _section_rule(label: str):
    st.markdown(
        f'<div class="section-rule">'
        f'<span class="section-rule-label">{label}</span>'
        f'<span class="section-rule-line"></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def show_history_page():

    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">Research Record</div>'
        '<h1>Analysis History</h1>'
        '<p>Every analysis you run is automatically saved here. '
        'The last 50 sessions are retained.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    user_data = get_user_data(st.session_state.username)
    history   = user_data.get("history", []) if user_data else []

    _section_rule(f"Recent Analyses — {len(history)} record(s)")

    if not history:
        st.markdown(
            '<div class="empty-state">'
            'No analyses yet. Run your first analysis on the '
            '<strong>Analyze Text</strong> page — it will appear here automatically.'
            '</div>',
            unsafe_allow_html=True
        )
        return

    for entry in history:
        h_pred     = entry.get("hybrid",   {}).get("prediction", "—")
        b_pred     = entry.get("baseline", {}).get("prediction", "—")
        h_conf     = entry.get("hybrid",   {}).get("confidence", "—")
        badge_cls  = "hbadge-cm" if h_pred == "Code-Mixed" else "hbadge-eng"
        snippet    = entry.get("input_text", "")
        snippet    = snippet[:120] + ("…" if len(snippet) > 120 else "")
        agree_txt  = "✓ Models agree" if entry.get("models_agree") else "⚠ Models disagree"
        pidgin_ct  = entry.get("features", {}).get("pidgin_count", 0)
        switch_ct  = entry.get("features", {}).get("switch_count", 0)
        entry_id   = entry.get("id", "")

        st.markdown(
            f'<div class="history-card">'
            f'<div class="history-meta">'
            f'<span class="history-ts">{entry.get("timestamp", "")}</span>'
            f'<span class="hbadge {badge_cls}">{h_pred}</span>'
            f'</div>'
            f'<div class="history-text">{snippet}</div>'
            f'<div class="history-badges">'
            f'<span class="hbadge">Baseline: {b_pred}</span>'
            f'<span class="hbadge">Hybrid confidence: {h_conf}</span>'
            f'<span class="hbadge">{pidgin_ct} pidgin · {switch_ct} switches</span>'
            f'<span class="hbadge">{agree_txt}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Save to bookmarks button per entry
        if st.button("★  Save this analysis", key=f"save_hist_{entry_id}"):
            analysis = {
                "input_text": entry.get("input_text", ""),
                "baseline":   entry.get("baseline",   {}),
                "hybrid":     entry.get("hybrid",     {}),
                "features":   entry.get("features",   {}),
                "models_agree": entry.get("models_agree", False),
            }
            ok, msg = save_bookmark(st.session_state.username, analysis)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
