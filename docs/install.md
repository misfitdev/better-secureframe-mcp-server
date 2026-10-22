---
title: Install alongside the official MCP
dek: "Use the Mac where Claude Code already holds your Secureframe sign-in."
permalink: /install/
---

You need macOS, [uv](https://docs.astral.sh/uv/getting-started/installation/), and Claude Code signed in to the official Secureframe MCP. The helper and your files must be on the same Mac/account as that sign-in for questionnaire uploads.

## Keep the official connection

If you are already signed in, keep that connection. Otherwise add the official server and authenticate through Claude Code's `/mcp` menu:

```sh
claude mcp add --transport http secureframe https://mcp.secureframe.com/
```

Use `https://mcp-uk.secureframe.com/` for a UK workspace. The official server's consent flow selects the user/company that this helper will also act as.

## Install or update the local helper

```sh
uv tool install --force --refresh 'git+{{ site.repository_url }}.git@{{ site.install_ref }}'
```

This installs the server from the current development branch.

For a checkout instead:

```sh
git clone --branch {{ site.install_ref }} {{ site.repository_url }}.git
cd better-secureframe-mcp-server
uv venv
uv pip install -e '.[dev]'
```

The checkout executables live in `.venv/bin/`.

## Check the cached OAuth sign-in

```sh
secureframe-probe-rest-auth
```

The probe reads Claude Code's Secureframe sign-in and sends one GET request to `/users?page=1&per_page=1`. It reports the HTTP status and authentication result. macOS may ask you to allow Keychain access.

If there are multiple sign-ins:

```sh
secureframe-probe-rest-auth --server-name secureframe --region us
```

Use the actual cached Claude Code MCP server name. `--region` accepts `us` or `uk`. A single matching sign-in determines its own API region.

The probe checks read access. Uploads require the signed-in user to have write permission.

## Add the local server

Find the executable:

```sh
command -v better-secureframe-mcp
```

Use that absolute path in the separate MCP connection:

```sh
claude mcp add secureframe-local-uploads -- /absolute/path/better-secureframe-mcp
```

For a checkout, use `/absolute/path/to/repo/.venv/bin/better-secureframe-mcp`. Restart the client or reload its MCP connections so it discovers the three local tools. Keep the official Secureframe server connected too.

Other MCP clients can launch the same executable over stdio on this Mac; questionnaire auth still comes from Claude Code's cache.

## Next steps

Follow the [upload workflows]({{ '/uploads/' | relative_url }}). If the probe cannot select a sign-in or the cached token has expired, use the [OAuth troubleshooting guide]({{ '/oauth/#troubleshooting' | relative_url }}).

Optional settings select a profile, region, or server name. See the [settings reference]({{ '/reference/#settings' | relative_url }}).
