#!/usr/bin/env python3
"""Convenience launcher for Claude Desktop / Cursor configs that point at a file.

The implementation lives in the ``better_secureframe_mcp`` package; after
``pip install -e .`` the ``better-secureframe-mcp`` console script is equivalent.
"""

from better_secureframe_mcp.server import main

if __name__ == "__main__":
    main()
