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

# Run the MCP server over stdio
run:
    python main.py

# Re-vendor the OpenAPI spec from the live docs
refresh-spec:
    curl -s https://api.secureframe.com/docs/openapi.json \
      | sed -n '/^openapi:/,/<\/script>/p' \
      | sed '/<\/script>/d' > docs/openapi.yaml
    @echo "Wrote docs/openapi.yaml"
