from __future__ import annotations

from typing import Any

import streamlit as st
import streamlit.components.v1 as components


def _dget(data: dict[str, Any], *path: str) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_container(payload: dict[str, Any]) -> dict[str, Any] | None:
    if "PROFILE_CONTAINER" in payload and isinstance(payload["PROFILE_CONTAINER"], dict):
        return payload["PROFILE_CONTAINER"]

    for key, value in payload.items():
        if key.endswith("_CONTAINER") and isinstance(value, dict):
            return value
    return None


def render_profile_card(payload: dict[str, Any], input_email: str | None = None) -> None:
    container = _first_container(payload)
    if not container:
        st.info("No profile container found in JSON output.")
        return

    profile = container.get("profile") or {}
    maps = container.get("maps") or {}
    play_games = container.get("play_games") or {}
    calendar = container.get("calendar") or {}

    gaia_id = profile.get("personId")
    full_name = _dget(profile, "names", "PROFILE", "fullname")
    email = _dget(profile, "emails", "PROFILE", "value") or input_email
    profile_photo = _dget(profile, "profilePhotos", "PROFILE") or {}
    cover_photo = _dget(profile, "coverPhotos", "PROFILE") or {}
    profile_photo_url = profile_photo.get("url")
    cover_photo_url = cover_photo.get("url")

    last_updated = _dget(profile, "sourceIds", "PROFILE", "lastUpdated")
    user_types = _dget(profile, "profileInfos", "PROFILE", "userTypes") or []
    apps = _dget(profile, "inAppReachability", "PROFILE", "apps") or []

    entity_type = _dget(profile, "extendedData", "dynamiteData", "entityType")
    customer_id = _dget(profile, "extendedData", "dynamiteData", "customerId")
    is_enterprise = _dget(profile, "extendedData", "gplusData", "isEntrepriseUser")

    maps_stats = maps.get("stats") or {}
    maps_reviews = maps.get("reviews") or []
    maps_photos = maps.get("photos") or []

    st.subheader("Baseball Card")
    st.markdown(
        """
        <style>
        .ghunt-card {
            border: 2px solid #0f172a;
            border-radius: 16px;
            padding: 1rem;
            background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        }
        .ghunt-kv {
            margin: 0.2rem 0;
            font-size: 0.95rem;
        }
        .ghunt-title {
            margin: 0 0 0.5rem 0;
            font-size: 1.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 2])

    with left:
        if profile_photo_url and not profile_photo.get("isDefault"):
            st.image(profile_photo_url, caption="Profile photo", use_container_width=True)
        elif profile_photo_url:
            st.image(profile_photo_url, caption="Default profile photo", use_container_width=True)
        else:
            st.info("No profile photo available.")

    with right:
        st.markdown('<div class="ghunt-card">', unsafe_allow_html=True)
        st.markdown(f'<h3 class="ghunt-title">{full_name or "Unknown Name"}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="ghunt-kv"><b>Email:</b> {email or "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ghunt-kv"><b>Gaia ID:</b> {gaia_id or "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ghunt-kv"><b>Last profile edit:</b> {last_updated or "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ghunt-kv"><b>Entity Type:</b> {entity_type or "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ghunt-kv"><b>Customer ID:</b> {customer_id or "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ghunt-kv"><b>Enterprise User:</b> {is_enterprise if is_enterprise is not None else "-"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if cover_photo_url and not cover_photo.get("isDefault"):
        st.image(cover_photo_url, caption="Cover photo", use_container_width=True)

    a, b, c, d = st.columns(4)
    a.metric("Maps Reviews", len(maps_reviews))
    b.metric("Maps Photos", len(maps_photos))
    c.metric("Apps Reachable", len(apps))
    d.metric("User Types", len(user_types))

    if user_types:
        st.write("User types:")
        st.code("\n".join(user_types))

    if apps:
        st.write("Activated apps:")
        st.code("\n".join(apps))

    if maps_stats:
        st.write("Maps stats:")
        st.json(maps_stats)

    if play_games:
        st.write("Play Games:")
        st.json(play_games)

    if calendar:
        st.write("Calendar:")
        st.json(calendar)

    if gaia_id:
        reviews_url = f"https://www.google.com/maps/contrib/{gaia_id}/reviews"
        reviews_url += "?igu=1" # https://stackoverflow.com/questions/8700636/how-to-show-google-com-in-an-iframe
        st.subheader("Google Reviews")
        st.markdown(f"[Open Google Maps reviews]({reviews_url})")
        components.iframe(reviews_url, height=420, scrolling=True)
