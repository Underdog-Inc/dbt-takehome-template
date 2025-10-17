#!/usr/bin/env bash
set -euo pipefail

# Install uv if missing
if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # ensure uv is on PATH for this session
  export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
fi

# Install DuckDB CLI if missing (macOS/Linux)
if ! command -v duckdb >/dev/null 2>&1; then
  echo "Installing DuckDB CLI..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew >/dev/null 2>&1; then
      brew install duckdb
    else
      echo "⚠️  Homebrew not found. Please install DuckDB manually from https://duckdb.org/docs/installation/"
    fi
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - download binary
    echo "Downloading DuckDB CLI for Linux..."
    curl -L https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip -o /tmp/duckdb.zip
    unzip -o /tmp/duckdb.zip -d /tmp/
    sudo mv /tmp/duckdb /usr/local/bin/
    chmod +x /usr/local/bin/duckdb
    rm /tmp/duckdb.zip
  else
    echo "⚠️  Unsupported OS for automatic DuckDB installation. Please install manually from https://duckdb.org/docs/installation/"
  fi
else
  echo "✅ DuckDB CLI already installed"
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

echo "\n ✅ Setup complete."
echo "\nTo use dbt, set the profiles directory in your current shell:"
echo "  export DBT_PROFILES_DIR=\"\$PWD/profiles\""
echo "\nOr source this script to keep the environment:"
echo "  source ./scripts/setup.sh"
echo "\nThen run: dbt deps && dbt seed --show && dbt build"
echo "\n💡 You can also query CSV files directly with DuckDB:"
echo "  duckdb -c \"SELECT * FROM 'seeds/users.csv' LIMIT 5;\""