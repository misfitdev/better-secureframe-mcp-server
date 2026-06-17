"""MCP resources exposing filterable fields, enums, and framework keys.

These let a client discover what it can filter on (and the allowed values)
without guessing or hand-writing Lucene.
"""

from __future__ import annotations

from typing import Any

from ..app import mcp
from ..schema import ENUMS, FRAMEWORK_KEYS, SEARCHABLE_FIELDS


@mcp.resource(
    "secureframe://reference/fields",
    name="Filterable fields (all resources)",
    mime_type="application/json",
)
def all_fields() -> dict[str, list[str]]:
    """The filterable Lucene fields for every resource."""
    return SEARCHABLE_FIELDS


@mcp.resource(
    "secureframe://reference/fields/{entity}",
    name="Filterable fields for a resource",
    mime_type="application/json",
)
def entity_fields(entity: str) -> dict[str, Any]:
    """Filterable Lucene fields for one resource (e.g. tests, controls, users)."""
    fields = SEARCHABLE_FIELDS.get(entity)
    if fields is None:
        return {
            "error": f"Unknown resource '{entity}'",
            "known_resources": sorted(SEARCHABLE_FIELDS),
        }
    return {"entity": entity, "fields": fields}


@mcp.resource(
    "secureframe://reference/enums",
    name="Known enum values",
    mime_type="application/json",
)
def enums() -> dict[str, list[str]]:
    """Allowed values for common enumerated filter fields."""
    return ENUMS


@mcp.resource(
    "secureframe://reference/frameworks",
    name="Framework keys",
    mime_type="application/json",
)
def framework_keys() -> dict[str, list[str]]:
    """Common framework keys for the ``framework`` filter / ``framework_keys`` field."""
    return {"framework_keys": FRAMEWORK_KEYS}
