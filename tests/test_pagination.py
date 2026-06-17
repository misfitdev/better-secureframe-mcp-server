import pytest

from better_secureframe_mcp import client


@pytest.mark.asyncio
async def test_auto_paginate_stops_on_short_page(monkeypatch):
    pages = {
        1: {"data": [{"id": str(i)} for i in range(100)]},
        2: {"data": [{"id": "100"}, {"id": "101"}]},  # short page -> stop
    }

    async def fake_get(endpoint, params=None):
        return pages[params["page"]]

    monkeypatch.setattr(client, "get", fake_get)
    result = await client.auto_paginate("/tests")
    assert result["pagination"]["pages_fetched"] == 2
    assert result["pagination"]["total_records"] == 102
    assert result["pagination"]["truncated"] is False
    assert len(result["data"]) == 102


@pytest.mark.asyncio
async def test_auto_paginate_propagates_error(monkeypatch):
    async def fake_get(endpoint, params=None):
        return {"error": "API Error 401: nope"}

    monkeypatch.setattr(client, "get", fake_get)
    result = await client.auto_paginate("/tests")
    assert result == {"error": "API Error 401: nope"}


@pytest.mark.asyncio
async def test_auto_paginate_respects_max_pages(monkeypatch):
    async def fake_get(endpoint, params=None):
        return {"data": [{"id": str(i)} for i in range(100)]}  # always full

    monkeypatch.setattr(client, "get", fake_get)
    result = await client.auto_paginate("/tests", max_pages=3)
    assert result["pagination"]["pages_fetched"] == 3
    assert result["pagination"]["truncated"] is True
