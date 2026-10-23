---
title: Upload local files to Secureframe
description: Three small tools that let Claude Code send files from your Mac to Secureframe.
permalink: /
---

Keep Secureframe's official MCP connected. This helper adds the local file access its tools need for evidence and questionnaires.

## Set up

On the Mac where Claude Code is signed in to Secureframe, run:

```sh
uv tool install --force --refresh 'git+{{ site.repository_url }}.git@{{ site.install_ref }}'
claude mcp add secureframe-local-uploads -- "$(command -v better-secureframe-mcp)"
```

Then reload Claude Code's MCP connections. The official Secureframe MCP handles ordinary Secureframe work; this helper handles local files.

## Add evidence or a signed NDA

Ask Claude Code to attach a local file. It will use both servers in this order:

1. **Prepare:** this helper reads the file and calculates its size and checksum.
2. **Stage:** the official MCP creates a Secureframe upload and returns a signed URL.
3. **Upload:** this helper sends the file to that URL.
4. **Attach:** the official MCP links the upload to a test, user, or Trust Center request.

Files can be up to **32 MB**. The signed URL lasts 15 minutes; the upload ID lasts one hour and can be used once. If the file changes, start again from step 1. User evidence also needs a `document_type`.

## Upload a questionnaire

Ask Claude Code to use `upload_security_questionnaire_file` with a local `file_path` and Secureframe `owner_id`. You can also provide `company_name`, `due_date` (`YYYY-MM-DD`), or `questionnaire_template`.

This tool uses Claude Code's Secureframe sign-in on macOS. If the sign-in expires, refresh it through the official MCP and retry. Before retrying an interrupted upload, check whether Secureframe created the questionnaire.

For multiple Secureframe sign-ins, see [optional settings]({{ site.repository_url }}/blob/{{ site.install_ref }}/env.example). The [source and development instructions]({{ site.repository_url }}) are on GitHub.
