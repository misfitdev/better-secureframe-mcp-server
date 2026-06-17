"""Security questionnaire tools (create via file upload)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.CREATE, tags={"questionnaires", "write"})
async def create_security_questionnaire(
    file_path: Annotated[
        str, Field(description="Local path to the questionnaire file to upload")
    ],
    owner_id: Annotated[str, Field(description="UUID of the questionnaire owner")],
    company_name: Annotated[
        str | None, Field(description="Name of the client requesting it")
    ] = None,
    due_date: Annotated[str | None, Field(description="Due date (ISO 8601)")] = None,
    questionnaire_template: Annotated[
        str | None, Field(description="Template to use")
    ] = None,
) -> dict[str, Any]:
    """Create a security questionnaire by uploading a file."""
    return await c.upload(
        "POST",
        "/security_questionnaires",
        file_path,
        params={
            "owner_id": owner_id,
            "company_name": company_name,
            "due_date": due_date,
            "questionnaire_template": questionnaire_template,
        },
    )
