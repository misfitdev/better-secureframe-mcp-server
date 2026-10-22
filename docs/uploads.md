---
title: Upload local files
dek: "Use official tools for evidence staging and attachment; stream questionnaire files through the local helper."
permalink: /uploads/
---

Use absolute local paths. The tools read files on the machine running the helper, so a path on another computer will not work.

## Evidence and signed NDAs

Stage and attach evidence through the official MCP. Use the local tools to read the file and send its bytes to storage.

1. Call local `prepare_local_file_upload(file_path)`.
2. Call official `create_file_upload` with the returned `filename`, `byte_size`, `checksum`, and `content_type`. Keep its `id`, `url`, and `headers`.
3. Call local `put_local_file_upload` with the same `file_path`, the returned `url` and all `headers`, and the `byte_size` and `checksum` from step 1.
4. After the PUT succeeds, call the appropriate official attachment tool with `upload_id=id`.

| Destination | Official attachment tool | Other inputs |
|---|---|---|
| Test evidence | `create_test_evidence` | `test_id`; optional `activity_completion` |
| User evidence | `create_user_evidence` | `user_id`, required `document_type`; optional `activity_completion` |
| Signed Trust Center NDA | `update_trust_center_request` | Request `id` and the relevant approval/document settings |

Completion dates use `YYYY-MM-DD`. User evidence types are restricted by the official API; the [tool reference]({{ '/reference/#official-user-evidence-types' | relative_url }}) lists them.

### What success means

The local PUT returns:

```json
{"uploaded": true, "byte_size": 12345, "attached": false}
```

`attached: false` is expected: storage has the bytes, but the official attachment call still needs to run. Do not call that attachment tool after a failed PUT.

### Limits and recovery

| Constraint | Behavior |
|---|---|
| File size | Official staging accepts files up to 32 MB. The local evidence helper enforces its 32 MB bound too. |
| Signed URL | Expires 15 minutes after staging. |
| Upload ID | Expires after one hour and can be redeemed once. |
| File changed after staging | The helper rejects the size/checksum mismatch before uploading. Prepare and stage again. |
| Reusing evidence for another record | Stage a fresh upload; do not reuse a redeemed ID. |
| Storage redirect or error | The helper does not follow redirects or attach evidence. Check expiry and stage again as needed. |

The signed URL authorizes the storage PUT. Send the raw file bytes with every header returned by staging.

## Questionnaire files

Use one local tool:

```text
upload_security_questionnaire_file(
  file_path="/Users/you/Downloads/questionnaire.xlsx",
  owner_id="<Secureframe owner UUID>",
  company_name="Customer name",
  due_date="2026-11-30",
  questionnaire_template="custom"
)
```

Only `file_path` and `owner_id` are required. See the [reference]({{ '/reference/#upload_security_questionnaire_file' | relative_url }}) for templates and inputs.

The tool streams the file as multipart to `POST /security_questionnaires`, using Claude Code's Secureframe OAuth sign-in.

Questionnaire creation is **not automatically retried**. If the response is interrupted, check whether the questionnaire was created before sending it again, to avoid duplicates.

## Permissions and read-only mode

`SECUREFRAME_READ_ONLY=true` blocks both upload tools; local metadata preparation stays available. The OAuth session carries the signed-in Secureframe user's permissions and selected company.
