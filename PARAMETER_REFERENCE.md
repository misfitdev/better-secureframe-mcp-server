# Better Secureframe MCP Server — Parameter Reference

You don't normally need this: just describe what you want in plain English and
the assistant maps it to the right tool parameters. This page is the human
reference for **which fields actually filter** on each resource and what values
they accept.

**These are empirically verified** against the live API (not copied from
Secureframe's docs, which are wrong about several of them). The Secureframe API
rejects many "obvious" filters with HTTP 400, silently returns nothing for
others, and is case-sensitive — see the
[API Reality Report](https://misfitdev.github.io/better-secureframe-mcp-server/api-reality-report.html)
for the gory details.

> Behavior to know: filters are **case-sensitive** and a wrong value/casing
> returns **zero rows with no error** (it looks like "no matches"). Booleans are
> lowercase `true`/`false`. Dates are ISO 8601.

---

## Verified filterable fields per resource

| Resource | Filters that work | Notable non-filters (look available, but aren't) |
|---|---|---|
| controls | `health_status`, `framework`, `custom`, `enabled`, `owner_name`, `key` | `implementation_status`, `owner_id` → **400** |
| tests | `health_status`, `test_type`, `framework`, `test_domain`, `enabled`, `custom`, `owner_name`, `vendor_name`, `key` | `owner_id` → **400** |
| users | `active`, `employee_type`, `in_audit_scope`, `email`, `department_id`, `onboarding_status` | `manager_name`, `role`, `access_role` → **400** |
| user_accounts | `active`, `has_user`, `email`, `vendor_name` | `username` → **400** |
| devices | `in_audit_scope`, `hard_drive_encrypted`, `password_enforcement_enabled`, `native_anti_virus_enabled`, `local_firewall_enabled`, `os`, `make`, `serial_number` | no person/owner field exists at all |
| risks | **none** — use raw `q` | `status`, `treatment`, `source`, `responsible_team`, `owner_id` all → **400** |
| frameworks | **none** — short list, just read it | `key` → **400** |
| framework_requirements | `health_status`, `enabled`, `key` | — |
| cloud_resources | `in_audit_scope`, `cloud_resource_type`, `vendor_name`, `region`, `third_party_id` | — |
| repositories | `in_audit_scope`, `private`, `vendor_name`, `name` | — |
| vendors (legacy) | `risk_level`, `archived`, `name` | `owner_id` → **400** |
| tprm/vendors | `risk_level`*, `archived`, `name` | `vendor_status`, `status`, `owner_id` → **400** |
| integration_connections | `status`, `vendor_name`, `name` | — |
| comments | `commentable_id`, `commentable_type` | — |
| trust_center_requests | `reviewed`, `email` | `company_name` → **400** |

\* TPRM `risk_level` is *accepted* but appears to **silently return zero** for the
value the API itself displays (`Low`) — treat results as unreliable.

---

## Enum values

- controls `health_status`: `healthy` | `unhealthy` | `draft` | `unmapped`
- tests `health_status`: `pass` | `fail` | `disabled`
- tests `test_type`: `integration` | `upload`
- tests `test_domain` (examples): Network Security, Data Security,
  Identity and Access Management, Vulnerability Management, Governance
- users `employee_type`: `employee` | `contractor` | `non_employee` | `auditor` | `external`
- framework_requirements `health_status`: `pass` | `fail` | `na` | `not_applicable` | `draft`
- **vendors (legacy) `risk_level`: lowercase `low` | `medium` | `high`**
- **tprm/vendors `risk_level`: capitalized `Low` | `Medium` | `High`** (same concept,
  different casing across the two endpoints — yes, really)

## Framework keys

Used by the `framework` parameter:

```
soc2_alpha, iso27001, iso27001_2022, CIS_IG1, hipaa, cmmc_l2,
FedRAMP_Low, FedRAMP_Moderate, FedRAMP_High, FedRAMP_20x,
gdpr, pci_dss, nist_csf
```

Note: the response field is `framework_keys` (and it often comes back **empty**),
but the field you actually *filter* on is `frameworks`. The `framework` parameter
hides that quirk for you.

---

## Raw Lucene escape hatch

Every `list_*` tool accepts a raw `q` for queries the typed parameters can't
express (ranges, wildcards). It's ANDed with any structured filters.

```lucene
next_due_date:[* TO 2026-01-01]   # tests due before a date
owner_name:Al*                    # wildcard
```

To discover what's filterable on a resource the hard way, send `q=<field>:x` and
watch for `400 "<Entity> is not filterable by <field>"`.
