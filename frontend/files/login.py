"""
frontend/pages/login.py
Sign In / Register page for NaijaCodeMix.
Styled to match the red sidebar + cream main app theme.
"""

import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from auth import register_user, login_user


def show_login_page():

    # ── Inject login-specific styles ─────────────────────────────────────────
    st.markdown("""
    <style>
    .auth-outer {
        display: flex;
        justify-content: center;
        padding: 3rem 1rem 2rem;
    }

    .auth-box {
        width: 100%;
        max-width: 440px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-top: 4px solid var(--accent);
        border-radius: 4px;
        padding: 2.5rem 2.5rem 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }

    .auth-logo {
        text-align: center;
        margin-bottom: 2rem;
    }

    .auth-logo .auth-eyebrow {
        font-family: var(--mono);
        font-size: 0.6rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 0.5rem;
        display: block;
    }

    .auth-logo h1 {
        font-family: var(--serif);
        font-size: 1.9rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 0.3rem;
        letter-spacing: -0.5px;
    }

    .auth-logo p {
        font-size: 0.82rem;
        color: var(--muted);
        margin: 0;
        font-style: italic;
    }

    .auth-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }

    .auth-tab-label {
        font-family: var(--mono);
        font-size: 0.65rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 1.25rem;
        display: block;
    }

    .auth-footer {
        text-align: center;
        font-size: 0.8rem;
        color: var(--muted);
        margin-top: 1.25rem;
        font-style: italic;
    }

    .auth-public-note {
        text-align: center;
        margin-top: 1.5rem;
        padding: 1rem 1.25rem;
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 3px;
        font-size: 0.82rem;
        color: var(--text-mid);
        line-height: 1.6;
    }

    .auth-public-note strong {
        color: var(--text);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Layout — centred narrow column ───────────────────────────────────────
    _, center, _ = st.columns([1, 1.4, 1])

    with center:

        # Logo / branding
        st.markdown("""
        <div class="auth-logo">
            <span class="auth-eyebrow">Research Instrument</span>
            <h1>NaijaCodeMix</h1>
            <p>Nigerian Pidgin–English Code-Switching Analysis</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Tab toggle ────────────────────────────────────────────────────────
        if "auth_tab" not in st.session_state:
            st.session_state.auth_tab = "signin"

        tab_col1, tab_col2 = st.columns(2)

        with tab_col1:
            if st.button(
                "Sign In",
                key="tab_signin",
                use_container_width=True,
                type="primary" if st.session_state.auth_tab == "signin" else "secondary"
            ):
                st.session_state.auth_tab = "signin"
                st.rerun()

        with tab_col2:
            if st.button(
                "Create Account",
                key="tab_register",
                use_container_width=True,
                type="primary" if st.session_state.auth_tab == "register" else "secondary"
            ):
                st.session_state.auth_tab = "register"
                st.rerun()

        st.markdown('<hr class="auth-divider">', unsafe_allow_html=True)

        # ── SIGN IN ───────────────────────────────────────────────────────────
        if st.session_state.auth_tab == "signin":

            st.markdown(
                '<span class="auth-tab-label">Sign in to your account</span>',
                unsafe_allow_html=True
            )

            si_username = st.text_input(
                "Username",
                key="si_username",
                placeholder="your username"
            )
            si_password = st.text_input(
                "Password",
                type="password",
                key="si_password",
                placeholder="••••••••"
            )

            if st.button("Sign In →", key="do_signin", use_container_width=True):
                if si_username.strip() and si_password:
                    success, msg, user_data = login_user(si_username, si_password)
                    if success:
                        st.session_state.logged_in  = True
                        st.session_state.username   = si_username.strip().lower()
                        st.session_state.full_name  = user_data["full_name"]
                        # Redirect to wherever they were trying to go
                        if "redirect_to" in st.session_state:
                            st.session_state.page = st.session_state.pop("redirect_to")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in both fields.")

            st.markdown(
                '<p class="auth-footer">No account yet? Click <strong>Create Account</strong> above.</p>',
                unsafe_allow_html=True
            )

        # ── REGISTER ──────────────────────────────────────────────────────────
        else:

            st.markdown(
                '<span class="auth-tab-label">Create a researcher account</span>',
                unsafe_allow_html=True
            )

            rg_name  = st.text_input(
                "Full Name",
                key="rg_name",
                placeholder="e.g. Chidi Okonkwo"
            )
            rg_user  = st.text_input(
                "Username",
                key="rg_user",
                placeholder="min 3 characters, lowercase"
            )
            rg_pass  = st.text_input(
                "Password",
                type="password",
                key="rg_pass",
                placeholder="min 6 characters"
            )
            rg_pass2 = st.text_input(
                "Confirm Password",
                type="password",
                key="rg_pass2",
                placeholder="repeat password"
            )

            if st.button("Create Account →", key="do_register", use_container_width=True):
                if rg_pass != rg_pass2:
                    st.error("Passwords do not match.")
                else:
                    success, msg = register_user(rg_name, rg_user, rg_pass)
                    if success:
                        st.success(f"{msg} You can now sign in.")
                        st.session_state.auth_tab = "signin"
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown(
                '<p class="auth-footer">Already have an account? Click <strong>Sign In</strong> above.</p>',
                unsafe_allow_html=True
            )

        # ── Public access note ────────────────────────────────────────────────
        st.markdown("""
        <div class="auth-public-note">
            <strong>No account needed</strong> to use the analyser.<br>
            Sign in only to access <strong>Analysis History</strong>
            and <strong>Saved Analyses</strong>.
        </div>
        """, unsafe_allow_html=True)
