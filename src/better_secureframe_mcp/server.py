"""Server entrypoint: registers all components and runs the MCP server."""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from .app import mcp
from .config import Config, load_config

# Importing these packages registers tools, resources, and prompts on `mcp`.
from . import prompts, resources, tools  # noqa: E402, F401


async def _apply_tool_filter(config: Config) -> int:
    """Drop tools whose tags don't match the configured include/exclude sets.

    Reduces the number of tool definitions sent to clients (and the tokens they
    cost) for deployments that only need a subset. No-op unless
    SECUREFRAME_TOOL_TAGS or SECUREFRAME_EXCLUDE_TAGS is set.
    """
    if not config.include_tags and not config.exclude_tags:
        return 0
    removed = 0
    for tool in await mcp.list_tools():
        if not config.keep_tool(frozenset(tool.tags)):
            mcp.local_provider.remove_tool(tool.name)
            removed += 1
    return removed


def main() -> None:
    # SECUREFRAME_ENV_FILE points at an env file outside the repo (e.g.
    # /tmp/secureframe.env) so secrets stay out of the project and out of any
    # committed MCP config. Falls back to the default ./.env search.
    load_dotenv(os.getenv("SECUREFRAME_ENV_FILE") or None)
    config = load_config()
    asyncio.run(_apply_tool_filter(config))

    if config.transport in {"http", "streamable-http", "sse"}:
        mcp.run(transport=config.transport, host=config.host, port=config.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
