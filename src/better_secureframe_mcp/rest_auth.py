"""Reuse Claude Code's Secureframe OAuth sign-in for REST calls."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

import httpx
from dotenv import load_dotenv

from . import claude_auth
from .config import load_config

API_URLS = {"https://api.secureframe.com", "https://api-uk.secureframe.com"}


def credential() -> claude_auth.ClaudeCredential:
    """Read the current OAuth access token; Claude Code owns refresh-token handling."""
    cfg = load_config()
    if cfg.base_url not in API_URLS:
        raise ValueError(
            "REST calls require an official Secureframe US or UK API URL."
        )
    return claude_auth.cached_credential(
        api_url=cfg.base_url if os.getenv("SECUREFRAME_API_URL") else None,
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


async def probe() -> dict[str, Any]:
    """Read one user to check auth; never return personnel data or credentials."""
    async with await asyncio.to_thread(rest_client) as rest:
        response = await rest.get("/users", params={"page": 1, "per_page": 1})
    try:
        payload = response.json()
    except ValueError:
        payload = None
    accepted = (
        response.is_success
        and isinstance(payload, dict)
        and isinstance(payload.get("data"), list)
    )
    return {
        "auth_mode": "claude_code",
        "status_code": response.status_code,
        "accepted": accepted,
        "note": (
            "REST accepted this credential for reading users; write access is untested."
            if accepted
            else "The OAuth session may be expired/revoked, or the user may lack "
            "permission. No write was attempted."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe Secureframe REST auth with one read-only request."
    )
    parser.add_argument(
        "--claude-code",
        action="store_true",
        help="Use Claude Code's macOS OAuth sign-in (the only authentication method).",
    )
    parser.add_argument(
        "--server-name", help="Select a Claude Code MCP server by name."
    )
    parser.add_argument("--region", choices=["us", "uk"], help="Select a data region.")
    args = parser.parse_args()
    load_dotenv(os.getenv("SECUREFRAME_ENV_FILE") or None)
    if args.server_name:
        os.environ["SECUREFRAME_CLAUDE_SERVER_NAME"] = args.server_name
    if args.region:
        os.environ["SECUREFRAME_API_URL"] = (
            "https://api-uk.secureframe.com"
            if args.region == "uk"
            else "https://api.secureframe.com"
        )
    try:
        result = asyncio.run(probe())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from None
    except httpx.HTTPError:
        print("REST auth probe could not reach Secureframe.", file=sys.stderr)
        raise SystemExit(2) from None
    print(json.dumps(result, indent=2))
    if not result["accepted"]:
        raise SystemExit(1)
