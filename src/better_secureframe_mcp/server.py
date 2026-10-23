"""Run the three local upload tools over stdio."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from .supplemental import mcp


def main() -> None:
    load_dotenv(os.getenv("SECUREFRAME_ENV_FILE") or None)
    mcp.run()


if __name__ == "__main__":
    main()
