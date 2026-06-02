import streamlit as st

def prediction_card(model_name, prediction, confidence, color_class, description, fill_class="conf-fill-red"):

    html_content = (
        '<div class="card">'
        f'<div class="card-eyebrow">{model_name}</div>'
        f'<div class="prediction-verdict {color_class}">{prediction}</div>'
        '<div class="conf-wrap">'
        '<div class="conf-row">'
        '<span class="conf-name">Confidence</span>'
        f'<span class="conf-pct">{confidence}%</span>'
        '</div>'
        '<div class="conf-track">'
        f'<div class="{fill_class}" style="width:{confidence}%"></div>'
        '</div>'
        '</div>'
        '<div style="font-size:0.78rem; color:var(--muted); font-family:var(--mono);">'
        f'{description}'
        '</div>'
        '</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)