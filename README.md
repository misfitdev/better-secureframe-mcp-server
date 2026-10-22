# Secureframe Local Upload Helpers

A supplemental MCP server for local-file uploads alongside the [official Secureframe MCP](https://mcp.secureframe.com/mcp_docs). Keep ordinary reads and writes on the official server and its existing signed-in session.

**OAuth only.** On macOS, REST calls reuse the Secureframe OAuth sign-in already stored by Claude Code. No API keys, copied access tokens, auth-mode settings, or credentials file are supported or required.

The default server exposes three tools:

| Tool | Purpose | Authorization |
|---|---|---|
| `prepare_local_file_upload` | Compute filename, byte size, base64 MD5 checksum and MIME type locally. No file bytes enter the conversation. | None |
| `put_local_file_upload` | PUT raw local bytes to the signed URL returned by official `create_file_upload`. | Signed URL issued through official MCP's OAuth session |
| `upload_security_questionnaire_file` | Upload realistic questionnaire files through REST multipart, avoiding the official MCP's small inline-base64 limit. | Claude Code's cached Secureframe OAuth sign-in |

This server is independent of Secureframe. The previous 60-tool server remains available in [legacy mode](docs/legacy-server.md), using the same OAuth-only authentication.

## Install and connect

On the macOS machine where Claude Code is signed in to the official Secureframe MCP:

```sh
uv tool install --force --refresh 'git+https://github.com/misfitdev/better-secureframe-mcp-server.git@codex/supplemental-local-uploads'
secureframe-probe-rest-auth
```

No env file or copied credential is needed. The probe makes **one GET `/users?page=1&per_page=1`** and prints only the status and auth result, never personnel data or credentials. It performs no writes. The previously shipped `--claude-code` flag remains accepted, but OAuth reuse is now the only method.

Keep your official MCP connection configured and signed in. Add this helper separately, using the absolute path reported by `command -v better-secureframe-mcp`:

```sh
claude mcp add secureframe-local-uploads -- /absolute/path/better-secureframe-mcp
```

Other MCP clients can launch that executable over stdio on the same Mac/account. The supplemental server supports stdio only because it reads local files. Evidence helpers do not read the credential cache: the official MCP issues their signed upload URLs.

For development from a checkout:

```sh
uv venv
uv pip install -e '.[dev]'
```

**Existing installations:** the executable defaults to supplemental mode. Set `SECUREFRAME_MCP_MODE=legacy` to retain the previous tools. Authentication is OAuth-only in either mode; previous API-key/manual-token environment variables are no longer read.

## Upload evidence using your existing official login

Ask your assistant to upload a local file and use these tools in sequence:

1. **Local:** `prepare_local_file_upload(file_path)`.
2. **Official:** `create_file_upload` with the returned `filename`, `byte_size`, `checksum`, and `content_type`. Keep its `id`, `url`, and `headers`.
3. **Local:** `put_local_file_upload(file_path, url, headers, byte_size, checksum)`. Pass every returned header unchanged and the metadata from step 1.
4. **Official:** `create_test_evidence(test_id, upload_id=id)` or `create_user_evidence(user_id, upload_id=id, document_type=...)`. Optional `activity_completion` is a `YYYY-MM-DD` date.

This also works for signed NDAs via official `update_trust_center_request(upload_id=id, ...)`. The helper only sends bytes; it does not attach the file. Do not call the attachment tool after a failed PUT.

The helper verifies the staged checksum and size, sends raw bytes rather than multipart/base64, and does not follow redirects or add OAuth credentials to storage requests. Signed URLs must use HTTPS and resolve to a public host.

Upstream limits evidence to **32 MB**. Signed URLs expire after **15 minutes**; upload IDs expire after **1 hour** and are **single-use**. These are upstream restrictions. User evidence requires a document type; the old local user-evidence tool omitted this required API parameter.

## Upload a realistic questionnaire

Call `upload_security_questionnaire_file(file_path, owner_id, ...)`. Optional inputs are `company_name`, `due_date`, and `questionnaire_template` (the current API enum).

The [REST API contract](https://api.secureframe.com/docs#tag/security-questionnaire/POST/security_questionnaires) accepts multipart `file` uploads; it does not list `upload_id` as a questionnaire input. The helper therefore streams the local file to REST using Claude Code's existing OAuth sign-in. It imposes no small inline-base64 limit. Server-side REST file limits still apply and have not been measured here. Creation is not automatically retried.

A real probe on a signed-in Mac returned HTTP 200 with the cached OAuth credential for reading users. This establishes REST read acceptance; it does not establish questionnaire write permission or a successful live multipart upload. Automated tests cover multipart behavior with mocked requests.

## How OAuth reuse works

The loader reads Claude Code's `mcpOAuth` entry matching an exact official Secureframe MCP URL. It never substitutes Claude's account token or another MCP server's credential. macOS may ask you to allow Keychain access.

If multiple sign-ins exist, select the cached server explicitly:

```sh
secureframe-probe-rest-auth --server-name secureframe --region us
```

`--region` accepts `us` or `uk`; a single matching cached login automatically selects its API region. For the running helper, optional `SECUREFRAME_CLAUDE_SERVER_NAME` and `SECUREFRAME_API_URL` settings make the same selection. Ambiguous sign-ins fail rather than silently selecting a different company.

The reader supports Claude Code's Keychain format (checked against installed Claude Code 2.1.283), plus its `.credentials.json` fallback **only when the Keychain item does not exist**. It respects `CLAUDE_CONFIG_DIR` / `CLAUDE_SECURESTORAGE_CONFIG_DIR`; `SECUREFRAME_CLAUDE_KEYCHAIN_SERVICE` selects a nonstandard service name. Future Claude Code storage changes may require an adapter update.

The loader never writes the cache, rotates a refresh token, or starts a new login. If the cached access token has expired, use the official server in Claude Code to refresh/authenticate, then retry. REST calls reread the cache to pick up Claude's refreshed credential. There is no fallback to another auth method. Authenticated calls are restricted to official US/UK API origins.

## Settings and development

`SECUREFRAME_READ_ONLY=true` blocks both upload tools while leaving local metadata preparation available. `SECUREFRAME_TOOL_TAGS` / `SECUREFRAME_EXCLUDE_TAGS` filter exposed tools; tags include `uploads`, `questionnaires`, `read`, and `write`. See [env.example](env.example) for optional settings. Env files are optional configuration only, with no credentials to supply.

```sh
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

API contracts were checked against live OpenAPI documentation on 2026-10-22. Local tests use synthetic credential caches and mocked network requests; they do not access the real Keychain or perform live uploads.

[MIT license](LICENSE).
