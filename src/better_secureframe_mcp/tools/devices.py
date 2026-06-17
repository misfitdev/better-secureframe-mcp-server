"""Device tools (read-only)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"devices", "read"})
async def list_devices(
    in_audit_scope: bool | None = None,
    hard_drive_encrypted: bool | None = None,
    password_enforcement_enabled: bool | None = None,
    native_anti_virus_enabled: bool | None = None,
    local_firewall_enabled: bool | None = None,
    os: Annotated[str | None, Field(description="Operating system")] = None,
    make: str | None = None,
    serial_number: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List managed devices and their security posture."""
    return await c.list_resource(
        "/devices",
        filters={
            "in_audit_scope": in_audit_scope,
            "hard_drive_encrypted": hard_drive_encrypted,
            "password_enforcement_enabled": password_enforcement_enabled,
            "native_anti_virus_enabled": native_anti_virus_enabled,
            "local_firewall_enabled": local_firewall_enabled,
            "os": os,
            "make": make,
            "serial_number": serial_number,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"devices", "read"})
async def get_device(
    id: Annotated[str, Field(description="Device UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one device by ID."""
    return await c.get_resource(
        f"/devices/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )
