---
title: Better Secureframe MCP Server
---

# Better Secureframe MCP Server

A complete, modern [Model Context Protocol](https://modelcontextprotocol.io/)
server for the Secureframe compliance platform — full read + write coverage of
the API, structured (Lucene-free) filtering, SLSA build provenance, and a real
test/CI setup. It began as the official `secureframe/secureframe-mcp-server`,
which exposed only a small read-only slice and had gone stale, and was rebuilt
from scratch.

> Independent project. **Not affiliated with or endorsed by Secureframe.**

## Documentation

- **[MCP server — install & usage](mcp-server.md)** — how to install, connect it
  to Claude Code / Claude Desktop / Cursor / Codex / Gemini, filter without
  Lucene, and the full tool catalog.
- **[Secureframe API — Empirical Reality Report](api-reality-report.md)** — an
  evidence-first audit of what the Secureframe REST API actually returns and
  supports versus what its docs imply. Probed against a live account, read-only,
  fully anonymized.

## Source

[`github.com/misfitdev/better-secureframe-mcp-server`](https://github.com/misfitdev/better-secureframe-mcp-server)
