"""Explicit REST credentials and a read-only probe for MCP bearer compatibility."""

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


def _auth_mode() -> str:
    mode = os.getenv("SECUREFRAME_REST_AUTH", "auto").strip().lower()
    if mode == "auto":
        mode = (
            "api_key"
            if os.getenv("SECUREFRAME_API_KEY", "").strip()
            and os.getenv("SECUREFRAME_API_SECRET", "").strip()
            else "claude_code"
        )
    if mode not in {"api_key", "mcp_token", "claude_code"}:
        raise ValueError(
            "SECUREFRAME_REST_AUTH must be auto, api_key, mcp_token, or claude_code."
        )
    return mode


def rest_client() -> httpx.AsyncClient:
    """Resolve credentials per call; only Claude Code owns its refresh-token cache."""
    mode = _auth_mode()
    cfg = load_config(require_credentials=mode == "api_key")
    if cfg.base_url not in API_URLS:
        raise ValueError(
            "Supplemental REST uploads require a Secureframe US or UK API URL."
        )
    base_url = cfg.base_url
    if mode == "claude_code":
        cached = claude_auth.cached_credential(
            api_url=cfg.base_url if os.getenv("SECUREFRAME_API_URL") else None,
            server_name=os.getenv("SECUREFRAME_CLAUDE_SERVER_NAME") or None,
        )
        authorization = f"Bearer {cached.access_token}"
        base_url = cached.api_url
    elif mode == "mcp_token":
        token = os.getenv("SECUREFRAME_MCP_ACCESS_TOKEN", "").strip()
        if not token:
            raise ValueError(
                "Set SECUREFRAME_MCP_ACCESS_TOKEN locally to test REST bearer auth. "
                "MCP token acceptance by REST is experimental and unverified."
            )
        authorization = f"Bearer {token}"
    else:
        authorization = cfg.auth_header
    return httpx.AsyncClient(
        base_url=base_url,
        headers={"Authorization": authorization, "Accept": "application/json"},
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
        "auth_mode": _auth_mode(),
        "status_code": response.status_code,
        "accepted": accepted,
        "note": (
            "REST accepted this credential for reading users; write access is untested."
            if accepted
            else "A rejection may mean an expired/invalid token, unsupported bearer auth, "
            "or insufficient user permissions. No write was attempted."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe Secureframe REST auth with one read-only request."
    )
    parser.add_argument(
        "--claude-code",
        action="store_true",
        help="Read the existing Secureframe access token from Claude Code on macOS.",
    )
    parser.add_argument(
        "--server-name", help="Select a Claude Code MCP server by name."
    )
    parser.add_argument("--region", choices=["us", "uk"], help="Select a data region.")
    args = parser.parse_args()
    load_dotenv(os.getenv("SECUREFRAME_ENV_FILE") or None)
    if args.claude_code:
        os.environ["SECUREFRAME_REST_AUTH"] = "claude_code"
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
