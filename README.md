# Secureframe Local Upload Helpers

Three local-file tools for the [official Secureframe MCP](https://mcp.secureframe.com/mcp_docs). The official server handles Secureframe data; this one reads files on your Mac for evidence and questionnaires.

## Install

On the signed-in Mac:

```sh
uv tool install --force --refresh 'git+https://github.com/misfitdev/better-secureframe-mcp-server.git@main'
claude mcp add secureframe-local-uploads -- "$(command -v better-secureframe-mcp)"
```

Keep the official MCP connected and reload the client's MCP connections.

## Evidence and signed NDAs

1. Local `prepare_local_file_upload(file_path)` computes metadata.
2. Official `create_file_upload` stages it and returns `id`, `url`, and `headers`.
3. Local `put_local_file_upload(file_path, url, headers, byte_size, checksum)` sends the bytes.
4. Official `create_test_evidence`, `create_user_evidence`, or `update_trust_center_request` attaches `upload_id=id`.

User evidence requires `document_type`. Evidence is limited to 32 MB. Signed URLs expire in 15 minutes; upload IDs expire in one hour and are single-use.

## Questionnaires

Call `upload_security_questionnaire_file(file_path, owner_id)`. Optional inputs: `company_name`, `due_date` (`YYYY-MM-DD`), and `questionnaire_template`.

If OAuth expires, refresh/authenticate through the official MCP in Claude Code and retry.

## Optional settings

No settings file or credentials are needed. If Claude Code has multiple Secureframe sign-ins, set `SECUREFRAME_CLAUDE_SERVER_NAME` to the cached server name and, if needed, `SECUREFRAME_API_URL` to `https://api.secureframe.com` or `https://api-uk.secureframe.com`.

For a custom Claude Code profile, set `CLAUDE_CONFIG_DIR` to its directory. `SECUREFRAME_CLAUDE_KEYCHAIN_SERVICE` can select a custom macOS Keychain service.

## Development

```sh
uv venv
uv pip install -e '.[dev]'
just test
just lint
```

The [upload guide](https://misfitdev.github.io/better-secureframe-mcp-server/) is a static page in `docs/`.

[MIT license](LICENSE).
