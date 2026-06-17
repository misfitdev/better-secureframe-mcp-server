"""Integration tools: connections (read + archive) and custom data publishing."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"integrations", "read"})
async def list_integration_connections(
    status: str | None = None,
    vendor_name: str | None = None,
    name: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List integration connections and their status."""
    return await c.list_resource(
        "/integration_connections",
        filters={"status": status, "vendor_name": vendor_name, "name": name},
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"integrations", "read"})
async def get_integration_connection(
    id: Annotated[str, Field(description="Integration connection UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one integration connection by ID."""
    return await c.get_resource(
        f"/integration_connections/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.DESTRUCTIVE, tags={"integrations", "write"})
async def archive_integration_connection(
    id: Annotated[str, Field(description="Integration connection UUID")],
    confirm: Annotated[bool, Field(description="Must be true to archive")] = False,
) -> dict[str, Any]:
    """Archive an integration connection. Destructive: requires confirm=true."""
    return await c.write(
        "PUT",
        f"/integration_connections/{id}/archive",
        destructive=True,
        confirm=confirm,
    )


@mcp.tool(annotations=c.CREATE, tags={"integrations", "write", "custom"})
async def publish_custom_integration_data(
    id: Annotated[str, Field(description="Custom connection UUID")],
    schema_slug: Annotated[str, Field(description="Data type slug, e.g. 'users'")],
    vendor_slug: Annotated[
        str, Field(description="Vendor slug; must match the connection's vendor")
    ],
    resource_data: Annotated[
        list[dict[str, Any]],
        Field(description="Array of resource objects (each needs a primary id)"),
    ],
    partial: Annotated[
        bool, Field(description="If true, only update fields present in the data")
    ] = False,
) -> dict[str, Any]:
    """Publish resource data to a custom integration connection."""
    return await c.write(
        "POST",
        f"/custom_connections/{id}/data",
        json_data={
            "schema_slug": schema_slug,
            "vendor_slug": vendor_slug,
            "resource_data": resource_data,
            "partial": partial,
        },
    )
