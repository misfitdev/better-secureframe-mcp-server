"""Miscellaneous read-only tools."""

from __future__ import annotations

from typing import Any

from ..app import mcp
from . import _common as c


@mcp.tool(annotations=c.READ, tags={"user_security_settings", "read"})
async def list_user_security_settings() -> dict[str, Any]:
    """List the company's user security settings (password policy, MFA, etc.)."""
    return await c.get_resource("/user_security_settings")
