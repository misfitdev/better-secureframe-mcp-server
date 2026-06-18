"""Framework and framework-requirement tools (read-only)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"frameworks", "read"})
async def list_frameworks(
    q: Annotated[
        str | None,
        Field(
            description="Raw Lucene query (the frameworks endpoint has no verified structured filters)"
        ),
    ] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List compliance frameworks enabled for the company (typically a short list)."""
    return await c.list_resource(
        "/frameworks",
        filters=None,
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"frameworks", "read"})
async def get_framework(
    id: Annotated[str, Field(description="Framework UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one framework by ID."""
    return await c.get_resource(
        f"/frameworks/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.READ, tags={"frameworks", "read"})
async def list_framework_requirements(
    health_status: (
        Literal["pass", "fail", "na", "not_applicable", "draft"] | None
    ) = None,
    enabled: bool | None = None,
    key: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List framework requirements (individual controls a framework mandates)."""
    return await c.list_resource(
        "/framework_requirements",
        filters={"health_status": health_status, "enabled": enabled, "key": key},
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"frameworks", "read"})
async def get_framework_requirement(
    id: Annotated[str, Field(description="Framework requirement UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one framework requirement by ID."""
    return await c.get_resource(
        f"/framework_requirements/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )
