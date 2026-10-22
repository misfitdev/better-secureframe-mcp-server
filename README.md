# Secureframe Local Upload Helpers

A supplemental MCP server for local-file uploads alongside the [official Secureframe MCP](https://mcp.secureframe.com/mcp_docs). Keep ordinary reads and writes on the official server and its existing signed-in session.

The default server exposes three tools:

| Tool | Purpose | Authentication |
|---|---|---|
| `prepare_local_file_upload` | Compute filename, byte size, base64 MD5 checksum and MIME type locally. No file bytes enter the conversation. | None |
| `put_local_file_upload` | PUT raw local bytes to the signed URL returned by official `create_file_upload`. | Signed URL supplied by official MCP |
| `upload_security_questionnaire_file` | Upload realistic questionnaire files through the documented REST multipart endpoint, avoiding the official MCP's small inline-base64 limit. | API key/secret, or explicitly experimental MCP bearer token |

This server is independent of Secureframe. The previous 60-tool server remains available in [legacy mode](docs/legacy-server.md).

## Install and connect

```sh
uv venv
uv pip install -e '.[dev]'
```

Keep your official MCP connection configured and signed in. Add this local server separately (use the absolute executable path):

```sh
claude mcp add secureframe-local-uploads -- /absolute/path/.venv/bin/better-secureframe-mcp
```

Or configure another MCP client to launch that executable over stdio. Evidence helpers require no credentials, separate login, access to another client's token cache, or OAuth token forwarding. The supplemental server supports stdio only because it reads local files.

**Existing installations:** the executable now defaults to supplemental mode. Set `SECUREFRAME_MCP_MODE=legacy` to keep the previous tools and transport options.

## Upload evidence using your existing official login

Ask your assistant to upload a local file and use these tools in sequence:

1. **Local:** `prepare_local_file_upload(file_path)`.
2. **Official:** `create_file_upload` with the returned `filename`, `byte_size`, `checksum`, and `content_type`. Keep its `id`, `url`, and `headers`.
3. **Local:** `put_local_file_upload(file_path, url, headers, byte_size, checksum)`. Pass every returned header unchanged and the metadata from step 1.
4. **Official:** `create_test_evidence(test_id, upload_id=id)` or `create_user_evidence(user_id, upload_id=id, document_type=...)`. Optional `activity_completion` is a `YYYY-MM-DD` date.

This also works for signed NDAs via official `update_trust_center_request(upload_id=id, ...)`. The helper only sends bytes; it does not attach the file. Do not call the attachment tool after a failed PUT.

The helper verifies that the file still matches the staged checksum and size, sends raw bytes rather than multipart/base64, and does not follow redirects or add API credentials to storage requests. Signed URLs must use HTTPS and resolve to a public host.

The upstream staging endpoint limits files to **32 MB**. Signed URLs expire after **15 minutes**; upload IDs expire after **1 hour** and are **single-use**. These are upstream restrictions, not limits this helper bypasses. User evidence requires a document type; the old local user-evidence tool omitted this required API parameter.

## Upload a realistic questionnaire

The current [REST API contract](https://api.secureframe.com/docs#tag/security-questionnaire/POST/security_questionnaires) accepts multipart `file` uploads. It does not list `upload_id` as a questionnaire input. Consequently, the evidence signed-URL workflow cannot replace this call.

Configure credentials in your local environment or an env file outside the repository:

```sh
export SECUREFRAME_ENV_FILE=/absolute/path/secureframe-local.env
```

The referenced file can contain:

```dotenv
SECUREFRAME_API_KEY=your_key
SECUREFRAME_API_SECRET=your_secret
# UK: https://api-uk.secureframe.com
SECUREFRAME_API_URL=https://api.secureframe.com
```

Then call `upload_security_questionnaire_file(file_path, owner_id, ...)`. Optional inputs are `company_name`, `due_date`, and `questionnaire_template` (the current API enum). Multipart is streamed from the file; there is no small inline-base64 limit imposed by this wrapper. Server-side REST file limits still apply and have not been measured here. Creation is not automatically retried.

API keys and your official OAuth login can refer to different users/companies: use credentials for the intended destination.

## Experiment: does the REST API accept the existing MCP token?

**Unverified:** official OAuth discovery advertises the MCP resource and `mcp` scope. The public REST contract documents API key/secret authentication, not bearer tokens. The code provides an explicit opt-in so this can be checked on a signed-in system without assuming compatibility.

Locally obtain a current access token from the signed-in client's supported credential interface or cache. Cache formats and OS keychains differ by client; this project does not guess their locations or modify their caches. Supply the access token as `SECUREFRAME_MCP_ACCESS_TOKEN` in the private env file, then add:

```dotenv
SECUREFRAME_REST_AUTH=mcp_token
```

Do not paste the token into chat, commit it, or pass it as a command-line argument. Run:

```sh
SECUREFRAME_ENV_FILE=/absolute/path/secureframe-local.env .venv/bin/secureframe-probe-rest-auth
```

The probe makes **one GET `/users?page=1&per_page=1`** and prints only the status and auth result, never personnel data or the credential. It performs no writes. A 2xx response establishes that this token worked for that read; it does not establish write permissions. A 401/403 does not by itself distinguish token expiry, unsupported bearer auth, and user permissions.

In this experimental mode, questionnaire uploads use `Authorization: Bearer <token>`. There is no automatic fallback to an API key. The helper does not refresh the token, so supply a fresh access token when needed. Concurrently sharing a rotating refresh-token cache would require coordination with the owning client; this implementation only consumes an explicitly supplied access token.

Set `SECUREFRAME_REST_AUTH=api_key` (the default) to use documented API authentication. Supplemental authenticated REST calls are limited to the official US/UK API origins. No REST token compatibility claim is made until verified against the actual service.

## Settings and development

`SECUREFRAME_READ_ONLY=true` blocks both upload tools while leaving local metadata preparation available. Existing `SECUREFRAME_TOOL_TAGS` / `SECUREFRAME_EXCLUDE_TAGS` filters apply; tags include `uploads`, `questionnaires`, `read`, and `write`. Env files load at process startup, so restart the helper after changing credentials.

```sh
uv pip install -e '.[dev]'
.venv/bin/pytest -q
.venv/bin/ruff check src/better_secureframe_mcp/supplemental.py src/better_secureframe_mcp/rest_auth.py
```

API contracts were checked against the live OpenAPI documentation on 2026-10-22. Automated tests mock MCP storage/REST boundaries; they do not prove real-service token acceptance or successful uploads.

[MIT license](LICENSE).
