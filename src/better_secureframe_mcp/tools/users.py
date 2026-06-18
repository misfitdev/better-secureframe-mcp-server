"""User (personnel) tools: read, update, evidence upload."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c

EmployeeType = Literal["employee", "contractor", "non_employee", "auditor", "external"]


@mcp.tool(annotations=c.READ, tags={"users", "read"})
async def list_users(
    active: bool | None = None,
    employee_type: EmployeeType | None = None,
    in_audit_scope: bool | None = None,
    email: str | None = None,
    department_id: str | None = None,
    onboarding_status: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List personnel and their compliance status with structured filtering."""
    return await c.list_resource(
        "/users",
        filters={
            "active": active,
            "employee_type": employee_type,
            "in_audit_scope": in_audit_scope,
            "email": email,
            "department_id": department_id,
            "onboarding_status": onboarding_status,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"users", "read"})
async def get_user(
    id: Annotated[str, Field(description="User UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one user by ID."""
    return await c.get_resource(
        f"/users/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.UPDATE, tags={"users", "write"})
async def update_user(
    id: Annotated[str, Field(description="User UUID")],
    active: bool | None = None,
    employee_type: EmployeeType | None = None,
    in_audit_scope: bool | None = None,
    start_date: Annotated[str | None, Field(description="ISO 8601 date")] = None,
    end_date: Annotated[str | None, Field(description="ISO 8601 date")] = None,
) -> dict[str, Any]:
    """Update a user (status, employee type, audit scope, employment dates)."""
    return await c.write(
        "PUT",
        f"/users/{id}",
        params={
            "active": active,
            "employee_type": employee_type,
            "in_audit_scope": in_audit_scope,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


@mcp.tool(annotations=c.CREATE, tags={"users", "write", "evidence"})
async def create_user_evidence(
    user_id: Annotated[str, Field(description="User UUID to attach evidence to")],
    file_path: Annotated[str, Field(description="Local path to the file to upload")],
) -> dict[str, Any]:
    """Upload a local file as evidence for a user."""
    return await c.upload("POST", f"/users/{user_id}/evidences", file_path)
