"""Reuse Claude Code's Secureframe OAuth sign-in for REST calls."""

from __future__ import annotations

import os

import httpx

from . import claude_auth
from .config import api_url

API_URLS = {"https://api.secureframe.com", "https://api-uk.secureframe.com"}


def credential() -> claude_auth.ClaudeCredential:
    """Read the current OAuth access token; Claude Code owns refresh-token handling."""
    selected_url = api_url()
    if selected_url is not None and selected_url not in API_URLS:
        raise ValueError("REST calls require an official Secureframe US or UK API URL.")
    return claude_auth.cached_credential(
        api_url=selected_url,
        server_name=os.getenv("SECUREFRAME_CLAUDE_SERVER_NAME") or None,
    )


def rest_client() -> httpx.AsyncClient:
    """Build an isolated REST client using only the cached Secureframe OAuth sign-in."""
    cached = credential()
    return httpx.AsyncClient(
        base_url=cached.api_url,
        headers={
            "Authorization": f"Bearer {cached.access_token}",
            "Accept": "application/json",
        },
        timeout=120.0,
        follow_redirects=False,
        trust_env=False,
    )
