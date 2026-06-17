"""Repository tools: read, update."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"repositories", "read"})
async def list_repositories(
    in_audit_scope: bool | None = None,
    private: bool | None = None,
    vendor_name: Literal["Github", "Gitlab", "Bitbucket"] | None = None,
    name: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List code repositories in audit scope."""
    return await c.list_resource(
        "/repositories",
        filters={
            "in_audit_scope": in_audit_scope,
            "private": private,
            "vendor_name": vendor_name,
            "name": name,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"repositories", "read"})
async def get_repository(
    id: Annotated[str, Field(description="Repository UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one repository by ID."""
    return await c.get_resource(
        f"/repositories/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.UPDATE, tags={"repositories", "write"})
async def update_repository(
    id: Annotated[str, Field(description="Repository UUID")],
    in_audit_scope: bool | None = None,
    out_of_audit_scope_reason: str | None = None,
    owner_id: Annotated[
        str | None, Field(description="UUID of the owning user")
    ] = None,
) -> dict[str, Any]:
    """Update a repository's audit scope or owner."""
    return await c.write(
        "PUT",
        f"/repositories/{id}",
        params={
            "in_audit_scope": in_audit_scope,
            "out_of_audit_scope_reason": out_of_audit_scope_reason,
            "owner_id": owner_id,
        },
    )
