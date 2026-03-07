from __future__ import annotations

import asyncio
import base64
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Awaitable

import streamlit as st

from ghunt.helpers import auth
from ghunt.helpers.utils import get_httpx_client
from ghunt.objects.base import GHuntCreds


def _run_async(coro: Awaitable[Any]) -> Any:
    """Run a coroutine from synchronous Streamlit code."""
    try:
        return asyncio.run(coro)
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" not in str(exc):
            raise
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def run_with_capture(coro: Awaitable[Any]) -> tuple[str, BaseException | None, Any]:
    """Execute coroutine and capture stdout/stderr output."""
    buffer = io.StringIO()
    caught: BaseException | None = None
    result: Any = None

    with redirect_stdout(buffer), redirect_stderr(buffer):
        try:
            result = _run_async(coro)
        except BaseException as exc:  # noqa: BLE001
            caught = exc

    return buffer.getvalue(), caught, result


def load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.is_file():
        return None

    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None


async def verify_saved_session() -> None:
    client = get_httpx_client()
    try:
        await auth.load_and_auth(client)
    finally:
        await client.aclose()


async def _login_from_master(master_token: str) -> None:
    client = get_httpx_client()
    try:
        creds = GHuntCreds()
        creds.android.authorization_tokens = {}
        creds.android.master_token = master_token
        creds.cookies = {"a": "a"}
        creds.osids = {"a": "a"}

        await auth.gen_cookies_and_osids(client, creds)
        creds.save_creds()
    finally:
        await client.aclose()


async def login_with_oauth_token(oauth_token: str) -> dict[str, Any]:
    client = get_httpx_client()
    try:
        master_token, services, owner_email, owner_name = await auth.android_master_auth(client, oauth_token)
    finally:
        await client.aclose()

    await _login_from_master(master_token)

    return {
        "owner_name": owner_name,
        "owner_email": owner_email,
        "service_count": len(services),
        "services": services,
    }


async def login_with_master_token(master_token: str) -> None:
    await _login_from_master(master_token)


def _decode_companion_payload(encoded_payload: str) -> dict[str, Any]:
    blob = encoded_payload.strip()
    if not blob:
        raise ValueError("Companion payload is empty.")

    padding = "=" * (-len(blob) % 4)
    try:
        data = base64.b64decode(blob + padding).decode("utf-8")
        payload = json.loads(data)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Companion payload is not valid base64 JSON.") from exc

    if not isinstance(payload, dict):
        raise ValueError("Companion payload must decode to a JSON object.")
    return payload


async def login_with_companion_payload(encoded_payload: str) -> dict[str, Any]:
    payload = _decode_companion_payload(encoded_payload)
    print(payload)
    oauth_token = payload.get("oauth_token")
    if not oauth_token:
        raise ValueError("Companion payload is missing 'oauth_token'.")

    result = await login_with_oauth_token(oauth_token)
    result["payload_keys"] = sorted(payload.keys())
    return result


def clear_saved_session() -> str:
    creds = GHuntCreds()
    path = Path(creds.creds_path)

    if not path.is_file():
        return f"No credentials file found at {path}."

    path.unlink()
    return f"Deleted credentials file at {path}."


def render_result(output: str, error: BaseException | None, json_payload: Any = None) -> None:
    if error is None:
        st.success("Completed.")
    elif isinstance(error, SystemExit):
        code = error.code if isinstance(error.code, int) else 1
        if code == 0:
            st.info("Command completed.")
        else:
            st.error(f"Command exited with status {code}.")
    else:
        st.error(f"Execution failed: {error}")

    if output.strip():
        st.subheader("Console Output")
        st.code(output)

    if json_payload is not None:
        st.subheader("JSON Output")
        st.json(json_payload)
