from better_secureframe_mcp.shaping import shape


def test_flatten_list_envelope():
    payload = {
        "data": [
            {
                "id": "1",
                "type": "test",
                "attributes": {"health_status": "fail", "title": "T", "notes": None},
                "relationships": {"control": {"id": "c1"}},
            }
        ]
    }
    out = shape(payload)
    assert out == {
        "data": [{"id": "1", "type": "test", "health_status": "fail", "title": "T"}]
    }


def test_flatten_single_record():
    payload = {"data": {"id": "1", "type": "user", "attributes": {"email": "a@b.com"}}}
    out = shape(payload)
    assert out["data"] == {"id": "1", "type": "user", "email": "a@b.com"}


def test_field_projection_keeps_id():
    payload = {"data": [{"id": "1", "attributes": {"a": 1, "b": 2, "c": 3}}]}
    out = shape(payload, fields=["a"])
    assert out["data"] == [{"id": "1", "a": 1}]


def test_include_relationships():
    payload = {
        "data": [{"id": "1", "attributes": {"a": 1}, "relationships": {"x": "y"}}]
    }
    out = shape(payload, include_relationships=True)
    assert out["data"][0]["relationships"] == {"x": "y"}


def test_error_passthrough():
    assert shape({"error": "boom"}) == {"error": "boom"}


def test_pagination_preserved():
    payload = {"data": [], "pagination": {"total_records": 0}}
    assert shape(payload)["pagination"] == {"total_records": 0}
