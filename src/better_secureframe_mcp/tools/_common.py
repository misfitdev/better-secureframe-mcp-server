"""Shared helpers behind the curated tools.

These keep each tool thin: a tool declares its typed parameters, assembles a
filters dict, and delegates to ``list_resource`` / ``get_resource`` / ``write``.
"""

from __future__ import annotations

from typing import Any

from mcp.types import ToolAnnotations

from .. import client, query, shaping

# Reusable annotation presets.
READ = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
CREATE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True)
UPDATE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=True
)
DESTRUCTIVE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=True, openWorldHint=True
)


async def list_resource(
    endpoint: str,
    *,
    filters: dict[str, Any] | None = None,
    q: str | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    fields: list[str] | None = None,
    include: str | None = None,
    include_relationships: bool = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    lucene = query.build_query(filters, q)
    if lucene:
        params["q"] = lucene
    if include:
        params["include"] = include
    if include_relationships:
        params["relationships"] = True

    if auto_paginate:
        payload = await client.auto_paginate(endpoint, params)
    else:
        params["page"] = page
        params["per_page"] = min(per_page, 100)
        payload = await client.get(endpoint, params)

    return shaping.shape(
        payload, fields=fields, include_relationships=include_relationships
    )


async def get_resource(
    endpoint: str,
    *,
    fields: list[str] | None = None,
    include: str | None = None,
    include_relationships: bool = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if include:
        params["include"] = include
    if include_relationships:
        params["relationships"] = True
    payload = await client.get(endpoint, params)
    return shaping.shape(
        payload, fields=fields, include_relationships=include_relationships
    )


async def write(
    method: str,
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
    destructive: bool = False,
    confirm: bool = True,
) -> dict[str, Any]:
    try:
        client.ensure_writable()
    except client.WriteNotAllowedError as exc:
        return {"error": str(exc)}
    if destructive and not confirm:
        return {
            "error": "This is a destructive operation. Re-run with confirm=true to proceed.",
            "would_call": f"{method} {endpoint}",
        }
    payload = await client.request(method, endpoint, params=params, json_data=json_data)
    return shaping.shape(payload)


async def upload(
    method: str,
    endpoint: str,
    file_path: str,
    *,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        client.ensure_writable()
    except client.WriteNotAllowedError as exc:
        return {"error": str(exc)}
    payload = await client.upload(method, endpoint, file_path, params=params)
    return shaping.shape(payload)
