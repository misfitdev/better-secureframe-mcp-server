---
title: A Better Secureframe MCP
kicker: Get started
dek: "A complete, modern MCP server for the Secureframe API: full read and write coverage, structured filtering, and no hand-written Lucene."
---

A complete [Model Context Protocol](https://modelcontextprotocol.io/) server for
the Secureframe compliance platform: full read and write coverage of the API,
structured (Lucene-free) filtering, write safety, and a real test and CI setup.
It is an independent rebuild of the official, long-stale
[`secureframe/secureframe-mcp-server`](https://github.com/secureframe/secureframe-mcp-server)
(which exposed only a small read-only slice), and is not affiliated with or
endorsed by Secureframe. If you want to know why the API needed reverse
engineering, [The Secureframe API, for real](api-reality-report.md) is an
evidence-first, read-only audit of what it actually does. Optional, but it
explains the gaps you'll hit.

**Heads up:** this server can read and write your compliance data. Destructive
operations require `confirm=true`, and the whole server can be locked read-only
with `SECUREFRAME_READ_ONLY=true`. Always review AI-generated changes.

## Install

You need Secureframe API credentials (key + secret). The fastest path needs no
clone: [`uv`](https://docs.astral.sh/uv/) fetches, builds, and runs the server
straight from GitHub.

```bash
uvx --from git+https://github.com/misfitdev/better-secureframe-mcp-server.git better-secureframe-mcp
```

Prefer a local checkout? Clone and install the `better-secureframe-mcp` console
script instead:

```bash
git clone https://github.com/misfitdev/better-secureframe-mcp-server.git
cd better-secureframe-mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Connect a client

Add this to your client's MCP config. Claude Desktop
(`claude_desktop_config.json`), Cursor (`~/.cursor/mcp.json`), VS Code, and most
clients use this `mcpServers` shape:

```json
{
  "mcpServers": {
    "better-secureframe": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/misfitdev/better-secureframe-mcp-server.git",
        "better-secureframe-mcp"
      ],
      "env": {
        "SECUREFRAME_API_KEY": "your_key",
        "SECUREFRAME_API_SECRET": "your_secret"
      }
    }
  }
}
```

Claude Code, one command:

```bash
claude mcp add better-secureframe \
  -e SECUREFRAME_API_KEY=your_key -e SECUREFRAME_API_SECRET=your_secret \
  -- uvx --from git+https://github.com/misfitdev/better-secureframe-mcp-server.git better-secureframe-mcp
```

Codex (`~/.codex/config.toml`) and Gemini (`~/.gemini/settings.json`) take the
same `command` / `args` / `env` in their own format. Installed from a clone
instead of `uvx`? Set `command` to the absolute path of
`.venv/bin/better-secureframe-mcp` and drop the `args`.

### Environment variables

| Variable | Purpose |
|---|---|
| `SECUREFRAME_API_KEY` / `SECUREFRAME_API_SECRET` | credentials (required) |
| `SECUREFRAME_API_URL` | region endpoint (US default; UK `api-uk`) |
| `SECUREFRAME_ENV_FILE` | load creds from an env file outside the repo |
| `SECUREFRAME_READ_ONLY` | `true` disables all writes |
| `SECUREFRAME_TOOL_TAGS` / `SECUREFRAME_EXCLUDE_TAGS` | shrink the exposed tool set by tag |

## Filtering without Lucene

You talk to the assistant in plain English ("show me failing SOC 2 controls"); it
maps that to a typed tool call (`list_controls(health_status="unhealthy",
framework="soc2_alpha")`); the server compiles the Lucene query the API requires.
You don't need to know the field names. If you want the human-readable list of
which fields actually filter on each resource (and their allowed values), see
[PARAMETER_REFERENCE.md](https://github.com/misfitdev/better-secureframe-mcp-server/blob/main/PARAMETER_REFERENCE.md).

## What you get

- **Full API coverage:** 60 tools across all 64 API operations (lists, get-by-id
  detail, and writes), not just list endpoints.
- **Auto-pagination and response trimming** so you can actually retrieve
  everything without fighting the 100-per-page cap.
- **Write safety:** read/write annotations, `confirm=true` gates on destructive
  ops, and a global `SECUREFRAME_READ_ONLY` switch.
- **Discovery resources and workflow prompts** so the assistant finds filterable
  fields and runs common compliance flows on its own.

The full tool catalog and the always-current reference live in the
[README](https://github.com/misfitdev/better-secureframe-mcp-server#readme).

## Provenance

Verify a release artifact's build provenance:

```bash
gh attestation verify <file> --repo misfitdev/better-secureframe-mcp-server
```

## Source

[`github.com/misfitdev/better-secureframe-mcp-server`](https://github.com/misfitdev/better-secureframe-mcp-server)
