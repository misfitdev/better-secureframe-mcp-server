import asyncio

from better_secureframe_mcp.app import mcp

# Importing the server registers all tools, resources, and prompts.
import better_secureframe_mcp.server  # noqa: F401


def _by_name(items):
    return {item.name: item for item in items}


def test_tools_registered():
    tools = _by_name(asyncio.run(mcp.list_tools()))
    # 60 curated tools covering all 64 API operations.
    assert len(tools) >= 55
    # Spot-check a read, a write, and a destructive tool exist.
    assert "list_tests" in tools
    assert "update_test" in tools
    assert "archive_vendor" in tools


def test_read_only_annotations():
    tools = _by_name(asyncio.run(mcp.list_tools()))
    assert tools["list_controls"].annotations.readOnlyHint is True
    assert tools["delete_comment"].annotations.destructiveHint is True


def test_resources_and_prompts_registered():
    resources = asyncio.run(mcp.list_resources())
    templates = asyncio.run(mcp.list_resource_templates())
    prompts = _by_name(asyncio.run(mcp.list_prompts()))
    uris = [str(r.uri) for r in resources] + [str(t.uri_template) for t in templates]
    assert any("reference/enums" in u for u in uris)
    assert any("reference/fields/{entity}" in u for u in uris)
    assert "failing_controls_review" in prompts
