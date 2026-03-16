import streamlit as st
import streamlit.components.v1 as components

from ghunt.webui import (
    clear_saved_session,
    login_with_companion_payload,
    login_with_master_token,
    login_with_oauth_token,
    render_result,
    run_with_capture,
    verify_saved_session,
)

st.set_page_config(page_title="GHunt Web UI", page_icon="🔎", layout="wide")

COMPANION_REPO_URL = "https://github.com/mxrch/ghunt_companion"
COMPANION_CHROME_STORE_URL = "https://chrome.google.com/webstore/detail/ghunt-companion/dpdcofblfbmmnikcbmmiakkclocadjab"
COMPANION_FIREFOX_STORE_URL = "https://addons.mozilla.org/en-US/firefox/addon/ghunt-companion/"
COMPANION_CHROME_EXTENSION_URL = "chrome-extension://dpdcofblfbmmnikcbmmiakkclocadjab/popup.html"

def login_page() -> None:
    st.title("Login")
    st.caption("Manage GHunt credentials.")

    def _check_status() -> tuple[str, BaseException | None]:
        output, error, _ = run_with_capture(verify_saved_session())
        return output, error

    if "session_status" not in st.session_state:
        with st.spinner("Checking existing session..."):
            output, error = _check_status()
        st.session_state.session_status = {"output": output, "error": error}

    status = st.session_state.session_status
    if status["error"] is None:
        st.success("Already logged in with a valid stored session.")
    else:
        st.warning("No valid stored session detected.")

    if status["output"].strip():
        with st.expander("Status check details"):
            st.code(status["output"])

    if st.button("Re-check session status"):
        with st.spinner("Checking existing session..."):
            output, error = _check_status()
        st.session_state.session_status = {"output": output, "error": error}
        st.rerun()

    st.divider()

    st.subheader("GHunt Companion")
    st.caption("Open the extension directly when possible, or install/open via store links.")

    col1, col2, col3 = st.columns(3)
    col1.link_button("Open Companion Repo", COMPANION_REPO_URL, use_container_width=True)
    col2.link_button("Chrome Store", COMPANION_CHROME_STORE_URL, use_container_width=True)
    col3.link_button("Firefox Add-ons", COMPANION_FIREFOX_STORE_URL, use_container_width=True)

    components.html(
        f"""
        <div style="display:flex;gap:0.5rem;align-items:center;">
          <button id="open-ghunt-companion" style="padding:0.4rem 0.7rem;cursor:pointer;">
            Open Companion Extension
          </button>
          <span style="font-size:0.9rem;color:#666;">
            If extension opening is blocked, store tabs will open instead.
          </span>
        </div>
        <script>
          const openTargets = [
            "{COMPANION_CHROME_EXTENSION_URL}",
            "{COMPANION_CHROME_STORE_URL}",
            "{COMPANION_FIREFOX_STORE_URL}",
          ];
          document.getElementById("open-ghunt-companion").addEventListener("click", () => {{
            for (const url of openTargets) {{
              window.open(url, "_blank");
            }}
          }});
        </script>
        """,
        height=60,
    )

    st.divider()

    st.subheader("Generate Session From OAuth Token")
    oauth_token = st.text_input("OAuth token", type="password", placeholder="oauth2_4/...")
    if st.button("Generate from OAuth token"):
        if not oauth_token.strip():
            st.error("Provide an OAuth token.")
        else:
            output, error, data = run_with_capture(login_with_oauth_token(oauth_token.strip()))
            render_result(output, error)
            if error is None:
                st.session_state.session_status = {"output": "[+] Authenticated", "error": None}
            if error is None and data:
                st.subheader("Connected Account")
                st.json(data)

    st.divider()

    st.subheader("Generate Session From Companion Base64 Payload")
    companion_payload = st.text_area(
        "Companion payload",
        placeholder="Paste base64 payload produced by GHunt Companion",
        height=120,
    )
    if st.button("Generate from companion payload"):
        if not companion_payload.strip():
            st.error("Provide the companion base64 payload.")
        else:
            output, error, data = run_with_capture(login_with_companion_payload(companion_payload.strip()))
            render_result(output, error)
            if error is None:
                st.session_state.session_status = {"output": "[+] Authenticated", "error": None}
            if error is None and data:
                st.subheader("Connected Account")
                st.json(data)

    st.divider()

    st.subheader("Generate Session From Master Token")
    master_token = st.text_input("Master token", type="password", placeholder="aas_et/...")
    if st.button("Generate from master token"):
        if not master_token.strip():
            st.error("Provide a master token.")
        else:
            output, error, _ = run_with_capture(login_with_master_token(master_token.strip()))
            render_result(output, error)
            if error is None:
                st.session_state.session_status = {"output": "[+] Authenticated", "error": None}

    st.divider()

    st.subheader("Clean")
    if st.button("Delete saved credentials"):
        message = clear_saved_session()
        st.session_state.session_status = {"output": message, "error": RuntimeError("No valid session")}
        st.info(message)


pages = [
    st.Page(login_page, title="Login", icon=":material/login:"),
    st.Page("pages/2_Email.py", title="Email", icon=":material/email:"),
    st.Page("pages/3_Gaia.py", title="Gaia", icon=":material/badge:"),
    st.Page("pages/4_Drive.py", title="Drive", icon=":material/folder:"),
    st.Page("pages/5_Geolocate.py", title="Geolocate", icon=":material/location_on:"),
    st.Page("pages/6_Spiderdal.py", title="Spiderdal", icon=":material/hub:"),
    st.Page("pages/2_Utilities.py", title="Utilities", icon=":material/build:"),
]

navigation = st.navigation(pages, position="top")
navigation.run()
