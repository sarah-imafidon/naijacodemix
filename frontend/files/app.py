import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NaijaCodeMix — Research Tool",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# LOAD CSS
# =========================
def load_css():
    with open("frontend/styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =========================
# IMPORT PAGES
# =========================
from pages.analyze import show_analyze_page
from pages.comparison import show_comparison_page
from pages.about import show_about_page
from pages.batch_analysis import show_batch_page
from pages.login import show_login_page

# =========================
# SESSION STATE BOOTSTRAP
# =========================
if "page"       not in st.session_state:
    st.session_state.page       = "Analyze Text"
if "logged_in"  not in st.session_state:
    st.session_state.logged_in  = False
if "username"   not in st.session_state:
    st.session_state.username   = None
if "full_name"  not in st.session_state:
    st.session_state.full_name  = None

# =========================
# ROUTE GUARDS
# =========================
# Pages that require the user to be logged in
PROTECTED_PAGES = {"History", "Saved Analyses"}

# If the user tries to visit a protected page while logged out,
# remember where they wanted to go and send them to login.
if st.session_state.page in PROTECTED_PAGES and not st.session_state.logged_in:
    st.session_state.redirect_to = st.session_state.page
    st.session_state.page = "Sign In"

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    # ── Brand ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="eyebrow">Research Instrument</div>'
        '<h2>NaijaCodeMix<br>Detector</h2>'
        '<p>Nigerian Pidgin & English<br>Code-Switching Analysis</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── User greeting (when logged in) ───────────────────────────────────────
    if st.session_state.logged_in:
        st.markdown(
            f'<div style="'
            f'background:rgba(255,255,255,0.10);'
            f'border:1px solid rgba(255,255,255,0.15);'
            f'border-radius:4px;'
            f'padding:0.75rem 1rem;'
            f'margin-bottom:0.5rem;">'
            f'<div style="font-size:0.85rem;color:#ffffff;font-weight:500;">'
            f'{st.session_state.full_name}</div>'
            f'<div style="font-family:var(--mono);font-size:0.65rem;'
            f'color:rgba(255,255,255,0.5);margin-top:2px;">'
            f'@{st.session_state.username}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-section">Navigation</div>',
        unsafe_allow_html=True
    )

    # Public pages — always visible
    public_nav = [
        ("01", "Analyze Text"),
        ("02", "Batch Analysis"),
        ("03", "Model Comparison"),
        ("04", "About"),
    ]

    for num, label in public_nav:
        is_active = st.session_state.page == label
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(f"{num}  {label}", key=f"nav_{label}"):
            st.session_state.page = label
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    # Research account section
    st.markdown(
        '<div class="sidebar-section">Research Account</div>',
        unsafe_allow_html=True
    )

    if st.session_state.logged_in:
        # Protected pages — visible when logged in
        protected_nav = [
            ("05", "History"),
            ("06", "Saved Analyses"),
        ]
        for num, label in protected_nav:
            is_active = st.session_state.page == label
            if is_active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            if st.button(f"{num}  {label}", key=f"nav_{label}"):
                st.session_state.page = label
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        # Sign out button
        st.markdown("<div style='margin-top:0.5rem'>", unsafe_allow_html=True)
        if st.button("⏻  Sign Out", key="signout"):
            st.session_state.logged_in = False
            st.session_state.username  = None
            st.session_state.full_name = None
            if st.session_state.page in PROTECTED_PAGES:
                st.session_state.page = "Analyze Text"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Show lock icons for protected pages
        st.markdown(
            '<div style="font-family:var(--mono);font-size:0.75rem;'
            'color:rgba(255,255,255,0.4);padding:0.4rem 0.75rem;'
            'line-height:2.2;">'
            '🔒 History<br>'
            '🔒 Saved Analyses'
            '</div>',
            unsafe_allow_html=True
        )
        # Sign in button
        is_active = st.session_state.page == "Sign In"
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button("→  Sign In / Register", key="nav_signin"):
            st.session_state.page = "Sign In"
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    # ── System status ─────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-section">System Status</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;'
        'line-height:2.2;color:rgba(247,245,240,0.5);">'
        '● AfroXLMR Baseline<br>'
        '● Hybrid Model Active<br>'
        '● Feature Engine Ready'
        '</div>',
        unsafe_allow_html=True
    )

# =========================
# ROUTING
# =========================
page = st.session_state.page

if page == "Analyze Text":
    show_analyze_page()

elif page == "Batch Analysis":
    show_batch_page()

elif page == "Model Comparison":
    show_comparison_page()

elif page == "About":
    show_about_page()

elif page == "Sign In":
    show_login_page()

elif page == "History":
    if st.session_state.logged_in:
        from pages.history import show_history_page
        show_history_page()
    else:
        st.session_state.page = "Sign In"
        st.rerun()

elif page == "Saved Analyses":
    if st.session_state.logged_in:
        from pages.saved import show_saved_page
        show_saved_page()
    else:
        st.session_state.page = "Sign In"
        st.rerun()
