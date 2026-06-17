"""Vendor tools: legacy vendors and TPRM vendors (read + archive)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c

RiskLevel = Literal["Low", "Medium", "High"]


@mcp.tool(annotations=c.READ, tags={"vendors", "read"})
async def list_vendors(
    risk_level: RiskLevel | None = None,
    archived: bool | None = None,
    name: str | None = None,
    owner_id: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List vendors (legacy vendor API)."""
    return await c.list_resource(
        "/vendors",
        filters={
            "risk_level": risk_level,
            "archived": archived,
            "name": name,
            "owner_id": owner_id,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"vendors", "read"})
async def get_vendor(
    id: Annotated[str, Field(description="Vendor UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one vendor by ID."""
    return await c.get_resource(
        f"/vendors/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.DESTRUCTIVE, tags={"vendors", "write"})
async def archive_vendor(
    id: Annotated[str, Field(description="Vendor UUID")],
    confirm: Annotated[bool, Field(description="Must be true to archive")] = False,
    terminated_at: Annotated[
        str | None, Field(description="Termination date (ISO 8601)")
    ] = None,
) -> dict[str, Any]:
    """Archive a vendor. Destructive: requires confirm=true."""
    return await c.write(
        "PUT",
        f"/vendors/{id}/archive",
        params={"terminated_at": terminated_at},
        destructive=True,
        confirm=confirm,
    )


@mcp.tool(annotations=c.READ, tags={"tprm", "vendors", "read"})
async def list_tprm_vendors(
    risk_level: RiskLevel | None = None,
    archived: bool | None = None,
    vendor_status: Literal["draft", "completed"] | None = None,
    name: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List Third Party Risk Management vendors with risk details."""
    return await c.list_resource(
        "/tprm/vendors",
        filters={
            "risk_level": risk_level,
            "archived": archived,
            "vendor_status": vendor_status,
            "name": name,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"tprm", "vendors", "read"})
async def get_tprm_vendor(
    id: Annotated[str, Field(description="TPRM vendor UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one TPRM vendor by ID, including subassessment responses."""
    return await c.get_resource(
        f"/tprm/vendors/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.DESTRUCTIVE, tags={"tprm", "vendors", "write"})
async def archive_tprm_vendor(
    id: Annotated[str, Field(description="TPRM vendor UUID")],
    confirm: Annotated[bool, Field(description="Must be true to archive")] = False,
) -> dict[str, Any]:
    """Archive a TPRM vendor. Destructive: requires confirm=true."""
    return await c.write(
        "PUT", f"/tprm/vendors/{id}/archive", destructive=True, confirm=confirm
    )
