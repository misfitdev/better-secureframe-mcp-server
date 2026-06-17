"""Pre-built compliance workflow prompts."""

from __future__ import annotations

from ..app import mcp


@mcp.prompt(tags={"workflow"})
def failing_controls_review(framework: str = "soc2_alpha") -> str:
    """Review failing controls and tests for a framework and propose remediation."""
    return (
        f"Review the compliance posture for the '{framework}' framework.\n"
        f"1. Call list_controls(health_status='unhealthy', framework='{framework}', "
        "auto_paginate=true) to find failing controls.\n"
        f"2. Call list_tests(health_status='fail', framework='{framework}', "
        "auto_paginate=true) to find failing tests.\n"
        "3. Group the findings by control and by owner_name.\n"
        "4. For each failing test, summarize the failure_message and "
        "recommended_action, and propose a concrete remediation with priority."
    )


@mcp.prompt(tags={"workflow"})
def audit_readiness(framework: str = "soc2_alpha") -> str:
    """Assess audit readiness for a framework."""
    return (
        f"Assess audit readiness for '{framework}'.\n"
        f"1. list_frameworks(key='{framework}') for headline pass/fail counts.\n"
        f"2. list_framework_requirements(framework? health_status='fail') to find "
        "unmet requirements.\n"
        f"3. list_tests(health_status='fail', framework='{framework}', "
        "auto_paginate=true) for the underlying failing evidence.\n"
        "4. Produce a readiness summary: percent passing, top gaps, owners, and the "
        "shortest path to audit-ready."
    )


@mcp.prompt(tags={"workflow"})
def vendor_risk_review() -> str:
    """Review third-party vendor risk."""
    return (
        "Review third-party vendor risk.\n"
        "1. list_tprm_vendors(risk_level='High', archived=false, auto_paginate=true).\n"
        "2. For notable vendors, get_tprm_vendor(id) to inspect subassessment "
        "responses and last_reviewed_at.\n"
        "3. Flag high-risk vendors not reviewed recently and summarize the top risks "
        "with recommended actions."
    )


@mcp.prompt(tags={"workflow"})
def access_review() -> str:
    """Run a personnel/access review."""
    return (
        "Run an access review.\n"
        "1. list_users(active=true, in_audit_scope=true, auto_paginate=true).\n"
        "2. list_user_accounts(has_user=false, active=true, auto_paginate=true) to "
        "find unlinked active accounts (possible orphaned access).\n"
        "3. Highlight contractors/external users in scope and any accounts that "
        "should be linked or deactivated."
    )


@mcp.prompt(tags={"workflow"})
def evidence_gaps() -> str:
    """Find tests that need evidence uploaded."""
    return (
        "Find evidence gaps.\n"
        "1. list_tests(health_status='fail', test_type='upload', auto_paginate=true) "
        "to find upload-based tests that are failing for lack of evidence.\n"
        "2. Group by owner_name and test_domain.\n"
        "3. For each, state what evidence is needed (recommended_action) and who "
        "should provide it."
    )
