import streamlit as st
import json
from datetime import datetime


def export_results(report):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = (
        '<div class="export-box">'
        '<div class="export-info">'
        f'Analysis complete — <strong>{timestamp}</strong> <br>'
        'Download a structured JSON report.'
        '</div>'
        '</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)

    st.download_button(
        "Download Report (JSON)",
        json.dumps(report, indent=2),
        file_name=f"codemix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )