"""Risk register tools (read-only)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"risks", "read"})
async def list_risks(
    status: Annotated[str | None, Field(description="Risk status")] = None,
    treatment: Annotated[
        str | None, Field(description="Treatment decision, e.g. mitigate, accept")
    ] = None,
    source: str | None = None,
    responsible_team: str | None = None,
    owner_id: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List risks from the risk register with structured filtering."""
    return await c.list_resource(
        "/risks",
        filters={
            "status": status,
            "treatment": treatment,
            "source": source,
            "responsible_team": responsible_team,
            "owner_id": owner_id,
        },
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
