---
title: MCP server
kicker: Install & usage
dek: Installing the server and wiring it into an MCP client.
---

Full read and write access to the Secureframe compliance platform, for AI
assistants.

> ⚠️ This server can **read and write** your compliance data. Destructive
> operations require `confirm=true`; the whole server can be locked read-only
> with `SECUREFRAME_READ_ONLY=true`. Always review AI-generated changes.

For the authoritative, always-current version of everything below, see the
[README in the repo](https://github.com/misfitdev/better-secureframe-mcp-server#readme).

## Highlights

- **Full API coverage** — 60 tools across all 64 API operations (lists,
  get-by-id detail, and writes), not just list endpoints.
- **No hand-written Lucene** — list tools take typed parameters
  (`health_status="fail"`, `framework="soc2_alpha"`) and build the query for you;
  a raw `q` escape hatch remains for advanced cases.
- **Auto-pagination, response trimming, write safety** (annotations, confirm
  gates, read-only mode).
- **Discovery resources & workflow prompts** so the assistant can find filterable
  fields and run common compliance flows.

> Reality check: the underlying Secureframe API is inconsistent about which
> fields are actually filterable, never returns `owner_id`, and exposes no
> entity relationships. See the
> **[The Secureframe API, for real](api-reality-report.md)** for the full picture
> of what is and isn't possible — it explains why some otherwise-obvious tools
> (e.g. updating a control's owner, listing a test's evidence) don't exist.

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

You talk to the assistant in plain English ("show me failing SOC 2 controls");
it maps that to a typed tool call (`list_controls(health_status="unhealthy",
framework="soc2_alpha")`); the server compiles the Lucene query the API requires.
You don't need to know the field names — describe what you want in plain English
and the assistant maps it. If you want the human-readable list of which fields
actually filter on each resource (and their allowed values), see
[PARAMETER_REFERENCE.md](https://github.com/misfitdev/better-secureframe-mcp-server/blob/main/PARAMETER_REFERENCE.md).
(The server also ships this as machine-readable data the assistant consults
automatically — you never fetch it yourself.)

## Provenance

Verify a release artifact's build provenance:

```bash
gh attestation verify <file> --repo misfitdev/better-secureframe-mcp-server
```
