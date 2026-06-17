"""Cloud resource tools: read, update."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"cloud_resources", "read"})
async def list_cloud_resources(
    in_audit_scope: bool | None = None,
    cloud_resource_type: str | None = None,
    vendor_name: str | None = None,
    region: str | None = None,
    third_party_id: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List cloud resources discovered across connected integrations."""
    return await c.list_resource(
        "/cloud_resources",
        filters={
            "in_audit_scope": in_audit_scope,
            "cloud_resource_type": cloud_resource_type,
            "vendor_name": vendor_name,
            "region": region,
            "third_party_id": third_party_id,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"cloud_resources", "read"})
async def get_cloud_resource(
    id: Annotated[str, Field(description="Cloud resource UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one cloud resource by ID."""
    return await c.get_resource(
        f"/cloud_resources/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.UPDATE, tags={"cloud_resources", "write"})
async def update_cloud_resource(
    id: Annotated[str, Field(description="Cloud resource UUID")],
    in_audit_scope: bool | None = None,
    out_of_audit_scope_reason: str | None = None,
    owner_id: Annotated[
        str | None, Field(description="UUID of the owning user")
    ] = None,
) -> dict[str, Any]:
    """Update a cloud resource's audit scope or owner."""
    return await c.write(
        "PUT",
        f"/cloud_resources/{id}",
        params={
            "in_audit_scope": in_audit_scope,
            "out_of_audit_scope_reason": out_of_audit_scope_reason,
            "owner_id": owner_id,
        },
    )
