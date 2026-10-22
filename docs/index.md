---
title: Secureframe upload tools
dek: "Upload evidence, signed NDAs, and questionnaires from your Mac."
permalink: /
---

Run this server alongside the [official Secureframe MCP](https://mcp.secureframe.com/mcp_docs). It provides three local-file tools over stdio.

- `prepare_local_file_upload`: read a local file and compute its upload metadata.
- `put_local_file_upload`: send the file bytes to a signed upload URL.
- `upload_security_questionnaire_file`: create a questionnaire from a local file.

## Install

On the Mac where Claude Code is signed in to Secureframe:

```sh
uv tool install --force --refresh 'git+{{ site.repository_url }}.git@{{ site.install_ref }}'
secureframe-probe-rest-auth
```

[Connect the server]({{ '/install/' | relative_url }}) alongside your official MCP connection.

## Use the tools

- [Evidence and signed NDAs]({{ '/uploads/#evidence-and-signed-ndas' | relative_url }}): prepare the file, stage the upload with the official MCP, send bytes locally, and attach the upload ID.
- [Questionnaire files]({{ '/uploads/#questionnaire-files' | relative_url }}): call the local questionnaire tool with a file path and owner ID.
- [Tool reference]({{ '/reference/' | relative_url }}): parameters, return values, and settings.

## Authentication

Questionnaire uploads use Claude Code's Secureframe OAuth sign-in on macOS. Evidence uploads use signed storage URLs issued by the official MCP.

For sign-in selection, regions, expiry, and access errors, see [OAuth]({{ '/oauth/' | relative_url }}).
