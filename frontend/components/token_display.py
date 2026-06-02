import streamlit as st


def display_tokens(text, pidgin_keywords, english_words):

    pills_html = '<div class="tokens-wrap">'

    for word in text.split():
        clean = word.lower().strip(".,!?;:\"'")
        if clean in pidgin_keywords:
            pills_html += f'<span class="token token-pidgin">{word}</span> '
        elif clean in english_words:
            pills_html += f'<span class="token token-english">{word}</span> '
        else:
            pills_html += f'<span class="token token-neutral">{word}</span> '

    pills_html += '</div>'

    html_content = (
        '<div class="card">'
        '<div class="token-legend">'
        '<div class="legend-item"><div class="legend-dot dot-pidgin"></div>Pidgin token</div>'
        '<div class="legend-item"><div class="legend-dot dot-english"></div>English token</div>'
        '<div class="legend-item"><div class="legend-dot dot-neutral"></div>Unclassified</div>'
        '</div>'
        f'{pills_html}'
        '</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)