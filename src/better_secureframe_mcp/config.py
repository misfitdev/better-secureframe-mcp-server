"""Runtime configuration sourced from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _tagset(value: str | None) -> frozenset[str]:
    return frozenset(t.strip() for t in (value or "").split(",") if t.strip())


@dataclass(frozen=True)
class Config:
    base_url: str
    transport: str
    host: str
    port: int
    include_tags: frozenset[str]
    exclude_tags: frozenset[str]

    def keep_tool(self, tags: frozenset[str]) -> bool:
        """Whether a tool with these tags should be registered.

        Lets a deployment shrink the exposed tool surface (and the tokens its
        definitions cost) without code changes. Example: SECUREFRAME_TOOL_TAGS=controls,tests exposes only those resources.
        """
        if self.exclude_tags & tags:
            return False
        return not self.include_tags or bool(self.include_tags & tags)


def load_config() -> Config:
    # An explicit URL selects a region; OAuth resolution infers it when unset.
    base_url = os.getenv("SECUREFRAME_API_URL", "https://api.secureframe.com").rstrip(
        "/"
    )

    return Config(
        base_url=base_url,
        transport=os.getenv("SECUREFRAME_MCP_TRANSPORT", "stdio").strip().lower(),
        host=os.getenv("SECUREFRAME_MCP_HOST", "127.0.0.1").strip(),
        port=int(os.getenv("SECUREFRAME_MCP_PORT", "8000")),
        include_tags=_tagset(os.getenv("SECUREFRAME_TOOL_TAGS")),
        exclude_tags=_tagset(os.getenv("SECUREFRAME_EXCLUDE_TAGS")),
    )
