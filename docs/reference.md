---
title: Tool and settings reference
dek: "Parameters, return values, limits, and configuration."
permalink: /reference/
---

The server exposes these three tools.

## Prepare file metadata {#prepare_local_file_upload}

`prepare_local_file_upload` reads a local evidence or signed NDA file and returns metadata. It does not upload bytes or return file contents.

| Input | Required | Meaning |
|---|---|---|
| `file_path` | Yes | Local path on the helper's machine; `~` is expanded. |

Returns `filename`, `byte_size`, `checksum` (base64 MD5 of raw bytes), and `content_type` (guessed from the filename, with an octet-stream fallback). Pass these to official `create_file_upload`.

The helper rejects evidence over its 32 MB bound. It remains available in read-only mode.

## PUT file bytes {#put_local_file_upload}

`put_local_file_upload` PUTs local raw bytes to the URL from official `create_file_upload`. The signed URL authorizes the storage request.

| Input | Required | Meaning |
|---|---|---|
| `file_path` | Yes | The same local file used for preparation. |
| `url` | Yes | The signed HTTPS URL returned by official staging. |
| `headers` | Yes | All staging headers, unchanged, as an object of string values. |
| `byte_size` | Yes | The exact size declared when staging. |
| `checksum` | Yes | The checksum declared when staging. |

The file must still match both size and checksum. The URL must resolve to a public host, use HTTPS on the standard port, and contain no embedded username/password. Redirects are not followed.

Returns `uploaded: true`, `byte_size`, and `attached: false`. Call an official attachment tool next. This write is blocked by read-only mode.

## Upload a questionnaire {#upload_security_questionnaire_file}

`upload_security_questionnaire_file` streams a local questionnaire to the REST multipart endpoint using Claude Code's cached Secureframe OAuth sign-in. This creates a questionnaire and is blocked by read-only mode.

| Input | Required | Meaning |
|---|---|---|
| `file_path` | Yes | Local questionnaire file path; `~` is expanded. |
| `owner_id` | Yes | Secureframe owner UUID. |
| `company_name` | No | Requesting customer's name. |
| `due_date` | No | Date in `YYYY-MM-DD` format. |
| `questionnaire_template` | No | One of the template values below. |

Templates: `custom`, `caiq`, `hecvat`, `hecvat_lite`, `sig`, `sig_lite`, `ccpa`, `cis`, `nist`, `vsa`, `pci_dss`.

Returns the API result with record attributes flattened and null values omitted. The wrapper adds no small inline-base64 limit; actual questionnaire REST file limits are unmeasured. Creation is not automatically retried.

## Official user evidence types

These apply to official `create_user_evidence`, which you call after the local bytes have landed:

- `background_check_report`
- `ccpa_training_screenshot`
- `gdpr_training_screenshot`
- `handling_cui_training_screenshot`
- `hipaa_training_screenshot`
- `password_manager_screenshot`
- `password_policy_screenshot`
- `pci_secure_code_training_screenshot`
- `pci_training_screenshot`
- `security_training_screenshot`
- `security_training_new_hire_screenshot`

## Settings

Sign-in comes from Claude Code. These optional settings select the profile, region, and exposed tools.

| Setting | Default | Purpose |
|---|---|---|
| `SECUREFRAME_READ_ONLY` | `false` | Block uploads/writes; allow local metadata preparation. |
| `SECUREFRAME_CLAUDE_SERVER_NAME` | Unset | Select one cached Secureframe MCP server by its exact name. |
| `SECUREFRAME_API_URL` | Inferred | Select the official US or UK API region. |
| `CLAUDE_CONFIG_DIR` | Claude default | Select a Claude Code profile. |
| `CLAUDE_SECURESTORAGE_CONFIG_DIR` | Claude default | Override Claude Code's secure-storage profile. |
| `SECUREFRAME_CLAUDE_KEYCHAIN_SERVICE` | Derived from profile | Override a nonstandard Keychain service name. |
| `SECUREFRAME_ENV_FILE` | Optional `.env` lookup | Load ordinary settings at startup; no credentials belong here. |
| `SECUREFRAME_TOOL_TAGS` | Unset | Include tools matching at least one selected tag. |
| `SECUREFRAME_EXCLUDE_TAGS` | Unset | Hide tools matching a selected tag; exclusion wins. |

Tags are `uploads`, `questionnaires`, `read`, and `write`. `SECUREFRAME_EXCLUDE_TAGS=write` leaves metadata preparation exposed.

The server runs over stdio.

## Probe command

```sh
secureframe-probe-rest-auth [--server-name NAME] [--region us|uk]
```

Exit code `0` means the read-only REST probe accepted the credential, `1` means the service did not return the expected successful user-list response, and `2` means a local credential/configuration or connectivity error prevented the check.
