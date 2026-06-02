"""
frontend/pages/saved.py
Saved Analyses page — shows bookmarked analyses for the logged-in user.
"""

import streamlit as st
import json
from datetime import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent  # frontend/pages/ -> frontend/ -> project root
sys.path.append(str(ROOT_DIR))

from auth import get_user_data, delete_bookmark


def _section_rule(label: str):
    st.markdown(
        f'<div class="section-rule">'
        f'<span class="section-rule-label">{label}</span>'
        f'<span class="section-rule-line"></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def show_saved_page():

    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">Research Archive</div>'
        '<h1>Saved Analyses</h1>'
        '<p>Analyses you have bookmarked for reference. '
        'You can save up to 20 analyses.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    user_data = get_user_data(st.session_state.username)
    saved     = user_data.get("saved", []) if user_data else []

    _section_rule(f"Saved — {len(saved)} / 20")

    if not saved:
        st.markdown(
            '<div class="empty-state">'
            'No saved analyses yet.<br>'
            'After running an analysis, click <strong>★ Save Analysis</strong> '
            'or bookmark one from your <strong>History</strong> page.'
            '</div>',
            unsafe_allow_html=True
        )
        return

    for entry in saved:
        h_pred    = entry.get("hybrid",   {}).get("prediction", "—")
        b_pred    = entry.get("baseline", {}).get("prediction", "—")
        h_conf    = entry.get("hybrid",   {}).get("confidence", "—")
        badge_cls = "hbadge-cm" if h_pred == "Code-Mixed" else "hbadge-eng"
        snippet   = entry.get("input_text", "")
        snippet   = snippet[:120] + ("…" if len(snippet) > 120 else "")
        agree_txt = "✓ Models agree" if entry.get("models_agree") else "⚠ Models disagree"
        pidgin_ct = entry.get("features", {}).get("pidgin_count", 0)
        switch_ct = entry.get("features", {}).get("switch_count", 0)
        entry_id  = entry.get("id", "")

        st.markdown(
            f'<div class="history-card">'
            f'<div class="history-meta">'
            f'<span class="history-ts">Saved {entry.get("saved_at", "")}</span>'
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

        # Export + Delete per entry
        report_json = json.dumps(
            {**entry, "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            indent=2
        )

        col_dl, col_del, _ = st.columns([1, 1, 4])

        with col_dl:
            st.download_button(
                label="↓ Export JSON",
                data=report_json,
                file_name=f"saved_{entry_id}.json",
                mime="application/json",
                key=f"dl_{entry_id}"
            )

        with col_del:
            if st.button("✕ Delete", key=f"del_{entry_id}"):
                delete_bookmark(st.session_state.username, entry_id)
                st.rerun()