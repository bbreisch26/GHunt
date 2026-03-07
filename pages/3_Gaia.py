import tempfile
from pathlib import Path

import streamlit as st

from ghunt.modules import gaia as gaia_module
from ghunt.webui import load_json, render_profile_card, render_result, run_with_capture

st.title("Gaia")
st.caption("Run `ghunt gaia` from the web UI.")

gaia_id = st.text_input("Gaia ID", placeholder="123456789012345678901")

if st.button("Run gaia lookup"):
    if not gaia_id.strip():
        st.error("Provide a Gaia ID.")
    else:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            json_path = Path(tmp.name)

        output, error, _ = run_with_capture(gaia_module.hunt(None, gaia_id.strip(), json_path))
        payload = load_json(json_path)
        json_path.unlink(missing_ok=True)

        render_result(output, error, payload)
        if error is None and isinstance(payload, dict):
            render_profile_card(payload)
