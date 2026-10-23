# Project tasks. The toolchain and environment are provided by mise (see mise.toml).

# List available recipes
default:
    @just --list

# Install dependencies and git hooks
setup: install
    lefthook install

# Install runtime + dev dependencies into the active environment
install:
    uv pip install -e ".[dev]"

# Lint with ruff
lint:
    ruff check .

# Auto-format and apply safe fixes
fmt:
    ruff check --fix .
    ruff format .

# Check formatting without modifying files
check-fmt:
    ruff format --check .

# Run the test suite
test:
    pytest -q

# Build sdist and wheel, then validate
build:
    python -m build
    twine check dist/*

# Build the GitHub Pages documentation (Ruby + bundle install required).
docs-build:
    bundle exec jekyll build --source docs --destination docs/_site --strict_front_matter

# Validate links and anchors in the rendered documentation.
docs-check: docs-build
    python3 scripts/check_docs.py

# Run the MCP server over stdio
run:
    python main.py
