from __future__ import annotations

from pathlib import Path
from typing import Any

from ..app import mcp
from ..schema import ENUMS, FRAMEWORK_KEYS, SEARCHABLE_FIELDS

SPEC_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "openapi.yaml"
_OPENAPI_SPEC = None


def _get_openapi_spec() -> dict:
    global _OPENAPI_SPEC
    if _OPENAPI_SPEC is None:
        import yaml

        with open(SPEC_PATH, "r") as f:
            _OPENAPI_SPEC = yaml.safe_load(f)
    return _OPENAPI_SPEC


@mcp.resource(
    "secureframe://reference/fields",
    name="Filterable fields (all resources)",
    mime_type="application/json",
)
def all_fields() -> dict[str, list[str]]:
    return SEARCHABLE_FIELDS


@mcp.resource(
    "secureframe://reference/fields/{entity}",
    name="Filterable fields for a resource",
    mime_type="application/json",
)
def entity_fields(entity: str) -> dict[str, Any]:
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
    return ENUMS


@mcp.resource(
    "secureframe://reference/frameworks",
    name="Framework keys",
    mime_type="application/json",
)
def framework_keys() -> dict[str, list[str]]:
    return {"framework_keys": FRAMEWORK_KEYS}


@mcp.resource(
    "secureframe://reference/openapi",
    name="Secureframe OpenAPI Spec (full)",
    mime_type="application/yaml",
)
def openapi_spec() -> str:
    return SPEC_PATH.read_text()


@mcp.resource(
    "secureframe://reference/openapi/json",
    name="Secureframe OpenAPI Spec (JSON)",
    mime_type="application/json",
)
def openapi_spec_json() -> dict[str, Any]:
    return _get_openapi_spec()
