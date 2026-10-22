"""Check local links and anchors in the built Jekyll site."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.duplicates: list[str] = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        anchor = attributes.get("id")
        if anchor:
            if anchor in self.ids:
                self.duplicates.append(anchor)
            self.ids.add(anchor)
        for name in ("href", "src"):
            if attributes.get(name):
                self.links.append(attributes[name])


def check(site: Path, baseurl: str) -> list[str]:
    site = site.resolve()
    pages = {path: Page(path) for path in site.rglob("*.html")}
    errors = []
    if not pages:
        return [f"No built HTML pages in {site}"]
    prefix = baseurl.rstrip("/")
    for path, page in pages.items():
        relative = path.relative_to(site)
        errors.extend(
            f"{relative}: duplicate id #{anchor}" for anchor in page.duplicates
        )
        source_url = f"https://docs.invalid{prefix}/{relative.as_posix()}"
        for link in page.links:
            target = urlsplit(urljoin(source_url, link))
            if target.netloc != "docs.invalid" or target.scheme not in {
                "http",
                "https",
            }:
                continue
            target_path = unquote(target.path)
            if prefix and not target_path.startswith(prefix + "/"):
                errors.append(f"{relative}: link outside site base path: {link}")
                continue
            destination = (site / target_path[len(prefix) :].lstrip("/")).resolve()
            if not destination.is_relative_to(site):
                errors.append(f"{relative}: link outside built site: {link}")
                continue
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_file():
                errors.append(f"{relative}: missing target: {link}")
                continue
            if target.fragment and destination.suffix == ".html":
                anchors = pages.get(destination)
                if anchors is None or unquote(target.fragment) not in anchors.ids:
                    errors.append(f"{relative}: missing anchor: {link}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", nargs="?", type=Path, default=Path("docs/_site"))
    parser.add_argument("--baseurl", default="/better-secureframe-mcp-server")
    args = parser.parse_args()
    errors = check(args.site, args.baseurl)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(
        f"Docs links and anchors passed ({len(list(args.site.rglob('*.html')))} pages)."
    )


if __name__ == "__main__":
    main()
