"""Trust Center request tools: read, update (approve/reject resource requests).

Requires paid Trust Center features to be enabled on the account.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"trust_center", "read"})
async def list_trust_center_requests(
    reviewed: bool | None = None,
    company_name: str | None = None,
    email: str | None = None,
    q: Annotated[str | None, Field(description="Advanced raw Lucene query")] = None,
    fields: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    auto_paginate: bool = False,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """List Trust Center access requests."""
    return await c.list_resource(
        "/trust_center_requests",
        filters={"reviewed": reviewed, "company_name": company_name, "email": email},
        q=q,
        page=page,
        per_page=per_page,
        auto_paginate=auto_paginate,
        fields=fields,
        include_relationships=include_relationships,
    )


@mcp.tool(annotations=c.READ, tags={"trust_center", "read"})
async def get_trust_center_request(
    id: Annotated[str, Field(description="Trust Center request UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one Trust Center request by ID."""
    return await c.get_resource(
        f"/trust_center_requests/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.UPDATE, tags={"trust_center", "write"})
async def update_trust_center_request(
    id: Annotated[str, Field(description="Trust Center request UUID")],
    approve_all_resources: bool | None = None,
    approved_trust_center_resource_request_ids: list[str] | None = None,
    rejected_trust_center_resource_request_ids: list[str] | None = None,
    custom_response: str | None = None,
    document_security: str | None = None,
    do_not_send_notification: bool | None = None,
) -> dict[str, Any]:
    """Approve or reject a Trust Center access request (in whole or per-resource)."""
    return await c.write(
        "PUT",
        f"/trust_center_requests/{id}",
        params={
            "approve_all_resources": approve_all_resources,
            "approved_trust_center_resource_request_ids": (
                approved_trust_center_resource_request_ids
            ),
            "rejected_trust_center_resource_request_ids": (
                rejected_trust_center_resource_request_ids
            ),
            "custom_response": custom_response,
            "document_security": document_security,
            "do_not_send_notification": do_not_send_notification,
        },
    )
