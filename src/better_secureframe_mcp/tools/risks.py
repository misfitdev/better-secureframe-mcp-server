"""Risk register tools (read-only)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"risks", "read"})
async def list_risks(
    q: Annotated[
        str | None,
        Field(
            description=(
                "Raw Lucene query. The risks endpoint exposes no verified "
                "structured filter fields (status/treatment/source/owner_id all "
                "return HTTP 400 'not filterable'), so filtering is via raw q only."
            )
        ),
    ] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List risks from the risk register.

    Note: the Secureframe API rejects (400) every obvious risk filter field, so
    this tool offers no structured filters — use `q` if you know a filterable
    field, otherwise page through and filter client-side.
    """
    return await c.list_resource(
        "/risks",
        filters=None,
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"risks", "read"})
async def get_risk(
    id: Annotated[str, Field(description="Risk UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one risk by ID."""
    return await c.get_resource(
        f"/risks/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )
