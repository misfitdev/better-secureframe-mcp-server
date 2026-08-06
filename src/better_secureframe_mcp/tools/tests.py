"""Test (compliance check) tools: read, update, evidence upload, exports.

All filterable fields extracted from the OpenAPI spec description tables.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"tests", "read"})
async def list_tests(
    health_status: Literal["pass", "fail", "disabled"] | None = None,
    test_type: Literal["integration", "upload"] | None = None,
    framework: Annotated[
        str | None, Field(description="Framework key, e.g. soc2_alpha")
    ] = None,
    test_domain: Annotated[
        str | None, Field(description="e.g. 'Network Security', 'Data Security'")
    ] = None,
    enabled: bool | None = None,
    custom: bool | None = None,
    owner_name: str | None = None,
    vendor_name: str | None = None,
    key: str | None = None,
    author_name: str | None = None,
    created_at: str | None = None,
    description: str | None = None,
    enabled_field_updated_by_user: str | None = None,
    last_evaluated: str | None = None,
    next_due_date: str | None = None,
    pass_filter: str | None = None,
    passed_with_upload: bool | None = None,
    promote_at: str | None = None,
    recommended_action: str | None = None,
    required_implementation_date: str | None = None,
    resource_category: str | None = None,
    status: str | None = None,
    test_function: str | None = None,
    test_interval_seconds: str | None = None,
    title: str | None = None,
    tolerance_window_seconds: str | None = None,
    updated_at: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List compliance tests with pass/fail status and structured filtering.

    All filterable fields from the OpenAPI spec description tables are supported.
    """
    return await c.list_resource(
        "/tests",
        filters={
            "health_status": health_status,
            "test_type": test_type,
            "frameworks": framework,
            "test_domain": test_domain,
            "enabled": enabled,
            "custom": custom,
            "owner_name": owner_name,
            "vendor_name": vendor_name,
            "key": key,
            "author_name": author_name,
            "created_at": created_at,
            "description": description,
            "enabled_field_updated_by_user": enabled_field_updated_by_user,
            "last_evaluated": last_evaluated,
            "next_due_date": next_due_date,
            "pass": pass_filter,
            "passed_with_upload": passed_with_upload,
            "promote_at": promote_at,
            "recommended_action": recommended_action,
            "required_implementation_date": required_implementation_date,
            "resource_category": resource_category,
            "status": status,
            "test_function": test_function,
            "test_interval_seconds": test_interval_seconds,
            "title": title,
            "tolerance_window_seconds": tolerance_window_seconds,
            "updated_at": updated_at,
        },
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"tests", "read"})
async def get_test(
    id: Annotated[str, Field(description="Test UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one test by ID."""
    return await c.get_resource(
        f"/tests/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.UPDATE, tags={"tests", "write"})
async def update_test(
    id: Annotated[str, Field(description="Test UUID")],
    enabled: bool | None = None,
    disabled_justification: str | None = None,
    owner_id: Annotated[
        str | None, Field(description="UUID of the owning user")
    ] = None,
    next_due_date: Annotated[str | None, Field(description="ISO 8601 datetime")] = None,
    promote_at: Annotated[str | None, Field(description="ISO 8601 datetime")] = None,
    passed_with_upload_justification: str | None = None,
    test_interval_seconds: int | None = None,
    tolerance_window_seconds: int | None = None,
) -> dict[str, Any]:
    """Update a test (enable/disable, ownership, schedule)."""
    return await c.write(
        "PUT",
        f"/tests/{id}",
        params={
            "enabled": enabled,
            "disabled_justification": disabled_justification,
            "owner_id": owner_id,
            "next_due_date": next_due_date,
            "promote_at": promote_at,
            "passed_with_upload_justification": passed_with_upload_justification,
            "test_interval_seconds": test_interval_seconds,
            "tolerance_window_seconds": tolerance_window_seconds,
        },
    )


@mcp.tool(annotations=c.CREATE, tags={"tests", "write", "evidence"})
async def create_test_evidence(
    test_id: Annotated[str, Field(description="Test UUID to attach evidence to")],
    file_path: Annotated[str, Field(description="Local path to the file to upload")],
    activity_completion: Annotated[
        str | None, Field(description="Date the activity was completed (ISO 8601)")
    ] = None,
) -> dict[str, Any]:
    """Upload a local file as evidence for a test."""
    return await c.upload(
        "POST",
        f"/tests/{test_id}/evidences",
        file_path,
        params={"activity_completion": activity_completion},
    )


@mcp.tool(annotations=c.CREATE, tags={"tests", "write", "export"})
async def create_test_export(
    test_id: Annotated[str, Field(description="Test UUID to export")],
) -> dict[str, Any]:
    """Start a test export job. Poll get_test_export with the returned ID."""
    return await c.write("POST", f"/tests/{test_id}/exports")


@mcp.tool(annotations=c.READ, tags={"tests", "read", "export"})
async def get_test_export(
    id: Annotated[str, Field(description="Test export UUID")],
) -> dict[str, Any]:
    """Read the status/result of a test export."""
    return await c.get_resource(f"/test_exports/{id}")
