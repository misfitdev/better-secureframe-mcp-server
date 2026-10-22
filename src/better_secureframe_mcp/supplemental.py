"""Local file helpers that complement the signed-in official Secureframe MCP."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import ipaddress
import mimetypes
import socket
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import urlsplit

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from . import client, rest_auth, shaping
from .tools import _common as c

MAX_EVIDENCE_BYTES = 32 * 1024 * 1024
QuestionnaireTemplate = Literal[
    "custom",
    "caiq",
    "hecvat",
    "hecvat_lite",
    "sig",
    "sig_lite",
    "ccpa",
    "cis",
    "nist",
    "vsa",
    "pci_dss",
]

mcp = FastMCP(
    name="Secureframe Local Upload Helpers",
    instructions="""Supplement the official Secureframe MCP; use it for ordinary reads
and writes. To attach a local file as test or user evidence:
1. prepare_local_file_upload(file_path) computes metadata without returning file bytes.
2. Call the OFFICIAL create_file_upload with that metadata, using its existing auth.
3. put_local_file_upload sends the bytes to the returned url with every returned
header unchanged. Pass the byte_size and checksum from step 1.
4. Call the OFFICIAL create_test_evidence or create_user_evidence with the upload id.
User evidence requires document_type. The same flow supports signed Trust Center NDAs
via the official update_trust_center_request. Upload URLs expire in 15 minutes;
upload ids expire in 1 hour and are single-use. Evidence is limited to 32 MB.
For realistic questionnaire files, upload_security_questionnaire_file uses the REST
multipart endpoint using Claude Code's existing macOS Secureframe OAuth sign-in.
Do not send file bytes or credentials in chat.
""",
)


def _read_evidence(file_path: str) -> bytes:
    try:
        with Path(file_path).expanduser().open("rb") as stream:
            content = stream.read(MAX_EVIDENCE_BYTES + 1)
    except OSError as exc:
        raise ToolError(f"Cannot read local file: {exc.strerror}") from exc
    if len(content) > MAX_EVIDENCE_BYTES:
        raise ToolError("The official evidence upload endpoint limits files to 32 MB.")
    return content


def _checksum(content: bytes) -> str:
    # MD5 is mandated by the upload protocol, not used as a security primitive.
    return base64.b64encode(
        hashlib.md5(content, usedforsecurity=False).digest()
    ).decode("ascii")


async def _validate_upload_url(url: str) -> None:
    try:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or parsed.port not in (None, 443)
        ):
            raise ValueError
        addresses = await asyncio.to_thread(
            socket.getaddrinfo, parsed.hostname, 443, type=socket.SOCK_STREAM
        )
        if not addresses or any(
            not ipaddress.ip_address(address[4][0]).is_global for address in addresses
        ):
            raise ValueError
    except (ValueError, OSError) as exc:
        raise ToolError("Upload URL must use HTTPS and a public storage host.") from exc


@mcp.tool(annotations=c.READ, tags={"uploads", "read"})
async def prepare_local_file_upload(
    file_path: Annotated[
        str, Field(description="Local evidence or signed NDA file path")
    ],
) -> dict[str, Any]:
    """Compute filename, byte size, base64 MD5 and MIME type for official create_file_upload.

    Reads locally; does not upload or return file contents. Maximum 32 MB.
    """
    content = await asyncio.to_thread(_read_evidence, file_path)
    filename = Path(file_path).name
    return {
        "filename": filename,
        "byte_size": len(content),
        "checksum": _checksum(content),
        "content_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
    }


@mcp.tool(annotations=c.CREATE, tags={"uploads", "write"})
async def put_local_file_upload(
    file_path: str,
    url: Annotated[
        str, Field(description="Signed url from official create_file_upload")
    ],
    headers: Annotated[
        dict[str, str],
        Field(description="All headers from create_file_upload, unchanged"),
    ],
    byte_size: Annotated[int, Field(ge=0, le=MAX_EVIDENCE_BYTES)],
    checksum: Annotated[
        str, Field(description="Checksum declared in create_file_upload")
    ],
) -> dict[str, Any]:
    """PUT local raw bytes to the official signed URL; no API key or OAuth token needed.

    Checks that the file still matches the staged metadata. Does not attach evidence;
    after success call the official evidence tool with its upload_id.
    """
    content = await asyncio.to_thread(_read_evidence, file_path)
    if len(content) != byte_size or _checksum(content) != checksum:
        raise ToolError("File changed since staging. Prepare and stage a new upload.")
    await _validate_upload_url(url)
    try:
        # Separate client: never forward Secureframe API credentials or cookies.
        async with httpx.AsyncClient(
            timeout=120.0, follow_redirects=False, trust_env=False
        ) as storage:
            response = await storage.put(url, headers=headers, content=content)
    except httpx.HTTPError:
        # HTTP exception strings may contain the secret signed URL.
        raise ToolError(
            "Storage upload failed. Check connectivity and URL expiry."
        ) from None
    if not 200 <= response.status_code < 300:
        raise ToolError(
            f"Storage returned HTTP {response.status_code}; evidence was not attached. "
            "Check expiry and stage a new upload if necessary."
        )
    return {"uploaded": True, "byte_size": len(content), "attached": False}


@mcp.tool(annotations=c.CREATE, tags={"questionnaires", "uploads", "write"})
async def upload_security_questionnaire_file(
    file_path: Annotated[
        str, Field(description="Local questionnaire path; sent as multipart")
    ],
    owner_id: str,
    company_name: str | None = None,
    due_date: date | None = None,
    questionnaire_template: QuestionnaireTemplate | None = None,
) -> dict[str, Any]:
    """Upload a realistic questionnaire file through REST, avoiding MCP's inline size limit.

    Reuses Claude Code's Secureframe OAuth sign-in on macOS.
    Uses the API's file limits, not the evidence staging endpoint's 32 MB limit.
    No automatic retry: retrying a successful but interrupted creation can duplicate it.
    """
    try:
        rest = await asyncio.to_thread(rest_auth.rest_client)
    except ValueError as exc:
        raise ToolError(str(exc)) from None
    async with rest:
        result = await client.upload(
            "POST",
            "/security_questionnaires",
            str(Path(file_path).expanduser()),
            http_client=rest,
            params={
                "owner_id": owner_id,
                "company_name": company_name,
                "due_date": due_date.isoformat() if due_date else None,
                "questionnaire_template": questionnaire_template,
            },
        )
    return shaping.shape(result)
