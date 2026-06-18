# Better Secureframe MCP Server

A complete, modern [Model Context Protocol](https://modelcontextprotocol.io/)
server for the [Secureframe](https://secureframe.com) compliance automation
platform. It gives AI assistants like Claude and Cursor structured access to
your compliance data across SOC 2, ISO 27001, CMMC, FedRAMP, HIPAA, and more —
controls, tests, risks, vendors, evidence, personnel, and the rest of the API.

> **Why "Better"?** This started as the official
> [`secureframe/secureframe-mcp-server`](https://github.com/secureframe/secureframe-mcp-server),
> but it exposed only a small slice of the API (11 read-only list endpoints),
> still required hand-written Lucene, and hadn't been touched in a very long
> time. This is an independent fork — **completely rebuilt** with full read +
> write coverage of the API, structured (Lucene-free) filtering, modern MCP
> features, and a real test/CI setup. It is **not affiliated with or endorsed by
> Secureframe.** Install from
> [`misfitdev/better-secureframe-mcp-server`](https://github.com/misfitdev/better-secureframe-mcp-server).

> ⚠️ **This server can read and write your compliance data.** Write operations
> (create/update/archive/delete) are included and hit your live system of
> record. Destructive operations require explicit confirmation, and the whole
> server can be locked to read-only with `SECUREFRAME_READ_ONLY=true`. Always
> review AI-generated changes before relying on them.

📖 **Docs site:** <https://misfitdev.github.io/better-secureframe-mcp-server/> —
install/usage plus the **[Secureframe API Empirical Reality Report](https://misfitdev.github.io/better-secureframe-mcp-server/api-reality-report.html)**
(an evidence-first, anonymized audit of what the API actually supports).

---

## What's new

- **Full API coverage** — 60 tools spanning all 64 Secureframe API operations,
  including get-by-id detail tools and write operations, not just list endpoints.
- **No hand-written Lucene** — list tools take ordinary typed parameters
  (`health_status="fail"`, `framework="soc2_alpha"`) and build the API's Lucene
  query for you. A raw `q` parameter remains as an advanced escape hatch.
- **Auto-pagination** — pass `auto_paginate=true` to fetch every page (the API
  caps each page at 100 records).
- **Smaller responses** — the JSON:API envelope is flattened, nulls dropped, and
  `fields=[...]` lets you project only what you need.
- **Discovery resources** — `secureframe://reference/*` resources document the
  filterable fields, enum values, and framework keys per resource.
- **Workflow prompts** — ready-made flows for audit readiness, failing-control
  review, vendor risk, access review, and evidence gaps.
- **Write safety** — tools carry MCP annotations (`readOnlyHint`,
  `destructiveHint`, `idempotentHint`); destructive ops require `confirm=true`.

---

## Quick start

### Prerequisites
- Python 3.10+
- Secureframe API credentials ([how to get them](#obtaining-api-credentials))
- Claude Desktop, Cursor, or any MCP-compatible client

### Install

```bash
git clone https://github.com/misfitdev/better-secureframe-mcp-server.git
cd better-secureframe-mcp-server

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .

cp env.example .env                 # then edit .env with your credentials
```

---

## Connecting an MCP client

After `pip install -e .`, the server runs as the console script
`better-secureframe-mcp` (equivalently `python /abs/path/main.py`). It speaks
stdio. **Use absolute paths** in client configs — most clients don't run from
the repo. Examples below use `/abs/path/.venv/bin/better-secureframe-mcp`.

> There is no `claude mcp install` — the command is **`claude mcp add`**.

### Claude Code

```bash
claude mcp add better-secureframe \
  -e SECUREFRAME_API_KEY=your_key -e SECUREFRAME_API_SECRET=your_secret \
  -- /abs/path/.venv/bin/better-secureframe-mcp
```

- Default scope is `local` (your machine only, `~/.claude.json`). Add
  `--scope project` to write a committed `.mcp.json` for teammates, or
  `--scope user` for all your projects.
- Verify with `claude mcp list` / `/mcp` in a session.

Committed **`.mcp.json`** (use `${VAR}` so secrets aren't in the repo — values
come from the shell Claude Code was launched in):

```json
{
  "mcpServers": {
    "better-secureframe": {
      "command": "/abs/path/.venv/bin/better-secureframe-mcp",
      "env": {
        "SECUREFRAME_API_KEY": "${SECUREFRAME_API_KEY}",
        "SECUREFRAME_API_SECRET": "${SECUREFRAME_API_SECRET}",
        "SECUREFRAME_API_URL": "${SECUREFRAME_API_URL:-https://api.secureframe.com}"
      }
    }
  }
}
```

(`claude mcp add-json better-secureframe '{...}'` takes the same object on the CLI.)

### Claude Desktop / Cursor

Add to the MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json`
for Claude Desktop; Cursor's MCP settings are equivalent):

```json
{
  "mcpServers": {
    "better-secureframe": {
      "command": "/abs/path/.venv/bin/better-secureframe-mcp",
      "env": {
        "SECUREFRAME_API_KEY": "your_api_key",
        "SECUREFRAME_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

### Codex CLI

```bash
codex mcp add better-secureframe \
  --env SECUREFRAME_API_KEY=your_key --env SECUREFRAME_API_SECRET=your_secret \
  -- /abs/path/.venv/bin/better-secureframe-mcp
```

Or in `~/.codex/config.toml` (use `env_vars` to forward from your shell instead
of hardcoding):

```toml
[mcp_servers.better-secureframe]
command = "/abs/path/.venv/bin/better-secureframe-mcp"
env_vars = ["SECUREFRAME_API_KEY", "SECUREFRAME_API_SECRET"]
```

### Gemini CLI

```bash
gemini mcp add better-secureframe \
  -e SECUREFRAME_API_KEY="$SECUREFRAME_API_KEY" -e SECUREFRAME_API_SECRET="$SECUREFRAME_API_SECRET" \
  /abs/path/.venv/bin/better-secureframe-mcp
```

Or in `~/.gemini/settings.json` (`$VAR`/`${VAR}` reference your shell env):

```json
{
  "mcpServers": {
    "better-secureframe": {
      "command": "/abs/path/.venv/bin/better-secureframe-mcp",
      "env": {
        "SECUREFRAME_API_KEY": "$SECUREFRAME_API_KEY",
        "SECUREFRAME_API_SECRET": "$SECUREFRAME_API_SECRET"
      }
    }
  }
}
```

### Credentials

The server needs `SECUREFRAME_API_KEY` and `SECUREFRAME_API_SECRET`. Three ways,
pick by how much you want secrets to stay out of files:

1. **Inline in your client config** — simplest; fine for non-committed scopes
   (Claude Code `local`/`user`, Claude Desktop, `~/.codex/config.toml`).
2. **A gitignored `.env` in the repo** — the server auto-loads it
   (python-dotenv). Just `cp env.example .env` and fill it in; the config then
   needs no `env` block at all.
3. **An env file outside the repo** — set `SECUREFRAME_ENV_FILE=/tmp/secureframe.env`
   in the config and write your secrets to that path yourself. Best when the
   config is committed (`.mcp.json`, project `config.toml`): the secret never
   touches the repo or the config.

To avoid hardcoding, reference your shell environment instead: `${VAR}` in
Claude Code / Gemini configs, or `env_vars = [...]` in Codex.

A stdio server inherits the client's environment at launch, so you can't inject
credentials by exporting them in a subshell mid-session — option 3 is the clean
in-session path: point the config at `SECUREFRAME_ENV_FILE=/tmp/secureframe.env`,
write your keys to that file in your terminal (not through the agent, so they
stay out of the transcript), then reconnect the server (`/mcp`) or restart.

### Environment variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECUREFRAME_API_KEY` | Your Secureframe API key | ✅ |
| `SECUREFRAME_API_SECRET` | Your Secureframe API secret | ✅ |
| `SECUREFRAME_API_URL` | API endpoint (defaults to US) | ❌ |
| `SECUREFRAME_ENV_FILE` | Path to an env file to load (e.g. `/tmp/secureframe.env`); falls back to `./.env` | ❌ |
| `SECUREFRAME_READ_ONLY` | `true` disables all writes | ❌ |
| `SECUREFRAME_MCP_TRANSPORT` | `stdio` (default) or `http` | ❌ |
| `SECUREFRAME_MCP_HOST` / `SECUREFRAME_MCP_PORT` | Bind address for `http` (default `127.0.0.1:8000`) | ❌ |
| `SECUREFRAME_TOOL_TAGS` | Comma-separated tags to allowlist (e.g. `controls,tests`) | ❌ |
| `SECUREFRAME_EXCLUDE_TAGS` | Comma-separated tags to drop (e.g. `write`) | ❌ |

**Regions:** US `https://api.secureframe.com` (default) · UK `https://api-uk.secureframe.com`

---

## Filtering without Lucene

The Secureframe API only filters via a raw Lucene `q` string. Two layers remove
that burden so nobody hand-writes Lucene:

1. **You talk to an AI assistant in plain English.** Ask Claude (or Cursor, etc.)
   "show me failing SOC 2 controls" and it maps that to a tool call with typed
   parameters — `list_controls(health_status="unhealthy", framework="soc2_alpha")`.
2. **This server turns those parameters into the Lucene query.** It builds
   `q=health_status:unhealthy AND frameworks:soc2_alpha` and sends it to the API.

So yes — through a chatbot it's natural language in, the right records out, with
no Lucene written by anyone. The reason it's reliable (rather than the model
guessing field names) is that the tools expose the filterable fields as typed,
enum-constrained parameters, and the `secureframe://reference/*` resources list
the legal fields and values. The model fills in the blanks; the server, not the
model, generates the query string.

You can also call the tools directly in code with the same typed parameters:

```python
# Failing SOC 2 controls — no Lucene needed
list_controls(health_status="unhealthy", framework="soc2_alpha", auto_paginate=True)

# Failing integration tests, only the fields you care about
list_tests(health_status="fail", test_type="integration",
           fields=["title", "owner_name", "failure_message"])

# Inactive contractors
list_users(employee_type="contractor", active=False)

# High-risk, non-archived vendors
list_tprm_vendors(risk_level="High", archived=False)
```

Need something the typed parameters can't express? Use the raw escape hatch — it
is ANDed with any structured filters:

```python
list_tests(health_status="fail", q="next_due_date:[* TO 2026-01-01]")
```

The `secureframe://reference/fields/{entity}`, `.../enums`, and
`.../frameworks` resources list what each resource supports.

---

## Tools

All 64 API operations are covered by 60 tools. Reads are `list_*` / `get_*`;
writes are annotated and, where destructive, require `confirm=true`.

| Resource | Tools |
|----------|-------|
| Controls | `list_controls`, `get_control` |
| Tests | `list_tests`, `get_test`, `update_test`, `create_test_evidence`, `create_test_export`, `get_test_export` |
| Users | `list_users`, `get_user`, `update_user`, `create_user_evidence` |
| User accounts | `list_user_accounts`, `get_user_account`, `link_user_account` |
| Devices | `list_devices`, `get_device` |
| Risks | `list_risks`, `get_risk` |
| Frameworks | `list_frameworks`, `get_framework`, `list_framework_requirements`, `get_framework_requirement` |
| Cloud resources | `list_cloud_resources`, `get_cloud_resource`, `update_cloud_resource` |
| Repositories | `list_repositories`, `get_repository`, `update_repository` |
| Vendors | `list_vendors`, `get_vendor`, `archive_vendor` |
| TPRM vendors | `list_tprm_vendors`, `get_tprm_vendor`, `archive_tprm_vendor` |
| Integrations | `list_integration_connections`, `get_integration_connection`, `archive_integration_connection`, `publish_custom_integration_data` |
| Evidence | `get_evidence` |
| Comments | `list_comments`, `get_comment`, `create_comment`, `update_comment`, `delete_comment` |
| Knowledge Base | `get/create/update/delete_knowledge_base_question`, `get/create/update/delete_knowledge_base_answer` |
| Security questionnaires | `create_security_questionnaire` |
| Trust Center | `list_trust_center_requests`, `get_trust_center_request`, `update_trust_center_request` |
| Framework asset scopes | `list_framework_asset_scopes`, `create_framework_asset_scope` |
| Security settings | `list_user_security_settings` |

### Write safety

- Tools that mutate data are not marked read-only; destructive ones
  (`archive_*`, `delete_*`) set `destructiveHint` and require `confirm=true`.
- Set `SECUREFRAME_READ_ONLY=true` to refuse every write regardless of `confirm`.

---

## Keeping tool definitions out of context (deferred loading)

This server exposes 60 tools. Loading all their definitions into a model's
context costs tokens every request. There are two ways to avoid that — one for
the consumer, one for the operator.

**Consumer side (recommended): the Claude API tool search tool.** `defer_loading`
is set by the application making the Messages API request, not by this server.
Run the server over HTTP (`SECUREFRAME_MCP_TRANSPORT=http`), connect via the
[MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector),
and mark the toolset deferred alongside a
[tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool).
Claude then loads only the 3–5 tools each request actually needs:

```json
{
  "model": "claude-opus-4-8",
  "mcp_servers": [
    { "type": "url", "url": "https://your-host:8000/mcp", "name": "secureframe" }
  ],
  "tools": [
    { "type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex" },
    {
      "type": "mcp_toolset",
      "mcp_server_name": "secureframe",
      "default_config": { "defer_loading": true }
    }
  ]
}
```

Tool names are namespaced by resource and verb (`list_tests`, `archive_vendor`),
and descriptions carry domain keywords, so regex/BM25 tool search surfaces the
right tools reliably.

**Operator side: shrink the surface with tags.** Every tool is tagged with its
resource plus `read`/`write`. Use `SECUREFRAME_EXCLUDE_TAGS=write` for a
read-only server (24 write tools removed), or `SECUREFRAME_TOOL_TAGS=controls,tests`
to expose only what a deployment needs. This reduces front-loaded tokens for any
client, including ones that don't support tool search.

---

## Resources & prompts

**Resources** (reference data the assistant can read):
- `secureframe://reference/fields` and `.../fields/{entity}`
- `secureframe://reference/enums`
- `secureframe://reference/frameworks`

**Prompts** (multi-step workflows): `failing_controls_review`,
`audit_readiness`, `vendor_risk_review`, `access_review`, `evidence_gaps`.

---

## Development

[mise](https://mise.jdx.dev) provides the toolchain (Python, uv, ruff, just,
lefthook) and the virtualenv; [just](https://just.systems) runs the tasks; git
hooks are managed by [lefthook](https://lefthook.dev). With mise installed and
activated in the repo:

```bash
just setup        # install deps (into .venv) + git hooks
just test         # run the test suite
just lint         # ruff
just fmt          # auto-format and fix
just build        # build sdist + wheel and validate
just run          # start the server over stdio
just refresh-spec # re-vendor docs/openapi.yaml from the live docs
```

`just` (no args) lists everything. Pre-commit runs ruff lint + format check;
pre-push runs the test suite.

CI (`.github/workflows/ci.yml`) lints, tests across Python 3.10–3.13, and builds
the package. Tagging `vX.Y.Z` triggers `release.yml`, which builds, generates
SLSA build provenance (`actions/attest-build-provenance`), and cuts a GitHub
Release. (PyPI publishing is present but commented out.) Verify provenance with:

```bash
gh attestation verify <downloaded-file> --repo misfitdev/better-secureframe-mcp-server
```

The vendored OpenAPI spec lives at `docs/openapi.yaml`; `src/better_secureframe_mcp/schema.py`
mirrors its filterable fields and enums.

---

## Obtaining API credentials

In the Secureframe console: **Your Profile → Company settings → API keys**.
The secret is shown only once at creation — store it securely. Both the key and
secret go in the `Authorization` header (handled for you by this server).

---

## License

MIT — see [LICENSE](LICENSE).
