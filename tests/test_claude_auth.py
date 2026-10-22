import json
import subprocess
from types import SimpleNamespace

import pytest

from better_secureframe_mcp import claude_auth, rest_auth


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in (
        "CLAUDE_CONFIG_DIR",
        "CLAUDE_SECURESTORAGE_CONFIG_DIR",
        "SECUREFRAME_CLAUDE_KEYCHAIN_SERVICE",
        "SECUREFRAME_CLAUDE_SERVER_NAME",
        "SECUREFRAME_API_KEY",
        "SECUREFRAME_API_SECRET",
        "SECUREFRAME_API_URL",
        "SECUREFRAME_REST_AUTH",
        "SECUREFRAME_MCP_ACCESS_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("USER", "test-user")
    monkeypatch.setattr(claude_auth.sys, "platform", "darwin")
    monkeypatch.setattr(claude_auth.time, "time", lambda: 1_800_000_000)

    def no_live_keychain(*args, **kwargs):
        raise AssertionError("Tests must not read the real Keychain")

    monkeypatch.setattr(claude_auth.subprocess, "run", no_live_keychain)


def entry(**overrides):
    return {
        "serverName": "secureframe",
        "serverUrl": "https://mcp.secureframe.com/",
        "accessToken": "synthetic-access-token",
        "refreshToken": "never-use-refresh",
        "expiresAt": 1_800_003_600_000,
        **overrides,
    }


def cache(monkeypatch, *entries):
    monkeypatch.setattr(
        claude_auth,
        "_read_cache",
        lambda: {
            "mcpOAuth": {
                f"server|{index}": value for index, value in enumerate(entries)
            },
            "claudeAiOauth": {"accessToken": "must-not-use-account-token"},
        },
    )


def test_keychain_read_is_captured_and_never_written(monkeypatch):
    calls = []

    def security(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(
            returncode=0, stdout=json.dumps({"mcpOAuth": {"a": entry()}})
        )

    monkeypatch.setattr(claude_auth.subprocess, "run", security)
    credential = claude_auth.cached_credential()
    assert credential.access_token == "synthetic-access-token"
    assert "synthetic-access-token" not in repr(credential)
    assert calls == [
        (
            [
                "/usr/bin/security",
                "find-generic-password",
                "-a",
                "test-user",
                "-s",
                "Claude Code-credentials",
                "-w",
            ],
            {"capture_output": True, "text": True, "timeout": 15, "check": False},
        )
    ]


def test_exact_secureframe_origin_match_not_server_name(monkeypatch):
    cache(
        monkeypatch,
        entry(serverUrl="https://mcp.secureframe.com.attacker.example/"),
        entry(serverUrl="https://mcp.secureframe.com/?other=token"),
        entry(serverUrl="https://mcp.secureframe.com/private"),
        entry(serverUrl="https://unrelated.example/"),
    )
    with pytest.raises(ValueError, match="No matching"):
        claude_auth.cached_credential()


def test_selects_secureframe_without_requiring_particular_name(monkeypatch):
    cache(
        monkeypatch,
        entry(serverName="other", serverUrl="https://unrelated.example/"),
        entry(serverName="my-compliance-tools"),
    )
    assert claude_auth.cached_credential().server_name == "my-compliance-tools"


def test_multiple_companies_require_explicit_selection(monkeypatch):
    cache(
        monkeypatch, entry(), entry(serverName="second-company", accessToken="second")
    )
    with pytest.raises(ValueError, match="Multiple Secureframe"):
        claude_auth.cached_credential()
    assert (
        claude_auth.cached_credential(server_name="second-company").access_token
        == "second"
    )


def test_uk_region_is_inferred_and_can_be_selected(monkeypatch):
    cache(monkeypatch, entry(serverUrl="https://mcp-uk.secureframe.com/"))
    assert claude_auth.cached_credential().api_url == "https://api-uk.secureframe.com"
    cache(monkeypatch, entry(), entry(serverUrl="https://mcp-uk.secureframe.com/"))
    assert claude_auth.cached_credential(
        api_url="https://api.secureframe.com"
    ).api_url == ("https://api.secureframe.com")


def test_expired_access_token_is_not_refreshed(monkeypatch):
    cache(monkeypatch, entry(expiresAt=1_799_999_999_000))
    with pytest.raises(ValueError, match="has expired"):
        claude_auth.cached_credential()


def test_expired_other_company_does_not_silently_select_active_company(monkeypatch):
    cache(
        monkeypatch,
        entry(serverName="expired-company", expiresAt=1_799_999_999_000),
        entry(serverName="active-company", accessToken="other-company"),
    )
    with pytest.raises(ValueError, match="Multiple Secureframe"):
        claude_auth.cached_credential()
    with pytest.raises(ValueError, match="has expired"):
        claude_auth.cached_credential(server_name="expired-company")


@pytest.mark.parametrize("expiry", [True, "tomorrow", float("nan")])
def test_unrecognized_expiry_is_not_silently_used(monkeypatch, expiry):
    cache(monkeypatch, entry(expiresAt=expiry))
    with pytest.raises(ValueError, match="expiry"):
        claude_auth.cached_credential()


def test_no_token_no_account_token_fallback(monkeypatch):
    cache(monkeypatch, entry(accessToken=""))
    with pytest.raises(ValueError, match="No matching"):
        claude_auth.cached_credential()


@pytest.mark.parametrize(
    "result",
    [
        SimpleNamespace(returncode=36, stdout="DO-NOT-PRINT", stderr="DO-NOT-PRINT"),
        SimpleNamespace(returncode=0, stdout="DO-NOT-PRINT"),
    ],
)
def test_cache_errors_never_echo_keychain_contents(monkeypatch, result):
    monkeypatch.setattr(claude_auth.subprocess, "run", lambda *a, **k: result)
    with pytest.raises(ValueError) as exc:
        claude_auth.cached_credential()
    assert "DO-NOT-PRINT" not in str(exc.value)


def test_keychain_timeout_is_sanitized(monkeypatch):
    def timeout(*a, **k):
        raise subprocess.TimeoutExpired("security", 15, output="DO-NOT-PRINT")

    monkeypatch.setattr(claude_auth.subprocess, "run", timeout)
    with pytest.raises(ValueError) as exc:
        claude_auth.cached_credential()
    assert "DO-NOT-PRINT" not in str(exc.value)


def test_file_fallback_only_when_keychain_item_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_SECURESTORAGE_CONFIG_DIR", str(tmp_path))
    (tmp_path / ".credentials.json").write_text(
        json.dumps({"mcpOAuth": {"a": entry()}})
    )
    monkeypatch.setattr(
        claude_auth.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=44,
            stdout="",
        ),
    )
    assert claude_auth.cached_credential().server_name == "secureframe"
    monkeypatch.setattr(
        claude_auth.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=36,
            stdout="",
        ),
    )
    with pytest.raises(ValueError, match="Keychain did not allow"):
        claude_auth.cached_credential()


def test_custom_storage_namespace_and_override_precedence(monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", "/profile")
    service, _ = claude_auth._storage_location()
    assert (
        service
        == "Claude Code-credentials"
        + "-"
        + (claude_auth.hashlib.sha256(b"/profile").hexdigest()[:8])
    )
    monkeypatch.setenv("CLAUDE_SECURESTORAGE_CONFIG_DIR", "")
    assert claude_auth._storage_location()[0] == "Claude Code-credentials"


@pytest.mark.asyncio
async def test_default_rest_auth_reuses_cached_token_and_infers_region(monkeypatch):
    cache(monkeypatch, entry(serverUrl="https://mcp-uk.secureframe.com/"))
    async with rest_auth.rest_client() as client:
        assert str(client.base_url) == "https://api-uk.secureframe.com"
        assert client.headers["authorization"] == "Bearer synthetic-access-token"


@pytest.mark.asyncio
@pytest.mark.parametrize("old_mode", ["api_key", "mcp_token", "auto"])
async def test_removed_credentials_and_modes_cannot_override_oauth(
    monkeypatch, old_mode
):
    monkeypatch.setenv("SECUREFRAME_REST_AUTH", old_mode)
    monkeypatch.setenv("SECUREFRAME_API_KEY", "obsolete-key")
    monkeypatch.setenv("SECUREFRAME_API_SECRET", "obsolete-secret")
    monkeypatch.setenv("SECUREFRAME_MCP_ACCESS_TOKEN", "obsolete-token")
    cache(monkeypatch, entry())
    async with rest_auth.rest_client() as client:
        assert client.headers["authorization"] == "Bearer synthetic-access-token"


def test_missing_oauth_login_cannot_fall_back_to_removed_credentials(monkeypatch):
    monkeypatch.setenv("SECUREFRAME_API_KEY", "obsolete-key")
    monkeypatch.setenv("SECUREFRAME_API_SECRET", "obsolete-secret")
    monkeypatch.setenv("SECUREFRAME_MCP_ACCESS_TOKEN", "obsolete-token")
    cache(monkeypatch)
    with pytest.raises(ValueError, match="No matching"):
        rest_auth.rest_client()
