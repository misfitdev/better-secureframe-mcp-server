# Secureframe Local Upload Helpers

Local-file tools for use alongside the [official Secureframe MCP](https://mcp.secureframe.com/mcp_docs).

| Tool | Operation |
|---|---|
| `prepare_local_file_upload` | Compute filename, byte size, checksum, and content type. |
| `put_local_file_upload` | PUT local bytes to the signed URL returned by official staging. |
| `upload_security_questionnaire_file` | Create a questionnaire from a local file using multipart REST. |

Questionnaire uploads use Claude Code's Secureframe OAuth sign-in on macOS. Evidence uploads use signed storage URLs issued by the official MCP.

## Install

On the Mac where Claude Code is signed in to Secureframe:

```sh
uv tool install --force --refresh 'git+https://github.com/misfitdev/better-secureframe-mcp-server.git@codex/supplemental-local-uploads'
secureframe-probe-rest-auth
```

Find the executable with `command -v better-secureframe-mcp`, then add it as a separate MCP connection:

```sh
claude mcp add secureframe-local-uploads -- /absolute/path/better-secureframe-mcp
```

Keep the official Secureframe MCP connected. The local helper runs over stdio on the same Mac/account as your files and Claude Code sign-in.

## Upload evidence or a signed NDA

1. Call local `prepare_local_file_upload(file_path)`.
2. Call official `create_file_upload` with the returned metadata. Keep its `id`, `url`, and `headers`.
3. Call local `put_local_file_upload(file_path, url, headers, byte_size, checksum)`.
4. After success, call official `create_test_evidence`, `create_user_evidence`, or `update_trust_center_request` with `upload_id=id`.

User evidence requires `document_type`. Completion dates use `YYYY-MM-DD`. The local PUT reports `attached: false` until you complete the official attachment call.

Evidence is limited to 32 MB. Signed URLs expire after 15 minutes; upload IDs expire after one hour and are single-use. A changed file must be prepared and staged again.

## Upload a questionnaire

Call `upload_security_questionnaire_file(file_path, owner_id, ...)`. Optional inputs are `company_name`, `due_date`, and `questionnaire_template`.

Creation is not automatically retried. If the response is interrupted, check whether the questionnaire was created before resubmitting it.

## OAuth

To select a sign-in when multiple entries exist:

```sh
secureframe-probe-rest-auth --server-name secureframe --region us
```

For the running helper, optional `SECUREFRAME_CLAUDE_SERVER_NAME` and `SECUREFRAME_API_URL` settings select the entry. See [env.example](env.example) for settings.

Claude Code manages login and refresh. If the cached access token expires, use the official MCP in Claude Code to refresh/authenticate, then retry the local tool.

## Documentation

- [Installation](https://misfitdev.github.io/better-secureframe-mcp-server/install/)
- [Upload workflows](https://misfitdev.github.io/better-secureframe-mcp-server/uploads/)
- [OAuth and troubleshooting](https://misfitdev.github.io/better-secureframe-mcp-server/oauth/)
- [Tool reference](https://misfitdev.github.io/better-secureframe-mcp-server/reference/)

## Development

```sh
uv venv
uv pip install -e '.[dev]'
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

Use `.venv/bin/better-secureframe-mcp` for a checkout installation.

To build and check the documentation, use Ruby 3.3 and Bundler:

```sh
bundle install
just docs-check
```

To preview it locally:

```sh
bundle exec jekyll serve --source docs --destination docs/_site
```

Open `http://127.0.0.1:4000/better-secureframe-mcp-server/`.

[MIT license](LICENSE).
