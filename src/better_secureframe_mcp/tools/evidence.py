"""Evidence tools (read-only)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"evidence", "read"})
async def get_evidence(
    id: Annotated[str, Field(description="Evidence UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one evidence record by ID.

    To attach new evidence, use create_test_evidence or create_user_evidence.
    """
    return await c.get_resource(
        f"/evidences/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )
