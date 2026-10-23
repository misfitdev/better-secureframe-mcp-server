"""Optional region selection for Claude Code's cached Secureframe sign-in."""

from __future__ import annotations

import os


def api_url() -> str | None:
    """Return an explicit API region, or let the cached OAuth entry select it."""
    value = os.getenv("SECUREFRAME_API_URL")
    return value.rstrip("/") if value else None
