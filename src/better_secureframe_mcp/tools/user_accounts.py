"""User account tools (accounts from integrations): read, link."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"user_accounts", "read"})
async def list_user_accounts(
    active: bool | None = None,
    has_user: Annotated[
        bool | None, Field(description="Whether the account is linked to a person")
    ] = None,
    email: str | None = None,
    vendor_name: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List user accounts sourced from integrations."""
    return await c.list_resource(
        "/user_accounts",
        filters={
            "active": active,
            "has_user": has_user,
            "email": email,
            "vendor_name": vendor_name,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"user_accounts", "read"})
async def get_user_account(
    id: Annotated[str, Field(description="User account UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one user account by ID."""
    return await c.get_resource(
        f"/user_accounts/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.UPDATE, tags={"user_accounts", "write"})
async def link_user_account(
    id: Annotated[str, Field(description="User account UUID")],
    user_id: Annotated[
        str | None,
        Field(description="User UUID to link. Omit to unlink the account."),
    ] = None,
) -> dict[str, Any]:
    """Link (or unlink) an integration user account to a person."""
    return await c.write(
        "PUT", f"/user_accounts/{id}/link", params={"user_id": user_id}
    )
