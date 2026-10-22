"""Explicit REST credentials and a read-only probe for MCP bearer compatibility."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any

import httpx
from dotenv import load_dotenv

from .config import load_config

API_URLS = {"https://api.secureframe.com", "https://api-uk.secureframe.com"}


def rest_client() -> httpx.AsyncClient:
    """Build an isolated client; never discover or read another client's token cache."""
    mode = os.getenv("SECUREFRAME_REST_AUTH", "api_key").strip().lower()
    if mode not in {"api_key", "mcp_token"}:
        raise ValueError("SECUREFRAME_REST_AUTH must be api_key or mcp_token.")
    cfg = load_config(require_credentials=mode == "api_key")
    if cfg.base_url not in API_URLS:
        raise ValueError(
            "Supplemental REST uploads require a Secureframe US or UK API URL."
        )
    if mode == "mcp_token":
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
        base_url=cfg.base_url,
        headers={"Authorization": authorization, "Accept": "application/json"},
        timeout=120.0,
        follow_redirects=False,
        trust_env=False,
    )


async def probe() -> dict[str, Any]:
    """Read one user to check auth; never return personnel data or credentials."""
    async with rest_client() as rest:
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
        "auth_mode": os.getenv("SECUREFRAME_REST_AUTH", "api_key").strip().lower(),
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
    load_dotenv(os.getenv("SECUREFRAME_ENV_FILE") or None)
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
