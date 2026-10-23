"""Run the three local upload tools over stdio."""

from __future__ import annotations

from .supplemental import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
