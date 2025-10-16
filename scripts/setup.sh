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

echo "\n ✅ Setup complete."
echo "\nTo use dbt, set the profiles directory in your current shell:"
echo "  export DBT_PROFILES_DIR=\"\$PWD/profiles\""
echo "\nOr source this script to keep the environment:"
echo "  source ./scripts/setup.sh"
echo "\nThen run: dbt deps && dbt seed --show && dbt build"