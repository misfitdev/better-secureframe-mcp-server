"""The shared FastMCP application instance.

Kept in its own module so tool/resource/prompt modules can import ``mcp``
without creating an import cycle with the server entrypoint.
"""

from __future__ import annotations

from fastmcp import FastMCP

INSTRUCTIONS = """\
Read and write access to the Secureframe compliance automation platform
(SOC 2, ISO 27001, CMMC, FedRAMP, HIPAA, and more).

Filtering: list_* tools accept ordinary typed parameters (e.g. health_status,
framework, risk_level) that are compiled into the API's Lucene query for you.
You do not need to write Lucene. Use the `q` parameter only as an advanced
escape hatch for queries the structured parameters cannot express. The
secureframe://reference/* resources document the filterable fields and their
allowed values per resource.

Retrieval: pass auto_paginate=true on list_* tools to fetch every page (the API
caps each page at 100 records). Use `fields` to project only the attributes you
need and keep responses small.

Writes: tools that create/update/archive/delete data are annotated accordingly.
Destructive operations require confirm=true. The whole server can be forced
read-only by setting SECUREFRAME_READ_ONLY=true.

Tool categories (search/discover by these keywords when using deferred loading):
controls, tests, users, user_accounts, devices, risks, frameworks,
framework_requirements, cloud_resources, repositories, vendors, tprm,
integrations, evidence, comments, knowledge_base, questionnaires, trust_center,
framework_asset_scopes. Each resource has list_/get_ read tools; mutating tools
are named create_/update_/archive_/delete_.
"""

mcp = FastMCP(name="Better Secureframe MCP Server", instructions=INSTRUCTIONS)
