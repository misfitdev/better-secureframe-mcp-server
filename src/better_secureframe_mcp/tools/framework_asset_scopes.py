"""Framework asset scope tools for cloud resources, devices, and repositories.

A framework asset scope defines whether an asset is in scope for a framework.
Scopes are immutable; to change a scope you create a new one.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c

ParentType = Literal["cloud_resources", "devices", "repositories"]


def _endpoint(parent_type: str, parent_id: str) -> str:
    return f"/{parent_type}/{parent_id}/framework_asset_scopes"


@mcp.tool(annotations=c.READ, tags={"framework_asset_scopes", "read"})
async def list_framework_asset_scopes(
    parent_type: Annotated[
        ParentType, Field(description="The kind of asset the scopes belong to")
    ],
    parent_id: Annotated[str, Field(description="UUID of the parent asset")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """List the framework asset scopes for a cloud resource, device, or repository."""
    return await c.get_resource(
        _endpoint(parent_type, parent_id),
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.CREATE, tags={"framework_asset_scopes", "write"})
async def create_framework_asset_scope(
    parent_type: Annotated[ParentType, Field(description="The kind of asset to scope")],
    parent_id: Annotated[str, Field(description="UUID of the parent asset")],
    framework_id: Annotated[
        str, Field(description="UUID of the framework to scope to")
    ],
    active: Annotated[
        bool | None, Field(description="Whether the scope is active")
    ] = None,
    manually_scoped_reason: Annotated[
        str | None, Field(description="Reason if manually scoped")
    ] = None,
) -> dict[str, Any]:
    """Create a framework asset scope for an asset (scopes are immutable once created)."""
    return await c.write(
        "POST",
        _endpoint(parent_type, parent_id),
        params={
            "framework_id": framework_id,
            "active": active,
            "manually_scoped_reason": manually_scoped_reason,
        },
    )
