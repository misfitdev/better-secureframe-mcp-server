"""Control tools (read-only)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"controls", "read"})
async def list_controls(
    health_status: Literal["healthy", "unhealthy", "draft", "unmapped"] | None = None,
    framework: Annotated[
        str | None, Field(description="Framework key, e.g. soc2_alpha, iso27001_2022")
    ] = None,
    custom: bool | None = None,
    enabled: bool | None = None,
    owner_name: str | None = None,
    key: Annotated[str | None, Field(description="Control key/identifier")] = None,
    q: Annotated[
        str | None, Field(description="Advanced raw Lucene query (escape hatch)")
    ] = None,
    fields: Annotated[
        list[str] | None, Field(description="Only return these attributes")
    ] = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: Annotated[
        bool, Field(description="Fetch every page (API caps pages at 100 records)")
    ] = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List security controls across frameworks with structured filtering.

    No Lucene required: set health_status, framework, etc. directly.
    """
    return await c.list_resource(
        "/controls",
        filters={
            "health_status": health_status,
            "frameworks": framework,
            "custom": custom,
            "enabled": enabled,
            "owner_name": owner_name,
            "key": key,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"controls", "read"})
async def get_control(
    id: Annotated[str, Field(description="Control UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one control by ID, including its full detail."""
    return await c.get_resource(
        f"/controls/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )
