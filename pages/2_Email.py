import tempfile
from pathlib import Path

import streamlit as st

from ghunt.modules import email as email_module
from ghunt.webui import load_json, render_profile_card, render_result, run_with_capture

st.title("Email")
st.caption("Run `ghunt email` from the web UI.")

email_address = st.text_input("Email address", placeholder="target@gmail.com")

if st.button("Run email lookup"):
    if not email_address.strip():
        st.error("Provide an email address.")
    else:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            json_path = Path(tmp.name)

        output, error, _ = run_with_capture(email_module.hunt(None, email_address.strip(), json_path))
        payload = load_json(json_path)
        json_path.unlink(missing_ok=True)

        render_result(output, error, payload)
        if error is None and isinstance(payload, dict):
            render_profile_card(payload, input_email=email_address.strip())
