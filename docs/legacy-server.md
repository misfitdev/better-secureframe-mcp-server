# Legacy tool surface

The default server supplements the official Secureframe MCP with three local upload tools. The earlier 60-tool surface is retained for existing workflows by setting `SECUREFRAME_MCP_MODE=legacy`.

**Authentication is OAuth-only in both modes.** Legacy REST calls reuse Claude Code's existing Secureframe OAuth sign-in on macOS. API keys and manually supplied tokens are no longer supported. See the [main setup guide](../README.md) for installation, sign-in selection, and expiry handling.

```sh
SECUREFRAME_MCP_MODE=legacy better-secureframe-mcp
```

## Capabilities

Legacy tools cover controls, tests, users, user accounts, devices, risks, frameworks and requirements, cloud resources, repositories, vendors, TPRM, integrations, evidence, comments, Knowledge Base, questionnaires, Trust Center, framework asset scopes, and security settings. They preserve the earlier list/get/create/update/archive/delete tool names.

List tools accept structured filter arguments and advanced raw Lucene `q`. `auto_paginate=true` combines pages, with a 50-page runaway guard and a `truncated` indicator. Responses are flattened and nulls removed; `fields` projects selected attributes. See the [parameter reference](../PARAMETER_REFERENCE.md).

The server exposes reference resources for fields, enums, framework keys, and the vendored OpenAPI specification, plus workflow prompts for audit readiness, failing controls, vendor risk, access review, and evidence gaps.

Destructive tools require `confirm=true`. `SECUREFRAME_READ_ONLY=true` refuses writes, and the tool-tag filters can hide writes or restrict categories. The optional HTTP transport settings remain available in legacy mode.

The official MCP has broader coverage than this historical tool surface. Prefer the default supplemental mode and official tools for current workflows. In particular, the supplemental evidence workflow leaves staging and attachment to official tools, which require a document type for user evidence.

## OAuth lifecycle

Each REST call reads the current cached OAuth credential. The shared HTTP connection pool does not retain an Authorization header between calls, so a later call picks up credentials refreshed by Claude Code. This server does not refresh or modify Claude's credential cache itself.

All REST destinations are restricted to the official US/UK API origins. A missing or expired cached sign-in fails without a fallback credential. Metadata and tool registration do not require a credential lookup at startup.
