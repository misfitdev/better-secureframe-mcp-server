"""Flatten and trim the Secureframe JSON:API response envelope.

Raw responses wrap every record in ``{id, type, attributes, relationships}`` and
include many null fields. Flattening to ``{id, **attributes}`` and dropping nulls
substantially reduces token usage for LLM consumers.
"""

from __future__ import annotations

from typing import Any


def _flatten_record(
    record: dict[str, Any],
    fields: list[str] | None,
    include_relationships: bool,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        return record

    flat: dict[str, Any] = {}
    if "id" in record:
        flat["id"] = record["id"]
    if "type" in record:
        flat["type"] = record["type"]

    attributes = record.get("attributes")
    if isinstance(attributes, dict):
        flat.update(attributes)
    else:
        # Already flat (e.g. an auto-paginated merge of flattened records).
        flat.update({k: v for k, v in record.items() if k not in {"relationships"}})

    if include_relationships and isinstance(record.get("relationships"), dict):
        flat["relationships"] = record["relationships"]

    if fields:
        keep = set(fields) | {"id"}
        flat = {k: v for k, v in flat.items() if k in keep}

    return {k: v for k, v in flat.items() if v is not None}


def shape(
    payload: dict[str, Any],
    *,
    fields: list[str] | None = None,
    include_relationships: bool = False,
) -> dict[str, Any]:
    """Flatten ``data`` records and drop nulls, preserving error/pagination keys."""
    if not isinstance(payload, dict):
        return payload
    if payload.get("error"):
        return payload

    data = payload.get("data")
    if isinstance(data, list):
        shaped = [_flatten_record(rec, fields, include_relationships) for rec in data]
    elif isinstance(data, dict):
        shaped = _flatten_record(data, fields, include_relationships)
    else:
        return payload

    out: dict[str, Any] = {"data": shaped}
    for key in ("pagination", "meta", "links"):
        if key in payload:
            out[key] = payload[key]
    return out
