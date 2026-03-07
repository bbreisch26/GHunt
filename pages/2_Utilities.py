import streamlit as st

from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.helpers import auth
from ghunt.helpers.gmail import is_email_registered
from ghunt.helpers.utils import get_httpx_client
from ghunt.webui import run_with_capture


async def _check_google_email_exists(email: str) -> bool:
    as_client = get_httpx_client()
    try:
        return await is_email_registered(as_client, email)
    finally:
        await as_client.aclose()


async def _name_lookup(email: str) -> dict[str, object]:
    as_client = get_httpx_client()
    try:
        creds = await auth.load_and_auth(as_client)
        people_api = PeoplePaHttp(creds)
        found, person = await people_api.people_lookup(as_client, email, params_template="just_name")
    finally:
        await as_client.aclose()

    profile_name = person.names.get("PROFILE")
    return {
        "found": found,
        "gaia_id": person.personId,
        "profile_container_present": "PROFILE" in person.names,
        "name": profile_name.fullname if profile_name else "",
        "name_containers": list(person.names.keys()),
    }


st.title("Utilities")
st.caption("Quick GHunt utility tools.")

st.subheader("Name Lookup")
st.caption("Requires a valid GHunt login session.")
email_for_name = st.text_input("Email for name lookup", placeholder="target@gmail.com")
if st.button("Lookup name"):
    if not email_for_name.strip():
        st.error("Provide an email address.")
    else:
        output, error, result = run_with_capture(_name_lookup(email_for_name.strip()))
        if error is not None:
            st.error(f"Execution failed: {error}")
        else:
            if not result["found"]:
                st.warning("No person record found for this email.")
            else:
                st.success("Lookup completed.")
            st.json(result)

        if output.strip():
            with st.expander("Console output"):
                st.code(output)
