"""Multipart upload to Secureframe's questionnaire endpoint."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx


async def upload(
    endpoint: str,
    file_path: str,
    *,
    params: dict[str, Any],
    http_client: httpx.AsyncClient,
) -> dict[str, Any]:
    path = Path(file_path)
    if not path.is_file():
        return {"error": f"File not found: {file_path}"}

    clean_params = {key: value for key, value in params.items() if value is not None}
    try:
        stream = await asyncio.to_thread(path.open, "rb")
        try:
            response = await http_client.post(
                endpoint,
                params=clean_params,
                files={"file": (path.name, stream)},
            )
        finally:
            await asyncio.to_thread(stream.close)
    except OSError as exc:
        return {"error": f"Could not read upload file: {exc.strerror}"}
    except httpx.RequestError:
        return {"error": "Questionnaire upload failed. Check connectivity."}

    if response.is_error:
        return {"error": f"API Error {response.status_code}: {response.text}"}
    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"error": "Response was not valid JSON"}
