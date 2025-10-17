#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

# Install uv if missing
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  Write-Host "Installing uv..."
  Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing | Invoke-Expression
}

# Install DuckDB CLI if missing (Windows)
if (-not (Get-Command duckdb -ErrorAction SilentlyContinue)) {
  Write-Host "Installing DuckDB CLI..."
  $duckdbUrl = "https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-windows-amd64.zip"
  $tempZip = Join-Path $env:TEMP "duckdb.zip"
  $installDir = Join-Path $env:LOCALAPPDATA "duckdb"
  
  Invoke-WebRequest -Uri $duckdbUrl -OutFile $tempZip
  Expand-Archive -Path $tempZip -DestinationPath $installDir -Force
  Remove-Item $tempZip
  
  # Add to PATH for this session
  $env:Path = "$installDir;$env:Path"
  
  Write-Host "✅ DuckDB CLI installed to $installDir"
  Write-Host "⚠️  Add $installDir to your PATH permanently in System Environment Variables"
} else {
  Write-Host "✅ DuckDB CLI already installed"
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
Write-Host "`n💡 You can also query CSV files directly with DuckDB:"
Write-Host "  duckdb -c `"SELECT * FROM 'seeds/users.csv' LIMIT 5;`""