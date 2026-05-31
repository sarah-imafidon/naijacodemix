import streamlit as st
import sys
from pathlib import Path

# app.py lives at: project_root/frontend/app.py
# So:
#   Path(__file__).parent       = project_root/frontend/
#   Path(__file__).parent.parent = project_root/
FRONTEND_DIR = Path(__file__).parent
ROOT_DIR     = FRONTEND_DIR.parent

# Add both to path so all imports work
sys.path.append(str(ROOT_DIR))
sys.path.append(str(FRONTEND_DIR))

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
# LOAD CSS — absolute path, works everywhere
# =========================
def load_css():
    css_path = FRONTEND_DIR / "styles" / "main.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# JS fallback — styles the expand button directly in the live DOM
st.markdown("""
<script>
function styleExpandBtn() {
    const selectors = [
        '[data-testid="stSidebarExpandButton"]',
        '[data-testid="collapsedControl"]',
        'button[aria-label="Open sidebar"]',
        'button[aria-label="open sidebar"]'
    ];
    for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el) {
            el.style.setProperty('background-color', '#c0392b', 'important');
            el.style.setProperty('border-radius',    '0 8px 8px 0', 'important');
            el.style.setProperty('width',            '2.4rem', 'important');
            el.style.setProperty('height',           '3.2rem', 'important');
            el.style.setProperty('border',           '2px solid rgba(247,245,240,0.4)', 'important');
            el.style.setProperty('border-left',      'none', 'important');
            el.style.setProperty('box-shadow',       '4px 0 12px rgba(192,57,43,0.4)', 'important');
            const svg = el.querySelector('svg');
            if (svg) {
                svg.style.setProperty('stroke',       '#f7f5f0', 'important');
                svg.style.setProperty('stroke-width', '3', 'important');
                svg.style.setProperty('width',        '1.5rem', 'important');
                svg.style.setProperty('height',       '1.5rem', 'important');
            }
        }
    }
}
styleExpandBtn();
setTimeout(styleExpandBtn, 300);
setTimeout(styleExpandBtn, 1000);
</script>
""", unsafe_allow_html=True)

# =========================
# IMPORT PAGES — from frontend/pages/
# =========================
from frontend.pages.analyze import show_analyze_page
from frontend.pages.comparison import show_comparison_page
from frontend.pages.about import show_about_page
from frontend.pages.batch_analysis import show_batch_page
from frontend.pages.login import show_login_page

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
if "show_signin_toast" not in st.session_state:
    st.session_state.show_signin_toast = False

# Fire toast exactly once after sign-in
if st.session_state.show_signin_toast:
    st.toast(f"Welcome back, {st.session_state.full_name}! 👋", icon="✅")
    st.session_state.show_signin_toast = False

# =========================
# PROTECTED PAGES
# =========================
PROTECTED_PAGES = {"History", "Saved Analyses"}

if st.session_state.page in PROTECTED_PAGES and not st.session_state.logged_in:
    st.session_state.redirect_to = st.session_state.page
    st.session_state.page = "Sign In"

# =========================
# TOP-RIGHT AUTH BUTTON
# =========================
_, auth_col = st.columns([7, 1])
with auth_col:
    if st.session_state.logged_in:
        st.markdown(
            f'<div style="font-family:var(--mono);font-size:0.72rem;'
            f'color:var(--sidebar-bg);font-weight:600;text-align:right;'
            f'padding:0.35rem 0;letter-spacing:0.5px;white-space:nowrap;">'
            f'@{st.session_state.username}</div>',
            unsafe_allow_html=True
        )
    else:
        if st.button("→ Sign In", key="topbar_signin"):
            st.session_state.page = "Sign In"
            st.rerun()

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="eyebrow">Research Instrument</div>'
        '<h2>NaijaCodeMix<br>Detector</h2>'
        '<p>Nigerian Pidgin & English<br>Code-Switching Analysis</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.logged_in:
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.10);'
            f'border:1px solid rgba(255,255,255,0.15);border-radius:4px;'
            f'padding:0.75rem 1rem;margin-bottom:0.5rem;">'
            f'<div style="font-size:0.85rem;color:#ffffff;font-weight:500;">'
            f'{st.session_state.full_name}</div>'
            f'<div style="font-family:var(--mono);font-size:0.65rem;'
            f'color:rgba(255,255,255,0.5);margin-top:2px;">'
            f'@{st.session_state.username}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="sidebar-section">Navigation</div>',
        unsafe_allow_html=True
    )

    for num, label in [
        ("01", "Analyze Text"),
        ("02", "Batch Analysis"),
        ("03", "Model Comparison"),
        ("04", "About"),
    ]:
        is_active = st.session_state.page == label
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(f"{num}  {label}", key=f"nav_{label}"):
            st.session_state.page = label
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-section">Research Account</div>',
        unsafe_allow_html=True
    )

    if st.session_state.logged_in:
        for num, label in [("05", "History"), ("06", "Saved Analyses")]:
            is_active = st.session_state.page == label
            if is_active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            if st.button(f"{num}  {label}", key=f"nav_{label}"):
                st.session_state.page = label
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        if st.button("⏻  Sign Out", key="signout"):
            st.session_state.logged_in = False
            st.session_state.username  = None
            st.session_state.full_name = None
            if st.session_state.page in PROTECTED_PAGES:
                st.session_state.page = "Analyze Text"
            st.rerun()
    else:
        st.markdown(
            '<div style="font-family:var(--mono);font-size:0.75rem;'
            'color:rgba(255,255,255,0.4);padding:0.4rem 0.75rem;'
            'line-height:2.4;">'
            '🔒 History<br>🔒 Saved Analyses'
            '</div>',
            unsafe_allow_html=True
        )
        is_active = st.session_state.page == "Sign In"
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button("→  Sign In / Register", key="nav_signin"):
            st.session_state.page = "Sign In"
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

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
        from frontend.pages.history import show_history_page
        show_history_page()
    else:
        st.session_state.page = "Sign In"
        st.rerun()

elif page == "Saved Analyses":
    if st.session_state.logged_in:
        from frontend.pages.saved import show_saved_page
        show_saved_page()
    else:
        st.session_state.page = "Sign In"
        st.rerun()