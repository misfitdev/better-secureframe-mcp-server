---
title: Secureframe uploads
dek: "Local file tools for the official Secureframe MCP."
permalink: /
---

## Install

On the Mac where Claude Code is signed in to Secureframe:

```sh
uv tool install --force --refresh 'git+{{ site.repository_url }}.git@{{ site.install_ref }}'
claude mcp add secureframe-local-uploads -- "$(command -v better-secureframe-mcp)"
```

Keep the official Secureframe MCP connected. Reload the client's MCP connections after installation.

## Evidence

1. Call local `prepare_local_file_upload(file_path)`.
2. Call official `create_file_upload` with the returned metadata. Keep its `id`, `url`, and `headers`.
3. Call local `put_local_file_upload(file_path, url, headers, byte_size, checksum)`.
4. Call official `create_test_evidence` or `create_user_evidence` with `upload_id=id`.

User evidence requires `document_type`. For a signed NDA, attach the upload with official `update_trust_center_request`.

Evidence is limited to 32 MB. Signed URLs expire after 15 minutes; upload IDs expire after one hour and are single-use. If the file changes, prepare and stage it again.

## Questionnaires

```text
upload_security_questionnaire_file(file_path, owner_id)
```

Optional inputs: `company_name`, `due_date` (`YYYY-MM-DD`), and `questionnaire_template`.

The tool uploads the file as multipart using Claude Code's Secureframe OAuth sign-in on macOS. If the session expires, use the official MCP in Claude Code to refresh/authenticate, then retry.

For multiple sign-ins, select the cached server with `SECUREFRAME_CLAUDE_SERVER_NAME` and the region with `SECUREFRAME_API_URL`. See [optional settings]({{ site.repository_url }}/blob/{{ site.install_ref }}/env.example).

Questionnaire creation is not automatically retried. If a response is interrupted, check whether the questionnaire was created before resubmitting it.
