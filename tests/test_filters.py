"""Tests for filter parameters added from OpenAPI spec description tables."""

from better_secureframe_mcp.query import build_query


def test_controls_new_filters():
    """Test that new control filters build correct queries."""
    # Test author_name filter
    q = build_query({"author_name": "John"})
    assert q == "author_name:John"

    # Test description filter (should be quoted if spaces)
    q = build_query({"description": "security control"})
    assert q == 'description:"security control"'

    # Test multiple new filters
    q = build_query({"author_name": "John", "enabled": True, "custom": False})
    assert "author_name:John" in q
    assert "enabled:true" in q
    assert "custom:false" in q


def test_tests_new_filters():
    """Test that new test filters build correct queries."""
    # Test test_domain filter
    q = build_query({"test_domain": "Network Security"})
    assert q == 'test_domain:"Network Security"'

    # Test vendor_name filter
    q = build_query({"vendor_name": "AWS"})
    assert q == "vendor_name:AWS"

    # Test multiple new filters
    q = build_query({"test_type": "integration", "enabled": True, "custom": True})
    assert "test_type:integration" in q
    assert "enabled:true" in q
    assert "custom:true" in q


def test_users_new_filters():
    """Test that new user filters build correct queries."""
    # Test employee_type filter
    q = build_query({"employee_type": "contractor"})
    assert q == "employee_type:contractor"

    # Test department_id filter
    q = build_query({"department_id": "dept_123"})
    assert q == "department_id:dept_123"

    # Test multiple new filters
    q = build_query(
        {"active": True, "employee_type": "employee", "in_audit_scope": True}
    )
    assert "active:true" in q
    assert "employee_type:employee" in q
    assert "in_audit_scope:true" in q


def test_risks_new_filters():
    """Test that new risk filters build correct queries."""
    # Test source filter
    q = build_query({"source": "Internal Audit"})
    assert q == 'source:"Internal Audit"'

    # Test responsible_team filter
    q = build_query({"responsible_team": "Security"})
    assert q == "responsible_team:Security"

    # Test multiple new filters
    q = build_query({"status": "Open", "treatment": "mitigate", "source": "Audit"})
    assert "status:Open" in q
    assert "treatment:mitigate" in q
    assert "source:Audit" in q


def test_date_filters_quoting():
    """Test that date filters with special characters are handled correctly."""
    # Dates with special characters should be quoted
    q = build_query({"created_at": "2024-01-01"})
    assert q == "created_at:2024-01-01"

    # Dates in range queries (already handled by raw q)
    q = build_query({}, raw_q="created_at:[2024-01-01 TO 2024-12-31]")
    assert q == "created_at:[2024-01-01 TO 2024-12-31]"
