"""Knowledge Base tools: questions and answers (full CRUD)."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from ..app import mcp
from . import _common as c

# ---------------------------------------------------------------- Questions


@mcp.tool(annotations=c.READ, tags={"knowledge_base", "read"})
async def get_knowledge_base_question(
    id: Annotated[str, Field(description="Knowledge Base question UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one Knowledge Base question by ID."""
    return await c.get_resource(
        f"/knowledge_base_questions/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.CREATE, tags={"knowledge_base", "write"})
async def create_knowledge_base_question(
    content: Annotated[str, Field(description="The question text")],
    owner_id: Annotated[
        str | None, Field(description="UUID of the owning user")
    ] = None,
    review_frequency: Annotated[
        str | None, Field(description="How often to review the answer")
    ] = None,
) -> dict[str, Any]:
    """Create a Knowledge Base question."""
    return await c.write(
        "POST",
        "/knowledge_base_questions",
        params={
            "content": content,
            "owner_id": owner_id,
            "review_frequency": review_frequency,
        },
    )


@mcp.tool(annotations=c.UPDATE, tags={"knowledge_base", "write"})
async def update_knowledge_base_question(
    id: Annotated[str, Field(description="Knowledge Base question UUID")],
    content: str | None = None,
    manual_review_requested: bool | None = None,
    owner_id: str | None = None,
    review_frequency: str | None = None,
) -> dict[str, Any]:
    """Update a Knowledge Base question."""
    return await c.write(
        "PUT",
        f"/knowledge_base_questions/{id}",
        params={
            "content": content,
            "manual_review_requested": manual_review_requested,
            "owner_id": owner_id,
            "review_frequency": review_frequency,
        },
    )


@mcp.tool(annotations=c.DESTRUCTIVE, tags={"knowledge_base", "write"})
async def delete_knowledge_base_question(
    id: Annotated[str, Field(description="Knowledge Base question UUID")],
    confirm: Annotated[bool, Field(description="Must be true to delete")] = False,
) -> dict[str, Any]:
    """Delete a Knowledge Base question. Destructive: requires confirm=true."""
    return await c.write(
        "DELETE", f"/knowledge_base_questions/{id}", destructive=True, confirm=confirm
    )


# ---------------------------------------------------------------- Answers


@mcp.tool(annotations=c.READ, tags={"knowledge_base", "read"})
async def get_knowledge_base_answer(
    id: Annotated[str, Field(description="Knowledge Base answer UUID")],
    include_relationships: bool = False,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get one Knowledge Base answer by ID."""
    return await c.get_resource(
        f"/knowledge_base_answers/{id}",
        include_relationships=include_relationships,
        fields=fields,
    )


@mcp.tool(annotations=c.CREATE, tags={"knowledge_base", "write"})
async def create_knowledge_base_answer(
    content: Annotated[str, Field(description="The answer text")],
    knowledge_base_question_id: Annotated[
        str, Field(description="UUID of the question this answers")
    ],
    type: Annotated[str, Field(description="The answer type")],
    primary_answer: Annotated[
        bool | None, Field(description="Mark as the primary answer")
    ] = None,
) -> dict[str, Any]:
    """Create a Knowledge Base answer for a question."""
    return await c.write(
        "POST",
        "/knowledge_base_answers",
        params={
            "content": content,
            "knowledge_base_question_id": knowledge_base_question_id,
            "type": type,
            "primary_answer": primary_answer,
        },
    )


@mcp.tool(annotations=c.UPDATE, tags={"knowledge_base", "write"})
async def update_knowledge_base_answer(
    id: Annotated[str, Field(description="Knowledge Base answer UUID")],
    content: str | None = None,
    primary_answer: bool | None = None,
    type: str | None = None,
) -> dict[str, Any]:
    """Update a Knowledge Base answer."""
    return await c.write(
        "PUT",
        f"/knowledge_base_answers/{id}",
        params={"content": content, "primary_answer": primary_answer, "type": type},
    )


@mcp.tool(annotations=c.DESTRUCTIVE, tags={"knowledge_base", "write"})
async def delete_knowledge_base_answer(
    id: Annotated[str, Field(description="Knowledge Base answer UUID")],
    confirm: Annotated[bool, Field(description="Must be true to delete")] = False,
) -> dict[str, Any]:
    """Delete a Knowledge Base answer. Destructive: requires confirm=true."""
    return await c.write(
        "DELETE", f"/knowledge_base_answers/{id}", destructive=True, confirm=confirm
    )
