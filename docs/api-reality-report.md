---
title: "Secureframe API: an empirical reality report"
kicker: Field report · read side
dek: What the API actually returns and supports, versus what its docs imply. Verified against a live account, read-only, fully anonymized.
---

> An evidence-first, falsification-style audit of what the Secureframe REST API
> **actually** returns and supports, versus what its OpenAPI document and
> developer docs **imply**. Every claim here was verified against a live
> production account; nothing is taken from the docs on faith.

**Status:** independent analysis. Not affiliated with or endorsed by Secureframe.
**Probed:** 2026-06-18, read-only (no writes), single production tenant.
**Scope:** the read surface — `list`, `get`, sub-resources, filtering, pagination,
relationships. Writes were deliberately **not** exercised (live account).

---

## BLUF

The API works, but it is **incomplete, inconsistent, and actively misleading** in
ways that cost real engineering time:

1. **The relationship graph is fake.** Every response carries a JSON:API
   `relationships` object and the docs advertise `include`/`relationships`
   params, but in practice `relationships` is **always empty** and `include`
   does nothing. There is **no server-side traversal** between entities at all.
2. **What you can filter on ≠ what is returned ≠ what is documented.** You filter
   tests by `frameworks:` (undocumented) while the response only ever contains an
   empty `framework_keys` field. Documented filters like `implementation_status`
   (controls) and `vendor_status` (TPRM vendors) **return HTTP 400 — not
   filterable.** Some filters (TPRM `risk_level`) are accepted but **silently
   return zero results** for the values the API itself returns.
3. **You can't join people to their assets.** `owner_id` is **write-only** — you
   set it on a `PUT`, but `get`/`list` never return it (only the display string
   `owner_name`). Devices expose **no** user/owner/email field at all. Account↔
   person links are only inferable by email string-matching.
4. **No counts, no totals.** No `meta`/`pagination` block anywhere; the only way
   to know how many records exist is to paginate to exhaustion (100/page cap).
5. **Schema drift.** Undocumented enum values (`unmapped`, `not_applicable`),
   inconsistent casing across endpoints (`low` vs `Low`), the same field name
   with different shapes across endpoints (`data_collected` object vs array),
   and numeric fields returned as strings.
6. **Discovery dead-ends.** Evidence, knowledge-base answers, and test exports
   have **no list endpoint** and cannot be enumerated; evidence is also
   metadata-only (no file/URL), so an attached report can be neither found nor
   downloaded via the API. (Meanwhile `knowledge_base_questions` has an
   **undocumented** working list endpoint.)

Net effect: you cannot build a faithful client from the documentation. You must
probe the live API, hard-code undocumented field names, and reconstruct every
relationship client-side from fragile denormalized strings.

---

## The trap: what careful reading gets you

The damning part isn't that the API has bugs — every API does. It's that the
documentation **reliably leads a competent engineer to the wrong conclusion**,
and the API then fails **silently**: empty arrays, zero rows, dropped fields —
not errors. For a compliance system of record, silent-empty is the worst
possible failure mode, because *"no results"* reads as *"nothing is wrong / you
are compliant."* This API will tell you everything is fine while returning you
nothing.

None of the inferences below are sloppy. Each is the conclusion you reach by
reading the OpenAPI spec and developer docs *carefully*. The API does not reward
careful reading; it punishes it.

| What the docs lead a careful engineer to conclude | What the API actually does | How you find out |
|---|---|---|
| "The endpoint supports Lucene filtering and `implementation_status` is in the schema, so I can filter controls by it." | **HTTP 400** `not filterable by implementation_status`. The spec never lists *which* fields are filterable — and the word "filterable" appears **zero** times in it. | At runtime, in prod, per field |
| "The response field is `framework_keys`, so I filter by `framework_keys:`." | **400.** The field that actually filters is `frameworks` — a name that appears **nowhere** in the spec. Reading the schema *more* carefully makes you *more* wrong. | 400, then guesswork |
| "I'll just read `framework_keys` off each test/control." | It's an **empty array on every row.** The thing you can filter by is not in the payload; the thing in the payload is empty. | Silently — you get `[]` |
| "I set `owner_id` with `PUT /tests/{id}`, so I can read it back and filter by it." | `get`/`list` **never return `owner_id`** (0 of 100), and `q=owner_id:` is **400.** It is write-only. You cannot verify your own write or join tests to people. | You diff your write and it "vanished" |
| "Every response has a `relationships` object and the docs expose `include`/`relationships` — so I'll pull a test's evidence/controls/framework." | `relationships` is **always `{}`**; `include` is **ignored**. Your graph traversal returns nothing, forever. | Silently — empty graph |
| "Evidence is a documented resource attached to tests; I'll list a test's evidence and fetch the report." | **No list endpoint** (404), **no link** from the test, and evidence is **metadata-only** (no file/URL). The attached report is unreachable by API. | 404 + a dead end |
| "`per_page=500` to pull everything; I'll read the total from `meta`." | Silently **capped at 100**; there is **no `meta`/total anywhere.** Your "fetch all" quietly truncates and you ship a partial dataset believing it's complete. | Never — unless you count |
| "`risk_level:Low` matches the `Low` the API just showed me." | **Zero rows, no error** (TPRM). Legacy vendors store `low`; TPRM shows `Low`; one of them silently matches nothing. | Silently — empty result |
| "Filtering is filtering; `health_status:Fail` is fine." | **Case-sensitive, zero rows, no error.** On a dashboard, a casing slip renders "0 failing controls." | Silently — looks compliant |
| "`health_status` is `{healthy, unhealthy, draft}` per the schema." | Production data contains **`unmapped`** (controls) and **`not_applicable`** (requirements). Your enum validation rejects real data. | Exception on live data |
| "`asset_value` / `exposure_factor` are numbers." | Returned as **strings** — inconsistently (a sibling seconds field is an int). Your arithmetic or typed deserialization breaks. | Type error / `NaN` |
| "`data_collected` has one shape." | **Object** on legacy vendors, **array** on TPRM vendors. Same name, same concept, two shapes. Your parser crashes on whichever you didn't test. | Crash on the other endpoint |
| "Personnel, devices, and accounts are all modeled, so I can build a person→asset inventory." | **No field links a device to a person.** Accounts link to people only by **email** string-matching. An authoritative ownership inventory is **impossible**. | When the auditor asks |
| "Knowledge-base answers list like questions do." | Answers **404** (no list); questions have an **undocumented** working list; and you can't get from a question to its answers (relationships empty). | 404 + asymmetry |

The through-line: **the spec is not technically lying — it is lying by
omission**, and it pairs that omission with silent-empty failures. It documents
generic Lucene filtering but never the filterable set; it ships a relationships
envelope it never populates; it defines enums it then violates; it returns
shapes its own schema doesn't describe. The only reliable specification of this
API is the running API.

---

## Method & anonymization

- Requests were issued read-only against a live tenant using ordinary API
  credentials. No `POST`/`PUT`/`DELETE` was sent.
- Sample sizes: up to 100 records per endpoint for behavioral checks, 25 for
  field inventory.
- **All data shown is pseudonymized.** A deterministic map replaces every
  identifying value with a stable fake (same real value → same fake), so
  cross-entity joins remain demonstrable while no real data is published. Names →
  `EntityN`/`NameN`, emails → `personN@example.com`, UUIDs → recomputed fake
  UUIDs, third-party/vendor names → `Vendor-N`, free text → `<text:LEN>`.
  Framework identifiers shown (`soc2_alpha`) are industry-standard, not tenant
  data; specific requirement keys are genericized.
- "Filterable?" was determined with an oracle: a non-matching filter on a
  supported field returns `200` with zero rows, while an unsupported field
  returns `400 "<Entity> is not filterable by <field>"`.

---

## Entity catalog (read side)

| Entity | `list` | `get/{id}` | Notable reality |
|---|---|---|---|
| controls | ✅ | ✅ | `owner_name` but **no `owner_id`**; `framework_ids`/`framework_keys` arrays come back **empty**; real mapping is in `framework_requirement_keys`; undocumented `health_status: unmapped` |
| tests | ✅ | ✅ | `owner_name` only; `framework_keys` **always empty** yet you filter by `frameworks:`; `test_interval_seconds` is a **string**, `tolerance_window_seconds` an **int** |
| users | ✅ | ✅ | Person records; join key to accounts is `email` |
| user_accounts | ✅ | ✅ | Integration accounts; `has_user: bool` but **no `user_id`** — link to a person only by `email` |
| devices | ✅ | ✅ | **No field links a device to a human** (no user/owner/email/assignee) |
| risks | ✅ | ✅ | Many undocumented fields (`impact`, `likelihood`, `residual_*`, `company_id`); numeric fields (`asset_value`, `exposure_factor`, `annualized_rate_of_occurrence`) returned as **strings**; most rows have **no `owner_id`** |
| frameworks | ✅ | ✅ | Roll-up counts; `key` like `soc2_alpha` |
| framework_requirements | ✅ | ✅ | Undocumented `health_status: not_applicable` |
| cloud_resources | ✅ | ✅ | `vendor_name`, `third_party_id`; no human link |
| repositories | ✅ | ✅ | `vendor_name` (git host), `third_party_id` |
| vendors (legacy) | ✅ | ✅ | `risk_level: low` (**lowercase**); `data_collected` is an **object** (map of bools); some rows missing `created_at` |
| tprm/vendors | ✅ | ✅ | `risk_level: Low` (**capitalized**); `data_collected` is an **array of objects**; two status fields (`status` + `vendor_status`), **neither filterable** |
| integration_connections | ✅ | ✅ | Minimal (`name`, `status`, `vendor_name`) |
| comments | ✅ | ✅ | Polymorphic via `commentable_id` + `commentable_type` |
| trust_center_requests | ✅ | ✅ | Contains requester PII (name, email, company, job title) |
| user_security_settings | ✅ (index→1) | — | Deeply nested RBAC matrix (roles, components, privileges) |
| evidences | ❌ **404** | ✅ (id only) | **Unlistable**; metadata-only (no file/URL); ID undiscoverable |
| knowledge_base_questions | ⚠️ **works, undocumented** | ✅ | Index returns rows though the spec documents only `get/{id}` |
| knowledge_base_answers | ❌ **404** | ✅ (id only) | Unlistable; ID undiscoverable |
| test_exports | ❌ **404** | ✅ (id only) | Only obtainable from the `create` response |

---

## The relationship graph: implied vs real

The OpenAPI envelope (a `relationships` object on every record) and the
`include`/`relationships` query params imply a traversable graph like:

```
User ──owns──> Test / Control / Risk / Vendor
User ──has──>  UserAccount (integration identity)
User ──uses──> Device
Test ──covers──> FrameworkRequirement ──in──> Framework
Test ──has──>  Evidence
Comment ──on──> (anything)
```

**What the API actually delivers:**

```
relationships: {}        # always empty, on every entity
include=<anything>       # ignored; no `included` array ever returned
```

So none of those edges are traversable server-side. The only way to relate
entities is to **join client-side on denormalized fields**, and those fields are
weak:

| Desired link | Only available join key | Works? |
|---|---|---|
| Test/Control → owner (person) | `owner_name` (display string) | ⚠️ name only; **no stable `owner_id`** is ever returned |
| UserAccount → person | `email` string match | ⚠️ fragile; `has_user` says *linked* but not *to whom* |
| **Device → person** | — | ❌ **impossible** (no field) |
| Test → Evidence | — | ❌ impossible (no list, no relationship, no link field) |
| Test → Framework | `frameworks` filter only | ⚠️ filterable but the value isn't in the response (`framework_keys` is empty) |
| Risk/Vendor → owner | `owner_id` | ⚠️ present on some rows only |

### The human ↔ asset problem, concretely

A core compliance question — *"which person owns this device / this failing
test?"* — is **not answerable from the API**:

- **Devices** carry `device_name`, `serial_number`, `os`, encryption flags, etc.,
  but **nothing** identifying the human who uses them. Example anonymized device:

  ```json
  { "id": "d44eafda-…", "device_name": "Entity4", "serial_number": "SN-0001",
    "os": "<text:12>", "hard_drive_encrypted": true, "in_audit_scope": true }
  ```
  There is no `user_id`, `owner`, `email`, or `assigned_to` — and `q=owner_id:…`,
  `q=user_id:…`, `q=email:…` all return **400 not filterable**.

- **Tests/Controls** show `owner_name: "Entity3"` (a display string) but never
  `owner_id`. Across 100 tests: `owner_id` returned **0 times**, `owner_name`
  100 times. You can render an owner's name but cannot reliably link it back to a
  `users` record (names aren't unique or stable; the only stable key, `owner_id`,
  is write-only).

- **UserAccount → User** is only joinable by `email`:
  ```json
  { "id": "bfd918d6-…", "email": "person5@example.com", "has_user": true,
    "vendor_name": "Vendor-1", "third_party_id": "374c7171-…" }
  ```
  `has_user: true` confirms a person is linked, but the person's `id` is absent —
  so matching an integration identity (e.g., a chat/SSO account) to a person
  requires email string-matching, which fails for shared, service, or
  alias-addressed accounts.

---

## Findings & gap analysis

Severity: **S1** = blocks a reasonable use case · **S2** = forces fragile
workarounds · **S3** = friction / correctness footgun.

| # | Sev | Documented / implied | Observed reality |
|---|---|---|---|
| 1 | S1 | JSON:API `relationships` + `include`/`relationships` params imply a traversable entity graph | `relationships` is **always `{}`**; `include` is ignored (no `included`). No server-side traversal exists. |
| 2 | S1 | Evidence is a first-class resource; tests/users have evidence | `GET /evidences` is **404**; evidence has **no list**, **no link** from tests, and is **metadata-only** (no file/URL). An attached report can be neither discovered nor downloaded via API. |
| 3 | S1 | Personnel, devices, and accounts are all modeled | **No device→person link** exists; **account→person** only by email. You cannot build an authoritative person→asset inventory. |
| 4 | S2 | `owner_id` is the owner reference (writable on `PUT /tests/{id}` etc.) | `owner_id` is **never returned** by `get`/`list` (0/100 on tests) and **not filterable**. It is effectively **write-only** — you can't read back what you set, or join on it. |
| 5 | S2 | Docs/spec field names describe filtering | **Filterable field names are undocumented and differ from response fields.** Tests filter by `frameworks:` (works, 100/100 match) but `framework_keys:` → **400**, and the response only contains `framework_keys` (empty). |
| 6 | S2 | `implementation_status` (control), `vendor_status`/`status` (TPRM) are fields | These are **not filterable** — `q=implementation_status:…` and `q=vendor_status:…` return **400**. A client trusting the docs builds broken queries. |
| 7 | S2 | `risk_level` filters TPRM vendors | Accepted (no 400) but **returns 0** for the exact value the API itself returns (`Low`) — a **silent-failure filter**. |
| 8 | S3 | Filtering on enums | **Case-sensitive with silent zero**: `health_status:fail` → 5, `health_status:Fail` → **0** (no error). A casing typo looks like "nothing matches." |
| 9 | S3 | Documented enums (e.g., control `health_status ∈ healthy/unhealthy/draft`) | Undocumented values in the wild: control `health_status: unmapped`, framework-requirement `health_status: not_applicable`. |
| 10 | S3 | One canonical shape per concept | **Cross-endpoint inconsistency**: `risk_level` is `low` (legacy vendors) vs `Low` (TPRM); `data_collected` is an **object** on vendors and an **array** on TPRM vendors. |
| 11 | S3 | Typed schema | Numeric fields returned as **strings** (`asset_value`, `exposure_factor`, `annualized_rate_of_occurrence`, `test_interval_seconds`), inconsistently (sibling `tolerance_window_seconds` is an int). |
| 12 | S2 | Pagination with discoverable totals | **No `meta`/`pagination`/total** anywhere. `per_page` caps at 100; page beyond range returns `[]`. Total record counts require full pagination. |
| 13 | S3 | Spec lists `get/{id}` only for KB questions | `GET /knowledge_base_questions` **works** (undocumented). Docs under-describe here while over-promising elsewhere. |
| 14 | S3 | Empty/standard field set per entity | Live responses include **undocumented fields** not in the published schema (e.g., risk `impact`/`likelihood`/`residual_*`/`company_id`; TPRM `contract_*`, `onboarded_at`). |

---

## What actually works (in fairness)

- **List + get-by-id** are present and reliable for the 16 core entities.
- **Lucene filtering genuinely works** when you use the right (undocumented)
  field name and exact-case value — verified: `health_status:fail` returns
  exactly the failing tests (5/5 matched).
- **Unknown-field errors are useful**: `400 "<Entity> is not filterable by
  <field>"` is a precise, machine-readable signal (and is, ironically, the best
  way to *discover* the real filter surface).
- **Boolean `AND`** composes correctly in `q`.
- Pagination, while metadata-free, is consistent (stable 100/page, empty past
  the end).

---

## Practical guidance for anyone building on this API

1. **Don't trust the docs for filtering.** Probe each entity with
   `q=<field>:sentinel` and watch for `400 "not filterable by <field>"` to map
   the real, undocumented filter surface before you ship queries.
2. **Match value casing exactly**, and treat an empty result as "possibly a
   casing/field error," not "no data."
3. **Reconstruct relationships yourself.** Pull every entity in full, then join
   in your own store. Expect to join people↔accounts by **email** and accept
   that **devices cannot be attributed to people** via the API.
4. **Treat `owner_id` as write-only**; render ownership from `owner_name` and
   keep your own id↔name map if you need stable joins.
5. **Compute your own totals** by paginating to exhaustion (100/page).
6. **Evidence files are out of reach** — fetch them from the web console; the API
   only confirms metadata.

---

## Appendix — anonymized sample records

Representative records, fully pseudonymized (structure preserved, values fake):

```json
// user
{ "id": "73bd52b0-…", "active": true, "employee_type": "employee",
  "in_audit_scope": true, "onboarding_status": "completed",
  "email": "person1@example.com", "first_name": "Name2", "last_name": "Name3",
  "manager_name": "Entity…", "name": "Entity3" }

// user_account (integration identity) — links to a person only by email
{ "id": "bfd918d6-…", "active": false, "email": "person5@example.com",
  "has_user": true, "vendor_name": "Vendor-1", "third_party_id": "374c7171-…" }

// device — note: no human-linking field of any kind
{ "id": "d44eafda-…", "device_name": "Entity4", "serial_number": "SN-0001",
  "os": "<text:12>", "make": "<text:10>", "hard_drive_encrypted": true,
  "remote_ip": "203.0.113.2", "in_audit_scope": true }

// test — owner_name present, owner_id absent; framework_keys empty though
// the row is filterable by frameworks:soc2_alpha
{ "id": "61a28dae-…", "key": "PHYS-04-8", "health_status": "disabled",
  "test_type": "upload", "test_domain": "Data Security", "owner_name": "Entity…",
  "framework_keys": [], "test_interval_seconds": "2629746" }

// control — health_status "unmapped" (undocumented); requirement mapping lives
// in framework_requirement_keys, not framework_keys
{ "id": "3d3215ec-…", "key": "NET-03-1", "health_status": "unmapped",
  "implementation_status": "implemented", "owner_name": "Entity…",
  "framework_keys": [], "framework_requirement_keys": ["FWK_REQ-01","FWK_REQ-02"] }
```
