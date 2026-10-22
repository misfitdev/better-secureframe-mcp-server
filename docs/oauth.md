---
title: OAuth
dek: "Use the Secureframe sign-in stored by Claude Code on macOS."
permalink: /oauth/
---

Authenticate the official Secureframe server through Claude Code's `/mcp` menu. The local server reads that sign-in for questionnaire uploads.

Evidence storage PUTs use the signed URL returned by official `create_file_upload`.

## Select a sign-in

The helper selects a cached OAuth entry by its official Secureframe URL:

| OAuth server | REST destination |
|---|---|
| `https://mcp.secureframe.com/` | `https://api.secureframe.com` |
| `https://mcp-uk.secureframe.com/` | `https://api-uk.secureframe.com` |

A single matching entry determines the region. If multiple sign-ins exist, select the server name and region:

```sh
secureframe-probe-rest-auth --server-name secureframe --region uk
```

For the running MCP server, set `SECUREFRAME_CLAUDE_SERVER_NAME` and, if needed, `SECUREFRAME_API_URL`. The selected user/company determines where files are uploaded and which permissions apply.

## Profiles and Keychain access

Run the helper under the same macOS account and Claude Code profile as the Secureframe sign-in. `CLAUDE_CONFIG_DIR` and `CLAUDE_SECURESTORAGE_CONFIG_DIR` select the profile. `SECUREFRAME_CLAUDE_KEYCHAIN_SERVICE` selects a custom Keychain service.

macOS may prompt for access to Claude Code's Keychain record. Unlock the login Keychain and allow access when prompted.

## Expiry

Claude Code manages the OAuth login and token refresh. The helper rereads the credential for each REST call.

If the cached access token has expired, use the official Secureframe MCP in Claude Code to refresh/authenticate, then retry the local tool.

## Check access

```sh
secureframe-probe-rest-auth
```

The probe makes one GET request to `/users?page=1&per_page=1`. It returns the HTTP status and authentication result. Exit codes are listed in the [command reference]({{ '/reference/#probe-command' | relative_url }}).

## Troubleshooting

| Result | Action |
|---|---|
| No credential cache | Sign in to the official Secureframe server through Claude Code's `/mcp` menu on this Mac/account. |
| No matching entry | Check the official URL, server name, region, and Claude profile. |
| Multiple sign-ins | Select a server name and, if needed, a region. |
| Cached token expired | Use the official MCP in Claude Code to refresh/authenticate, then rerun. |
| Keychain denied or locked | Unlock the login Keychain and allow access if macOS prompts. |
| REST returns 401/403 | Check the OAuth session and the user's Secureframe permissions. |
| Unsupported cache format | Update the helper and report the Claude Code version and sanitized error. |
| A different OS | Run questionnaire uploads on the signed-in Mac. |
