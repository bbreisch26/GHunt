import json
import tempfile
from pathlib import Path

import streamlit as st

from ghunt.modules import geolocate as geolocate_module
from ghunt.webui import load_json, render_result, run_with_capture

st.title("Geolocate")
st.caption("Run `ghunt geolocate` from the web UI.")

mode = st.radio("Input mode", ("BSSID", "Raw request JSON"))

bssid = ""
raw_request = ""
if mode == "BSSID":
    bssid = st.text_input("BSSID", placeholder="30:86:2d:c4:29:d0")
else:
    raw_request = st.text_area(
        "Raw geolocation request JSON",
        placeholder='{"wifiAccessPoints": [{"macAddress": "30:86:2d:c4:29:d0"}]}',
        height=160,
    )

if st.button("Run geolocate"):
    input_file: Path | None = None
    if mode == "BSSID":
        if not bssid.strip():
            st.error("Provide a BSSID.")
            st.stop()
    else:
        if not raw_request.strip():
            st.error("Provide a raw JSON request.")
            st.stop()
        try:
            parsed = json.loads(raw_request)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
            st.stop()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as tmp:
            json.dump(parsed, tmp)
            input_file = Path(tmp.name)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        json_path = Path(tmp.name)

    output, error, _ = run_with_capture(geolocate_module.main(None, bssid.strip() if bssid else None, input_file, json_path))
    payload = load_json(json_path)

    if input_file:
        input_file.unlink(missing_ok=True)
    json_path.unlink(missing_ok=True)

    render_result(output, error, payload)
