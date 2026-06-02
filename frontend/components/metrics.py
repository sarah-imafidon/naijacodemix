import streamlit as st


def metrics_row(features):

    html_content = (
        '<div class="metric-row">'
        '<div class="metric-cell">'
        f'<div class="metric-val highlight">{features["pidgin_count"]}</div>'
        '<div class="metric-lbl">Pidgin Tokens</div>'
        '</div>'
        '<div class="metric-cell">'
        f'<div class="metric-val">{features["switch_count"]}</div>'
        '<div class="metric-lbl">Switch Points</div>'
        '</div>'
        '<div class="metric-cell">'
        f'<div class="metric-val">{round(features["english_ratio"], 2)}</div>'
        '<div class="metric-lbl">English Ratio</div>'
        '</div>'
        '<div class="metric-cell">'
        f'<div class="metric-val">{"Yes" if features["contains_pidgin"] else "No"}</div>'
        '<div class="metric-lbl">Pidgin Present</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)