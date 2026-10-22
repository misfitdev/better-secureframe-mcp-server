"""Read Claude Code's cached Secureframe access token on macOS without modifying it."""

from __future__ import annotations

import getpass
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

MCP_TO_API = {
    "https://mcp.secureframe.com": "https://api.secureframe.com",
    "https://mcp-uk.secureframe.com": "https://api-uk.secureframe.com",
}


class ClaudeAuthError(ValueError):
    """A cached credential cannot be safely selected or read."""


@dataclass(frozen=True)
class ClaudeCredential:
    access_token: str = field(repr=False)
    api_url: str
    server_name: str


def _storage_location() -> tuple[str, Path]:
    # Matches Claude Code 2.1.283's secure-storage namespace, including profiles.
    override = os.getenv("CLAUDE_SECURESTORAGE_CONFIG_DIR")
    if override is not None:
        directory = override
    else:
        configured = os.getenv("CLAUDE_CONFIG_DIR", "")
        directory = str(Path(configured).expanduser().resolve()) if configured else ""
    directory = unicodedata.normalize("NFC", directory)
    suffix = (
        "-" + hashlib.sha256(directory.encode()).hexdigest()[:8] if directory else ""
    )
    return (
        "Claude Code-credentials" + suffix,
        Path(directory) if directory else Path.home() / ".claude",
    )


def _read_cache() -> dict[str, Any]:
    if sys.platform != "darwin":
        raise ClaudeAuthError(
            "Claude Code Keychain reuse currently supports macOS only."
        )
    service, directory = _storage_location()
    service = os.getenv("SECUREFRAME_CLAUDE_KEYCHAIN_SERVICE", service)
    account = os.getenv("USER") or getpass.getuser()
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", account):
        account = "claude-code-user"
    try:
        result = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-a",
                account,
                "-s",
                service,
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        raise ClaudeAuthError(
            "Could not read Claude Code's macOS Keychain entry."
        ) from None
    if result.returncode == 0:
        raw = result.stdout
    elif result.returncode == 44:
        # Claude Code can fall back to this file when its Keychain item is absent.
        try:
            raw = (directory / ".credentials.json").read_text()
        except OSError:
            raise ClaudeAuthError(
                "No Claude Code credential cache found. Sign in to the official "
                "Secureframe server using Claude Code /mcp first."
            ) from None
    else:
        # Do not echo security's output or silently use a different account/store.
        raise ClaudeAuthError(
            "macOS Keychain did not allow access to Claude Code's credentials. "
            "Unlock the login Keychain and allow access if macOS prompts."
        )
    try:
        cache = json.loads(raw)
    except (ValueError, TypeError):
        raise ClaudeAuthError(
            "Claude Code's credential cache is not valid JSON."
        ) from None
    if not isinstance(cache, dict):
        raise ClaudeAuthError(
            "Claude Code's credential cache has an unsupported format."
        )
    return cache


def cached_credential(
    *, api_url: str | None = None, server_name: str | None = None
) -> ClaudeCredential:
    """Select one unexpired official Secureframe entry, never by name alone."""
    entries = _read_cache().get("mcpOAuth", {})
    if not isinstance(entries, dict):
        raise ClaudeAuthError("Claude Code's mcpOAuth cache has an unsupported format.")
    candidates: set[ClaudeCredential] = set()
    matches: set[ClaudeCredential] = set()
    expired = False
    for entry in entries.values():
        if not isinstance(entry, dict):
            continue
        url = entry.get("serverUrl")
        if not isinstance(url, str):
            continue
        # Exact origins and root path only: a server named 'secureframe' is not proof.
        if url.rstrip("/") not in MCP_TO_API:
            continue
        parsed = urlsplit(url)
        if parsed.path not in ("", "/"):
            continue
        target = MCP_TO_API[url.rstrip("/")]
        if api_url is not None and target != api_url:
            continue
        name = entry.get("serverName")
        if not isinstance(name, str) or (
            server_name is not None and name != server_name
        ):
            continue
        token = entry.get("accessToken")
        if not isinstance(token, str) or not token.strip():
            continue
        credential = ClaudeCredential(token.strip(), target, name)
        matches.add(credential)
        expiry = entry.get("expiresAt")
        if expiry is not None:
            if (
                isinstance(expiry, bool)
                or not isinstance(expiry, (int, float))
                or not math.isfinite(expiry)
            ):
                raise ClaudeAuthError(
                    "Claude Code's token expiry has an unsupported format."
                )
            # Claude Code writes JavaScript Date.now() milliseconds, not seconds.
            if expiry <= (time.time() + 5) * 1000:
                expired = True
                continue
        candidates.add(credential)
    if len(matches) > 1:
        raise ClaudeAuthError(
            "Multiple Secureframe sign-ins found in Claude Code. Select one with "
            "--server-name NAME (or SECUREFRAME_CLAUDE_SERVER_NAME); use --region "
            "if they differ by region."
        )
    if candidates:
        return candidates.pop()
    if expired:
        raise ClaudeAuthError(
            "Claude Code's Secureframe access token has expired. Use the official "
            "server in Claude Code /mcp to refresh it, then rerun. This helper "
            "does not rotate or modify Claude Code's refresh token."
        )
    raise ClaudeAuthError(
        "No matching Secureframe access token found in Claude Code. Authenticate "
        "the official server in /mcp and check the selected server name/region."
    )
