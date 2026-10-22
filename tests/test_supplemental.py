import base64
import hashlib
import socket
from datetime import date
from unittest.mock import Mock

import httpx
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from better_secureframe_mcp import rest_auth, server, supplemental
from better_secureframe_mcp.config import load_config


@pytest.fixture(autouse=True)
def clean_auth(monkeypatch):
    for name in (
        "SECUREFRAME_API_KEY",
        "SECUREFRAME_API_SECRET",
        "SECUREFRAME_API_URL",
        "SECUREFRAME_MCP_ACCESS_TOKEN",
        "SECUREFRAME_REST_AUTH",
        "SECUREFRAME_READ_ONLY",
        "SECUREFRAME_MCP_MODE",
        "SECUREFRAME_MCP_TRANSPORT",
        "SECUREFRAME_TOOL_TAGS",
        "SECUREFRAME_EXCLUDE_TAGS",
        "SECUREFRAME_CLAUDE_SERVER_NAME",
    ):
        monkeypatch.delenv(name, raising=False)
    # These existing tests exercise explicit API-key/manual-token modes only.
    monkeypatch.setenv("SECUREFRAME_REST_AUTH", "api_key")


@pytest.fixture
def evidence(tmp_path):
    path = tmp_path / "evidence.pdf"
    path.write_bytes(b"%PDF-1.7\n\x00\xff local evidence\n")
    return path


@pytest.mark.asyncio
async def test_metadata_matches_raw_bytes(evidence):
    result = await supplemental.prepare_local_file_upload(str(evidence))
    assert result == {
        "filename": "evidence.pdf",
        "byte_size": evidence.stat().st_size,
        "checksum": base64.b64encode(
            hashlib.md5(evidence.read_bytes(), usedforsecurity=False).digest()
        ).decode(),
        "content_type": "application/pdf",
    }


@pytest.mark.asyncio
async def test_missing_and_oversize_files(evidence, monkeypatch):
    with pytest.raises(ToolError, match="Cannot read"):
        await supplemental.prepare_local_file_upload(str(evidence.parent / "missing"))
    monkeypatch.setattr(supplemental, "MAX_EVIDENCE_BYTES", 5)
    with pytest.raises(ToolError, match="32 MB"):
        await supplemental.prepare_local_file_upload(str(evidence))


@pytest.mark.asyncio
async def test_put_sends_exact_bytes_and_headers_without_api_auth(
    evidence, monkeypatch
):
    metadata = await supplemental.prepare_local_file_upload(str(evidence))
    monkeypatch.setenv("SECUREFRAME_API_KEY", "must-not-forward")
    monkeypatch.setenv("SECUREFRAME_MCP_ACCESS_TOKEN", "also-must-not-forward")
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))],
    )
    requests = []

    async def storage(request):
        requests.append(request)
        assert request.method == "PUT"
        assert await request.aread() == evidence.read_bytes()
        assert request.headers["content-md5"] == metadata["checksum"]
        assert request.headers["x-upload-test"] == "unchanged"
        assert "authorization" not in request.headers
        return httpx.Response(200)

    original = httpx.AsyncClient
    monkeypatch.setattr(
        supplemental.httpx,
        "AsyncClient",
        lambda **kwargs: original(transport=httpx.MockTransport(storage), **kwargs),
    )
    result = await supplemental.put_local_file_upload(
        str(evidence),
        "https://storage.example/evidence?signature=secret",
        {"Content-MD5": metadata["checksum"], "X-Upload-Test": "unchanged"},
        metadata["byte_size"],
        metadata["checksum"],
    )
    assert result == {
        "uploaded": True,
        "byte_size": metadata["byte_size"],
        "attached": False,
    }
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_changed_file_is_rejected_before_network(evidence):
    metadata = await supplemental.prepare_local_file_upload(str(evidence))
    evidence.write_bytes(b"changed")
    with pytest.raises(ToolError, match="File changed"):
        await supplemental.put_local_file_upload(
            str(evidence),
            "https://unused.example",
            {},
            metadata["byte_size"],
            metadata["checksum"],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/file",
        "https://name:password@example.com/file",
        "https://example.com:8443/file",
        "https://127.0.0.1/file",
    ],
)
async def test_signed_upload_url_checks(url):
    with pytest.raises(ToolError, match="public storage host"):
        await supplemental._validate_upload_url(url)


@pytest.mark.asyncio
async def test_put_does_not_follow_redirects_or_report_upload_success(
    evidence, monkeypatch
):
    metadata = await supplemental.prepare_local_file_upload(str(evidence))

    async def valid_url(url):
        pass

    monkeypatch.setattr(supplemental, "_validate_upload_url", valid_url)
    calls = []

    def redirect(request):
        calls.append(request)
        return httpx.Response(307, headers={"Location": "https://other.example"})

    original = httpx.AsyncClient
    monkeypatch.setattr(
        supplemental.httpx,
        "AsyncClient",
        lambda **kwargs: original(transport=httpx.MockTransport(redirect), **kwargs),
    )
    with pytest.raises(ToolError, match="HTTP 307"):
        await supplemental.put_local_file_upload(
            str(evidence),
            "https://storage.example/file",
            {},
            metadata["byte_size"],
            metadata["checksum"],
        )
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_read_only_blocks_both_uploads_without_credentials(evidence, monkeypatch):
    monkeypatch.setenv("SECUREFRAME_READ_ONLY", "true")
    metadata = await supplemental.prepare_local_file_upload(str(evidence))
    with pytest.raises(ToolError, match="disabled"):
        await supplemental.put_local_file_upload(
            str(evidence),
            "https://unused.example",
            {},
            metadata["byte_size"],
            metadata["checksum"],
        )
    with pytest.raises(ToolError, match="disabled"):
        await supplemental.upload_security_questionnaire_file(str(evidence), "owner")


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["api_key", "mcp_token"])
async def test_realistic_questionnaire_multipart_auth_and_no_retry(
    tmp_path, monkeypatch, mode
):
    path = tmp_path / "questionnaire.xlsx"
    content = b"binary questionnaire\x00\xff" * 100_000
    path.write_bytes(content)
    monkeypatch.setenv("SECUREFRAME_REST_AUTH", mode)
    monkeypatch.setenv("SECUREFRAME_API_KEY", "key")
    monkeypatch.setenv("SECUREFRAME_API_SECRET", "secret")
    monkeypatch.setenv("SECUREFRAME_MCP_ACCESS_TOKEN", "access-token")
    original = rest_auth.rest_client
    requests = []

    async def rest(request):
        requests.append(request)
        assert request.url.path == "/security_questionnaires"
        assert request.url.params == httpx.QueryParams(
            {
                "owner_id": "owner",
                "due_date": "2026-11-01",
                "questionnaire_template": "sig",
            }
        )
        assert request.headers["authorization"] == (
            "Bearer access-token" if mode == "mcp_token" else "key secret"
        )
        body = await request.aread()
        assert content in body
        assert b'filename="questionnaire.xlsx"' in body
        assert request.headers["content-type"].startswith("multipart/form-data;")
        return httpx.Response(503, text="unavailable")

    def fake_client():
        configured = original()
        configured._transport = httpx.MockTransport(rest)
        return configured

    monkeypatch.setattr(rest_auth, "rest_client", fake_client)
    result = await supplemental.upload_security_questionnaire_file(
        str(path),
        "owner",
        due_date=date(2026, 11, 1),
        questionnaire_template="sig",
    )
    assert "503" in result["error"]
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_missing_questionnaire_credentials_are_clear(evidence):
    with pytest.raises(ToolError, match="SECUREFRAME_API_KEY"):
        await supplemental.upload_security_questionnaire_file(str(evidence), "owner")


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [200, 401, 403])
async def test_auth_probe_does_not_expose_user_data_or_token(monkeypatch, status):
    monkeypatch.setenv("SECUREFRAME_REST_AUTH", "mcp_token")

    async def check(request):
        assert request.method == "GET"
        assert request.url.path == "/users"
        assert request.url.params == httpx.QueryParams({"page": "1", "per_page": "1"})
        return httpx.Response(status, json={"data": [{"name": "private-user"}]})

    monkeypatch.setattr(
        rest_auth,
        "rest_client",
        lambda: httpx.AsyncClient(
            base_url="https://api.secureframe.com",
            transport=httpx.MockTransport(check),
        ),
    )
    result = await rest_auth.probe()
    assert result["accepted"] is (status == 200)
    assert result["status_code"] == status
    assert "private-user" not in str(result)


def test_token_auth_requires_explicit_opt_in_and_official_origin(monkeypatch):
    monkeypatch.setenv("SECUREFRAME_MCP_ACCESS_TOKEN", "token")
    with pytest.raises(ValueError, match="SECUREFRAME_API_KEY"):
        rest_auth.rest_client()
    monkeypatch.setenv("SECUREFRAME_REST_AUTH", "mcp_token")
    monkeypatch.setenv("SECUREFRAME_API_URL", "https://other.example")
    with pytest.raises(ValueError, match="Secureframe US or UK"):
        rest_auth.rest_client()


@pytest.mark.asyncio
async def test_only_supplemental_tools_exposed_and_user_document_type_not_redefined():
    async with Client(supplemental.mcp) as connection:
        tools = {tool.name: tool for tool in await connection.list_tools()}
        assert set(tools) == {
            "prepare_local_file_upload",
            "put_local_file_upload",
            "upload_security_questionnaire_file",
        }
        assert tools["prepare_local_file_upload"].annotations.readOnlyHint is True
        result = await connection.call_tool(
            "upload_security_questionnaire_file",
            {
                "file_path": "/unused",
                "owner_id": "owner",
                "questionnaire_template": "made_up",
            },
            raise_on_error=False,
        )
        assert result.is_error


def test_default_entrypoint_needs_no_api_credentials(monkeypatch):
    monkeypatch.setattr(server, "load_dotenv", lambda *a: None)
    run = Mock()
    monkeypatch.setattr(supplemental.mcp, "run", run)
    server.main()
    run.assert_called_once_with()
    assert load_config(require_credentials=False).api_key == ""


def test_legacy_mode_still_requires_credentials(monkeypatch):
    monkeypatch.setattr(server, "load_dotenv", lambda *a: None)
    monkeypatch.setenv("SECUREFRAME_MCP_MODE", "legacy")
    with pytest.raises(ValueError, match="SECUREFRAME_API_KEY"):
        server.main()
