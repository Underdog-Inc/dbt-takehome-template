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

# Install DuckDB CLI if missing
if (-not (Get-Command duckdb -ErrorAction SilentlyContinue)) {
  Write-Host "Installing DuckDB CLI..."
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install DuckDB.cli
  } elseif (Get-Command choco -ErrorAction SilentlyContinue) {
    choco install duckdb
  } else {
    Write-Host "⚠️  Neither winget nor chocolatey found. Skipping DuckDB CLI installation."
    Write-Host "   You can install it manually from: https://duckdb.org/docs/installation/"
  }
}

Write-Host "`n✅ Setup complete."
Write-Host "To activate the virtual environment:"
Write-Host "  . .\\.venv\\Scripts\\Activate.ps1"
Write-Host "To use dbt, the profiles directory will be set automatically."
Write-Host "Then run: uv run dbt deps; uv run dbt build"
Write-Host ""
if (Get-Command duckdb -ErrorAction SilentlyContinue) {
  Write-Host "💡 Query Parquet files directly with DuckDB CLI:"
  Write-Host "  duckdb -c `"SELECT * FROM 'source_data/*.parquet' LIMIT 5;`""
} else {
  Write-Host "💡 To query Parquet files directly, install DuckDB CLI:"
  Write-Host "  Download from https://duckdb.org/docs/installation/"
}