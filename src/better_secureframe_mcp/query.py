"""Compile structured filters into a Lucene query string.

The Secureframe API only accepts a raw Lucene ``q`` string for filtering list
endpoints. This module lets tools expose ordinary typed parameters and assemble
the Lucene query server-side, so callers never have to hand-write Lucene.
"""

from __future__ import annotations

import re
from typing import Any

# Characters that force a value to be quoted (anything outside a safe token set).
_SAFE_TOKEN = re.compile(r"^[A-Za-z0-9_.\-:@]+$")


def lucene_value(value: Any) -> str:
    """Render a single value as a Lucene term, quoting/escaping when needed."""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if text == "" or not _SAFE_TOKEN.match(text):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _clause(field: str, value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        terms = [f"{field}:{lucene_value(v)}" for v in value if v is not None]
        if not terms:
            return None
        if len(terms) == 1:
            return terms[0]
        return "(" + " OR ".join(terms) + ")"
    return f"{field}:{lucene_value(value)}"


def build_query(
    filters: dict[str, Any] | None = None,
    raw_q: str | None = None,
) -> str | None:
    """Build a Lucene query from structured filters and/or a raw escape-hatch.

    ``filters`` maps Lucene field names to values (scalars, bools, or lists that
    become OR groups). Clauses are joined with AND. ``raw_q`` is ANDed in as-is
    for power users. Returns ``None`` when there is nothing to filter on.
    """
    clauses: list[str] = []
    for field, value in (filters or {}).items():
        clause = _clause(field, value)
        if clause is not None:
            clauses.append(clause)

    if raw_q and raw_q.strip():
        clauses.append(f"({raw_q.strip()})" if clauses else raw_q.strip())

    if not clauses:
        return None
    return " AND ".join(clauses)
