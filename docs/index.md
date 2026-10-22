---
title: Secureframe Local Upload Helpers
kicker: Get started
dek: "Supplement the official Secureframe MCP with local-file uploads using its existing OAuth sign-in."
---

Use the official [Secureframe MCP](https://mcp.secureframe.com/mcp_docs) for normal reads and writes. This independent supplemental server adds local-file evidence helpers and realistic multipart questionnaire uploads.

Authentication is **OAuth only**: REST calls reuse Claude Code's existing Secureframe sign-in from macOS Keychain. No API keys, copied tokens, separate login, or credentials file are needed.

## Install and check OAuth

On the Mac where Claude Code is already signed in:

```sh
uv tool install --force --refresh 'git+https://github.com/misfitdev/better-secureframe-mcp-server.git@codex/supplemental-local-uploads'
secureframe-probe-rest-auth
```

The probe performs one read-only request and reports its status without printing credentials or personnel data. If multiple sign-ins exist, add `--server-name NAME` and optionally `--region us` or `--region uk`.

Add the helper to your MCP client using its absolute executable path:

```sh
claude mcp add secureframe-local-uploads -- /absolute/path/better-secureframe-mcp
```

Keep the official MCP connected. This helper runs over stdio on the same Mac/account.

## Local evidence files

1. Call local `prepare_local_file_upload(file_path)` to compute metadata.
2. Call official `create_file_upload` to stage it through the existing OAuth session.
3. Call local `put_local_file_upload` with the returned signed URL/headers and prepared checksum/size.
4. Call official `create_test_evidence`, `create_user_evidence`, or `update_trust_center_request` to attach the upload ID.

The upstream staging limit is 32 MB. URLs expire in 15 minutes; upload IDs expire in one hour and are single-use. User evidence requires `document_type`.

## Questionnaire files

`upload_security_questionnaire_file(file_path, owner_id, ...)` streams multipart bytes to the REST endpoint using the cached OAuth sign-in. It avoids the official MCP's small inline-base64 limit; upstream file limits still apply. Live REST read acceptance has been confirmed on a signed-in system; live questionnaire writes remain unverified.

## Settings

`SECUREFRAME_READ_ONLY=true` blocks uploads. Optional tool-tag filters control exposed tools. Set `SECUREFRAME_MCP_MODE=legacy` to retain the earlier 60-tool surface, which now also uses OAuth only.

The helper reads but never refreshes or modifies Claude Code's cache. When a token expires, use the official MCP in Claude Code to refresh/authenticate and retry.

See the [full setup and usage guide](https://github.com/misfitdev/better-secureframe-mcp-server/tree/codex/supplemental-local-uploads#readme) and [source](https://github.com/misfitdev/better-secureframe-mcp-server).
