import httpx
import pytest

from better_secureframe_mcp import client, rest_auth
from better_secureframe_mcp.claude_auth import ClaudeCredential


@pytest.mark.asyncio
async def test_legacy_requests_reread_oauth_without_caching_authorization(monkeypatch):
    tokens = iter(["first-oauth", "refreshed-oauth"])
    requests = []

    def credential():
        return ClaudeCredential(
            next(tokens), "https://api-uk.secureframe.com", "secureframe"
        )

    async def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"data": []})

    monkeypatch.setattr(rest_auth, "credential", credential)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as shared:
        monkeypatch.setattr(client, "_client", shared)
        assert await client.get("/users") == {"data": []}
        assert await client.get("/tests") == {"data": []}
        assert "authorization" not in shared.headers
    assert [str(r.url) for r in requests] == [
        "https://api-uk.secureframe.com/users",
        "https://api-uk.secureframe.com/tests",
    ]
    assert [r.headers["authorization"] for r in requests] == [
        "Bearer first-oauth",
        "Bearer refreshed-oauth",
    ]


@pytest.mark.asyncio
async def test_legacy_multipart_upload_uses_cached_oauth(tmp_path, monkeypatch):
    path = tmp_path / "file.pdf"
    path.write_bytes(b"local bytes")
    monkeypatch.setattr(
        rest_auth,
        "credential",
        lambda: ClaudeCredential(
            "cached-oauth",
            "https://api.secureframe.com",
            "secureframe",
        ),
    )
    requests = []

    async def respond(request):
        requests.append(request)
        assert request.headers["authorization"] == "Bearer cached-oauth"
        assert b"local bytes" in await request.aread()
        return httpx.Response(200, json={"data": {"id": "uploaded"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as shared:
        monkeypatch.setattr(client, "_client", shared)
        assert await client.upload("POST", "/security_questionnaires", str(path)) == {
            "data": {"id": "uploaded"},
        }
    assert len(requests) == 1
    assert str(requests[0].url) == "https://api.secureframe.com/security_questionnaires"


@pytest.mark.asyncio
async def test_legacy_requests_fail_without_oauth_before_network(monkeypatch):
    def no_login():
        raise ValueError("No matching Secureframe access token found in Claude Code.")

    def no_network(request):
        raise AssertionError("No request should be made without OAuth")

    monkeypatch.setattr(rest_auth, "credential", no_login)
    async with httpx.AsyncClient(transport=httpx.MockTransport(no_network)) as shared:
        monkeypatch.setattr(client, "_client", shared)
        result = await client.get("/users")
    assert "No matching Secureframe" in result["error"]
