---
title: MCP Server — Install & Usage
---

# Better Secureframe MCP Server — Install & Usage

Read + write access to the Secureframe compliance platform (SOC 2, ISO 27001,
CMMC, FedRAMP, HIPAA, and more) for AI assistants like Claude and Cursor.

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
> **[API Empirical Reality Report](api-reality-report.md)** for the full picture
> of what is and isn't possible — it explains why some otherwise-obvious tools
> (e.g. updating a control's owner, listing a test's evidence) don't exist.

## Install

```bash
git clone https://github.com/misfitdev/better-secureframe-mcp-server.git
cd better-secureframe-mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp env.example .env   # add your credentials
```

This provides the `better-secureframe-mcp` console script (stdio transport).

## Connect a client

Use the absolute path to the console script. Example for Claude Code:

```bash
claude mcp add better-secureframe \
  -e SECUREFRAME_API_KEY=your_key -e SECUREFRAME_API_SECRET=your_secret \
  -- /abs/path/.venv/bin/better-secureframe-mcp
```

Claude Desktop / Cursor (`mcpServers` JSON), Codex (`codex mcp add` /
`~/.codex/config.toml`), and Gemini (`gemini mcp add` / `~/.gemini/settings.json`)
are equivalent — see the README for each.

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
The `secureframe://reference/*` resources document the filterable fields.

## Provenance

Releases ship with SLSA build provenance via `actions/attest-build-provenance`.
Verify a downloaded artifact:

```bash
gh attestation verify <file> --repo misfitdev/better-secureframe-mcp-server
```
