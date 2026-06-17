# Better Secureframe MCP Server — Parameter Reference

Most filtering is now done with **typed tool parameters**, not Lucene. For
example, instead of `q="health_status:fail AND frameworks:soc2_alpha"` you call
`list_tests(health_status="fail", framework="soc2_alpha")`. This document lists
the common enum values those parameters accept.

The server also exposes this reference at runtime as MCP resources:
`secureframe://reference/fields`, `.../fields/{entity}`, `.../enums`, and
`.../frameworks`. The authoritative field list per resource is derived from the
vendored OpenAPI spec at `docs/openapi.yaml`.

---

## Enum values

### Controls
- `health_status`: `healthy` | `unhealthy` | `draft`
- `implementation_status`: `implemented` | `not_implemented`

### Tests
- `health_status`: `pass` | `fail` | `disabled`
- `test_type`: `integration` | `upload`
- `test_domain` (examples): Network Security, Data Security,
  Identity and Access Management, Vulnerability Management, Governance

### Users (personnel)
- `employee_type`: `employee` | `contractor` | `non_employee` | `auditor` | `external`
- `active`, `in_audit_scope`: `true` | `false`

### Framework requirements
- `health_status`: `pass` | `fail` | `na` | `draft`

### Vendors / TPRM vendors
- `risk_level`: `Low` | `Medium` | `High`
- `vendor_status`: `draft` | `completed`
- `archived`: `true` | `false`

### Repositories
- `vendor_name`: `Github` | `Gitlab` | `Bitbucket`
- `private`, `in_audit_scope`: `true` | `false`

---

## Framework keys

Used by the `framework` parameter (and the `framework_keys` Lucene field):

```
soc2_alpha, iso27001, iso27001_2022, CIS_IG1, hipaa, cmmc_l2,
FedRAMP_Low, FedRAMP_Moderate, FedRAMP_High, FedRAMP_20x,
gdpr, pci_dss, nist_csf
```

---

## Advanced: raw Lucene escape hatch

Every `list_*` tool accepts a raw `q` parameter for queries the typed
parameters cannot express (ranges, wildcards, OR across different fields). It is
ANDed with any structured filters you also pass.

```lucene
# Tests due before a date
next_due_date:[* TO 2026-01-01]

# Wildcard match on owner
owner_name:Al*
```

Notes:
- Boolean values are lowercase (`true` / `false`).
- Dates use ISO 8601 (`2026-01-15` or `2026-01-15T10:30:00Z`).
- Most string values are case-sensitive.
