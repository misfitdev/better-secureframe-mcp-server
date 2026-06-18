---
title: A Better Secureframe MCP
kicker: Overview
dek: A complete, rebuilt MCP server for Secureframe, plus an evidence-first audit of the API's read surface.
---

A complete, modern [Model Context Protocol](https://modelcontextprotocol.io/)
server for the Secureframe compliance platform: full read and write coverage of
the API, structured (Lucene-free) filtering, SLSA build provenance, and a real
test and CI setup. It began as the official
[`secureframe/secureframe-mcp-server`](https://github.com/secureframe/secureframe-mcp-server),
which exposed only a small read-only slice and had gone stale, and was rebuilt
from scratch.

> Independent project. **Not affiliated with or endorsed by Secureframe.**

## Start here

**[The Secureframe API, for real](api-reality-report.md)** is the reason this
project exists. It documents what the Secureframe REST API actually returns and
supports versus what its docs imply, verified read-only against a live account
and fully anonymized. Read it if you touch the API at all.

**[MCP server: install and usage](mcp-server.md)** covers installing the server
and wiring it into your MCP client, filtering without Lucene, and the full tool
catalog.

## Source

[`github.com/misfitdev/better-secureframe-mcp-server`](https://github.com/misfitdev/better-secureframe-mcp-server)
