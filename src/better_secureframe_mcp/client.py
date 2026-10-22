"""Shared async HTTP client for the Secureframe API.

A single AsyncClient is reused across requests (the original implementation
opened a fresh connection pool on every call). Transient failures (429 rate
limits and 5xx) are retried with exponential backoff.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from . import rest_auth

_PER_PAGE_MAX = 100  # Secureframe hard-caps page size at 100 regardless of request.
_MAX_RETRIES = 3
_BACKOFF_BASE = 0.5

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        # Content-Type is intentionally omitted so httpx sets it per request
        # (application/json for json= bodies, multipart for file uploads).
        _client = httpx.AsyncClient(
            headers={"Accept": "application/json"},
            timeout=60.0,
            follow_redirects=False,
            trust_env=False,
        )
    return _client


async def request(
    method: str,
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make a single API request, returning parsed JSON or an {"error": ...} dict."""
    client = get_client()
    try:
        oauth = await asyncio.to_thread(rest_auth.credential)
    except ValueError as exc:
        return {"error": str(exc)}
    clean_params = {k: v for k, v in (params or {}).items() if v is not None}

    last_error = ""
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = await client.request(
                method,
                f"{oauth.api_url}{endpoint}",
                params=clean_params,
                json=json_data,
                headers={"Authorization": f"Bearer {oauth.access_token}"},
            )
        except httpx.RequestError as exc:
            last_error = f"Request failed: {exc}"
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(_BACKOFF_BASE * (2**attempt))
                continue
            return {"error": last_error}

        if response.status_code == 429 or response.status_code >= 500:
            last_error = f"API Error {response.status_code}: {response.text}"
            if attempt < _MAX_RETRIES:
                retry_after = response.headers.get("Retry-After")
                delay = (
                    float(retry_after)
                    if retry_after and retry_after.isdigit()
                    else _BACKOFF_BASE * (2**attempt)
                )
                await asyncio.sleep(delay)
                continue
            return {"error": last_error}

        if response.is_error:
            return {"error": f"API Error {response.status_code}: {response.text}"}

        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"error": "Response was not valid JSON", "body": response.text}

    return {"error": last_error or "Unknown error"}


async def get(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    return await request("GET", endpoint, params=params)


async def upload(
    method: str,
    endpoint: str,
    file_path: str,
    *,
    params: dict[str, Any] | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Upload a local file as multipart/form-data (field name ``file``)."""
    import os

    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    client = http_client if http_client is not None else get_client()
    auth_headers = {}
    if http_client is None:
        try:
            oauth = await asyncio.to_thread(rest_auth.credential)
        except ValueError as exc:
            return {"error": str(exc)}
        endpoint = f"{oauth.api_url}{endpoint}"
        auth_headers["Authorization"] = f"Bearer {oauth.access_token}"
    clean_params = {k: v for k, v in (params or {}).items() if v is not None}
    try:
        fh = await asyncio.to_thread(open, file_path, "rb")
        try:
            files = {"file": (os.path.basename(file_path), fh)}
            response = await client.request(
                method, endpoint, params=clean_params, files=files, headers=auth_headers
            )
        finally:
            await asyncio.to_thread(fh.close)
    except OSError as exc:
        return {"error": f"Could not read upload file: {exc.strerror}"}
    except httpx.RequestError as exc:
        return {"error": f"Request failed: {exc}"}

    if response.is_error:
        return {"error": f"API Error {response.status_code}: {response.text}"}
    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"error": "Response was not valid JSON", "body": response.text}


async def auto_paginate(
    endpoint: str,
    params: dict[str, Any] | None = None,
    *,
    max_pages: int = 50,
) -> dict[str, Any]:
    """Fetch every page of a list endpoint and merge the ``data`` arrays.

    Stops at the first short/empty page or after ``max_pages`` (a runaway guard).
    Returns the standard envelope with a combined ``data`` list plus a
    ``pagination`` summary, or {"error": ...} on the first failing page.
    """
    params = dict(params or {})
    params["per_page"] = _PER_PAGE_MAX
    merged: list[Any] = []
    pages_fetched = 0

    for page in range(1, max_pages + 1):
        params["page"] = page
        result = await get(endpoint, params)
        if isinstance(result, dict) and result.get("error"):
            return result

        data = result.get("data") if isinstance(result, dict) else None
        if not isinstance(data, list):
            # Endpoint did not return a list envelope; hand back the raw result.
            return result if pages_fetched == 0 else {"data": merged}

        merged.extend(data)
        pages_fetched += 1
        if len(data) < _PER_PAGE_MAX:
            break

    return {
        "data": merged,
        "pagination": {
            "pages_fetched": pages_fetched,
            "total_records": len(merged),
            "truncated": pages_fetched >= max_pages,
        },
    }


async def aclose() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
