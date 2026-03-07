import tempfile
from pathlib import Path

import streamlit as st

from ghunt.modules import spiderdal as spiderdal_module
from ghunt.webui import load_json, render_result, run_with_capture

st.title("Spiderdal")
st.caption("Run `ghunt spiderdal` from the web UI.")

url = st.text_input("Website URL or domain", placeholder="https://cash.app")
package = st.text_input("Android package name", placeholder="com.squareup.cash")
fingerprint = st.text_input(
    "Certificate fingerprint (SHA256)",
    placeholder="21:A7:46:75:96:C1:68:65:0F:D7:B6:31:B6:54:22:EB:56:3E:1D:21:AF:F2:2D:DE:73:89:BA:0D:5D:73:87:48",
)
strict = st.checkbox("Strict URL mode", value=False)

if st.button("Run spiderdal"):
    if not url.strip() and not (package.strip() and fingerprint.strip()):
        st.error("Provide a URL/domain, or both package name and fingerprint.")
        st.stop()

    if bool(package.strip()) != bool(fingerprint.strip()):
        st.error("Package name and fingerprint must be provided together.")
        st.stop()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        json_path = Path(tmp.name)

    output, error, _ = run_with_capture(
        spiderdal_module.main(
            url.strip() or None,
            package.strip() or None,
            fingerprint.strip() or None,
            strict,
            json_path,
        )
    )
    payload = load_json(json_path)
    json_path.unlink(missing_ok=True)

    render_result(output, error, payload)
