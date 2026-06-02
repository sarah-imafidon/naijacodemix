import streamlit as st

def render_sidebar():

    with st.sidebar:

        st.markdown("""
        <div class="sidebar-brand">
            <div class="eyebrow">Research Instrument</div>
            <h2>NaijaCodeMix<br>Detector</h2>
            <p>Nigerian Pidgin & English<br>Code-Switching Analysis</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="sidebar-section">Navigation</div>',
            unsafe_allow_html=True
        )

        pages = [
            ("01", "Analyze Text"),
            ("02", "Model Comparison"),
            ("03", "About")
        ]

        for num, label in pages:

            is_active = st.session_state.page == label

            if is_active:
                st.markdown(
                    '<div class="nav-active">',
                    unsafe_allow_html=True
                )

            if st.button(f"{num}  {label}", key=f"nav_{label}"):

                st.session_state.page = label
                st.rerun()

            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="sidebar-section">System Status</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div style="
            font-family:monospace;
            font-size:0.7rem;
            line-height:2;
            color:#666688;
        ">
            ● AfroXLMR Baseline<br>
            ● Hybrid Model Active<br>
            ● Feature Engine Ready
        </div>
        """, unsafe_allow_html=True)