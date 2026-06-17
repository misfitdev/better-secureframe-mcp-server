from better_secureframe_mcp.config import Config


def _cfg(include=(), exclude=()):
    return Config(
        api_key="k",
        api_secret="s",
        base_url="https://api.secureframe.com",
        read_only=False,
        transport="stdio",
        host="127.0.0.1",
        port=8000,
        include_tags=frozenset(include),
        exclude_tags=frozenset(exclude),
    )


def test_no_filters_keeps_everything():
    cfg = _cfg()
    assert cfg.keep_tool(frozenset({"controls", "read"})) is True
    assert cfg.keep_tool(frozenset({"vendors", "write"})) is True


def test_exclude_write_drops_writes():
    cfg = _cfg(exclude={"write"})
    assert cfg.keep_tool(frozenset({"controls", "read"})) is True
    assert cfg.keep_tool(frozenset({"vendors", "write"})) is False


def test_include_allowlists_resources():
    cfg = _cfg(include={"controls", "tests"})
    assert cfg.keep_tool(frozenset({"controls", "read"})) is True
    assert cfg.keep_tool(frozenset({"tests", "write"})) is True
    assert cfg.keep_tool(frozenset({"vendors", "read"})) is False


def test_exclude_wins_over_include():
    cfg = _cfg(include={"tests"}, exclude={"write"})
    assert cfg.keep_tool(frozenset({"tests", "read"})) is True
    assert cfg.keep_tool(frozenset({"tests", "write"})) is False
