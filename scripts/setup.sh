#!/usr/bin/env bash
set -euo pipefail

# Install uv if missing
if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # ensure uv is on PATH for this session
  export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
fi

# Pin Python (optional): uv will pick a suitable interpreter
# uv python pin 3.11

# Create venv if needed
if [ ! -d .venv ]; then
  echo "Creating .venv with uv..."
  uv venv .venv
fi

# Activate venv
# shellcheck disable=SC1091
source .venv/bin/activate

# Install deps from pyproject
uv pip install -e .

# Ensure dbt profile points to repo-local example
export DBT_PROFILES_DIR="$PWD/profiles"

# First‑run helpers
mkdir -p .dbt
cp -n profiles/profiles.example.yml profiles/profiles.yml 2>/dev/null || true

# Install DuckDB CLI if missing
if ! command -v duckdb >/dev/null 2>&1; then
  echo "Installing DuckDB CLI..."
  if command -v brew >/dev/null 2>&1; then
    brew install duckdb
  else
    echo "⚠️  Homebrew not found. Skipping DuckDB CLI installation."
    echo "   You can install it manually from: https://duckdb.org/docs/installation/"
  fi
fi

echo ""
echo "✅ Setup complete."
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate"
echo "To use dbt, set the profiles directory in your current shell:"
echo "  export DBT_PROFILES_DIR=\"\$PWD/profiles\""
echo "Then run: dbt deps && dbt build"
echo ""
if command -v duckdb >/dev/null 2>&1; then
  echo "💡 Query Parquet files directly with DuckDB CLI:"
  echo "  duckdb -c \"SELECT * FROM 'source_data/*.parquet' LIMIT 5;\""
else
  echo "💡 To query Parquet files directly, install DuckDB CLI:"
  echo "  brew install duckdb  # or download from https://duckdb.org/docs/installation/"
fi