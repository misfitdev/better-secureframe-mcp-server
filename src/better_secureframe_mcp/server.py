"""Server entrypoint: registers all components and runs the MCP server."""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

# Importing these packages registers tools, resources, and prompts on `mcp`.
from . import prompts, resources, tools  # noqa: F401
from .app import mcp
from .config import Config, load_config


async def _apply_tool_filter(config: Config, application: FastMCP = mcp) -> int:
    """Drop tools whose tags don't match the configured include/exclude sets.

    Reduces the number of tool definitions sent to clients (and the tokens they
    cost) for deployments that only need a subset. No-op unless
    SECUREFRAME_TOOL_TAGS or SECUREFRAME_EXCLUDE_TAGS is set.
    """
    if not config.include_tags and not config.exclude_tags:
        return 0
    removed = 0
    for tool in await application.list_tools():
        if not config.keep_tool(frozenset(tool.tags)):
            application.local_provider.remove_tool(tool.name)
            removed += 1
    return removed


def main() -> None:
    # SECUREFRAME_ENV_FILE points at an env file outside the repo (e.g.
    # /tmp/secureframe.env) so secrets stay out of the project and out of any
    # committed MCP config. Falls back to the default ./.env search.
    load_dotenv(os.getenv("SECUREFRAME_ENV_FILE") or None)
    mode = os.getenv("SECUREFRAME_MCP_MODE", "supplemental").strip().lower()
    if mode not in {"supplemental", "legacy"}:
        raise ValueError("SECUREFRAME_MCP_MODE must be supplemental or legacy.")
    config = load_config(require_credentials=mode == "legacy")
    if mode == "supplemental":
        from .supplemental import mcp as application

        if config.transport != "stdio":
            raise ValueError("Local upload helpers support stdio transport only.")
    else:
        application = mcp
    asyncio.run(_apply_tool_filter(config, application))

    if config.transport in {"http", "streamable-http", "sse"}:
        application.run(transport=config.transport, host=config.host, port=config.port)
    else:
        application.run()


if __name__ == "__main__":
    main()
