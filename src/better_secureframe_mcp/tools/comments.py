"""Comment tools (full CRUD)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"comments", "read"})
async def list_comments(
    commentable_id: Annotated[
        str | None, Field(description="ID of the commented-on resource")
    ] = None,
    commentable_type: Annotated[
        str | None, Field(description="Type of resource, e.g. test, risk, vendor")
    ] = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List comments, optionally scoped to a specific resource."""
    return await c.list_resource(
        "/comments",
        filters={
            "commentable_id": commentable_id,
            "commentable_type": commentable_type,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"comments", "read"})
async def get_comment(
    id: Annotated[str, Field(description="Comment UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one comment by ID."""
    return await c.get_resource(
        f"/comments/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.CREATE, tags={"comments", "write"})
async def create_comment(
    commentable_id: Annotated[
        str, Field(description="ID of the resource to comment on")
    ],
    commentable_type: Annotated[
        str, Field(description="Type of resource, e.g. test, risk, vendor")
    ],
    content: Annotated[str, Field(description="The comment text")],
    conversation_id: Annotated[
        str | None, Field(description="Optional conversation to thread under")
    ] = None,
) -> dict[str, Any]:
    """Create a comment on a resource."""
    return await c.write(
        "POST",
        "/comments",
        params={
            "commentable_id": commentable_id,
            "commentable_type": commentable_type,
            "content": content,
            "conversation_id": conversation_id,
        },
    )


@mcp.tool(annotations=c.UPDATE, tags={"comments", "write"})
async def update_comment(
    id: Annotated[str, Field(description="Comment UUID")],
    content: Annotated[str, Field(description="The new comment text")],
) -> dict[str, Any]:
    """Update a comment's content."""
    return await c.write("PUT", f"/comments/{id}", params={"content": content})


@mcp.tool(annotations=c.DESTRUCTIVE, tags={"comments", "write"})
async def delete_comment(
    id: Annotated[str, Field(description="Comment UUID")],
    confirm: Annotated[bool, Field(description="Must be true to delete")] = False,
) -> dict[str, Any]:
    """Delete a comment. Destructive: requires confirm=true."""
    return await c.write("DELETE", f"/comments/{id}", destructive=True, confirm=confirm)
