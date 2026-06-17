from better_secureframe_mcp.query import build_query, lucene_value


def test_empty_returns_none():
    assert build_query({}) is None
    assert build_query({"a": None}) is None
    assert build_query(None, None) is None


def test_single_filter():
    assert build_query({"health_status": "fail"}) == "health_status:fail"


def test_multiple_filters_anded():
    q = build_query({"health_status": "fail", "frameworks": "soc2_alpha"})
    assert q == "health_status:fail AND frameworks:soc2_alpha"


def test_bool_lowercased():
    assert build_query({"active": False}) == "active:false"
    assert build_query({"active": True}) == "active:true"


def test_list_becomes_or_group():
    q = build_query({"frameworks": ["soc2_alpha", "iso27001"]})
    assert q == "(frameworks:soc2_alpha OR frameworks:iso27001)"


def test_single_item_list_no_parens():
    assert build_query({"frameworks": ["soc2_alpha"]}) == "frameworks:soc2_alpha"


def test_value_with_space_is_quoted():
    assert build_query({"test_domain": "Network Security"}) == (
        'test_domain:"Network Security"'
    )


def test_raw_q_anded_in():
    q = build_query({"health_status": "fail"}, raw_q="owner_name:Alice")
    assert q == "health_status:fail AND (owner_name:Alice)"


def test_raw_q_only():
    assert build_query({}, raw_q="custom:true") == "custom:true"


def test_lucene_value_escapes_quotes():
    assert lucene_value('a "quoted" value') == '"a \\"quoted\\" value"'


def test_none_filters_skipped():
    q = build_query({"health_status": "fail", "test_type": None, "enabled": True})
    assert q == "health_status:fail AND enabled:true"
