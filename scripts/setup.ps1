#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

# Install uv if missing
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  Write-Host "Installing uv..."
  Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing | Invoke-Expression
}

# Optional: pin Python
# uv python pin 3.11

# Create venv if needed
if (-not (Test-Path ".venv")) {
  Write-Host "Creating .venv with uv..."
  uv venv .venv
}

# Install deps
uv pip install -e .

# Point dbt to repo-local profile
$env:DBT_PROFILES_DIR = (Join-Path (Get-Location) "profiles")

if (-not (Test-Path "profiles/profiles.yml")) {
  Copy-Item "profiles/profiles.example.yml" "profiles/profiles.yml"
}

Write-Host "`n✅ Setup complete. Activate with: . .\\.venv\\Scripts\\Activate.ps1"
Write-Host "Then run: uv run dbt deps; uv run dbt seed --show; uv run dbt build"
Write-Host "`n💡 You can also query CSV files directly with DuckDB CLI (via uvx):"
Write-Host "  uvx duckdb -c `"SELECT * FROM 'seeds/users.csv' LIMIT 5;`""