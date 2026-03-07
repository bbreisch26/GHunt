import tempfile
from pathlib import Path

import streamlit as st

from ghunt.modules import drive as drive_module
from ghunt.webui import load_json, render_result, run_with_capture

st.title("Drive")
st.caption("Run `ghunt drive` from the web UI.")

file_id = st.text_input(
    "File or folder ID",
    placeholder="1N__vVu4c9fCt4EHxfthUNzVOs_tp8l6tHcMBnpOZv_M",
)

if st.button("Run drive lookup"):
    if not file_id.strip():
        st.error("Provide a file or folder ID.")
    else:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            json_path = Path(tmp.name)

        output, error, _ = run_with_capture(drive_module.hunt(None, file_id.strip(), json_path))
        payload = load_json(json_path)
        json_path.unlink(missing_ok=True)

        render_result(output, error, payload)
