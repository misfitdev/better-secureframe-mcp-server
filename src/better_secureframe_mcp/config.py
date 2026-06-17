"""Runtime configuration sourced from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _tagset(value: str | None) -> frozenset[str]:
    return frozenset(t.strip() for t in (value or "").split(",") if t.strip())


@dataclass(frozen=True)
class Config:
    api_key: str
    api_secret: str
    base_url: str
    read_only: bool
    transport: str
    host: str
    port: int
    include_tags: frozenset[str]
    exclude_tags: frozenset[str]

    @property
    def auth_header(self) -> str:
        # Secureframe expects "<key> <secret>" in the Authorization header.
        return f"{self.api_key} {self.api_secret}"

    def keep_tool(self, tags: frozenset[str]) -> bool:
        """Whether a tool with these tags should be registered.

        Lets a deployment shrink the exposed tool surface (and the tokens its
        definitions cost) without code changes. Example: SECUREFRAME_EXCLUDE_TAGS=write
        for a read-only server, or SECUREFRAME_TOOL_TAGS=controls,tests to expose
        only those resources.
        """
        if self.exclude_tags & tags:
            return False
        if self.include_tags and not (self.include_tags & tags):
            return False
        return True


def load_config() -> Config:
    api_key = os.getenv("SECUREFRAME_API_KEY", "").strip()
    api_secret = os.getenv("SECUREFRAME_API_SECRET", "").strip()
    if not api_key or not api_secret:
        raise ValueError(
            "SECUREFRAME_API_KEY and SECUREFRAME_API_SECRET must be set. "
            "Create an API key in Secureframe under Company settings -> API keys."
        )

    # US is the default region; UK instances use https://api-uk.secureframe.com.
    base_url = os.getenv("SECUREFRAME_API_URL", "https://api.secureframe.com").rstrip(
        "/"
    )

    return Config(
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
        read_only=_truthy(os.getenv("SECUREFRAME_READ_ONLY")),
        transport=os.getenv("SECUREFRAME_MCP_TRANSPORT", "stdio").strip().lower(),
        host=os.getenv("SECUREFRAME_MCP_HOST", "127.0.0.1").strip(),
        port=int(os.getenv("SECUREFRAME_MCP_PORT", "8000")),
        include_tags=_tagset(os.getenv("SECUREFRAME_TOOL_TAGS")),
        exclude_tags=_tagset(os.getenv("SECUREFRAME_EXCLUDE_TAGS")),
    )
